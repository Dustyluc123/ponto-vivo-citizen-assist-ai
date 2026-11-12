/*
  Ponto Vivo - Assistente Inteligente de Filas de Atendimento
  Arquitetura e Organizacao de Computadores - FIAP Global Solution 2026.2
  Lucas Barreto Santana - RM 573149 - 1CCPG

  O que o programa faz:
    - Botao ENTRADA soma uma pessoa a fila; botao ATENDER tira uma (nunca fica negativa).
    - Estima a espera com 1-NN (vizinho mais proximo) numa tabela de exemplos.
    - Mostra fila e espera no LCD 16x2 (I2C) e acende LED verde (fila curta)
      ou vermelho (fila longa).
    - A cada mudanca da fila, publica um JSON via MQTT pelo Wi-Fi.
    - Registra eventos, previsoes e estado da conexao no monitor serial.

  Os tempos da tabela sao ficticios (do enunciado) e nao representam
  servicos publicos reais.
*/

#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// ============================================================
// 1. Configuracao (constantes: o compilador grava na Flash)
// ============================================================

// GPIO usados
const uint8_t PINO_ENTRADA  = 18;  // botao ENTRADA (liga no GND, usa pull-up interno)
const uint8_t PINO_ATENDER  = 19;  // botao ATENDER
const uint8_t PINO_LED_VERDE    = 25;
const uint8_t PINO_LED_VERMELHO = 26;
// I2C do LCD: SDA = GPIO 21, SCL = GPIO 22 (padrao do ESP32)

// Regras da fila
const uint8_t LIMIAR_FILA_LONGA = 7;    // 7 ou mais = fila longa (LED vermelho): espera estimada acima de 20 min
const uint8_t FILA_MAXIMA       = 99;   // limite para caber no display
const unsigned long DEBOUNCE_MS = 50;   // tempo para o sinal do botao estabilizar

// Rede (o Wokwi oferece a rede aberta "Wokwi-GUEST")
const char* WIFI_REDE   = "Wokwi-GUEST";
const char* WIFI_SENHA  = "";
const char* MQTT_BROKER = "broker.hivemq.com";
const uint16_t MQTT_PORTA = 1883;
const char* DISPOSITIVO = "fila01";
const char* TOPICO      = "fiap/gs2026/pontovivo/fila01";
const unsigned long INTERVALO_RECONEXAO_MS = 5000;

// Tabela de exemplos do 1-NN: pessoas na fila -> tempo observado (min).
// E const, entao fica na Flash junto com o codigo (somente leitura).
struct Exemplo {
  uint8_t pessoas;
  uint8_t minutos;
};

const Exemplo EXEMPLOS[] = {
  {0, 0}, {2, 6}, {4, 12}, {6, 18}, {8, 25}, {10, 32}
};
const uint8_t TOTAL_EXEMPLOS = sizeof(EXEMPLOS) / sizeof(EXEMPLOS[0]);
const uint8_t MAIOR_EXEMPLO  = 10;  // acima disso, a estimativa sai da faixa

// ============================================================
// 2. Estado do programa (variaveis globais: ficam na RAM)
// ============================================================

int fila = 0;  // pessoas aguardando; so muda por entrarNaFila() e atender()

struct Previsao {
  uint8_t minutos;      // tempo do exemplo escolhido
  uint8_t vizinho;      // quantidade de pessoas do exemplo escolhido
  uint8_t distancia;    // |fila - vizinho|
  bool empate;          // dois exemplos a mesma distancia
  bool foraDaFaixa;     // fila maior que o maior exemplo
};
Previsao previsao;

struct Botao {
  uint8_t pino;
  const char* nome;
  bool leituraAnterior;        // ultima leitura bruta do pino
  bool estadoEstavel;          // estado aceito depois do debounce
  unsigned long ultimaMudanca; // quando a leitura bruta mudou pela ultima vez
};
Botao botaoEntrada = {PINO_ENTRADA, "ENTRADA", HIGH, HIGH, 0};
Botao botaoAtender = {PINO_ATENDER, "ATENDER", HIGH, HIGH, 0};

LiquidCrystal_I2C lcd(0x27, 16, 2);  // endereco I2C 0x27, 16 colunas, 2 linhas
WiFiClient redeTcp;
PubSubClient mqtt(redeTcp);

bool wifiConectadoAntes = false;
bool envioPendente = true;              // publica o estado inicial quando conectar
unsigned long ultimaTentativaMqtt = 0;
unsigned long ultimaTrocaAviso = 0;
bool mostrandoAviso = false;            // alterna a 2a linha quando fora da faixa

// ============================================================
// 3. Entrada: leitura dos botoes com debounce
// ============================================================

