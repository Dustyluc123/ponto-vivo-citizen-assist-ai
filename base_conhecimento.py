"""Classe BaseConhecimento: o conjunto de todas as orientações.
Lê o JSON, lista categorias e encontra a melhor orientação para uma pergunta."""

import json

from orientacao import Orientacao

# Campos que toda orientação do JSON precisa ter
CAMPOS_OBRIGATORIOS = ("id", "categoria", "titulo", "palavras_chave", "resposta",
                       "documentos", "onde", "fonte", "verificado_em")

# Pesos e limites da busca (constantes: dá para ajustar aqui sem mexer no resto do código)
PONTOS_PALAVRA_CHAVE = 3
PONTOS_TITULO = 1
TAMANHO_MINIMO_PALAVRA = 4
LIMITE_ALTA = 6
LIMITE_MEDIA = 3

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
           "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ç": "c"}


def normalizar(texto):
    """Deixa o texto em minúsculas, sem acentos e sem pontuação.
    Coloca um espaço no começo e no fim para comparar palavras inteiras."""
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()":
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


def confianca(pontos):
    """Transforma a pontuação em nível de confiança."""
    if pontos >= LIMITE_ALTA:
        return "ALTA"
    if pontos >= LIMITE_MEDIA:
        return "MÉDIA"
    return "BAIXA"


class BaseConhecimento:
    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []  # lista de objetos Orientacao (composição)

    def carregar(self):
        """Lê o JSON e cria os objetos Orientacao.
        Devolve True se carregou alguma orientação e False se não conseguiu.
        Nunca trava: arquivo ausente ou corrompido vira uma mensagem."""
        self.orientacoes = []

        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                registros = json.load(arquivo)
        except FileNotFoundError:
            print(f"Erro: o arquivo {self.caminho} não foi encontrado.")
            return False
        except json.JSONDecodeError:
            print(f"Erro: o arquivo {self.caminho} está corrompido (JSON inválido).")
            return False

        if not isinstance(registros, list):
            print("Erro: a base de conhecimento precisa ser uma lista de orientações.")
            return False

        for registro in registros:
            # Pula registros que não são dicionário ou que estão sem algum campo
            if not isinstance(registro, dict):
                print("Aviso: um registro inválido da base foi ignorado.")
                continue
            faltando = [campo for campo in CAMPOS_OBRIGATORIOS if campo not in registro]
            if faltando:
                print(f"Aviso: orientação {registro.get('id', '?')} ignorada, faltam: {', '.join(faltando)}.")
                continue

            orientacao = Orientacao(
                registro["id"],
                registro["categoria"],
                registro["titulo"],
                registro["palavras_chave"],
                registro["resposta"],
                registro["documentos"],
                registro["onde"],
                registro["fonte"],
                registro["verificado_em"],
            )
            self.orientacoes.append(orientacao)

        return len(self.orientacoes) > 0

    def categorias(self):
        """Devolve a lista de categorias, sem repetir, na ordem em que aparecem no JSON."""
        lista = []
        for orientacao in self.orientacoes:
            if orientacao.categoria not in lista:
                lista.append(orientacao.categoria)
        return lista

    def por_categoria(self, categoria):
        """Devolve as orientações de uma categoria."""
        return [o for o in self.orientacoes if o.categoria == categoria]

    def pontuar(self, pergunta, orientacao):
        """+3 por palavra-chave na pergunta, +1 por palavra (4+ letras) no título.
        A pergunta já deve chegar normalizada."""
        pontos = 0

        # Palavra-chave inteira dentro da pergunta: +3
        for chave in orientacao.palavras_chave:
            if normalizar(chave) in pergunta:
                pontos += PONTOS_PALAVRA_CHAVE

        # Palavra da pergunta (4 letras ou mais) que aparece no título: +1
        titulo = normalizar(orientacao.titulo)
        palavras_contadas = []
        for palavra in pergunta.split():
            if len(palavra) >= TAMANHO_MINIMO_PALAVRA and palavra not in palavras_contadas:
                if " " + palavra + " " in titulo:
                    pontos += PONTOS_TITULO
                    palavras_contadas.append(palavra)

        return pontos

    def buscar(self, pergunta):
        """Devolve lista de tuplas (pontos, orientacao), da maior para a menor.
        Só entram orientações com pelo menos 1 ponto."""
        pergunta = normalizar(pergunta)
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta, orientacao)
            if pontos > 0:
                resultados.append((pontos, orientacao))

        # Ordena pelo primeiro item da tupla (os pontos), do maior para o menor.
        # Em empate, mantém a ordem do JSON.
        resultados.sort(key=lambda tupla: tupla[0], reverse=True)
        return resultados
