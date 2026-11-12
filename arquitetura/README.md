<h1 align="center">Ponto Vivo — Fila Inteligente</h1>

<p align="center">
  <strong>Contribuição de Arquitetura e Organização de Computadores ao Citizen Assist AI.</strong><br />
  Fila de atendimento simulada no Wokwi com ESP32: contagem por botões, previsão de espera com 1-NN e envio dos dados por MQTT.
</p>

<p align="center">
  <img alt="ESP32" src="https://img.shields.io/badge/ESP32-DevKit_C-e7352c?logo=espressif&logoColor=white" />
  <img alt="Arduino" src="https://img.shields.io/badge/Arduino-C%2B%2B-00979d?logo=arduino&logoColor=white" />
  <img alt="Wokwi" src="https://img.shields.io/badge/simula%C3%A7%C3%A3o-Wokwi-6f42c1" />
  <img alt="MQTT" src="https://img.shields.io/badge/IoT-MQTT-660066?logo=mqtt&logoColor=white" />
</p>

> Esta pasta contém **apenas** a contribuição da disciplina de Arquitetura e Organização de Computadores. O assistente principal está na [raiz do repositório](../README.md).

---

## Índice

- [Integrante](#integrante)
- [Resumo](#resumo)
- [Circuito](#circuito)
- [Como funciona](#como-funciona)
- [Previsão com 1-NN](#previsão-com-1-nn)
- [Comunicação IoT](#comunicação-iot)
- [Testes](#testes)
- [Como executar](#como-executar)
- [Limitações](#limitações)

## Integrante

| Nome                  | RM     |
| --------------------- | ------ |
| Lucas Barreto Santana | 573149 |

## Resumo

Um ESP32 controla uma fila virtual de atendimento. O botão **ENTRADA** soma uma pessoa e o botão **ATENDER** tira uma. A cada mudança, o programa estima o tempo de espera procurando o exemplo mais parecido numa tabela (algoritmo 1-NN). O resultado aparece no display LCD, nos LEDs e no monitor serial, e é enviado pela internet para um servidor MQTT.

**Projeto no Wokwi:** https://wokwi.com/projects/480447178434064385

O relatório completo (5 páginas, com as capturas dos testes) está em [`relatorio_arquitetura.pdf`](relatorio_arquitetura.pdf), e as capturas também estão em [`evidencias/`](evidencias/).

## Circuito

| Componente | Ligação no ESP32 | Função |
| ---------- | ---------------- | ------ |
| Botão ENTRADA (verde) | GPIO 18 e GND | Soma uma pessoa |
| Botão ATENDER (azul) | GPIO 19 e GND | Tira uma pessoa |
| LCD 16×2 com I²C | SDA = GPIO 21, SCL = GPIO 22, 5 V, GND | Mostra fila e espera |
| LED verde + resistor 220 Ω | GPIO 25 | Fila curta (até 6 pessoas) |
| LED vermelho + resistor 220 Ω | GPIO 26 | Fila longa (7 pessoas ou mais) |

Os botões usam o **resistor de pull-up interno** do ESP32: o pino fica em 3,3 V (HIGH) com o botão solto e vai a 0 V (LOW) quando ele é apertado.

## Como funciona

```
BOTÕES ──GPIO──► ESP32 (CPU + RAM + Flash) ──► 1-NN ──┬──► LCD (I²C) e LEDs (GPIO)
                                                      └──► Wi-Fi ──► broker MQTT ──► receptor IoT
```

| Elemento | Onde está no código |
| -------- | ------------------- |
| Entrada / GPIO | `foiPressionado()`: lê o pino e aplica o debounce de 50 ms com `millis()` |
| CPU | `loop()` lê os botões, `entrarNaFila()` e `atender()` contam, `preverEspera()` faz a busca 1-NN |
| RAM | `fila`, `previsao` e o estado dos botões (variáveis globais); `distancia` e `resultado` (pilha) |
| Flash | o código e a tabela `EXEMPLOS`, declarada como `const` |
| Saída / I²C | `atualizarDisplay()` envia o texto ao LCD pelo barramento I²C |
| Wi-Fi | `verificarWifi()`, `verificarMqtt()` e `enviarEstado()` |

Ao ligar, o programa mostra no serial onde cada coisa ficou na memória. Na simulação:

```
[CPU]   ESP32-D0WDQ6-V3, 2 nucleos, 240 MHz
[RAM]   variavel fila       em 0x3FFC3A2C
[FLASH] tabela EXEMPLOS     em 0x3F410AC5
[FLASH] funcao preverEspera em 0x400D27C4
```

Endereços começando em `0x3FF` são da RAM interna; `0x3F4` e `0x400D` são regiões da Flash lidas pela CPU através da cache.

**Regras da fila:** a fila nunca fica negativa (ATENDER com fila vazia é ignorado e registrado no serial) e tem limite de 99 pessoas, para caber no display. Segurar o botão conta uma vez só, porque o programa reage apenas à borda de descida do sinal.

## Previsão com 1-NN

| Pessoas na fila | 0 | 2 | 4 | 6 | 8 | 10 |
| --------------- | - | - | - | - | - | -- |
| Espera (min)    | 0 | 6 | 12 | 18 | 25 | 32 |

O programa calcula a distância `|fila − pessoas do exemplo|` para os seis exemplos e fica com o menor.

- **Desempate:** com número ímpar de pessoas, dois exemplos ficam à mesma distância (com 5, os de 4 e 6). O programa escolhe o de **maior tempo**. É uma estimativa pessimista: para o cidadão, ser atendido antes do previsto é melhor do que esperar mais do que foi prometido.
- **Fora da faixa:** acima de 10 pessoas, o vizinho mais próximo é sempre o de 10 (32 min). O display mostra `+32 min` alternando com `Fora da faixa!`, o serial avisa que a espera real deve ser maior e o JSON leva `"fora_da_faixa": true`.

## Comunicação IoT

A cada mudança da fila, o ESP32 publica por **MQTT** no broker público `broker.hivemq.com` (porta 1883), tópico `fiap/gs2026/pontovivo/fila01`:

```json
{"dispositivo":"fila01","pessoas_na_fila":4,"espera_min":12,"fora_da_faixa":false}
```

A mensagem vai com `retain`, então quem assinar o tópico depois recebe o último estado. A conexão não trava a fila: se o Wi-Fi ou o broker caírem, os botões continuam funcionando, o programa tenta reconectar a cada 5 segundos e envia o estado atual assim que volta.

Para ver as mensagens chegando, abra o [cliente MQTT da HiveMQ](https://www.hivemq.com/demos/websocket-client/), clique em **Connect** e assine o tópico `fiap/gs2026/pontovivo/#`.

## Testes

| Teste | Ação | Esperado | Obtido |
| ----- | ---- | -------- | ------ |
| 1 | Iniciar o sistema | Fila = 0; espera = 0 | `Fila: 0 pessoas` / `Espera: 0 min`, LED verde |
| 2 | ENTRADA 4 vezes | Fila = 4; 12 min | `Fila: 4 pessoas` / `Espera: 12 min` |
| 3 | ATENDER uma vez | Fila = 3; nova previsão | `Fila: 3 pessoas` / `Espera: 12 min` (empate 2 e 4, fica o maior) |
| 4 | ATENDER com fila vazia | Fila continua 0 | Fila 0 e `ATENDER ignorado: fila vazia` no serial |
| 5 | Chegar a 8 pessoas | LED de fila longa | `Espera: 25 min`, LED vermelho aceso e verde apagado (o vermelho acende já com 7) |
| 6 | Mudar a fila com Wi-Fi ativo | Mensagem recebida no serviço IoT | JSON recebido no cliente MQTT da HiveMQ |
| Extra | Chegar a 11 pessoas | Aviso de fora da faixa | `Espera: +32 min` alternando com `Fora da faixa!` |

As capturas de tela de cada teste estão no relatório.

## Como executar

1. Abra o link do projeto no Wokwi e clique em **Start the simulation** (botão verde).
2. Espere aparecer `[MQTT] conectado` no monitor serial.
3. Clique nos botões ENTRADA e ATENDER e acompanhe o LCD, os LEDs e o serial.

Para montar do zero: crie um projeto ESP32 em [wokwi.com](https://wokwi.com/projects/new/esp32), cole o conteúdo de [`sketch/sketch.ino`](sketch/sketch.ino) e [`diagram.json`](diagram.json) e adicione as bibliotecas de [`libraries.txt`](libraries.txt) no Library Manager.

## Limitações

- Os tempos da tabela são fictícios (do enunciado) e não representam um serviço público real.
- A fila fica na RAM e volta a zero se o ESP32 reiniciar.
- O broker público não tem senha nem criptografia: serve para teste, não para dados reais.
- Com poucos exemplos, a previsão anda em degraus. Exemplos medidos de verdade e mais pontos na tabela melhorariam a estimativa.
