"""Cálculos de energia do abrigo Ponto Vivo.

Pergunta que a análise responde:
  "Qual a melhor forma de alimentar o ventilador e a eletrônica de um ponto de
   ônibus em São Paulo: ligar na rede elétrica ou usar energia solar com bateria?
   E vale a pena ligar o ventilador só quando precisa?"

Execute a partir da raiz do repositório:
  python energia/calculos.py

Gera energia/resultados.json, que o assistente usa na opção "Energia do Ponto Vivo".
Só usa a biblioteca padrão do Python.
"""

import csv
import json
import math
import os
from collections import defaultdict
from datetime import datetime

PASTA = os.path.dirname(os.path.abspath(__file__))
ARQ_TEMPERATURA = os.path.join(PASTA, "dados", "inmet_a701_sao_paulo_2025.csv")
ARQ_IRRADIACAO = os.path.join(PASTA, "dados", "irradiacao_sao_paulo_cresesb.csv")
ARQ_RESULTADOS = os.path.join(PASTA, "resultados.json")

# ---------------------------------------------------------------------------
# PREMISSAS
# "real"     = dado oficial com fonte (ver README)
# "estimado" = valor escolhido pelo autor, com justificativa no README
# ---------------------------------------------------------------------------

# Equipamentos do abrigo
POTENCIA_VENTILADOR_W = 20        # estimado: ventilador 12 V DC (faixa comum de 10 a 25 W)
QTD_VENTILADORES = 2              # estimado: um em cada lado do abrigo
POTENCIA_ELETRONICA_W = 1.0       # estimado: ESP32 + sensor + tela + LEDs, com folga (ligados 24 h)

# Regra do ventilador (a mesma do módulo de Computer Science)
TEMPERATURA_LIGA_C = 30           # estimado: liga com 30 °C ou mais
HORA_INICIO, HORA_FIM = 5, 23     # estimado: horário com ônibus e passageiros no ponto

# Cenário sem controle: ventilador num timer, ligado todo dia das 10h às 18h
HORAS_TIMER_POR_DIA = 8           # estimado

# Rede elétrica (Enel SP, subgrupo B3, modalidade convencional)
TARIFA_TUSD_R_MWH = 472.42        # real: ANEEL, REH 3.596/2026, vigência 04/07/2026 a 03/07/2027
TARIFA_TE_R_MWH = 316.96          # real: mesma resolução
ICMS = 0.18                       # real: alíquota geral de SP para consumo não residencial
PIS_COFINS = 0.05                 # estimado: varia todo mês na conta
CONSUMO_MINIMO_KWH_MES = 30       # real: custo de disponibilidade de ligação monofásica (ANEEL)
CUSTO_LIGACAO_NOVA_R = 2500       # estimado: padrão de entrada, cabos e obra num ponto sem energia
CUSTO_FONTE_12V_R = 80            # estimado: fonte para ligar os aparelhos 12 V na tomada

# Emissões
FATOR_EMISSAO_REDE_KG_KWH = 0.0385  # real: MCTI, fator médio do SIN em 2023 (38,5 kg CO2/MWh)
CO2_ONIBUS_G_PKM = 80             # real: Metrô SP, média de ônibus na RMSP (g CO2 por passageiro-km)
CO2_CARRO_G_PKM = 120             # real: Metrô SP, média de automóvel a gasolina na RMSP

# Sistema solar
PERFORMANCE_RATIO = 0.75          # estimado: perdas de calor, sujeira, cabos, controlador e bateria
PROFUNDIDADE_DESCARGA = 0.8       # estimado: uso seguro de bateria de lítio (LiFePO4)
DIAS_AUTONOMIA = 1                # estimado: aguentar 1 dia quente inteiro sem recarga
TENSAO_SISTEMA_V = 12
PAINEIS_COMERCIAIS_W = [50, 100, 150, 200, 250]
BATERIAS_COMERCIAIS_AH = [20, 30, 50, 60, 100]

