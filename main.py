"""Ponto Vivo — Citizen Assist AI
Ponto de entrada do programa: execute com  python main.py"""

import tela
from base_conhecimento import BaseConhecimento
from assistente import Assistente, ler_opcao

OPCOES = [
    ("1", "Fazer uma pergunta"),
    ("2", "Navegar por categorias"),
    ("3", "Ver indicadores"),
    ("4", "Exportar atendimentos (CSV)"),
    ("5", "Energia do Ponto Vivo"),
    ("0", "Sair"),
]


def mostrar_menu():
    print()
    tela.caixa([
        ("PONTO VIVO", ("negrito",)),
        ("Assistente do passageiro de ônibus de São Paulo", ()),
        ("Não é canal oficial da Prefeitura ou da SPTrans", ("apagado",)),
    ])
    for numero, texto in OPCOES:
        print(f"  {tela.cor(numero, 'ciano', 'negrito')}  {texto}")


def main():
    base = BaseConhecimento("data/base_conhecimento.json")
    if not base.carregar():
        tela.erro("Não foi possível carregar as orientações. Confira o arquivo e tente de novo.")
        return

    assistente = Assistente("Ponto Vivo", base)
    tela.sucesso(f"{len(base.orientacoes)} orientações carregadas em {len(base.categorias())} categorias.")
    tela.aviso("Importante: não digite nome, CPF, telefone ou e-mail.")

    try:
        while True:
            mostrar_menu()
            opcao = ler_opcao("\nEscolha uma opção: ", 0, 5)
            if opcao == 1:
                assistente.perguntar()
            elif opcao == 2:
                assistente.navegar()
            elif opcao == 3:
                assistente.indicadores()
            elif opcao == 4:
                assistente.exportar_csv()
            elif opcao == 5:
                assistente.energia()
            else:
                assistente.encerrar()
                break
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C ou fim da entrada: sai sem mostrar erro (o histórico já foi salvo a cada atendimento)
        print()
        tela.dica("Atendimento encerrado.")


if __name__ == "__main__":
    main()
