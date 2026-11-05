"""Classe Orientacao: representa UMA orientação da base de conhecimento
(um registro do arquivo data/base_conhecimento.json)."""

import tela

AVISO = "Aviso: este assistente NÃO é um canal oficial da Prefeitura ou da SPTrans."


class Orientacao:
    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave  # lista de textos
        self.resposta = resposta
        self.documentos = documentos          # lista de textos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    def exibir(self):
        """Mostra a orientação na tela, com fonte, data e o aviso de canal não oficial."""
        print()
        tela.caixa([(self.titulo, ("negrito",)), (self.categoria, ("apagado",))])
        print(tela.quebrar(self.resposta))

        tela.secao("Documentos necessários")
        for documento in self.documentos:
            print(tela.quebrar("• " + documento, recuo=4))

        tela.secao("Onde")
        print(tela.quebrar(self.onde, recuo=4))

        tela.secao("Fonte")
        print("    " + tela.cor(self.fonte, "azul"))
        print("    " + tela.cor(f"verificado em {self.verificado_em}", "apagado"))

        print()
        tela.aviso("  " + AVISO)