// Devolve true uma unica vez por aperto. Com INPUT_PULLUP o pino fica em
// HIGH (3,3 V) solto e vai para LOW (0 V) quando o botao liga ao GND.
// O contato mecanico "quica" e gera varias transicoes em poucos ms; so
// aceitamos a mudanca depois que a leitura fica igual por DEBOUNCE_MS.
bool foiPressionado(Botao &botao) {
  bool leitura = digitalRead(botao.pino);
  unsigned long agora = millis();

  if (leitura != botao.leituraAnterior) {
    botao.leituraAnterior = leitura;
    botao.ultimaMudanca = agora;
  }

  if (agora - botao.ultimaMudanca >= DEBOUNCE_MS && leitura != botao.estadoEstavel) {
    botao.estadoEstavel = leitura;
    return leitura == LOW;  // conta so a borda de descida (aperto), nao a soltura
  }
  return false;
}

// ============================================================
// 4. IA introdutoria: 1-NN (vizinho mais proximo)
// ============================================================

// Percorre os exemplos e escolhe o de quantidade mais proxima da fila.
// Criterio de desempate: em distancias iguais, fica o exemplo de MAIOR
// tempo (estimativa pessimista). Para o cidadao, esperar menos que o
// previsto e melhor do que esperar mais.
Previsao preverEspera(int pessoas) {
  Previsao resultado = {0, 0, 255, false, false};

  for (uint8_t i = 0; i < TOTAL_EXEMPLOS; i++) {
    int distancia = abs(pessoas - EXEMPLOS[i].pessoas);

    if (distancia < resultado.distancia) {
      resultado.distancia = distancia;
      resultado.vizinho = EXEMPLOS[i].pessoas;
      resultado.minutos = EXEMPLOS[i].minutos;
      resultado.empate = false;
    } else if (distancia == resultado.distancia) {
      resultado.empate = true;
      if (EXEMPLOS[i].minutos > resultado.minutos) {
        resultado.vizinho = EXEMPLOS[i].pessoas;
        resultado.minutos = EXEMPLOS[i].minutos;
      }
    }
  }

  resultado.foraDaFaixa = pessoas > MAIOR_EXEMPLO;
  return resultado;
}

// ============================================================
// 5. Saida: LCD (I2C), LEDs e monitor serial
// ============================================================

void atualizarLeds() {
  bool filaLonga = fila >= LIMIAR_FILA_LONGA;
  digitalWrite(PINO_LED_VERDE, filaLonga ? LOW : HIGH);
  digitalWrite(PINO_LED_VERMELHO, filaLonga ? HIGH : LOW);
}

void escreverLinha(uint8_t linha, const char* texto) {
  char buffer[17];
  snprintf(buffer, sizeof(buffer), "%-16s", texto);  // completa com espacos
  lcd.setCursor(0, linha);
  lcd.print(buffer);
}

void atualizarDisplay() {
  char linha[17];
  snprintf(linha, sizeof(linha), "Fila: %d %s", fila, fila == 1 ? "pessoa" : "pessoas");
  escreverLinha(0, linha);

  if (previsao.foraDaFaixa && mostrandoAviso) {
    escreverLinha(1, "Fora da faixa!");
  } else if (previsao.foraDaFaixa) {
    snprintf(linha, sizeof(linha), "Espera: +%d min", previsao.minutos);
    escreverLinha(1, linha);
  } else {
    snprintf(linha, sizeof(linha), "Espera: %d min", previsao.minutos);
    escreverLinha(1, linha);
  }
}

void registrarPrevisao() {
  Serial.printf("[1-NN] fila=%d -> vizinho=%d pessoas (distancia %d) -> %d min\n",
                fila, previsao.vizinho, previsao.distancia, previsao.minutos);
  if (previsao.empate) {
    Serial.println("[1-NN] empate entre dois exemplos: escolhido o de maior tempo (pessimista)");
  }
  if (previsao.foraDaFaixa) {
    Serial.printf("[1-NN] AVISO: fila acima de %d pessoas, fora da faixa dos exemplos. "
                  "Espera real deve ser maior que %d min.\n", MAIOR_EXEMPLO, previsao.minutos);
  }
}

// ============================================================
// 6. Regras da fila
// ============================================================

// Chamada sempre que a fila muda: recalcula, mostra e agenda o envio.
void filaMudou(const char* evento) {
  previsao = preverEspera(fila);
  mostrandoAviso = false;
  ultimaTrocaAviso = millis();
  Serial.printf("[EVENTO] %s -> fila=%d\n", evento, fila);
  registrarPrevisao();
  atualizarDisplay();
  atualizarLeds();
  envioPendente = true;
}

void entrarNaFila() {
  if (fila >= FILA_MAXIMA) {
    Serial.println("[EVENTO] ENTRADA ignorada: fila no limite do display (99)");
    return;
  }
  fila++;
  filaMudou("ENTRADA");
}

void atender() {
  if (fila == 0) {
    Serial.println("[EVENTO] ATENDER ignorado: fila vazia (permanece em 0)");
    return;  // regra: a fila nunca fica negativa
  }
  fila--;
  filaMudou("ATENDER");
}

// ============================================================
// 7. Wi-Fi e MQTT (IoT)
// ============================================================

