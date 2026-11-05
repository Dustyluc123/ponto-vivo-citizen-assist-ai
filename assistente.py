"""Classe Assistente: quem conversa com o passageiro.
Faz o atendimento, guarda o histórico e calcula os indicadores."""

import csv
import json
import time
from datetime import datetime

from base_conhecimento import LIMITE_MEDIA, confianca

CAMINHO_HISTORICO = "data/historico.json"
CAMINHO_CSV = "data/atendimentos.csv"

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
            print("Resposta vazia. Digite um número.")
            continue
        if not texto.isdigit():
            print(f"'{texto}' não é um número. Digite um número de {minimo} a {maximo}.")
            continue
        numero = int(texto)
        if numero < minimo or numero > maximo:
            print(f"Opção fora da faixa. Digite um número de {minimo} a {maximo}.")
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
        print("Resposta inválida. Digite s para sim ou n para não.")


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
            pergunta = input("\nDigite sua dúvida (0 para voltar): ").strip()

            if pergunta == "0":
                # Saiu sem encontrar: registra como dúvida sem solução
                if tentativas > 0:
                    tempo = round(time.time() - inicio, 1)
                    self.registrar("pergunta", ultima_sem_resposta, None, False, False, tentativas, tempo)
                return

            if not pergunta:
                print("Você não digitou nada. Escreva sua dúvida ou 0 para voltar.")
                continue

            if tem_dado_pessoal(pergunta):
                # Não conta como tentativa e não é registrado
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva sua dúvida.")
                continue

            tentativas += 1
            resultados = self.base.buscar(pergunta)

            if not resultados or resultados[0][0] < LIMITE_MEDIA:
                ultima_sem_resposta = pergunta
                print("\nNão encontrei uma orientação para essa dúvida.")
                print("Tente outras palavras, por exemplo: idoso, estudante, domingo, recarga, calor.")
                print("Ou volte (0) e navegue pelas categorias: " + ", ".join(self.base.categorias()) + ".")
                continue

            pontos, melhor = resultados[0]
            print(f"\nConfiança da resposta: {confianca(pontos)} ({pontos} pontos)")
            melhor.exibir()

            alternativas = [(p, o) for p, o in resultados[1:] if p >= LIMITE_MEDIA][:MAXIMO_ALTERNATIVAS]
            if alternativas:
                print("\nOutras orientações que podem ajudar:")
                for p, o in alternativas:
                    print(f"  - {o.titulo} ({p} pontos)")

            ajudou = ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
            tempo = round(time.time() - inicio, 1)
            self.registrar("pergunta", pergunta, melhor, True, ajudou, tentativas, tempo)

            if not ajudou:
                print("Obrigado por avisar. Tente perguntar de outro jeito ou navegue pelas categorias.")

            # Começa um novo atendimento
            inicio = time.time()
            tentativas = 0
            ultima_sem_resposta = ""

    def navegar(self):
        """Lista categorias e orientações numeradas, com '0 para voltar' em todas as telas."""
        categorias = self.base.categorias()

        while True:
            print("\nCategorias:")
            for numero, categoria in enumerate(categorias, start=1):
                print(f"  {numero}. {categoria}")
            print("  0. Voltar")
            escolha = ler_opcao("Escolha uma categoria: ", 0, len(categorias))
            if escolha == 0:
                return

            categoria = categorias[escolha - 1]
            inicio = time.time()
            orientacoes = self.base.por_categoria(categoria)

            while True:
                print(f"\n{categoria}:")
                for numero, orientacao in enumerate(orientacoes, start=1):
                    print(f"  {numero}. {orientacao.titulo}")
                print("  0. Voltar")
                escolha = ler_opcao("Escolha uma orientação: ", 0, len(orientacoes))
                if escolha == 0:
                    break

                orientacao = orientacoes[escolha - 1]
                orientacao.exibir()
                ajudou = ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
                tempo = round(time.time() - inicio, 1)
                self.registrar("categoria", categoria, orientacao, True, ajudou, 1, tempo)
                inicio = time.time()

    def encerrar(self):
        """Pede a nota de facilidade (1 a 5), grava nos atendimentos desta execução
        e atualiza o CSV para ele já sair com as notas."""
        nota = ler_opcao("\nDe 1 a 5, quão fácil foi usar o assistente? ", 1, 5)
        for atendimento in self.historico[self.inicio_sessao:]:
            atendimento["facilidade"] = nota
        self._salvar_historico()
        self.exportar_csv()
        print(f"Obrigado por usar o {self.nome}!")

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
        print("Aviso: histórico não encontrado ou inválido. Um novo histórico será criado.")
        return []

    def _salvar_historico(self):
        try:
            with open(self.caminho_historico, "w", encoding="utf-8") as arquivo:
                json.dump(self.historico, arquivo, ensure_ascii=False, indent=2)
        except OSError:
            print("Aviso: não foi possível salvar o histórico.")

    # ----- Indicadores e CSV -----

    def indicadores(self):
        """% encontrada, % ajudou, tempo médio, tentativas, facilidade, dúvidas sem solução."""
        total = len(self.historico)
        if total == 0:
            print("\nAinda não há atendimentos registrados.")
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

        print("\n===== Indicadores =====")
        print(f"Atendimentos:               {resultado['atendimentos']}")
        print(f"Resposta encontrada:        {resultado['encontrada_pct']}%")
        print(f"Taxa de acerto (ajudou):    {resultado['acerto_pct']}%")
        print(f"Tempo médio para encontrar: {resultado['tempo_medio_s']} s")
        print(f"Tentativas por atendimento: {resultado['tentativas_media']}")
        facilidade = resultado["facilidade_media"]
        print(f"Facilidade de uso (1 a 5):  {facilidade if facilidade is not None else 'sem notas ainda'}")
        print("Dúvidas sem solução:")
        if sem_solucao:
            for pergunta in sem_solucao:
                print(f"  - {pergunta}")
        else:
            print("  nenhuma")
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
            print("Erro: não foi possível exportar o CSV.")
            return False
        print(f"\n{len(self.historico)} atendimentos exportados para {self.caminho_csv}.")
        return True
