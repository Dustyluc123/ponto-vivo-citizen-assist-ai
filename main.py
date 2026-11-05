"""Ponto Vivo — Citizen Assist AI
Ponto de entrada do programa: execute com  python main.py"""

from base_conhecimento import BaseConhecimento
from assistente import Assistente, ler_opcao

MENU = """
========== PONTO VIVO ==========
Assistente do passageiro de ônibus de São Paulo
(não é canal oficial da Prefeitura ou da SPTrans)

  1. Fazer uma pergunta
  2. Navegar por categorias
  3. Ver indicadores
  4. Exportar atendimentos (CSV)
  0. Sair"""


def main():
    base = BaseConhecimento("data/base_conhecimento.json")
    if not base.carregar():
        print("Não foi possível carregar as orientações. Confira o arquivo e tente de novo.")
        return

    assistente = Assistente("Ponto Vivo", base)
    print(f"{len(base.orientacoes)} orientações carregadas em {len(base.categorias())} categorias.")
    print("Importante: não digite nome, CPF, telefone ou e-mail.")

    try:
        while True:
            print(MENU)
            opcao = ler_opcao("Escolha uma opção: ", 0, 4)
            if opcao == 1:
                assistente.perguntar()
            elif opcao == 2:
                assistente.navegar()
            elif opcao == 3:
                assistente.indicadores()
            elif opcao == 4:
                assistente.exportar_csv()
            else:
                assistente.encerrar()
                break
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C ou fim da entrada: sai sem mostrar erro (o histórico já foi salvo a cada atendimento)
        print("\nAtendimento encerrado.")


if __name__ == "__main__":
    main()
