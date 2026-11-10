"""Testes automáticos da lista encadeada e das validações.

Execute a partir da raiz do repositório:
  python dsa/testes.py
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import armazenamento  # noqa: E402
from lista_encadeada import ListaEncadeada  # noqa: E402
from registro import Registro  # noqa: E402


def novo(id, titulo="Serviço", categoria="Geral", requisitos=()):
    return Registro(id, titulo, categoria, "Descrição do serviço.", list(requisitos), "Posto SPTrans")


def ids(lista):
    return [registro.id for registro in lista]


def conferir_integridade(teste, lista):
    """Confere se cabeça, cauda e tamanho batem com os nós que realmente estão ligados."""
    nos = []
    atual = lista.cabeca
    while atual is not None:
        nos.append(atual)
        atual = atual.proximo
    teste.assertEqual(len(nos), len(lista))
    if nos:
        teste.assertIs(lista.cauda, nos[-1])
        teste.assertIsNone(lista.cauda.proximo)
    else:
        teste.assertIsNone(lista.cabeca)
        teste.assertIsNone(lista.cauda)


class TestListaVazia(unittest.TestCase):
    def setUp(self):
        self.lista = ListaEncadeada()

    def test_comeca_vazia(self):
        self.assertTrue(self.lista.esta_vazia())
        self.assertEqual(len(self.lista), 0)
        self.assertEqual(list(self.lista), [])

    def test_buscar_na_lista_vazia(self):
        self.assertEqual(self.lista.buscar_por_id(1), (None, 0))

    def test_pesquisar_na_lista_vazia(self):
        self.assertEqual(self.lista.pesquisar("titulo", "bilhete"), ([], 0))

    def test_remover_da_lista_vazia(self):
        self.assertIsNone(self.lista.remover(1))
        conferir_integridade(self, self.lista)

    def test_atualizar_na_lista_vazia(self):
        self.assertIsNone(self.lista.atualizar(1, titulo="Novo"))

    def test_ordenar_lista_vazia(self):
        self.assertEqual(self.lista.ordenar("titulo"), 0)
        conferir_integridade(self, self.lista)

    def test_indicadores_da_lista_vazia(self):
        self.assertEqual(self.lista.contar_por_categoria(), {})
        self.assertEqual(self.lista.proximo_id_livre(), 1)
        self.assertEqual(self.lista.desenhar(), "cabeça -> None")


class TestInsercao(unittest.TestCase):
    def test_insere_no_fim_e_mantem_ordem(self):
        lista = ListaEncadeada()
        for id in (3, 1, 2):
            lista.inserir(novo(id))
        self.assertEqual(ids(lista), [3, 1, 2])
        self.assertEqual(lista.cabeca.registro.id, 3)
        self.assertEqual(lista.cauda.registro.id, 2)
        conferir_integridade(self, lista)

    def test_id_duplicado_e_recusado(self):
        lista = ListaEncadeada()
        lista.inserir(novo(1))
        with self.assertRaises(ValueError):
            lista.inserir(novo(1, titulo="Outro"))
        self.assertEqual(len(lista), 1)
        self.assertEqual(lista.cabeca.registro.titulo, "Serviço")


class TestValidacaoDoRegistro(unittest.TestCase):
    def test_ids_invalidos(self):
        for valor in (0, -5, "abc", "", "1.5", None, True):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                novo(valor)

    def test_id_em_texto_e_aceito(self):
        self.assertEqual(novo(" 12 ").id, 12)

    def test_campos_obrigatorios_vazios(self):
        with self.assertRaises(ValueError):
            Registro(1, "   ", "Geral", "Desc", [], "Local")
        with self.assertRaises(ValueError):
            Registro(1, "Título", "Geral", "Desc", [], "")

    def test_requisitos_por_ponto_e_virgula(self):
        registro = Registro(1, "T", "C", "D", "RG;  CPF ; ;Comprovante", "L")
        self.assertEqual(registro.requisitos, ["RG", "CPF", "Comprovante"])


class TestBusca(unittest.TestCase):
    def setUp(self):
        self.lista = ListaEncadeada()
        self.lista.inserir(novo(1, "Bilhete Único do Estudante", "Tarifas e Direitos"))
        self.lista.inserir(novo(2, "Recarga do Bilhete Único", "Viagem e Informação"))
        self.lista.inserir(novo(3, "Ponto Fresco", "Energia e Sustentabilidade"))

    def test_buscar_id_existente_conta_nos_visitados(self):
        registro, visitados = self.lista.buscar_por_id(2)
        self.assertEqual(registro.titulo, "Recarga do Bilhete Único")
        self.assertEqual(visitados, 2)

    def test_buscar_id_inexistente_visita_todos(self):
        self.assertEqual(self.lista.buscar_por_id(99), (None, 3))

    def test_buscar_id_invalido(self):
        with self.assertRaises(ValueError):
            self.lista.buscar_por_id("dois")

    def test_pesquisa_sem_acento_e_sem_maiuscula(self):
        encontrados, visitados = self.lista.pesquisar("titulo", "BILHETE UNICO")
        self.assertEqual(ids(encontrados), [1, 2])
        self.assertEqual(visitados, 3)

    def test_pesquisa_por_categoria(self):
        encontrados, _ = self.lista.pesquisar("categoria", "informacao")
        self.assertEqual(ids(encontrados), [2])

    def test_pesquisa_sem_resultado(self):
        self.assertEqual(self.lista.pesquisar("titulo", "metrô")[0], [])

    def test_pesquisa_com_termo_ou_campo_invalido(self):
        with self.assertRaises(ValueError):
            self.lista.pesquisar("titulo", "   ")
        with self.assertRaises(ValueError):
            self.lista.pesquisar("descricao", "bilhete")


class TestAtualizacao(unittest.TestCase):
    def setUp(self):
        self.lista = ListaEncadeada()
        for id in (1, 2, 3):
            self.lista.inserir(novo(id))

    def test_atualiza_campos_sem_mudar_a_lista(self):
        self.lista.atualizar(2, titulo="Novo título", requisitos="RG; CPF")
        registro, _ = self.lista.buscar_por_id(2)
        self.assertEqual(registro.titulo, "Novo título")
        self.assertEqual(registro.requisitos, ["RG", "CPF"])
        self.assertEqual(ids(self.lista), [1, 2, 3])
        conferir_integridade(self, self.lista)

    def test_atualizar_inexistente(self):
        self.assertIsNone(self.lista.atualizar(99, titulo="X"))

    def test_nao_altera_id(self):
        registro, _ = self.lista.buscar_por_id(1)
        with self.assertRaises(ValueError):
            registro.atualizar(id=50)
        self.assertEqual(registro.id, 1)

    def test_valor_invalido_nao_altera_nada(self):
        with self.assertRaises(ValueError):
            self.lista.atualizar(1, titulo="Válido", local="  ")
        registro, _ = self.lista.buscar_por_id(1)
        self.assertEqual(registro.titulo, "Serviço")
        self.assertEqual(registro.local, "Posto SPTrans")


class TestRemocao(unittest.TestCase):
    def setUp(self):
        self.lista = ListaEncadeada()
        for id in (1, 2, 3, 4):
            self.lista.inserir(novo(id))

    def test_remove_cabeca(self):
        self.assertEqual(self.lista.remover(1).id, 1)
        self.assertEqual(ids(self.lista), [2, 3, 4])
        conferir_integridade(self, self.lista)

    def test_remove_meio(self):
        self.lista.remover(3)
        self.assertEqual(ids(self.lista), [1, 2, 4])
        conferir_integridade(self, self.lista)

    def test_remove_cauda_e_insere_depois(self):
        self.lista.remover(4)
        self.assertEqual(self.lista.cauda.registro.id, 3)
        self.lista.inserir(novo(9))
        self.assertEqual(ids(self.lista), [1, 2, 3, 9])
        conferir_integridade(self, self.lista)

    def test_remove_todos_ate_esvaziar(self):
        for id in (2, 4, 1, 3):
            self.lista.remover(id)
        self.assertTrue(self.lista.esta_vazia())
        conferir_integridade(self, self.lista)

    def test_remove_inexistente(self):
        self.assertIsNone(self.lista.remover(99))
        self.assertEqual(len(self.lista), 4)


class TestOrdenacao(unittest.TestCase):
    def setUp(self):
        self.lista = ListaEncadeada()
        dados = [
            (4, "Ônibus ou carro", "Energia"),
            (2, "Atende+", "Tarifas"),
            (5, "Bilhete de Estudante", "Tarifas"),
            (1, "olho Vivo", "Viagem"),
            (3, "Alagamento", "Clima"),
        ]
        for id, titulo, categoria in dados:
            self.lista.inserir(novo(id, titulo, categoria))

    def test_ordena_por_id(self):
        self.lista.ordenar("id")
        self.assertEqual(ids(self.lista), [1, 2, 3, 4, 5])
        conferir_integridade(self, self.lista)

    def test_ordena_por_titulo_ignorando_acento_e_maiuscula(self):
        self.lista.ordenar("titulo")
        titulos = [registro.titulo for registro in self.lista]
        self.assertEqual(titulos, ["Alagamento", "Atende+", "Bilhete de Estudante", "olho Vivo", "Ônibus ou carro"])
        conferir_integridade(self, self.lista)

    def test_ordena_por_categoria_e_titulo(self):
        self.lista.ordenar("categoria")
        self.assertEqual(ids(self.lista), [3, 4, 2, 5, 1])

    def test_e_estavel(self):
        lista = ListaEncadeada()
        for id in (7, 3, 9, 1):
            lista.inserir(novo(id, "Mesmo título"))
        lista.ordenar("titulo")
        self.assertEqual(ids(lista), [7, 3, 9, 1])

    def test_inserir_depois_de_ordenar_vai_para_o_fim(self):
        self.lista.ordenar("id")
        self.lista.inserir(novo(10))
        self.assertEqual(ids(self.lista)[-1], 10)
        conferir_integridade(self, self.lista)

    def test_um_unico_registro(self):
        lista = ListaEncadeada()
        lista.inserir(novo(1))
        self.assertEqual(lista.ordenar("titulo"), 0)
        conferir_integridade(self, lista)

    def test_criterio_invalido(self):
        with self.assertRaises(ValueError):
            self.lista.ordenar("cor")

    def test_comparacoes_nao_passam_de_n_log_n(self):
        lista = ListaEncadeada()
        for id in range(64, 0, -1):
            lista.inserir(novo(id))
        comparacoes = lista.ordenar("id")
        self.assertEqual(ids(lista), list(range(1, 65)))
        self.assertLessEqual(comparacoes, 64 * 6)  # n * log2(n)


class TestAnaliseEArmazenamento(unittest.TestCase):
    def test_contagem_por_categoria(self):
        lista = ListaEncadeada()
        for id, categoria in ((1, "A"), (2, "B"), (3, "A")):
            lista.inserir(novo(id, categoria=categoria))
        self.assertEqual(lista.contar_por_categoria(), {"A": 2, "B": 1})
        self.assertEqual(lista.proximo_id_livre(), 4)

    def test_salvar_e_carregar(self):
        lista = ListaEncadeada()
        lista.inserir(novo(5, "Primeiro", requisitos=["RG"]))
        lista.inserir(novo(2, "Segundo"))
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "registros.json")
            armazenamento.salvar(lista, caminho)
            carregada, ignorados = armazenamento.carregar(caminho)
        self.assertEqual(ignorados, 0)
        self.assertEqual(ids(carregada), [5, 2])
        self.assertEqual(carregada.cabeca.registro.requisitos, ["RG"])

    def test_arquivo_com_registros_ruins(self):
        dados = [
            novo(1).para_dict(),
            novo(1).para_dict(),                 # ID repetido
            {"id": 2, "titulo": "Sem os outros campos"},
            novo(3).para_dict(),
        ]
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "registros.json")
            with open(caminho, "w", encoding="utf-8") as arquivo:
                json.dump(dados, arquivo)
            lista, ignorados = armazenamento.carregar(caminho)
        self.assertEqual(ids(lista), [1, 3])
        self.assertEqual(ignorados, 2)

    def test_importa_base_do_ponto_vivo(self):
        lista = armazenamento.importar_base_ponto_vivo()
        self.assertEqual(len(lista), 15)
        self.assertEqual(len(lista.contar_por_categoria()), 4)
        conferir_integridade(self, lista)


if __name__ == "__main__":
    unittest.main(verbosity=2)
