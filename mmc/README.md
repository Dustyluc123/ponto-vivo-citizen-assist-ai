<h1 align="center">Ponto Vivo — Modelagem da Frota</h1>

<p align="center">
  <strong>Contribuição de Modelagem Matemática e Computacional ao Citizen Assist AI.</strong><br />
  Reconstrução da frota de ônibus por sistema linear e redistribuição por transformação linear, implementadas em Python.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.9+-3776ab?logo=python&logoColor=white" />
  <img alt="NumPy" src="https://img.shields.io/badge/NumPy-confer%C3%AAncia-013243?logo=numpy&logoColor=white" />
  <img alt="Jupyter" src="https://img.shields.io/badge/notebook-Jupyter_/_Colab-f37626?logo=jupyter&logoColor=white" />
  <img alt="FIAP GS 2026.2" src="https://img.shields.io/badge/FIAP-Global_Solution_2026.2-ed145b" />
</p>

> Esta pasta contém **apenas** a contribuição da disciplina de Modelagem Matemática e Computacional. O assistente principal está na [raiz do repositório](../README.md).

---

## Índice

- [Integrante](#integrante)
- [Resumo](#resumo)
- [Etapa 1: situação atual](#etapa-1-situação-atual)
- [Etapa 2: redistribuição](#etapa-2-redistribuição)
- [Como executar](#como-executar)
- [Limitações](#limitações)
- [Ligação com o Ponto Vivo](#ligação-com-o-ponto-vivo)

## Integrante

| Nome                  | RM     |
| --------------------- | ------ |
| Lucas Barreto Santana | 573149 |

## Resumo

Toda a solução, com as explicações de cada item (a até f das duas etapas), está no notebook [`mobilidade_frota.ipynb`](mobilidade_frota.ipynb), já executado.

| Resultado                                   | Valor                                  |
| ------------------------------------------- | -------------------------------------- |
| Distribuição atual recuperada (N, S, L, O)  | **(12, 20, 16, 24)**                   |
| Determinante da matriz do sistema           | **3** (diferente de zero: solução única) |
| Ônibus necessários no pico (N, S, L, O)     | **(14, 19, 18, 21)**, total de 72      |
| Passageiros sem vaga no pico, antes         | **160** (Norte e Leste)                |
| Ônibus movidos pela política                | **4**                                  |
| Distribuição depois da política             | **(14, 19, 18, 21)**                   |
| Passageiros sem vaga no pico, depois        | **0**                                  |

## Etapa 1: situação atual

**Variáveis:** N, S, L e O são os ônibus de cada centro operacional (inteiros, não negativos).

**Sistema matricial** montado com os quatro indicadores do Relatório I:

```
| 1  1  1  1 |   | N |   | 72 |     frota total
| 1  2  0  1 | · | S | = | 76 |     N + 2S + O
| 0  1  2  0 |   | L |   | 52 |     S + 2L
| 1  0  1  2 |   | O |   | 76 |     N + L + 2O
```

**Unicidade:** o escalonamento feito à mão (eliminação de Gauss com frações exatas) encontra 4 pivôs, então posto(A) = posto([A | b]) = 4 = número de incógnitas, e det(A) = 3. Pelo Teorema de Rouché–Capelli, o sistema é **possível e determinado**: existe uma única distribuição.

**Resolução e verificação:** a substituição regressiva dá **(12, 20, 16, 24)**, o mesmo resultado do `numpy.linalg.solve`. A solução satisfaz os quatro registros, é inteira e não negativa.

## Etapa 2: redistribuição

**Necessidade:** ônibus necessários = passageiros ÷ 40, arredondado para cima. Todas as divisões são exatas e somam 72, o tamanho da frota.

| Região | Atual | Necessário | Saldo | Ocupação no pico |
| ------ | ----- | ---------- | ----- | ---------------- |
| Norte  | 12    | 14         | −2    | 116,7%           |
| Sul    | 20    | 19         | +1    | 95,0%            |
| Leste  | 16    | 18         | −2    | 112,5%           |
| Oeste  | 24    | 21         | +3    | 87,5%            |

**Política proposta:** Oeste envia 2 ônibus para o Norte e 1 para o Leste; Sul envia 1 para o Leste.

Critérios: só cede quem tem sobra e só recebe quem tem falta; prioridade para regiões vizinhas (Norte–Oeste, Sul–Leste); o Oeste, com a maior sobra, cede mais; e são movidos só 4 ônibus, o mínimo para zerar as faltas.

**Transformação linear** T(x) = Mx, em que cada região envia uma fração fixa da sua frota (colunas = origem, linhas = destino):

```
      N     S     L     O
N  |  1     0     0   1/12 |
S  |  0   19/20   0     0  |
L  |  0    1/20   1   1/24 |
O  |  0     0     0    7/8 |
```

O coeficiente m<sub>ij</sub> é a fração dos ônibus da região j que passa a atender a região i. A diagonal é o que fica em cada região; fora dela, o que é transferido.

**Provas:**

- **Total preservado:** cada coluna de M soma 1, ou seja, 1ᵀM = 1ᵀ. Então 1ᵀ(Mx) = 1ᵀx para qualquer frota x.
- **Sem valores negativos:** todos os coeficientes de M são ≥ 0. Se x ≥ 0, cada nova quantidade é uma soma de produtos não negativos, logo Mx ≥ 0.

O notebook confere as duas propriedades na matriz e testa a transformação em 10.000 frotas aleatórias.

## Como executar

**No Google Colab:** abra o notebook pelo GitHub (Arquivo, Abrir notebook, aba GitHub) e use Ambiente de execução, Executar tudo. O Colab já tem o NumPy.

**No computador:**

```bash
# Na raiz do repositório
pip install numpy jupyter
jupyter notebook mmc/mobilidade_frota.ipynb
```

O escalonamento e as provas usam só a biblioteca padrão (`fractions`). O NumPy é usado apenas para conferir os resultados.

## Limitações

- As frações da matriz foram calculadas para a frota atual. Em outra frota, podem gerar quantidades fracionárias e seria preciso recalcular ou arredondar mantendo o total.
- A matriz descreve uma redistribuição única: aplicá-la de novo tiraria ônibus de regiões que já estariam equilibradas.
- A necessidade total é igual à frota. Qualquer ônibus em manutenção volta a deixar passageiros sem vaga.
- A demanda é de um único horário (pico). Os dados são hipotéticos, fornecidos pelo enunciado.

## Ligação com o Ponto Vivo

O abrigo Ponto Vivo conta quantas pessoas esperam em cada ponto. Somando esses dados por região, a demanda do Relatório II poderia ser medida de verdade, em vários horários, e a mesma matriz de redistribuição recalculada para cada faixa do dia.