# Preços (estimados, novembro de 2026, varejo brasileiro; conferir antes de usar)
PRECO_PAINEL_R_POR_W = 3.0        # estimado
PRECO_BATERIA_R_POR_AH = 22.0     # estimado: LiFePO4 12 V
PRECO_CONTROLADOR_R = 250         # estimado: controlador de carga MPPT 12 V
PRECO_INSTALACAO_SOLAR_R = 250    # estimado: suporte, cabos, fusíveis
VIDA_BATERIA_ANOS = 8             # estimado: cerca de 3.000 ciclos de 1 ciclo por dia
HORIZONTE_ANOS = 10

# Exemplo de deslocamento para a comparação ônibus × carro
KM_POR_DIA = 20                   # estimado: ida e volta ao trabalho
DIAS_UTEIS_MES = 22


# ---------------------------------------------------------------------------
# LEITURA DOS DADOS REAIS
# ---------------------------------------------------------------------------

def ler_horas_quentes():
    """Conta, para cada dia de 2025, quantas horas tiveram 30 °C ou mais
    no horário de funcionamento (estação INMET A701, São Paulo - Mirante)."""
    horas_por_dia = defaultdict(int)
    with open(ARQ_TEMPERATURA, encoding="utf-8") as arquivo:
        for linha in csv.DictReader(arquivo):
            if not linha["temperatura_c"]:
                continue  # hora sem medição
            momento = datetime.strptime(linha["data_hora_local"], "%Y-%m-%d %H:%M")
            if momento.year != 2025:
                continue
            quente = float(linha["temperatura_c"]) >= TEMPERATURA_LIGA_C
            if quente and HORA_INICIO <= momento.hour <= HORA_FIM:
                horas_por_dia[momento.date()] += 1
    return horas_por_dia


def ler_irradiacao():
    """Irradiação solar média diária (kWh/m².dia) por mês, painel inclinado a 24°."""
    irradiacao = {}
    with open(ARQ_IRRADIACAO, encoding="utf-8") as arquivo:
        for linha in csv.DictReader(arquivo):
            irradiacao[int(linha["mes"])] = float(linha["inclinado_24graus"])
    return irradiacao


# ---------------------------------------------------------------------------
# CÁLCULOS
# ---------------------------------------------------------------------------

def tarifa_r_kwh(com_impostos):
    """Tarifa em R$/kWh. Sem impostos é o valor da ANEEL; com impostos é estimado."""
    sem_impostos = (TARIFA_TUSD_R_MWH + TARIFA_TE_R_MWH) / 1000
    if not com_impostos:
        return sem_impostos
    return sem_impostos / (1 - ICMS - PIS_COFINS)


def proximo_comercial(valor, opcoes):
    """Menor tamanho comercial que atende o valor pedido."""
    for opcao in opcoes:
        if opcao >= valor:
            return opcao
    return opcoes[-1]


