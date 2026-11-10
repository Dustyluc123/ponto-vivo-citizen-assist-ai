"""Ponto Vivo — DSA: cadastro de serviços ao passageiro em lista encadeada.

Execute a partir da raiz do repositório:
  python dsa/main.py            usa e salva dsa/dados/registros.json
  python dsa/main.py --vazia    começa com a lista vazia e não salva nada (para testes)
"""

import os
import sys

PASTA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(PASTA))  # para usar o tela.py da raiz

import tela  # noqa: E402
import armazenamento  # noqa: E402
from lista_encadeada import CRITERIOS, ListaEncadeada  # noqa: E402
from registro import Registro, validar_id  # noqa: E402

OPCOES = [
    ("1", "Cadastrar serviço"),
    ("2", "Consultar por ID"),
    ("3", "Pesquisar por título ou categoria"),
    ("4", "Atualizar serviço"),
    ("5", "Excluir serviço"),
    ("6", "Ordenar e listar"),
    ("7", "Análise (indicadores)"),
    ("8", "Listar na ordem atual"),
    ("9", "Ver a estrutura da lista (nós)"),
    ("0", "Sair"),
]

AVISO_VAZIA = "A lista está vazia. Cadastre um serviço primeiro (opção 1)."


# ----------------------------------------------------------------------
# Leitura de dados com validação
# ----------------------------------------------------------------------
def entrada(mensagem):
    """input() que repete o texto digitado quando a entrada vem de um arquivo.
    Assim as evidências de teste mostram o que foi digitado em cada pergunta."""
    texto = input(mensagem)
    if not sys.stdin.isatty():
        print(texto)
    return texto


def ler_opcao(mensagem, minimo, maximo):
    """Repete a pergunta até receber um número dentro da faixa."""
    while True:
        texto = entrada(mensagem).strip()
        if texto.isdigit() and minimo <= int(texto) <= maximo:
            return int(texto)
        tela.erro(f"Opção inválida. Digite um número de {minimo} a {maximo}.")


def ler_id(mensagem):
    """Pede um ID até ser um inteiro positivo. Enter vazio cancela (devolve None)."""
    while True:
        texto = entrada(mensagem).strip()
        if not texto:
            return None
        try:
            return validar_id(texto)
        except ValueError as erro:
            tela.erro(str(erro))


def ler_texto(mensagem, atual=None):
    """Pede um texto obrigatório. Na atualização, Enter mantém o valor atual."""
    while True:
        texto = " ".join(entrada(mensagem).split())
        if texto:
            return texto
        if atual is not None:
            return atual
        tela.erro("Este campo não pode ficar vazio.")


def confirmar(mensagem):
    while True:
        resposta = entrada(mensagem).strip().lower()
        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "nao", "não"):
            return False
        tela.erro("Responda s ou n.")


# ----------------------------------------------------------------------
# Exibição
# ----------------------------------------------------------------------
def encurtar(texto, tamanho):
    return texto if len(texto) <= tamanho else texto[: tamanho - 1] + "…"


def mostrar_tabela(registros):
    largura_titulo = max(20, tela.largura() - 34)
    print()
    print("  " + tela.cor(f"{'ID':>3}  {'Título':<{largura_titulo}}  Categoria", "negrito"))
    for registro in registros:
        titulo = encurtar(registro.titulo, largura_titulo)
        categoria = encurtar(registro.categoria, 26)
        print(f"  {registro.id:>3}  {titulo:<{largura_titulo}}  {tela.cor(categoria, 'apagado')}")


def mostrar_registro(registro):
    print()
    tela.caixa([(f"#{registro.id}  {registro.titulo}", ("negrito",)), (registro.categoria, ("apagado",))])
    print(tela.quebrar(registro.descricao))
    tela.secao("Requisitos")
    if registro.requisitos:
        for item in registro.requisitos:
            print(tela.quebrar("• " + item, recuo=4))
    else:
        print(tela.quebrar("Nenhum requisito informado.", recuo=4))
    tela.secao("Onde")
    print(tela.quebrar(registro.local, recuo=4))
    if registro.fonte:
        tela.secao("Fonte")
        print("    " + tela.cor(registro.fonte, "azul"))


def escolher_categoria(lista, atual=None):
    """Mostra as categorias existentes para evitar nomes digitados de jeitos diferentes.
    Também aceita digitar uma categoria nova."""
    categorias = list(lista.contar_por_categoria())
    if categorias:
        tela.secao("Categorias existentes")
        for numero, nome in enumerate(categorias, start=1):
            print(f"    {tela.cor(str(numero), 'ciano')}  {nome}")
        tela.dica("    Digite o número de uma categoria ou o nome de uma nova.")
    texto = ler_texto("  Categoria: " if atual is None else f"  Categoria [{atual}]: ", atual)
    if texto.isdigit() and 1 <= int(texto) <= len(categorias):
        return categorias[int(texto) - 1]
    return texto


