"""Classe BaseConhecimento: o conjunto de todas as orientações.
Lê o JSON, lista categorias e encontra a melhor orientação para uma pergunta."""

import json

from orientacao import Orientacao

# Campos que toda orientação do JSON precisa ter
CAMPOS_OBRIGATORIOS = ("id", "categoria", "titulo", "palavras_chave", "resposta",
                       "documentos", "onde", "fonte", "verificado_em")


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
        """+3 por palavra-chave na pergunta, +1 por palavra (4+ letras) no título."""
        # TODO
        pass

    def buscar(self, pergunta):
        """Devolve lista de tuplas (pontos, orientacao), da maior para a menor."""
        # TODO
        pass