def calcular():
    horas_por_dia = ler_horas_quentes()
    irradiacao = ler_irradiacao()

    potencia_ventiladores_w = POTENCIA_VENTILADOR_W * QTD_VENTILADORES
    horas_quentes_ano = sum(horas_por_dia.values())
    dias_quentes = len(horas_por_dia)

    # Consumo anual (kWh)
    eletronica_kwh = POTENCIA_ELETRONICA_W * 24 * 365 / 1000
    vent_inteligente_kwh = potencia_ventiladores_w * horas_quentes_ano / 1000
    vent_timer_kwh = potencia_ventiladores_w * HORAS_TIMER_POR_DIA * 365 / 1000
    total_inteligente_kwh = eletronica_kwh + vent_inteligente_kwh
    total_timer_kwh = eletronica_kwh + vent_timer_kwh
    economia_controle = 1 - vent_inteligente_kwh / vent_timer_kwh

    # Dimensionamento solar mês a mês (pior dia de cada mês)
    pior_dia_por_mes = defaultdict(int)
    for dia, horas in horas_por_dia.items():
        pior_dia_por_mes[dia.month] = max(pior_dia_por_mes[dia.month], horas)

    meses = []
    for mes in range(1, 13):
        energia_dia_wh = potencia_ventiladores_w * pior_dia_por_mes[mes] + POTENCIA_ELETRONICA_W * 24
        painel_w = energia_dia_wh / (irradiacao[mes] * PERFORMANCE_RATIO)
        meses.append({
            "mes": mes,
            "horas_quentes_pior_dia": pior_dia_por_mes[mes],
            "energia_pior_dia_wh": round(energia_dia_wh, 1),
            "irradiacao_kwh_m2_dia": irradiacao[mes],
            "painel_necessario_w": round(painel_w, 1),
        })

    mes_critico = max(meses, key=lambda m: m["painel_necessario_w"])
    painel_w = proximo_comercial(mes_critico["painel_necessario_w"], PAINEIS_COMERCIAIS_W)
    energia_max_dia_wh = max(m["energia_pior_dia_wh"] for m in meses)
    bateria_wh = energia_max_dia_wh * DIAS_AUTONOMIA / PROFUNDIDADE_DESCARGA
    bateria_ah = proximo_comercial(bateria_wh / TENSAO_SISTEMA_V, BATERIAS_COMERCIAIS_AH)
    geracao_anual_kwh = sum(painel_w * irradiacao[m] * PERFORMANCE_RATIO * 30.4 for m in range(1, 13)) / 1000

    # Custos em 10 anos
    tarifa = tarifa_r_kwh(com_impostos=True)
    conta_minima_ano = CONSUMO_MINIMO_KWH_MES * 12 * tarifa
    custo_rede_sem_energia = CUSTO_LIGACAO_NOVA_R + CUSTO_FONTE_12V_R + conta_minima_ano * HORIZONTE_ANOS
    custo_rede_com_energia = CUSTO_FONTE_12V_R + total_inteligente_kwh * tarifa * HORIZONTE_ANOS

    custo_bateria = bateria_ah * PRECO_BATERIA_R_POR_AH
    trocas_bateria = math.ceil(HORIZONTE_ANOS / VIDA_BATERIA_ANOS) - 1
    custo_solar = (painel_w * PRECO_PAINEL_R_POR_W + custo_bateria + PRECO_CONTROLADOR_R
                   + PRECO_INSTALACAO_SOLAR_R + custo_bateria * trocas_bateria)

    # Emissões
    co2_rede_inteligente = total_inteligente_kwh * FATOR_EMISSAO_REDE_KG_KWH
    co2_rede_timer = total_timer_kwh * FATOR_EMISSAO_REDE_KG_KWH
    km_mes = KM_POR_DIA * DIAS_UTEIS_MES
    co2_evitado_onibus_mes = km_mes * (CO2_CARRO_G_PKM - CO2_ONIBUS_G_PKM) / 1000

    return {
        "clima": {
            "horas_quentes_ano": horas_quentes_ano,
            "dias_quentes_ano": dias_quentes,
            "temperatura_liga_c": TEMPERATURA_LIGA_C,
        },
        "consumo_kwh_ano": {
            "eletronica": round(eletronica_kwh, 1),
            "ventilador_inteligente": round(vent_inteligente_kwh, 1),
            "ventilador_timer": round(vent_timer_kwh, 1),
            "total_inteligente": round(total_inteligente_kwh, 1),
            "total_timer": round(total_timer_kwh, 1),
            "economia_controle_pct": round(100 * economia_controle, 1),
        },
        "solar": {
            "mes_critico": mes_critico["mes"],
            "painel_w": painel_w,
            "bateria_ah": bateria_ah,
            "bateria_wh": bateria_ah * TENSAO_SISTEMA_V,
            "geracao_anual_kwh": round(geracao_anual_kwh, 1),
            "meses": meses,
        },
        "custos_10_anos_r": {
            "tarifa_sem_impostos_r_kwh": round(tarifa_r_kwh(False), 4),
            "tarifa_com_impostos_r_kwh": round(tarifa, 4),
            "conta_minima_mes": round(conta_minima_ano / 12, 2),
            "rede_ponto_sem_energia": round(custo_rede_sem_energia),
            "rede_ponto_com_energia": round(custo_rede_com_energia),
            "solar_com_bateria": round(custo_solar),
            "trocas_bateria": trocas_bateria,
        },
        "co2_kg_ano": {
            "rede_inteligente": round(co2_rede_inteligente, 2),
            "rede_timer": round(co2_rede_timer, 2),
            "solar_operacao": 0,
        },
        "onibus_x_carro": {
            "km_mes": km_mes,
            "co2_evitado_kg_mes": round(co2_evitado_onibus_mes, 1),
            "co2_evitado_kg_ano": round(co2_evitado_onibus_mes * 12, 1),
        },
    }