void verificarWifi() {
  bool conectado = WiFi.status() == WL_CONNECTED;
  if (conectado && !wifiConectadoAntes) {
    Serial.print("[WIFI] conectado, IP ");
    Serial.println(WiFi.localIP());
  } else if (!conectado && wifiConectadoAntes) {
    Serial.println("[WIFI] conexao perdida, tentando de novo...");
  }
  wifiConectadoAntes = conectado;
}

// Tenta conectar ao broker sem travar a fila: uma tentativa a cada 5 s.
void verificarMqtt() {
  if (WiFi.status() != WL_CONNECTED || mqtt.connected()) return;
  if (millis() - ultimaTentativaMqtt < INTERVALO_RECONEXAO_MS) return;
  ultimaTentativaMqtt = millis();

  char idCliente[32];
  snprintf(idCliente, sizeof(idCliente), "pontovivo-%06lx", (unsigned long)(ESP.getEfuseMac() & 0xFFFFFF));
  Serial.printf("[MQTT] conectando a %s...\n", MQTT_BROKER);
  if (mqtt.connect(idCliente)) {
    Serial.println("[MQTT] conectado");
    envioPendente = true;  // manda o estado atual logo apos conectar
  } else {
    Serial.printf("[MQTT] falhou (codigo %d), nova tentativa em 5 s\n", mqtt.state());
  }
}

void enviarEstado() {
  if (!envioPendente || !mqtt.connected()) return;

  char mensagem[128];
  snprintf(mensagem, sizeof(mensagem),
           "{\"dispositivo\":\"%s\",\"pessoas_na_fila\":%d,\"espera_min\":%d,\"fora_da_faixa\":%s}",
           DISPOSITIVO, fila, previsao.minutos, previsao.foraDaFaixa ? "true" : "false");

  // retain = true: quem assinar o topico depois recebe o ultimo estado
  if (mqtt.publish(TOPICO, mensagem, true)) {
    Serial.printf("[MQTT] enviado em %s: %s\n", TOPICO, mensagem);
    envioPendente = false;
  } else {
    Serial.println("[MQTT] falha ao publicar, tenta de novo no proximo ciclo");
  }
}

// ============================================================
// 8. Onde cada coisa esta na memoria (evidencia para o relatorio)
// ============================================================

void mostrarMapaDeMemoria() {
  Serial.println("------------------------------------------------");
  Serial.printf("[CPU]   %s, %d nucleos, %lu MHz\n",
                ESP.getChipModel(), ESP.getChipCores(), (unsigned long)ESP.getCpuFreqMHz());
  Serial.printf("[RAM]   variavel fila       em 0x%08lX\n", (unsigned long)(uintptr_t)&fila);
  Serial.printf("[RAM]   struct previsao     em 0x%08lX\n", (unsigned long)(uintptr_t)&previsao);
  Serial.printf("[FLASH] tabela EXEMPLOS     em 0x%08lX\n", (unsigned long)(uintptr_t)EXEMPLOS);
  Serial.printf("[FLASH] funcao preverEspera em 0x%08lX\n", (unsigned long)(uintptr_t)&preverEspera);
  Serial.printf("[RAM]   heap livre: %lu bytes\n", (unsigned long)ESP.getFreeHeap());
  Serial.println("------------------------------------------------");
}

// ============================================================
// 9. setup() e loop()
// ============================================================

void setup() {
  Serial.begin(115200);
  delay(200);
  Serial.println();
  Serial.println("Ponto Vivo - fila de atendimento (ESP32 + 1-NN + MQTT)");
  mostrarMapaDeMemoria();

  pinMode(PINO_ENTRADA, INPUT_PULLUP);
  pinMode(PINO_ATENDER, INPUT_PULLUP);
  pinMode(PINO_LED_VERDE, OUTPUT);
  pinMode(PINO_LED_VERMELHO, OUTPUT);

  Wire.begin(21, 22);  // SDA, SCL
  lcd.init();
  lcd.backlight();

  filaMudou("INICIO");  // teste 1: fila = 0 e espera = 0

  // Wi-Fi em segundo plano: a fila funciona mesmo antes de conectar
  Serial.printf("[WIFI] conectando a %s...\n", WIFI_REDE);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_REDE, WIFI_SENHA, 6);  // canal 6 acelera a conexao no Wokwi
  mqtt.setServer(MQTT_BROKER, MQTT_PORTA);
}

void loop() {
  // Entrada
  if (foiPressionado(botaoEntrada)) entrarNaFila();
  if (foiPressionado(botaoAtender)) atender();

  // Fora da faixa: alterna a 2a linha entre a espera e o aviso a cada 2 s
  if (previsao.foraDaFaixa && millis() - ultimaTrocaAviso >= 2000) {
    mostrandoAviso = !mostrandoAviso;
    ultimaTrocaAviso = millis();
    atualizarDisplay();
  }

  // Comunicacao
  verificarWifi();
  verificarMqtt();
  mqtt.loop();
  enviarEstado();

  delay(5);  // pequena pausa; o debounce usa millis(), nao delay
}
