"""Funções de aparência do terminal: cores, caixas e quebra de linha.
Usa só a biblioteca padrão. Se o terminal não aceitar cores (ou a saída
for um arquivo), o texto aparece normal, sem os códigos de cor."""

import os
import shutil
import sys
import textwrap

# No Windows, este comando liga o suporte a cores no terminal
if os.name == "nt":
    os.system("")

USAR_COR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")

ESTILOS = {
    "negrito": "1",
    "apagado": "2",
    "verde": "32",
    "amarelo": "33",
    "vermelho": "31",
    "azul": "34",
    "ciano": "36",
}

LARGURA_MAXIMA = 72


def largura():
    """Largura útil da tela, no máximo LARGURA_MAXIMA colunas."""
    colunas = shutil.get_terminal_size((80, 24)).columns
    return max(40, min(colunas - 2, LARGURA_MAXIMA))


def cor(texto, *estilos):
    """Aplica um ou mais estilos (ex.: cor('oi', 'verde', 'negrito'))."""
    if not USAR_COR or not estilos:
        return texto
    codigos = ";".join(ESTILOS[estilo] for estilo in estilos)
    return f"\033[{codigos}m{texto}\033[0m"


def quebrar(texto, recuo=2):
    """Quebra um texto longo em várias linhas, com recuo à esquerda."""
    espaco = " " * recuo
    return textwrap.fill(texto, width=largura(), initial_indent=espaco, subsequent_indent=espaco)


def caixa(linhas, estilo="ciano"):
    """Desenha uma caixa com bordas arredondadas em volta das linhas.
    linhas é uma lista de tuplas (texto, estilos) para cada linha."""
    interno = largura() - 4
    print(cor("╭" + "─" * (interno + 2) + "╮", estilo))
    for texto, estilos in linhas:
        for pedaco in textwrap.wrap(texto, width=interno) or [""]:
            espacos = " " * (interno - len(pedaco))
            print(cor("│ ", estilo) + cor(pedaco, *estilos) + espacos + cor(" │", estilo))
    print(cor("╰" + "─" * (interno + 2) + "╯", estilo))


def secao(nome):
    """Subtítulo dentro de uma resposta."""
    print()
    print("  " + cor(nome, "negrito"))


def sucesso(texto):
    print(cor(texto, "verde"))


def aviso(texto):
    print(cor(texto, "amarelo"))


def erro(texto):
    print(cor(texto, "vermelho"))


def dica(texto):
    print(cor(texto, "apagado"))


def selo_confianca(nivel, pontos):
    """Mostra o nível de confiança colorido: ALTA em verde, MÉDIA em amarelo."""
    estilo = "verde" if nivel == "ALTA" else "amarelo"
    return cor(f" Confiança {nivel} ", estilo, "negrito") + cor(f"({pontos} pontos)", "apagado")