# ---------------------------------------------------------------------------
# SAÍDA
# ---------------------------------------------------------------------------

def mostrar(r):
    c, s, k, e = r["consumo_kwh_ano"], r["solar"], r["custos_10_anos_r"], r["co2_kg_ano"]
    print("PONTO VIVO - ANÁLISE DE ENERGIA DO ABRIGO\n")
    print(f"Horas com {r['clima']['temperatura_liga_c']} °C ou mais em 2025 (5h-23h): "
          f"{r['clima']['horas_quentes_ano']} h em {r['clima']['dias_quentes_ano']} dias\n")

    print("Consumo por ano")
    print(f"  Eletrônica (24 h):                  {c['eletronica']:>6} kWh")
    print(f"  Ventiladores com controle:          {c['ventilador_inteligente']:>6} kWh")
    print(f"  Ventiladores no timer (10h-18h):    {c['ventilador_timer']:>6} kWh")
    print(f"  Economia do controle inteligente:   {c['economia_controle_pct']:>6} %\n")

    print("Sistema solar dimensionado")
    print(f"  Mês crítico: {s['mes_critico']}  |  Painel: {s['painel_w']} W  |  "
          f"Bateria: {s['bateria_ah']} Ah ({s['bateria_wh']} Wh)  |  Geração: {s['geracao_anual_kwh']} kWh/ano\n")

    print(f"Custo em {HORIZONTE_ANOS} anos (R$)")
    print(f"  Tarifa Enel SP B3: R$ {k['tarifa_sem_impostos_r_kwh']}/kWh sem impostos, "
          f"R$ {k['tarifa_com_impostos_r_kwh']}/kWh com impostos (estimado)")
    print(f"  Rede, ponto SEM energia (ligação nova + conta mínima): R$ {k['rede_ponto_sem_energia']:>6}")
    print(f"  Rede, ponto que JÁ tem energia (só o consumo):         R$ {k['rede_ponto_com_energia']:>6}")
    print(f"  Solar com bateria ({k['trocas_bateria']} troca de bateria):              R$ {k['solar_com_bateria']:>6}\n")

    print("Emissões por ano")
    print(f"  Rede com controle: {e['rede_inteligente']} kg CO2  |  Rede no timer: {e['rede_timer']} kg CO2  |  Solar: 0 na operação")
    o = r["onibus_x_carro"]
    print(f"  Trocar o carro pelo ônibus ({o['km_mes']} km/mês) evita {o['co2_evitado_kg_mes']} kg CO2 por mês")


if __name__ == "__main__":
    resultados = calcular()
    mostrar(resultados)
    with open(ARQ_RESULTADOS, "w", encoding="utf-8") as arquivo:
        json.dump(resultados, arquivo, ensure_ascii=False, indent=2)
    print(f"\nResultados salvos em {ARQ_RESULTADOS}")
