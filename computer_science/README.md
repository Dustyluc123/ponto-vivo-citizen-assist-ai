# Computer Science — Módulo de decisão do Bilhete Único Estudantil

Contribuição da disciplina Computer Science ao Ponto Vivo (Citizen Assist AI). O programa faz quatro perguntas de sim ou não e indica se o estudante provavelmente tem meia tarifa, gratuidade ou alguma pendência no cadastro.

| Variável | Pergunta |
| -------- | -------- |
| P1 | O estudante tem matrícula ativa? |
| P2 | O estudante está no CadÚnico (baixa renda)? |
| P3 | A escola já enviou o lote de matrículas para a SPTrans? |
| P4 | O cadastro foi validado no sistema da SPTrans? |

| Saída | Expressão simplificada | Orientação |
| ----- | ---------------------- | ---------- |
| S1 | P1 · P2' · P3 · P4 | Meia tarifa |
| S2 | P1 · P2 · P3 · P4 | Gratuidade |
| S3 | P1' + P3' + P4' | Pendência no cadastro |

A tabela-verdade, a simplificação, os mapas de Karnaugh, os circuitos no logic.ly e os testes com as 16 combinações estão no relatório técnico em PDF entregue no portal.

## Como executar

```bash
python3 computer_science/main.py
```

Responda "sim" ou "nao" a cada pergunta. Qualquer outra resposta, como "talvez", é recusada e a pergunta é repetida.

Este módulo não é canal oficial da SPTrans e não confirma a concessão de nenhum benefício. Ele não pede nem guarda dados pessoais.