# ----------------------------------------------------------------------
# Operações do menu
# ----------------------------------------------------------------------
class Sistema:
    def __init__(self, lista, salvar_em_arquivo):
        self.lista = lista
        self.salvar_em_arquivo = salvar_em_arquivo

    def salvar(self):
        if self.salvar_em_arquivo:
            armazenamento.salvar(self.lista)

    def lista_vazia(self):
        if self.lista.esta_vazia():
            tela.aviso(AVISO_VAZIA)
            return True
        return False

    def cadastrar(self):
        tela.secao("Cadastrar serviço")
        sugestao = self.lista.proximo_id_livre()
        while True:
            texto = entrada(f"  ID (Enter para usar {sugestao}): ").strip()
            try:
                id = validar_id(texto or sugestao)
            except ValueError as erro:
                tela.erro(str(erro))
                continue
            existente, _ = self.lista.buscar_por_id(id)
            if existente is not None:
                tela.erro(f"O ID {id} já está em uso por \"{existente.titulo}\". Escolha outro.")
                continue
            break

        titulo = ler_texto("  Título: ")
        categoria = escolher_categoria(self.lista)
        descricao = ler_texto("  Descrição: ")
        requisitos = entrada("  Requisitos (separe por ; ou deixe vazio): ")
        local = ler_texto("  Onde é feito: ")
        fonte = entrada("  Fonte (link, opcional): ")

        try:
            registro = self.lista.inserir(Registro(id, titulo, categoria, descricao, requisitos, local, fonte))
        except ValueError as erro:
            tela.erro(str(erro))
            return
        self.salvar()
        tela.sucesso(f"Serviço #{registro.id} cadastrado. Total: {len(self.lista)}.")

    def consultar(self):
        if self.lista_vazia():
            return
        id = ler_id("  ID do serviço (Enter para voltar): ")
        if id is None:
            return
        registro, visitados = self.lista.buscar_por_id(id)
        tela.dica(f"  Busca sequencial: {visitados} de {len(self.lista)} nós visitados.")
        if registro is None:
            tela.aviso(f"Nenhum serviço com o ID {id}.")
            return
        mostrar_registro(registro)

    def pesquisar(self):
        if self.lista_vazia():
            return
        print("  1  Título\n  2  Categoria")
        campo = "titulo" if ler_opcao("  Pesquisar por: ", 1, 2) == 1 else "categoria"
        termo = ler_texto("  Digite o termo: ")
        encontrados, visitados = self.lista.pesquisar(campo, termo)
        tela.dica(f"  Busca sequencial: {visitados} nós visitados.")
        if not encontrados:
            tela.aviso(f"Nenhum serviço encontrado para \"{termo}\".")
            return
        tela.sucesso(f"{len(encontrados)} serviço(s) encontrado(s).")
        mostrar_tabela(encontrados)

    def atualizar(self):
        if self.lista_vazia():
            return
        id = ler_id("  ID do serviço a atualizar (Enter para voltar): ")
        if id is None:
            return
        registro, _ = self.lista.buscar_por_id(id)
        if registro is None:
            tela.aviso(f"Nenhum serviço com o ID {id}.")
            return

        tela.dica("  Enter mantém o valor atual entre colchetes. O ID não pode ser alterado.")
        campos = {
            "titulo": ler_texto(f"  Título [{registro.titulo}]: ", registro.titulo),
            "categoria": escolher_categoria(self.lista, registro.categoria),
            "descricao": ler_texto("  Descrição [Enter mantém]: ", registro.descricao),
            "local": ler_texto("  Onde é feito [Enter mantém]: ", registro.local),
        }
        requisitos = entrada(f"  Requisitos [{'; '.join(registro.requisitos) or 'nenhum'}]: ").strip()
        if requisitos:
            campos["requisitos"] = requisitos
        fonte = entrada("  Fonte [Enter mantém]: ").strip()
        if fonte:
            campos["fonte"] = fonte

        try:
            self.lista.atualizar(id, **campos)
        except ValueError as erro:
            tela.erro(str(erro))
            return
        self.salvar()
        tela.sucesso(f"Serviço #{id} atualizado.")

    def excluir(self):
        if self.lista_vazia():
            return
        id = ler_id("  ID do serviço a excluir (Enter para voltar): ")
        if id is None:
            return
        registro, _ = self.lista.buscar_por_id(id)
        if registro is None:
            tela.aviso(f"Nenhum serviço com o ID {id}.")
            return
        if not confirmar(f"  Excluir \"{registro.titulo}\"? (s/n): "):
            tela.dica("  Exclusão cancelada.")
            return
        self.lista.remover(id)
        self.salvar()
        tela.sucesso(f"Serviço #{id} excluído. Total: {len(self.lista)}.")

    def ordenar(self):
        if self.lista_vazia():
            return
        nomes = list(CRITERIOS)
        for numero, criterio in enumerate(nomes, start=1):
            print(f"  {numero}  {CRITERIOS[criterio][0]}")
        criterio = nomes[ler_opcao("  Ordenar por: ", 1, len(nomes)) - 1]
        comparacoes = self.lista.ordenar(criterio)
        self.salvar()
        tela.sucesso(f"Lista ordenada por {CRITERIOS[criterio][0]} com Merge Sort.")
        tela.dica(f"  {comparacoes} comparações para {len(self.lista)} registros.")
        mostrar_tabela(self.lista)

    def analisar(self):
        if self.lista_vazia():
            return
        contagem = self.lista.contar_por_categoria()
        total = len(self.lista)
        maior = max(len(nome) for nome in contagem)
        print()
        tela.caixa([("Análise dos serviços cadastrados", ("negrito",))])
        print(f"  Total de serviços: {tela.cor(str(total), 'negrito')}")
        print(f"  Categorias: {len(contagem)}")
        tela.secao("Serviços por categoria")
        for nome, quantidade in sorted(contagem.items(), key=lambda par: (-par[1], par[0])):
            barra = "█" * quantidade
            print(f"    {nome:<{maior}}  {tela.cor(barra, 'ciano')} {quantidade}")

        quantidades = [len(registro.requisitos) for registro in self.lista]
        mais_exigente = max(self.lista, key=lambda registro: len(registro.requisitos))
        sem_requisito = sum(1 for quantidade in quantidades if quantidade == 0)
        tela.secao("Requisitos")
        print(f"    Média por serviço: {tela.numero(sum(quantidades) / total)}")
        print(f"    Serviços que não pedem nada: {sem_requisito}")
        print(tela.quebrar(f"Serviço que mais pede: #{mais_exigente.id} {mais_exigente.titulo} "
                           f"({len(mais_exigente.requisitos)} requisitos)", recuo=4))

    def listar(self):
        if self.lista_vazia():
            return
        mostrar_tabela(self.lista)
        tela.dica(f"\n  {len(self.lista)} serviço(s).")

    def estrutura(self):
        print()
        print(tela.quebrar(self.lista.desenhar()))
        cabeca = self.lista.cabeca.registro.id if self.lista.cabeca else "None"
        cauda = self.lista.cauda.registro.id if self.lista.cauda else "None"
        tela.dica(f"  cabeça = {cabeca}   cauda = {cauda}   tamanho = {len(self.lista)}")


