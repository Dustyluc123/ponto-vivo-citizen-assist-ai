<h1 align="center">Ponto Vivo — DSA</h1>

<p align="center">
  <strong>Contribuição de Data Structures and Algorithms ao Citizen Assist AI.</strong><br />
  Cadastro de serviços ao passageiro de ônibus guardado em uma lista encadeada própria, com busca sequencial e Merge Sort feitos à mão.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.9+-3776ab?logo=python&logoColor=white" />
  <img alt="Sem dependências" src="https://img.shields.io/badge/depend%C3%AAncias-nenhuma-12a85f" />
  <img alt="Estrutura" src="https://img.shields.io/badge/estrutura-lista_encadeada-0b7285" />
  <img alt="Ordenação" src="https://img.shields.io/badge/ordena%C3%A7%C3%A3o-Merge_Sort-f59f00" />
  <img alt="Testes" src="https://img.shields.io/badge/testes-41_passando-12a85f" />
</p>

> Esta pasta contém **apenas** a contribuição da disciplina de Data Structures and Algorithms. O assistente principal está na [raiz do repositório](../README.md).

---

## Índice

- [Integrante](#integrante)
- [Recorte escolhido](#recorte-escolhido)
- [Funcionalidades](#funcionalidades)
- [Modelo dos registros](#modelo-dos-registros)
- [Lista encadeada](#lista-encadeada)
- [Algoritmo de busca](#algoritmo-de-busca)
- [Algoritmo de ordenação](#algoritmo-de-ordenação)
- [Análise Big-O](#análise-big-o)
- [Menu](#menu)
- [Estrutura de pastas](#estrutura-de-pastas)
- [Como executar](#como-executar)
- [Testes](#testes)
- [Limitações](#limitações)
- [Vídeo](#vídeo)

## Integrante

| Nome                  | RM     |
| --------------------- | ------ |
| Lucas Barreto Santana | 573149 |

## Recorte escolhido

**Serviços urbanos: transporte público por ônibus em São Paulo.**

O Ponto Vivo atende passageiros que esperam no ponto de ônibus, com atenção a idosos, pessoas com deficiência e estudantes. Este módulo é a parte de **cadastro** do assistente: quem mantém o Ponto Vivo (por exemplo, a equipe da prefeitura) cadastra, corrige, remove e organiza os serviços e orientações que o assistente mostra.

Na primeira execução, o programa importa as **15 orientações** da base do assistente de Python ([`data/base_conhecimento.json`](../data/base_conhecimento.json)), que têm fonte oficial e data de verificação. A partir daí, tudo fica na lista encadeada, e as alterações são salvas em [`dados/registros.json`](dados/registros.json).

## Funcionalidades

- [x] Lista encadeada própria (classes `No` e `ListaEncadeada`), sem guardar os dados em `list`
- [x] Cadastro com ID único, sugestão do próximo ID livre e recusa de ID duplicado
- [x] Consulta por ID com busca sequencial, mostrando quantos nós foram visitados
- [x] Pesquisa por título ou categoria, sem diferenciar maiúsculas nem acentos
- [x] Atualização campo a campo (Enter mantém o valor atual) sem mudar a forma da lista
- [x] Exclusão com confirmação, tratando cabeça, meio, cauda e único nó
- [x] Ordenação por ID, título ou categoria com **Merge Sort** próprio, religando os nós
- [x] Análise: total, quantidade por categoria, média de requisitos e serviço que mais pede documentos
- [x] Desenho da estrutura (`cabeça -> [1] -> [2] -> ... -> None`) para mostrar os nós de verdade
- [x] Tratamento de opção inválida, ID inválido, ID duplicado, campo vazio e lista vazia
- [x] Extensão opcional: salvar e carregar em JSON

## Modelo dos registros

Cada serviço é um objeto da classe `Registro` ([`registro.py`](registro.py)):

| Campo        | Tipo            | Obrigatório | Exemplo                                              | Validação                         |
| ------------ | --------------- | ----------- | ---------------------------------------------------- | --------------------------------- |
| `id`         | inteiro         | sim         | `7`                                                  | inteiro positivo e único na lista |
| `titulo`     | texto           | sim         | Integração do Bilhete Único: quantos ônibus com uma tarifa | não vazio, até 600 caracteres |
| `categoria`  | texto           | sim         | Viagem e Informação                                  | não vazio                         |
| `descricao`  | texto           | sim         | Com o Bilhete Único Comum, você paga uma tarifa...   | não vazio                         |
| `requisitos` | lista de textos | não         | `["Bilhete Único com crédito"]`                      | itens vazios são descartados      |
| `local`      | texto           | sim         | Ônibus municipais, Metrô e CPTM                      | não vazio                         |
| `fonte`      | texto           | não         | https://www.sptrans.com.br/...                       | livre                             |

O **ID nunca muda** depois do cadastro, porque é a chave usada para consultar, atualizar e excluir. Se algum campo da atualização for inválido, **nenhum** campo é alterado.

## Lista encadeada

Implementada em [`lista_encadeada.py`](lista_encadeada.py).

```
 cabeca                                              cauda
   |                                                   |
 [ 1 | o-]--> [ 2 | o-]--> [ 3 | o-]--> ... --> [ 15 | None ]
```

- **`No`**: guarda o `registro` e a referência `proximo` para o nó seguinte.
- **`ListaEncadeada`**: guarda `cabeca` (primeiro nó), `cauda` (último nó) e `tamanho`.

| Operação    | Como funciona                                                                                       |
| ----------- | --------------------------------------------------------------------------------------------------- |
| Inserção    | Confere se o ID já existe; depois liga o novo nó em `cauda.proximo` e move a cauda para ele          |
| Percurso    | Começa na cabeça e segue `proximo` até chegar em `None` (usado por listar, salvar e analisar)        |
| Remoção     | Anda com dois ponteiros (`anterior` e `atual`); ao achar o ID, faz `anterior.proximo = atual.proximo` |
| Atualização | Acha o nó e troca só os dados do registro; as ligações não mudam                                   |

Casos especiais da remoção, todos cobertos por testes:

| Caso              | O que muda                                          |
| ----------------- | --------------------------------------------------- |
| Remover a cabeça  | `cabeca` passa a ser o segundo nó                   |
| Remover a cauda   | `cauda` passa a ser o nó anterior                   |
| Remover o único nó | `cabeca` e `cauda` viram `None`                    |
| ID inexistente    | nada muda, a função devolve `None`                  |

Guardar a `cauda` deixa o encaixe do nó no fim em O(1), sem precisar andar a lista para achar o último.

## Algoritmo de busca

**Busca sequencial (linear)**, em `buscar_por_id` e `pesquisar`.

1. Começa na cabeça com um contador de nós visitados.
2. Compara o nó atual com o que se procura.
3. Se bateu, devolve o registro (na busca por ID) ou guarda na lista de resultados (na pesquisa por texto).
4. Se não bateu, segue para `proximo`. Ao chegar em `None` sem achar, a busca termina sem resultado e o menu avisa.

**Por que não busca binária?** A busca binária precisa pular direto para o elemento do meio. Em uma lista encadeada não há acesso por posição: chegar ao meio já custa percorrer metade da lista. Por isso a busca sequencial é a escolha correta para esta estrutura.

**Pesquisa por texto:** compara o termo com o título ou a categoria depois de **normalizar** os dois (minúsculas e sem acentos), então "ENERGIA", "energia" e "Energia" encontram o mesmo registro, e "onibus" acha "ônibus". A pesquisa visita **todos** os nós, porque pode haver mais de um resultado.

O menu mostra o trabalho real da busca, por exemplo `Busca sequencial: 7 de 15 nós visitados.` para o ID 7, e `15 de 15` para um ID inexistente.

## Algoritmo de ordenação

**Merge Sort** implementado do zero para lista encadeada, em `ordenar`, `_merge_sort`, `_dividir` e `_intercalar`. Não usa `sorted`, `list.sort` nem copia os registros para uma `list`: **ordena religando os próprios nós**.

1. **Caso base:** lista com 0 ou 1 nó já está ordenada.
2. **Dividir:** acha o meio com dois ponteiros. O `lento` anda 1 nó e o `rapido` anda 2; quando o `rapido` chega ao fim, o `lento` está no meio. A lista é cortada ali.
3. **Conquistar:** ordena cada metade chamando o próprio Merge Sort (recursão).
4. **Intercalar:** junta as duas metades ordenadas, sempre pegando o menor dos dois primeiros nós. Um nó sentinela evita tratar a cabeça como caso especial.
5. Depois de ordenar, anda até o último nó para atualizar a `cauda`.

Critérios disponíveis:

| Critério  | Chave comparada                           |
| --------- | ----------------------------------------- |
| ID        | número do ID                              |
| Título    | título normalizado (sem acento, minúsculo) |
| Categoria | categoria normalizada e, em empate, título |

**Por que Merge Sort?** Em lista encadeada ele é o mais adequado dos quatro estudados: não precisa de acesso por posição (o Quick Sort perde a escolha de pivô e a partição por índice), faz O(n log n) comparações **em qualquer caso** (Selection Sort e Insertion Sort chegam a O(n²), e o Quick Sort também, no pior caso) e é **estável**, ou seja, registros com a mesma chave mantêm a ordem anterior. Isso permite, por exemplo, ordenar por título e depois por categoria sem bagunçar os títulos dentro de cada categoria.

Medido nas evidências: ordenar os 15 serviços fez **35 comparações** por título, **38** por categoria e **37** por ID, abaixo de n·log₂n ≈ 59.

## Análise Big-O

n = número de registros na lista. A análise segue o código como ele está implementado.

| Operação                   | Função                         | Tempo           | Justificativa                                                                                         |
| -------------------------- | ------------------------------ | --------------- | ----------------------------------------------------------------------------------------------------- |
| Inserção (cadastro)        | `inserir`                      | **O(n)**        | Ligar na cauda é O(1), mas antes é preciso percorrer a lista para garantir que o ID não está repetido |
| Busca por ID               | `buscar_por_id`                | **O(n)**        | Melhor caso O(1) (ID na cabeça); pior caso visita os n nós (ID na cauda ou inexistente)                |
| Pesquisa por título/categoria | `pesquisar`                 | **O(n · m)**    | Visita sempre os n nós; cada comparação de texto custa até m, o tamanho do texto (tratado como constante, fica O(n)) |
| Atualização                | `atualizar`                    | **O(n)**        | Busca O(n) + troca dos campos O(1)                                                                     |
| Remoção                    | `remover`                      | **O(n)**        | Precisa achar o nó e o anterior a ele; religar é O(1). Remover a cabeça é O(1)                        |
| Ordenação                  | `ordenar` (Merge Sort)         | **O(n log n)**  | log n níveis de divisão e, em cada nível, n comparações ao intercalar. Igual no melhor, médio e pior caso |
| Percurso / listagem        | `__iter__`                     | O(n)            | Visita cada nó uma vez                                                                                 |
| Contagem por categoria     | `contar_por_categoria`         | O(n)            | Um percurso, com dicionário para somar (O(1) em média por categoria)                                   |
| Carregar o arquivo         | `armazenamento.carregar`       | O(n²)           | n inserções, cada uma O(n) por causa da conferência de ID. Com 15 registros é imperceptível           |

**Memória:** a lista usa O(n) (um nó por registro). O Merge Sort não cria nós novos: só usa O(log n) da pilha de recursão e um nó sentinela por intercalação.

## Menu

```
╭──────────────────────────────────────────────────────────────────────╮
│ PONTO VIVO  ·  Cadastro de serviços                                  │
│ Lista encadeada própria · Data Structures and Algorithms             │
╰──────────────────────────────────────────────────────────────────────╯
  1  Cadastrar serviço
  2  Consultar por ID
  3  Pesquisar por título ou categoria
  4  Atualizar serviço
  5  Excluir serviço
  6  Ordenar e listar
  7  Análise (indicadores)
  8  Listar na ordem atual
  9  Ver a estrutura da lista (nós)
  0  Sair
```

| Situação                       | O que o programa faz                                                     |
| ------------------------------ | ------------------------------------------------------------------------ |
| Opção fora de 0 a 9 ou texto   | "Opção inválida. Digite um número de 0 a 9." e pergunta de novo          |
| ID com letras, zero ou negativo | "O ID deve ser um número inteiro positivo." e pergunta de novo          |
| ID já usado no cadastro        | Mostra qual serviço usa o ID e pede outro                                |
| Campo obrigatório vazio        | "Este campo não pode ficar vazio." e pergunta de novo                    |
| Lista vazia (opções 2 a 8)     | "A lista está vazia. Cadastre um serviço primeiro (opção 1)."            |
| ID inexistente                 | "Nenhum serviço com o ID 99."                                            |
| Pesquisa sem resultado         | "Nenhum serviço encontrado para ..."                                     |
| Confirmação diferente de s/n   | "Responda s ou n." e pergunta de novo                                    |
| Ctrl+C ou fim da entrada       | Encerra sem mostrar erro                                                 |

## Estrutura de pastas

```
dsa/
├── README.md
├── main.py               # Menu interativo e leitura de dados com validação
├── lista_encadeada.py    # Classes No e ListaEncadeada: inserção, busca, remoção, Merge Sort
├── registro.py           # Classe Registro e validações
├── armazenamento.py      # Salvar e carregar em JSON e importar a base do Ponto Vivo
├── testes.py             # 41 testes automáticos (unittest)
├── dados/
│   └── registros.json    # Registros salvos (criado na primeira execução)
└── evidencias/
    ├── 01_lista_vazia_e_entradas_invalidas.txt
    ├── 02_operacoes_com_a_base.txt
    └── 03_testes_automaticos.txt
```

O menu reaproveita o [`tela.py`](../tela.py) da raiz para as cores e caixas. Só usa a biblioteca padrão do Python.

## Como executar

### Pré-requisitos

- [Python](https://www.python.org/) 3.9 ou mais novo

### Passo a passo

```bash
# Na raiz do repositório

# 1. Abre o menu (usa e salva dsa/dados/registros.json)
python dsa/main.py

# 2. Abre o menu com a lista vazia, sem salvar nada (para testar os casos de lista vazia)
python dsa/main.py --vazia

# 3. Roda os testes automáticos
python dsa/testes.py
```

Para voltar aos 15 serviços originais, apague `dsa/dados/registros.json` e abra o menu de novo: ele importa a base do Ponto Vivo outra vez.

## Testes

### Testes automáticos

[`testes.py`](testes.py) tem **41 testes** com `unittest`, todos passando ([`evidencias/03_testes_automaticos.txt`](evidencias/03_testes_automaticos.txt)). Eles conferem, depois de cada operação, se `cabeca`, `cauda` e `tamanho` batem com os nós que estão realmente ligados.

| Grupo                 | Testes | O que cobre                                                                    |
| --------------------- | ------ | ------------------------------------------------------------------------------ |
| Lista vazia           | 7      | Buscar, pesquisar, remover, atualizar, ordenar e analisar sem nenhum registro   |
| Inserção              | 2      | Ordem de inserção, cabeça e cauda corretas, recusa de ID duplicado             |
| Validação do registro | 4      | IDs inválidos (0, -5, "abc", vazio, "1.5", None, True), campos vazios, requisitos |
| Busca                 | 7      | ID existente e inexistente, ID inválido, pesquisa sem acento, sem resultado     |
| Atualização           | 4      | Atualizar campos, ID inexistente, ID não muda, valor inválido não altera nada  |
| Remoção               | 5      | Cabeça, meio, cauda, esvaziar a lista, ID inexistente                          |
| Ordenação             | 8      | Por ID, título e categoria, estabilidade, 1 registro, critério inválido, limite n·log n |
| Análise e arquivo     | 4      | Contagem por categoria, salvar e carregar, arquivo com registros ruins, importar a base |

### Testes pelo menu

Executados com as entradas digitadas registradas nos arquivos de [`evidencias/`](evidencias/).

| #  | Caso                       | Entrada                                  | Resultado esperado                                  | Resultado obtido                                                           | Situação |
| -- | -------------------------- | ---------------------------------------- | --------------------------------------------------- | -------------------------------------------------------------------------- | -------- |
| 1  | Opção inválida             | `abc` e depois `12`                      | Recusar e perguntar de novo                          | "Opção inválida. Digite um número de 0 a 9." duas vezes                    | ok       |
| 2  | Lista vazia                | Opções 2 a 8 com `--vazia`               | Avisar que a lista está vazia                        | "A lista está vazia. Cadastre um serviço primeiro (opção 1)." 7 vezes      | ok       |
| 3  | Estrutura vazia            | Opção 9 com `--vazia`                    | Mostrar a lista sem nós                              | `cabeça -> None`, cabeça e cauda = None, tamanho = 0                       | ok       |
| 4  | ID inválido no cadastro    | `abc` e depois `-3`                      | Recusar os dois                                      | "O ID deve ser um número inteiro positivo." duas vezes                     | ok       |
| 5  | Campo obrigatório vazio    | Título só com espaços                    | Recusar e pedir de novo                              | "Este campo não pode ficar vazio."                                         | ok       |
| 6  | Primeiro cadastro          | Serviço com ID sugerido 1                | Lista com 1 nó, cabeça = cauda = 1                   | "Serviço #1 cadastrado. Total: 1." e `cabeça -> [1] -> None`                | ok       |
| 7  | Consulta existente         | ID `7`                                   | Mostrar o serviço 7 visitando 7 nós                  | Integração do Bilhete Único, "7 de 15 nós visitados"                       | ok       |
| 8  | Consulta inexistente       | ID `99`                                  | Avisar que não existe, visitando os 15 nós           | "Nenhum serviço com o ID 99.", "15 de 15 nós visitados"                    | ok       |
| 9  | Pesquisa por título        | `bilhete`                                | Os serviços com "Bilhete" no título                  | 5 encontrados (IDs 2, 3, 4, 7 e 8)                                         | ok       |
| 10 | Pesquisa por categoria     | `ENERGIA` (maiúsculas)                   | Os 3 serviços de Energia e Sustentabilidade          | 3 encontrados (IDs 13, 14 e 15)                                            | ok       |
| 11 | Pesquisa sem resultado     | `metrô`                                  | Avisar que não achou                                 | "Nenhum serviço encontrado para "metrô"."                                  | ok       |
| 12 | ID duplicado               | ID `3` no cadastro                       | Recusar e dizer quem usa o ID                        | "O ID 3 já está em uso por "Bilhete Único de Estudante..."."               | ok       |
| 13 | Cadastro completo          | Enter (ID 16), categoria `1`, 3 requisitos | Inserir no fim                                      | "Serviço #16 cadastrado. Total: 16." e consulta visita 16 de 16 nós       | ok       |
| 14 | Atualização                | Novo título, Enter nos outros campos     | Trocar só o título                                   | Título novo, categoria, requisitos e local mantidos                        | ok       |
| 15 | Confirmação inválida       | `talvez` e depois `s`                    | Pedir s ou n e então excluir                         | "Responda s ou n." e "Serviço #16 excluído. Total: 15."                    | ok       |
| 16 | Excluir inexistente        | ID `99`                                  | Avisar que não existe                                | "Nenhum serviço com o ID 99."                                              | ok       |
| 17 | Ordenar por título         | Critério `2`                             | A a Z ignorando acento ("Ônibus" junto do "O")       | Ordem correta, 35 comparações                                              | ok       |
| 18 | Ordenar por categoria      | Critério `3`                             | Categoria A a Z e título dentro dela                 | Clima, Energia, Tarifas, Viagem, 38 comparações                            | ok       |
| 19 | Ordenar por ID             | Critério `1`                             | 1 a 15                                               | Ordem 1 a 15, 37 comparações                                               | ok       |
| 20 | Análise                    | Opção 7                                  | Total e quantidade por categoria                     | 15 serviços: Tarifas 6, Viagem 4, Energia 3, Clima 2; média de 2,1 requisitos | ok    |
| 21 | Estrutura após ordenar     | Opção 9                                  | Nós religados de 1 a 15, cauda = 15                  | `cabeça -> [1] -> ... -> [15] -> None`, cauda = 15                         | ok       |

Os casos 1 a 6 estão em [`01_lista_vazia_e_entradas_invalidas.txt`](evidencias/01_lista_vazia_e_entradas_invalidas.txt) e os casos 7 a 21 em [`02_operacoes_com_a_base.txt`](evidencias/02_operacoes_com_a_base.txt).

## Limitações

- Busca, atualização e remoção são O(n). Para milhares de registros, uma tabela hash por ID deixaria a consulta em O(1) em média, mas o enunciado pede a lista encadeada como estrutura principal.
- A pesquisa encontra trechos de texto, não sinônimos: "idoso" não acha "pessoa com 60 anos".
- Na atualização, Enter mantém os requisitos. Para trocar a lista de requisitos é preciso digitar a nova lista inteira.
- Os serviços vêm da base do Ponto Vivo, conferida em 05/11/2026. Este módulo **não é canal oficial** da Prefeitura nem da SPTrans.

## Vídeo

_Link da demonstração a adicionar._
