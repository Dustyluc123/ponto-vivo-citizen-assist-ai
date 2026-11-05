"""Classe Orientacao: representa UMA orientação da base de conhecimento
(um registro do arquivo data/base_conhecimento.json)."""


class Orientacao:
    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        # TODO: guardar cada parâmetro como atributo (self.id = id, ...)
        pass

    def exibir(self):
        """Mostra a orientação na tela, com fonte, data e o aviso de canal não oficial."""
        # TODO
        pass