def mostrar_menu():
    print()
    tela.caixa([
        ("PONTO VIVO  ·  Cadastro de serviços", ("negrito",)),
        ("Lista encadeada própria · Data Structures and Algorithms", ("apagado",)),
    ])
    for numero, texto in OPCOES:
        print(f"  {tela.cor(numero, 'ciano', 'negrito')}  {texto}")


def iniciar_lista(vazia):
    if vazia:
        tela.aviso("Modo lista vazia: nada será salvo em arquivo.")
        return ListaEncadeada()
    if os.path.exists(armazenamento.ARQ_REGISTROS):
        lista, ignorados = armazenamento.carregar()
        if ignorados:
            tela.aviso(f"{ignorados} registro(s) com problema no arquivo foram ignorados.")
        return lista
    lista = armazenamento.importar_base_ponto_vivo()
    armazenamento.salvar(lista)
    tela.dica("Primeira execução: serviços importados da base do assistente Ponto Vivo.")
    return lista


def main():
    vazia = "--vazia" in sys.argv
    try:
        lista = iniciar_lista(vazia)
    except (OSError, ValueError) as erro:
        tela.erro(f"Não foi possível carregar os registros: {erro}")
        return
    sistema = Sistema(lista, salvar_em_arquivo=not vazia)
    tela.sucesso(f"{len(lista)} serviço(s) carregado(s).")

    acoes = {
        1: sistema.cadastrar, 2: sistema.consultar, 3: sistema.pesquisar,
        4: sistema.atualizar, 5: sistema.excluir, 6: sistema.ordenar,
        7: sistema.analisar, 8: sistema.listar, 9: sistema.estrutura,
    }
    try:
        while True:
            mostrar_menu()
            opcao = ler_opcao("\nEscolha uma opção: ", 0, 9)
            if opcao == 0:
                tela.dica("Até logo.")
                break
            acoes[opcao]()
    except (KeyboardInterrupt, EOFError):
        print()
        tela.dica("Programa encerrado.")


if __name__ == "__main__":
    main()
