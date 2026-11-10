"""Lista encadeada simples feita do zero, sem usar list do Python para guardar os dados.

Cada No guarda um Registro e uma referência explícita para o próximo nó.
A lista guarda a cabeça (primeiro nó), a cauda (último nó) e o tamanho.

    cabeca                                cauda
      |                                     |
    [ 1 | o-]--> [ 2 | o-]--> [ 3 | o-]--> [ 4 | None ]

A complexidade de cada operação está comentada na própria função e explicada
no README da pasta dsa.
"""

from registro import normalizar, validar_id


class No:
    """Um elo da lista: o registro e a referência para o próximo nó."""

    def __init__(self, registro):
        self.registro = registro
        self.proximo = None


# Critérios de ordenação: nome mostrado no menu e a chave usada na comparação.
CRITERIOS = {
    "id": ("ID (crescente)", lambda r: r.id),
    "titulo": ("Título (A a Z)", lambda r: normalizar(r.titulo)),
    "categoria": ("Categoria e depois título (A a Z)", lambda r: (normalizar(r.categoria), normalizar(r.titulo))),
}

CAMPOS_PESQUISA = ("titulo", "categoria")


class ListaEncadeada:
    def __init__(self):
        self.cabeca = None
        self.cauda = None
        self.tamanho = 0
        self.comparacoes = 0  # contador usado para mostrar o trabalho da ordenação

    def __len__(self):
        return self.tamanho

    def esta_vazia(self):
        return self.cabeca is None

    def __iter__(self):
        """Percurso: começa na cabeça e segue as referências até chegar em None. O(n)."""
        atual = self.cabeca
        while atual is not None:
            yield atual.registro
            atual = atual.proximo

    # ------------------------------------------------------------------
    # Inserção
    # ------------------------------------------------------------------
    def inserir(self, registro):
        """Insere no fim da lista.
        Ligar o nó na cauda é O(1), mas antes é preciso conferir se o ID já existe,
        o que percorre a lista: O(n) no total."""
        existente, _ = self.buscar_por_id(registro.id)
        if existente is not None:
            raise ValueError(f"Já existe um registro com o ID {registro.id}.")

        novo = No(registro)
        if self.esta_vazia():
            self.cabeca = novo
        else:
            self.cauda.proximo = novo
        self.cauda = novo
        self.tamanho += 1
        return registro

    # ------------------------------------------------------------------
    # Busca
    # ------------------------------------------------------------------
    def buscar_por_id(self, id):
        """Busca sequencial (linear) pelo ID. Devolve (registro ou None, nós visitados).
        Lista encadeada não tem acesso direto por posição, então busca binária
        não se aplica: no pior caso visita os n nós. O(n)."""
        id = validar_id(id)
        visitados = 0
        atual = self.cabeca
        while atual is not None:
            visitados += 1
            if atual.registro.id == id:
                return atual.registro, visitados
            atual = atual.proximo
        return None, visitados

    def pesquisar(self, campo, termo):
        """Busca sequencial por trecho de texto no título ou na categoria,
        sem diferenciar maiúsculas nem acentos. Visita sempre todos os nós,
        porque pode haver mais de um resultado. O(n) comparações de texto.
        Devolve (lista de registros encontrados, nós visitados)."""
        if campo not in CAMPOS_PESQUISA:
            raise ValueError(f"Só é possível pesquisar por: {', '.join(CAMPOS_PESQUISA)}.")
        termo = normalizar(termo)
        if not termo:
            raise ValueError("Digite pelo menos uma letra para pesquisar.")

        encontrados = []
        visitados = 0
        atual = self.cabeca
        while atual is not None:
            visitados += 1
            if termo in normalizar(getattr(atual.registro, campo)):
                encontrados.append(atual.registro)
            atual = atual.proximo
        return encontrados, visitados

    # ------------------------------------------------------------------
    # Atualização e remoção
    # ------------------------------------------------------------------
    def atualizar(self, id, **campos):
        """Acha o registro (O(n)) e troca os campos. A lista não muda de forma,
        só o conteúdo do nó. Devolve o registro atualizado ou None se não existir."""
        registro, _ = self.buscar_por_id(id)
        if registro is None:
            return None
        registro.atualizar(**campos)
        return registro

    def remover(self, id):
        """Remove o nó com o ID informado e religa os vizinhos. O(n).
        Casos tratados: lista vazia, remover a cabeça, o meio, a cauda e o único nó.
        Devolve o registro removido ou None se não existir."""
        id = validar_id(id)
        anterior = None
        atual = self.cabeca
        while atual is not None and atual.registro.id != id:
            anterior = atual
            atual = atual.proximo

        if atual is None:
            return None

        if anterior is None:
            self.cabeca = atual.proximo        # era a cabeça
        else:
            anterior.proximo = atual.proximo   # pula o nó removido

        if atual is self.cauda:
            self.cauda = anterior              # era a cauda (vira None se a lista esvaziou)

        atual.proximo = None
        self.tamanho -= 1
        return atual.registro

    # ------------------------------------------------------------------
    # Ordenação: Merge Sort próprio para lista encadeada
    # ------------------------------------------------------------------
    def ordenar(self, criterio="id"):
        """Ordena a própria lista religando os nós (não copia para list nem usa sorted).
        Merge Sort: divide a lista ao meio, ordena cada metade e intercala.
        O(n log n) comparações em qualquer caso, memória extra O(log n) da recursão.
        É estável: registros com chave igual mantêm a ordem em que estavam.
        Devolve quantas comparações foram feitas."""
        if criterio not in CRITERIOS:
            raise ValueError(f"Critério inválido. Use: {', '.join(CRITERIOS)}.")
        chave = CRITERIOS[criterio][1]
        self.comparacoes = 0

        self.cabeca = self._merge_sort(self.cabeca, chave)

        # A cauda mudou de lugar: anda até o último nó para reencontrá-la. O(n)
        self.cauda = self.cabeca
        while self.cauda is not None and self.cauda.proximo is not None:
            self.cauda = self.cauda.proximo
        return self.comparacoes

    def _merge_sort(self, cabeca, chave):
        if cabeca is None or cabeca.proximo is None:
            return cabeca  # 0 ou 1 nó: já está ordenado
        meio = self._dividir(cabeca)
        esquerda = self._merge_sort(cabeca, chave)
        direita = self._merge_sort(meio, chave)
        return self._intercalar(esquerda, direita, chave)

    @staticmethod
    def _dividir(cabeca):
        """Acha o meio com dois ponteiros: o lento anda 1 nó, o rápido anda 2.
        Quando o rápido chega ao fim, o lento está no meio. Corta a lista ali."""
        lento = cabeca
        rapido = cabeca.proximo
        while rapido is not None and rapido.proximo is not None:
            lento = lento.proximo
            rapido = rapido.proximo.proximo
        meio = lento.proximo
        lento.proximo = None
        return meio

    def _intercalar(self, a, b, chave):
        """Junta duas listas já ordenadas em uma só, religando os nós.
        Usa um nó sentinela para não tratar a cabeça como caso especial."""
        sentinela = No(None)
        fim = sentinela
        while a is not None and b is not None:
            self.comparacoes += 1
            if chave(a.registro) <= chave(b.registro):  # <= mantém a ordenação estável
                fim.proximo = a
                a = a.proximo
            else:
                fim.proximo = b
                b = b.proximo
            fim = fim.proximo
        fim.proximo = a if a is not None else b
        return sentinela.proximo

    # ------------------------------------------------------------------
    # Análise
    # ------------------------------------------------------------------
    def contar_por_categoria(self):
        """Percorre a lista uma vez e conta quantos registros há em cada categoria. O(n)."""
        contagem = {}
        for registro in self:
            contagem[registro.categoria] = contagem.get(registro.categoria, 0) + 1
        return contagem

    def proximo_id_livre(self):
        """Maior ID + 1, para sugerir no cadastro. O(n)."""
        maior = 0
        for registro in self:
            maior = max(maior, registro.id)
        return maior + 1

    def desenhar(self):
        """Mostra os nós e as referências, ex.: HEAD -> [1] -> [2] -> None. O(n)."""
        partes = ["cabeça"]
        for registro in self:
            partes.append(f"[{registro.id}]")
        partes.append("None")
        return " -> ".join(partes)
