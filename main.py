"""Ponto Vivo — Citizen Assist AI
Ponto de entrada do programa: execute com  python main.py"""

from base_conhecimento import BaseConhecimento
from assistente import Assistente


def main():
    base = BaseConhecimento("data/base_conhecimento.json")
    base.carregar()

    assistente = Assistente("Ponto Vivo", base)

    # TODO: menu principal (1 perguntar, 2 navegar, 3 indicadores, 4 exportar CSV, 0 sair)
    print("Ponto Vivo — Citizen Assist AI (em construção)")


if __name__ == "__main__":
    main()
