"""Salvar e carregar os registros em JSON (extensão opcional: persistência em arquivo).

O arquivo só serve para não perder os dados ao fechar o programa.
Durante a execução, os registros ficam sempre na lista encadeada.
"""

import json
import os

from lista_encadeada import ListaEncadeada
from registro import Registro

PASTA = os.path.dirname(os.path.abspath(__file__))
ARQ_REGISTROS = os.path.join(PASTA, "dados", "registros.json")
ARQ_BASE_PONTO_VIVO = os.path.join(PASTA, "..", "data", "base_conhecimento.json")


def salvar(lista, caminho=ARQ_REGISTROS):
    """Percorre a lista e grava cada registro. O(n)."""
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    dados = [registro.para_dict() for registro in lista]
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


def carregar(caminho=ARQ_REGISTROS):
    """Lê o arquivo e insere registro por registro na lista encadeada.
    Registros com problema (campo faltando, ID repetido) são pulados e contados."""
    lista = ListaEncadeada()
    ignorados = 0
    with open(caminho, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    for item in dados:
        try:
            lista.inserir(Registro.de_dict(item))
        except (KeyError, TypeError, ValueError):
            ignorados += 1
    return lista, ignorados


def importar_base_ponto_vivo(caminho=ARQ_BASE_PONTO_VIVO):
    """Primeira execução: transforma as 15 orientações do assistente de Python
    em registros desta lista (resposta vira descrição, documentos viram requisitos)."""
    lista = ListaEncadeada()
    with open(caminho, encoding="utf-8") as arquivo:
        orientacoes = json.load(arquivo)
    for item in orientacoes:
        lista.inserir(Registro(
            item["id"], item["titulo"], item["categoria"], item["resposta"],
            item["documentos"], item["onde"], item["fonte"],
        ))
    return lista
