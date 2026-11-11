<h1 align="center">Ponto Vivo — Perfil dos Passageiros</h1>

<p align="center">
  <strong>Contribuição de Modelagem Linear para Aprendizado de Máquina ao Citizen Assist AI.</strong><br />
  Quem usa o ônibus e quem usa o metrô em São Paulo: classificação do perfil dos usuários com regressão logística e dados reais da Pesquisa Origem e Destino 2017.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.9+-3776ab?logo=python&logoColor=white" />
  <img alt="scikit-learn" src="https://img.shields.io/badge/scikit--learn-regress%C3%A3o_log%C3%ADstica-f7931e?logo=scikitlearn&logoColor=white" />
  <img alt="Dados" src="https://img.shields.io/badge/dados-OD_2017_Metr%C3%B4_SP-0b7285" />
  <img alt="Jupyter" src="https://img.shields.io/badge/notebook-Jupyter_/_Colab-f37626?logo=jupyter&logoColor=white" />
</p>

> Esta pasta contém **apenas** a contribuição da disciplina de Modelagem Linear para Aprendizado de Máquina. O assistente principal está na [raiz do repositório](../README.md).

---

## Índice

- [Integrante](#integrante)
- [Resumo](#resumo)
- [Base de dados](#base-de-dados)
- [Principais resultados](#principais-resultados)
- [Arquivos](#arquivos)
- [Como executar](#como-executar)
- [Limitações](#limitações)

## Integrante

| Nome                  | RM     |
| --------------------- | ------ |
| Lucas Barreto Santana | 573149 |

## Resumo

O modelo classifica, a partir do perfil de uma pessoa (sexo, faixa etária, escolaridade, faixa de renda, situação de trabalho e carros no domicílio), se ela usa o **ônibus municipal (SPTrans)** ou o **metrô**. Uma extensão inclui também o **trem (CPTM)**.

O relatório completo, com as seções Introdução, Metodologia, Resultados, Análise e Discussão e Conclusões, está em [`relatorio_perfil_transporte.pdf`](relatorio_perfil_transporte.pdf).

## Base de dados

**Pesquisa Origem e Destino 2017** da Região Metropolitana de São Paulo, feita pelo Metrô com entrevistas domiciliares. Dados reais, com um registro por viagem e o perfil de cada pessoa.

| Item | Detalhe |
| ---- | ------- |
| Fonte oficial | [Metrô de SP, portal de transparência](https://transparencia.metrosp.com.br/dataset/pesquisa-origem-e-destino) |
| Arquivo usado | `od_sao_paulo_2017_not_harmonized.csv.gz` (8,4 MB), redistribuído sem alteração pelo pacote [odbr](https://github.com/hsvab/odbr) |
| Recorte | moradores do município de São Paulo que usaram ônibus municipal, metrô ou trem |
| Unidade | uma pessoa (serviço da primeira viagem de transporte público do dia) |
| Tamanho final | 14.951 pessoas |

O arquivo de dados **não fica no repositório**: o notebook baixa sozinho e confere a impressão digital (SHA-256).

## Principais resultados

| Resultado | Valor |
| --------- | ----- |
| Característica mais associada ao serviço (qui-quadrado) | **escolaridade** (V de Cramér = 0,176), seguida da renda (0,147) |
| Superior completo × fundamental I incompleto | **2,69 vezes** a chance de usar metrô |
| Renda acima de 2 salários mínimos por pessoa | **1,74 vez** a chance de usar metrô |
| AUC ROC (teste) | **0,667** |
| Acurácia / acurácia balanceada (teste) | **61,3% / 61,9%** (referência: 60,6% / 50%) |
| Validação cruzada (5 partes) | acurácia 0,613 ± 0,007, AUC 0,668 ± 0,006 |
| Uso do metrô até 5 km do centro × acima de 10 km | **53% × cerca de 30%** |

Conclusão: os dois públicos são diferentes (quem usa ônibus tem menos escolaridade e renda), mas o perfil explica só parte da escolha. **Onde a pessoa mora** pesa muito, e o trem é praticamente explicado só pela localização. O público do ônibus é o público do Ponto Vivo: precisa de linguagem simples, atendimento no próprio ponto e divulgação das gratuidades.

## Arquivos

```
ml/
├── README.md
├── perfil_transporte.ipynb             # Código completo, já executado
├── relatorio_perfil_transporte.pdf     # Relatório com as 5 seções pedidas
└── figuras/                            # Gráficos gerados pelo notebook
    ├── 1_perfil_por_servico.png
    ├── 2_matriz_confusao_e_roc.png
    ├── 3_razoes_de_chances.png
    └── 4_matriz_confusao_tres_servicos.png
```

## Como executar

**No Google Colab:** abra o notebook pelo GitHub (Arquivo, Abrir notebook, aba GitHub) e use Ambiente de execução, Executar tudo. Todas as bibliotecas já vêm instaladas no Colab.

**No computador:**

```bash
# Na raiz do repositório
pip install pandas scikit-learn statsmodels scipy matplotlib jinja2 jupyter
jupyter notebook ml/perfil_transporte.ipynb
```

A divisão treino/teste e a validação cruzada usam semente fixa (42), então os números saem iguais aos do relatório.

## Limitações

- Dados de 2017: a rede de metrô e os hábitos mudaram desde então.
- A pesquisa não traz a distância até a estação mais próxima, que deve ser o fator de maior peso.
- O modelo é linear e não captura combinações entre características sem termos de interação.
