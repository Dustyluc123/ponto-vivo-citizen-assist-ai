"""Classe Assistente: quem conversa com o passageiro.
Faz o atendimento, guarda o histórico e calcula os indicadores."""

import csv
import json
import time
from datetime import datetime

import tela
from base_conhecimento import LIMITE_MEDIA, confianca

CAMINHO_HISTORICO = "data/historico.json"
CAMINHO_CSV = "data/atendimentos.csv"
CAMINHO_ENERGIA = "energia/resultados.json"  # gerado por energia/calculos.py

# Colunas do histórico e do CSV
CAMPOS_ATENDIMENTO = ["data", "origem", "pergunta", "id_orientacao", "encontrou",
                      "ajudou", "tentativas", "tempo_segundos", "facilidade"]

MINIMO_DIGITOS_DADO_PESSOAL = 8
MAXIMO_ALTERNATIVAS = 2


# ---------- Funções de apoio para ler o teclado sem travar ----------

def ler_opcao(mensagem, minimo, maximo):
    """Pede um número entre minimo e maximo. Repete até a resposta ser válida."""
    while True:
        texto = input(mensagem).strip()
        if not texto:
            tela.erro("Resposta vazia. Digite um número.")
            continue
        if not texto.isdigit():
            tela.erro(f"'{texto}' não é um número. Digite um número de {minimo} a {maximo}.")
            continue
        numero = int(texto)
        if numero < minimo or numero > maximo:
            tela.erro(f"Opção fora da faixa. Digite um número de {minimo} a {maximo}.")
            continue
        return numero


def ler_sim_nao(mensagem):
    """Pede s ou n. Repete até a resposta ser válida. Devolve True para sim."""
    while True:
        texto = input(mensagem).strip().lower()
        if texto in ("s", "sim"):
            return True
        if texto in ("n", "nao", "não"):
            return False
        tela.erro("Resposta inválida. Digite s para sim ou n para não.")


def tem_dado_pessoal(texto):
    """True se o texto parece ter CPF, telefone ou e-mail (8+ dígitos ou @)."""
    digitos = sum(1 for caractere in texto if caractere.isdigit())
    return digitos >= MINIMO_DIGITOS_DADO_PESSOAL or "@" in texto


# ---------- Classe ----------

