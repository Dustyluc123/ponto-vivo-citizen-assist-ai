"""Classe BaseConhecimento: o conjunto de todas as orientações.
Lê o JSON, lista categorias e encontra a melhor orientação para uma pergunta."""

from orientacao import Orientacao


class BaseConhecimento:
    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []  # lista de objetos Orientacao

    def carregar(self):
        """Lê o JSON e cria os objetos Orientacao.
        Não pode travar se o arquivo não existir ou estiver corrompido."""
        # TODO
        pass

    def categorias(self):
        """Devolve a lista de categorias, sem repetir."""
        # TODO
        pass

    def por_categoria(self, categoria):
        """Devolve as orientações de uma categoria."""
        # TODO
        pass

    def pontuar(self, pergunta, orientacao):
        """+3 por palavra-chave na pergunta, +1 por palavra (4+ letras) no título."""
        # TODO
        pass

    def buscar(self, pergunta):
        """Devolve lista de tuplas (pontos, orientacao), da maior para a menor."""
        # TODO
        pass
