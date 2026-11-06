<h1 align="center">Ponto Vivo — Energia</h1>

<p align="center">
  <strong>Contribuição de Soluções em Energias Renováveis e Sustentáveis ao Citizen Assist AI.</strong><br />
  Como alimentar o ventilador e a eletrônica de um ponto de ônibus em São Paulo, e como levar essa análise para as respostas do assistente.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.9+-3776ab?logo=python&logoColor=white" />
  <img alt="Dados INMET" src="https://img.shields.io/badge/temperatura-INMET_2025-0b7285" />
  <img alt="Dados CRESESB" src="https://img.shields.io/badge/sol-CRESESB-f59f00" />
  <img alt="Tarifa ANEEL" src="https://img.shields.io/badge/tarifa-ANEEL_2026-12a85f" />
</p>

> Esta pasta contém **apenas** a contribuição da disciplina de Energias Renováveis. O assistente principal está na [raiz do repositório](../README.md).

---

## Índice

- [Integrante](#integrante)
- [Público e necessidade energética](#público-e-necessidade-energética)
- [Resumo da análise](#resumo-da-análise)
- [Dados utilizados](#dados-utilizados)
- [Premissas estimadas](#premissas-estimadas)
- [Consumo e controle inteligente](#consumo-e-controle-inteligente)
- [Dimensionamento do sistema solar](#dimensionamento-do-sistema-solar)
- [Alternativas comparadas](#alternativas-comparadas)
- [Recomendações](#recomendações)
- [Limitações](#limitações)
- [Integração ao assistente](#integração-ao-assistente)
- [Como executar e testar](#como-executar-e-testar)
- [Testes com usuários](#testes-com-usuários)
- [Referências](#referências)
- [Vídeo](#vídeo)

## Integrante

| Nome                  | RM     |
| --------------------- | ------ |
| Lucas Barreto Santana | 573149 |

## Público e necessidade energética

**Público:** passageiros de ônibus de São Paulo que esperam no ponto, com atenção a idosos, pessoas com deficiência e trabalhadores que ficam expostos ao calor.

**Necessidade energética:** o abrigo Ponto Vivo precisa de energia para dois ventiladores pequenos (ligados só no calor) e para a eletrônica que conta as pessoas, mede a temperatura, mostra a espera na tela e envia os dados (ligada 24 horas). A maioria dos pontos de ônibus simples não tem ligação elétrica.

**Pergunta da análise:** para um mesmo ponto e um mesmo período de 10 anos, o que é melhor: ligar na rede elétrica ou usar energia solar com bateria? E quanto economiza ligar o ventilador só quando precisa?

## Resumo da análise

| Resultado                                                 | Valor                          |
| --------------------------------------------------------- | ------------------------------ |
| Horas com 30 °C ou mais em 2025 (5h às 23h, INMET A701)    | **332 h em 85 dias**           |
| Energia economizada pelo controle inteligente do ventilador | **88,6 %**                     |
| Consumo anual do abrigo com controle                      | **22,1 kWh** (cerca de 1,8 kWh/mês) |
| Sistema solar necessário                                  | **painel de 150 W + bateria LiFePO4 de 50 Ah** |
| Custo em 10 anos, ponto sem energia: solar                | **R$ 3.150** (estimado)        |
| Custo em 10 anos, ponto sem energia: rede elétrica        | **R$ 6.271** (estimado)        |
| Custo em 10 anos, ponto que já tem energia: rede          | **R$ 306** (estimado)          |

Conclusão: **em ponto sem energia, o solar é a melhor opção**; em ponto que já tem energia, a rede com controle inteligente é mais barata. Em qualquer caso, ligar o ventilador só com calor e gente esperando corta quase 90 % do gasto do ventilador.

## Dados utilizados

| Dado | Valor | Unidade | Período | Origem | Arquivo |
| ---- | ----- | ------- | ------- | ------ | ------- |
| Temperatura do ar, de hora em hora | 8.760 medições | °C | 01/01/2025 a 31/12/2025 | INMET, estação automática A701 (São Paulo - Mirante de Santana) | [`dados/inmet_a701_sao_paulo_2025.csv`](dados/inmet_a701_sao_paulo_2025.csv) |
| Irradiação solar média diária por mês | 4,12 a 5,22 (painel a 24°) | kWh/m².dia | média histórica | CRESESB/CEPEL, SunData, estação São Paulo (23,5° S; 46,649° O) | [`dados/irradiacao_sao_paulo_cresesb.csv`](dados/irradiacao_sao_paulo_cresesb.csv) |
| Tarifa Enel SP, subgrupo B3, convencional | TUSD 472,42 + TE 316,96 = 789,38 | R$/MWh (sem impostos) | 04/07/2026 a 03/07/2027 | ANEEL, Resolução Homologatória 3.596/2026 (dados abertos) | `calculos.py` |
| ICMS sobre energia não residencial em SP | 18 | % | 2026 | Secretaria da Fazenda de SP | `calculos.py` |
| Custo de disponibilidade (consumo mínimo cobrado) | 30 | kWh/mês (monofásico) | vigente | ANEEL (regras de fornecimento) | `calculos.py` |
| Fator de emissão da rede elétrica (SIN) | 0,0385 | kg CO2/kWh | média de 2023 | MCTI | `calculos.py` |
| Emissão por passageiro na RMSP | ônibus 80, carro a gasolina 120 | g CO2/passageiro-km | média publicada | Metrô de São Paulo | `calculos.py` |

Os horários do INMET vêm em UTC e foram convertidos para o horário de Brasília (UTC−3). As horas sem medição (47 no arquivo) foram ignoradas.

## Premissas estimadas

Valores que não vêm de uma fonte oficial. Todos ficam no topo de [`calculos.py`](calculos.py) e podem ser mudados.

| Premissa | Valor | Justificativa |
| -------- | ----- | ------------- |
| Potência de cada ventilador 12 V DC | 20 W | Ventiladores 12 V comerciais ficam entre 10 e 25 W |
| Quantidade de ventiladores | 2 | Um de cada lado do abrigo |
| Eletrônica (ESP32, sensor, tela, LEDs) | 1 W, 24 h | O ESP32 consome em média cerca de 80 mA; o valor tem folga para tela e conversores |
| Temperatura que liga o ventilador | 30 °C | Mesma regra do módulo de Computer Science |
| Horário de uso | 5h às 23h | Horário em que há ônibus e passageiros |
| Cenário sem controle | timer das 10h às 18h, todos os dias | Forma simples de ligar um ventilador sem sensor |
| PIS/COFINS | 5 % | Varia todo mês na conta; usado só na tarifa com impostos |
| Ligação nova à rede (padrão, cabos, obra) | R$ 2.500 | Ordem de grandeza; precisa de orçamento real |
| Fonte 12 V para ligar na tomada | R$ 80 | Preço de varejo |
| Perdas do sistema solar (performance ratio) | 0,75 | Calor no painel, sujeira, cabos, controlador e bateria |
| Uso máximo da bateria | 80 % | Uso seguro de bateria de lítio LiFePO4 |
| Autonomia | 1 dia | Aguentar um dia quente inteiro sem sol |
| Painel solar | R$ 3,00 por W | Preço de varejo, novembro de 2026 |
| Bateria LiFePO4 12 V | R$ 22 por Ah | Preço de varejo, novembro de 2026 |
| Controlador MPPT + instalação | R$ 250 + R$ 250 | Preço de varejo |
| Vida útil da bateria | 8 anos | Cerca de 3.000 ciclos, um por dia |
| Trajeto para comparar ônibus e carro | 20 km/dia, 22 dias/mês | Ida e volta ao trabalho |

## Consumo e controle inteligente

O ventilador só liga quando **está calor (30 °C ou mais), tem gente no ponto e a bateria tem carga**. Com os dados reais de 2025:

| Item | Horas por ano | Energia por ano |
| ---- | ------------: | --------------: |
| Eletrônica (24 h) | 8.760 h | 8,8 kWh |
| Ventiladores com controle inteligente | 332 h | 13,3 kWh |
| Ventiladores no timer (10h às 18h) | 2.920 h | 116,8 kWh |

O controle inteligente reduz a energia dos ventiladores em **88,6 %** (de 116,8 para 13,3 kWh por ano). O abrigo inteiro passa a gastar **22,1 kWh por ano**, cerca de 1,8 kWh por mês.

Horas quentes por mês em 2025: janeiro 36, fevereiro 89, março 42, abril 3, maio a julho 0, agosto 11, setembro 25, outubro 28, novembro 15, dezembro 83.

## Dimensionamento do sistema solar

Para cada mês, o cálculo usa o **pior dia** (o dia com mais horas quentes) e a irradiação daquele mês:

```
energia do pior dia (Wh) = 40 W × horas quentes do pior dia + 1 W × 24 h
painel necessário (W)    = energia do pior dia ÷ (irradiação do mês × 0,75)
bateria (Wh)             = maior energia diária × 1 dia ÷ 0,8
```

| Mês | Horas quentes no pior dia | Energia do pior dia | Irradiação (24°) | Painel necessário |
| --: | ------------------------: | ------------------: | ---------------: | ----------------: |
| 1   | 7  | 304 Wh | 4,72 | 86 W  |
| 2   | 9  | 384 Wh | 5,22 | 98 W  |
| 3   | 7  | 304 Wh | 4,83 | 84 W  |
| 10  | 10 | 424 Wh | 4,64 | **122 W** |
| 12  | 10 | 424 Wh | 5,05 | 112 W |
| 5 a 7 | 0 | 24 Wh | 4,12 a 4,24 | 8 W |

O mês crítico é **outubro**: dia de 10 horas quentes com menos sol que dezembro. O painel comercial que atende é o de **150 W**. A bateria precisa de 530 Wh, então a escolhida é a **LiFePO4 de 12 V e 50 Ah (600 Wh)**. Esse painel gera cerca de **191 kWh por ano**, bem mais que os 22 kWh consumidos: a sobra garante folga em dias nublados.

## Alternativas comparadas

Mesma necessidade (ventiladores com controle + eletrônica) e mesmo período (10 anos, sem reajuste de preços):

| Critério | Rede elétrica (ponto sem energia) | Rede elétrica (ponto que já tem energia) | Solar + bateria |
| -------- | --------------------------------- | ---------------------------------------- | --------------- |
| **Custo inicial** | R$ 2.580 (ligação nova + fonte) | R$ 80 (fonte) | R$ 2.050 (painel, bateria, controlador, instalação) |
| **Custo de operação** | R$ 30,76/mês: a Enel cobra no mínimo 30 kWh, mesmo o ponto gastando 1,8 kWh | só o consumo: cerca de R$ 23/ano | sem conta; troca da bateria no 8º ano (R$ 1.100) |
| **Total em 10 anos** | **R$ 6.271** | **R$ 306** | **R$ 3.150** |
| **Viabilidade** | Precisa de obra, padrão de entrada e pedido à distribuidora | Imediata | Instala sem obra; funciona em ponto isolado e **quando falta luz** |
| **Impacto ambiental** | 0,85 kg CO2/ano (rede brasileira é pouco poluente) | 0,85 kg CO2/ano | 0 na operação; a fabricação do painel e da bateria tem impacto e a bateria precisa de descarte correto |

O ponto que mais pesa contra a rede num ponto sem energia é o **consumo mínimo cobrado**: o abrigo gasta cerca de 1,8 kWh por mês, mas a conta cobra 30 kWh. Ou seja, paga-se cerca de 16 vezes mais energia do que se usa.

O CO2 do abrigo é pequeno nos três casos, porque a eletricidade brasileira vem em grande parte de fontes renováveis. O ganho ambiental grande do Ponto Vivo está em outro lugar: **deixar o ônibus mais atraente**. Uma pessoa que troca o carro pelo ônibus em 440 km por mês evita cerca de **17,6 kg de CO2 por mês**, mais do que o abrigo emitiria em 20 anos ligado na rede.

## Recomendações

1. **Ponto sem energia:** usar **solar com bateria**. Custa cerca de metade da ligação nova em 10 anos, não depende de obra e continua funcionando em queda de energia.
2. **Ponto que já tem energia** (abrigo com iluminação ou painel de propaganda): usar a **rede**, que sai mais barata.
3. **Sempre:** ligar o ventilador **só com calor, gente esperando e bateria com carga**. Isso corta 88,6 % da energia dos ventiladores e permite um painel menor.
4. **Para o passageiro:** o assistente explica como o Ponto Fresco funciona e quanto CO2 se evita ao trocar o carro pelo ônibus.

## Limitações

- **As estimativas não são resultados garantidos.** Preços de equipamentos, custo da ligação nova e PIS/COFINS são estimativas e precisam de orçamento real.
- A temperatura é da estação do INMET no Mirante de Santana, medida na sombra. Num abrigo com telhado de metal ao sol, a temperatura pode ser maior, e o ventilador ligaria mais horas.
- Foi usado um único ano (2025). Anos mais quentes aumentariam o consumo.
- A irradiação é uma média histórica. Vários dias nublados seguidos no verão podem esgotar a bateria; nesse caso o ventilador para e a eletrônica continua.
- A tarifa considera a classe B3 convencional da Enel SP, sem bandeiras tarifárias e sem reajustes futuros.
- Os valores de emissão do Metrô de SP são médias publicadas e variam com o veículo e a lotação.
- O sistema não foi construído fisicamente; a análise é de projeto.

## Integração ao assistente

A análise entra no Citizen Assist AI de duas formas:

1. **Opção 5 do menu, "Energia do Ponto Vivo"**: lê [`resultados.json`](resultados.json), gerado por `calculos.py`, e mostra quando o ventilador liga, a comparação de custos em 10 anos, a recomendação e as limitações. Se os cálculos mudarem, a tela muda junto.
2. **Três orientações novas** na base de conhecimento, na categoria **Energia e Sustentabilidade**:

| ID | Orientação | Exemplo de pergunta |
| -: | ---------- | ------------------- |
| 13 | Ponto Fresco: o ventilador movido a energia solar | "o ventilador funciona com energia solar?" |
| 14 | Por que o ventilador liga só com calor e gente esperando | "por que o ventilador desligou?" |
| 15 | Ônibus ou carro: quanto CO2 você deixa de emitir | "ir de ônibus polui menos que carro?" |

Toda resposta mostra a fonte, a data e o aviso de que os valores são estimativas de um projeto acadêmico.

## Como executar e testar

```bash
# Na raiz do repositório

# 1. Refaz os cálculos e gera energia/resultados.json
python energia/calculos.py

# 2. Abre o assistente e escolha a opção 5 (ou pergunte sobre o ventilador)
python main.py
```

Para testar outra premissa (por exemplo, ventilador de 25 W ou ligar com 28 °C), mude o valor no topo de `calculos.py` e rode de novo.

## Testes com usuários

Ver [`testes_usuarios.md`](testes_usuarios.md). Sem nomes nem dados pessoais dos participantes.

## Referências

Consultadas em 06/11/2026.

- INMET — Dados históricos anuais (estação A701, 2025): https://portal.inmet.gov.br/dadoshistoricos
- CRESESB/CEPEL — SunData, irradiação solar para São Paulo: https://cresesb.cepel.br/index.php?section=sundata
- ANEEL — Dados abertos, tarifas das distribuidoras (REH 3.596/2026, Enel SP): https://dadosabertos.aneel.gov.br/dataset/tarifas-distribuidoras-energia-eletrica
- Secretaria da Fazenda de SP — Resposta à Consulta 33164/2026 (ICMS de 18 % para consumo não residencial): https://legislacao.fazenda.sp.gov.br/Paginas/RC33164_2026.aspx
- O Setor Elétrico, com dados do MCTI — Fator médio de emissão do SIN em 2023: https://www.osetoreletrico.com.br/?p=159478
- Metrô de São Paulo — Emissões por passageiro-km na RMSP: https://www.metro.sp.gov.br/2020/09/22/funcionamento-do-metro-evita-a-emissao-de-842-mil-toneladas-de-co2-em-apenas-um-ano/

## Vídeo

_Link do YouTube (não listado, até 3 minutos) a adicionar._