class Assistente:
    def __init__(self, nome, base, caminho_historico=CAMINHO_HISTORICO, caminho_csv=CAMINHO_CSV):
        self.nome = nome
        self.base = base                      # objeto BaseConhecimento (composição)
        self.caminho_historico = caminho_historico
        self.caminho_csv = caminho_csv
        self.historico = self._carregar_historico()
        self.inicio_sessao = len(self.historico)  # atendimentos desta execução começam aqui

    # ----- Atendimento -----

    def perguntar(self):
        """Recebe dúvidas em texto livre e mostra a melhor orientação + até 2 alternativas.
        Um atendimento pode ter várias tentativas, até a pessoa achar a resposta ou voltar."""
        inicio = time.time()
        tentativas = 0
        ultima_sem_resposta = ""

        while True:
            pergunta = input("\n" + tela.cor("Digite sua dúvida", "negrito") + tela.cor(" (0 para voltar)", "apagado") + ": ").strip()

            if pergunta == "0":
                # Saiu sem encontrar: registra como dúvida sem solução
                if tentativas > 0:
                    tempo = round(time.time() - inicio, 1)
                    self.registrar("pergunta", ultima_sem_resposta, None, False, False, tentativas, tempo)
                return

            if not pergunta:
                tela.erro("Você não digitou nada. Escreva sua dúvida ou 0 para voltar.")
                continue

            if tem_dado_pessoal(pergunta):
                # Não conta como tentativa e não é registrado
                tela.aviso("Atenção: não digite CPF, telefone ou e-mail. Reescreva sua dúvida.")
                continue

            tentativas += 1
            resultados = self.base.buscar(pergunta)

            if not resultados or resultados[0][0] < LIMITE_MEDIA:
                ultima_sem_resposta = pergunta
                print()
                tela.aviso("Não encontrei uma orientação para essa dúvida.")
                tela.dica("Tente outras palavras, por exemplo: idoso, estudante, domingo, recarga, calor.")
                tela.dica("Ou volte (0) e navegue pelas categorias: " + ", ".join(self.base.categorias()) + ".")
                continue

            pontos, melhor = resultados[0]
            print("\n" + tela.selo_confianca(confianca(pontos), pontos))
            melhor.exibir()

            alternativas = [(p, o) for p, o in resultados[1:] if p >= LIMITE_MEDIA][:MAXIMO_ALTERNATIVAS]
            if alternativas:
                tela.secao("Outras orientações que podem ajudar")
                for p, o in alternativas:
                    print("    • " + o.titulo + tela.cor(f"  ({p} pontos)", "apagado"))

            ajudou = ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
            tempo = round(time.time() - inicio, 1)
            self.registrar("pergunta", pergunta, melhor, True, ajudou, tentativas, tempo)

            if not ajudou:
                tela.dica("Obrigado por avisar. Tente perguntar de outro jeito ou navegue pelas categorias.")

            # Começa um novo atendimento
            inicio = time.time()
            tentativas = 0
            ultima_sem_resposta = ""

    def navegar(self):
        """Lista categorias e orientações numeradas, com '0 para voltar' em todas as telas."""
        categorias = self.base.categorias()

        while True:
            print()
            tela.caixa([("Categorias", ("negrito",))])
            for numero, categoria in enumerate(categorias, start=1):
                print(f"  {tela.cor(str(numero), 'ciano', 'negrito')}  {categoria}")
            print(f"  {tela.cor('0', 'ciano', 'negrito')}  " + tela.cor("Voltar", "apagado"))
            escolha = ler_opcao("Escolha uma categoria: ", 0, len(categorias))
            if escolha == 0:
                return

            categoria = categorias[escolha - 1]
            inicio = time.time()
            orientacoes = self.base.por_categoria(categoria)

            while True:
                print()
                tela.caixa([(categoria, ("negrito",))])
                for numero, orientacao in enumerate(orientacoes, start=1):
                    print(f"  {tela.cor(str(numero), 'ciano', 'negrito')}  {orientacao.titulo}")
                print(f"  {tela.cor('0', 'ciano', 'negrito')}  " + tela.cor("Voltar", "apagado"))
                escolha = ler_opcao("Escolha uma orientação: ", 0, len(orientacoes))
                if escolha == 0:
                    break

                orientacao = orientacoes[escolha - 1]
                orientacao.exibir()
                ajudou = ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
                tempo = round(time.time() - inicio, 1)
                self.registrar("categoria", categoria, orientacao, True, ajudou, 1, tempo)
                inicio = time.time()

    def energia(self):
        """Mostra a análise de energia do abrigo (contribuição de Energias Renováveis).
        Os números vêm de energia/resultados.json, gerado por energia/calculos.py."""
        try:
            with open(CAMINHO_ENERGIA, "r", encoding="utf-8") as arquivo:
                r = json.load(arquivo)
        except (FileNotFoundError, json.JSONDecodeError):
            tela.erro("Análise de energia não encontrada. Rode: python energia/calculos.py")
            return

        clima, consumo, solar = r["clima"], r["consumo_kwh_ano"], r["solar"]
        custos, onibus = r["custos_10_anos_r"], r["onibus_x_carro"]

        print()
        tela.caixa([("Energia do Ponto Vivo", ("negrito",)),
                    ("Como alimentar o ventilador e a eletrônica do abrigo", ("apagado",))])

        tela.secao("Quando o ventilador precisa ligar")
        print(tela.quebrar(f"Em 2025, São Paulo teve {clima['horas_quentes_ano']} horas com "
                           f"{clima['temperatura_liga_c']} °C ou mais (das 5h às 23h), em "
                           f"{clima['dias_quentes_ano']} dias. Ligando só nessas horas, o ventilador gasta "
                           f"{tela.numero(consumo['economia_controle_pct'])}% menos energia do que num timer das 10h às 18h.", 4))

        tela.secao("Comparação em 10 anos")
        linhas = [
            ("Solar + bateria (ponto sem energia)", custos["solar_com_bateria"]),
            ("Rede elétrica (ponto sem energia)", custos["rede_ponto_sem_energia"]),
            ("Rede elétrica (ponto que já tem energia)", custos["rede_ponto_com_energia"]),
        ]
        for nome, valor in linhas:
            print(f"    {nome:<42}" + tela.cor(f"R$ {tela.numero(valor, 0)}", "ciano", "negrito"))
        print(tela.quebrar(f"Sistema solar: painel de {solar['painel_w']} W e bateria de "
                           f"{solar['bateria_ah']} Ah. A rede cobra no mínimo 30 kWh por mês "
                           f"(R$ {tela.numero(custos['conta_minima_mes'], 2)} com impostos), mesmo o ponto gastando "
                           f"cerca de {tela.numero(consumo['total_inteligente'] / 12)} kWh.", 4))

        tela.secao("Recomendação")
        print(tela.quebrar("Ponto sem energia: usar solar com bateria. Sai mais barato que fazer uma "
                           "ligação nova e continua funcionando quando falta luz.", 4))
        print(tela.quebrar("Ponto que já tem energia: usar a rede, com o ventilador ligando só "
                           "com calor e gente esperando.", 4))

        tela.secao("Você também pode ajudar")
        print(tela.quebrar(f"Trocar o carro pelo ônibus em {onibus['km_mes']} km por mês evita cerca de "
                           f"{tela.numero(onibus['co2_evitado_kg_mes'])} kg de CO2 por mês (médias do Metrô de SP).", 4))

        print()
        tela.aviso(tela.quebrar("Limitações: preços de equipamentos e custo de ligação são estimativas. "
                                "A temperatura é da estação do INMET no Mirante de Santana; dentro do "
                                "abrigo pode ser diferente. Valores não são garantidos.", 2))
        tela.dica("  Detalhes, dados e fontes: energia/README.md")

    def encerrar(self):
        """Pede a nota de facilidade (1 a 5), grava nos atendimentos desta execução
        e atualiza o CSV para ele já sair com as notas."""
        nota = ler_opcao("\nDe 1 a 5, quão fácil foi usar o assistente? ", 1, 5)
        for atendimento in self.historico[self.inicio_sessao:]:
            atendimento["facilidade"] = nota
        self._salvar_historico()
        self.exportar_csv()
        tela.sucesso(f"Obrigado por usar o {self.nome}!")

    # ----- Histórico -----

    def registrar(self, origem, pergunta, orientacao, encontrou, ajudou, tentativas, tempo):
        """Salva um atendimento em data/historico.json."""
        atendimento = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": orientacao.id if orientacao else None,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": tempo,
            "facilidade": None,
        }
        self.historico.append(atendimento)
        self._salvar_historico()

    def _carregar_historico(self):
        """Lê o histórico salvo. Se não existir ou estiver corrompido, começa vazio."""
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if isinstance(dados, list):
                return dados
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        tela.aviso("Aviso: histórico não encontrado ou inválido. Um novo histórico será criado.")
        return []

    def _salvar_historico(self):
        try:
            with open(self.caminho_historico, "w", encoding="utf-8") as arquivo:
                json.dump(self.historico, arquivo, ensure_ascii=False, indent=2)
        except OSError:
            tela.erro("Aviso: não foi possível salvar o histórico.")

    # ----- Indicadores e CSV -----

    def indicadores(self):
        """% encontrada, % ajudou, tempo médio, tentativas, facilidade, dúvidas sem solução."""
        total = len(self.historico)
        if total == 0:
            print()
            tela.aviso("Ainda não há atendimentos registrados.")
            return None

        encontrados = [a for a in self.historico if a["encontrou"]]
        ajudaram = [a for a in self.historico if a["ajudou"]]
        notas = [a["facilidade"] for a in self.historico if a.get("facilidade")]
        sem_solucao = [a["pergunta"] for a in self.historico if not a["ajudou"]]

        resultado = {
            "atendimentos": total,
            "encontrada_pct": round(100 * len(encontrados) / total, 1),
            "acerto_pct": round(100 * len(ajudaram) / total, 1),
            "tempo_medio_s": round(sum(a["tempo_segundos"] for a in encontrados) / len(encontrados), 1) if encontrados else 0,
            "tentativas_media": round(sum(a["tentativas"] for a in self.historico) / total, 1),
            "facilidade_media": round(sum(notas) / len(notas), 1) if notas else None,
            "sem_solucao": sem_solucao,
        }

        facilidade = resultado["facilidade_media"]
        linhas = [
            ("Atendimentos", str(resultado["atendimentos"])),
            ("Resposta encontrada", f"{resultado['encontrada_pct']}%"),
            ("Taxa de acerto (ajudou)", f"{resultado['acerto_pct']}%"),
            ("Tempo médio para encontrar", f"{resultado['tempo_medio_s']} s"),
            ("Tentativas por atendimento", str(resultado["tentativas_media"])),
            ("Facilidade de uso (1 a 5)", str(facilidade) if facilidade is not None else "sem notas ainda"),
        ]

        print()
        tela.caixa([("Indicadores", ("negrito",))])
        for nome, valor in linhas:
            print(f"  {nome:<28}" + tela.cor(valor, "ciano", "negrito"))

        tela.secao("Dúvidas sem solução")
        if sem_solucao:
            for pergunta in sem_solucao:
                print("    • " + pergunta)
        else:
            tela.dica("    nenhuma")
        return resultado

    def exportar_csv(self):
        """Exporta os atendimentos para data/atendimentos.csv com csv.DictWriter."""
        try:
            with open(self.caminho_csv, "w", newline="", encoding="utf-8") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_ATENDIMENTO)
                escritor.writeheader()
                for atendimento in self.historico:
                    escritor.writerow({campo: atendimento.get(campo) for campo in CAMPOS_ATENDIMENTO})
        except OSError:
            tela.erro("Erro: não foi possível exportar o CSV.")
            return False
        print()
        tela.sucesso(f"{len(self.historico)} atendimentos exportados para {self.caminho_csv}.")
        return True
