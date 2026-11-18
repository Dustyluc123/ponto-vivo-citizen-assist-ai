def obter_resposta(pergunta):
  while True:
    resposta = (
        input(pergunta + " (Digite 'sim' ou 'nao'): ").strip().lower()
    )
    if resposta in ["sim", "s", "1"]:
      return True
    elif resposta in ["nao", "não", "n", "0"]:
      return False
    else:
      print(
          "Resposta invalida ('talvez' ou termo nao reconhecido). Por favor,"
          " digite apenas 'sim' ou 'nao'."
      )


def main():
  print("=== SISTEMA CONSULTOR DE BENEFICIO SPTRANS ===")
  print(
      "AVISO: Este assistente e uma ferramenta de orientacao academica e nao"
      " constitui um canal oficial da SPTrans.\n"
  )

  # Coleta das 4 perguntas de entrada
  p1 = obter_resposta("1. O estudante possui vinculo ativo de matricula?")
  p2 = obter_resposta("2. O estudante esta cadastrado no CadUnico (baixa renda)?")
  p3 = obter_resposta(
      "3. A escola ja enviou o lote de matricula para a SPTrans?"
  )
  p4 = obter_resposta(
      "4. A validacao cadastral foi concluida no portal da SPTrans?"
  )

  # Calculo das saídas binarias com base nas expressoes simplificadas
  s1 = p1 and (not p2) and p3 and p4
  s2 = p1 and p2 and p3 and p4
  s3 = (not p1) or (not p3) or (not p4)

  print("\n--- RESULTADO DA ANALISE ---")
  if s2:
    print(
        "Orientacao: Gratuidade Total concedida! Seu perfil atende a todos os"
        " requisitos de baixa renda e matricula regularizada."
    )
  elif s1:
    print(
        "Orientacao: Meia Tarifa concedida! Matricula e dados validados, sem"
        " registro no CadUnico."
    )
  elif s3:
    print(
        "Orientacao: Pendencia / Bloqueio. Ha divergencia ou ausencia de"
        " informacoes. Procure a secretaria da escola ou verifique o portal da"
        " SPTrans."
    )


if __name__ == "__main__":
  main()