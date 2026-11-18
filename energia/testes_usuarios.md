# Testes com usuários — Energia

Teste feito em 18/11/2026 com pessoas de fora do projeto, que já tinham participado do teste do assistente (Python). Cada pessoa usou o assistente sozinha e, depois de cada situação, respondeu se entendeu, se achou útil e o que estava confuso ou faltou. Sem nomes ou dados pessoais dos participantes.

| # | Situação testada | Entendeu? (s/n) | Achou útil? (s/n) | Comentário | Ajuste feito |
|---|---|---|---|---|---|
| 1 | Opção 5 do menu ("Energia do Ponto Vivo"): ler a análise de energia do abrigo | s | s | "Acho que ficou muito técnico para alguém de fora." | Acrescentei no início da opção 5 a seção "Em poucas palavras", que resume sem termos técnicos: quando o ventilador liga, quanto o abrigo gasta comparado a uma lâmpada de LED e quanto custa o solar contra a ligação na rede. |
| 2 | Opção 1, pergunta: "o ventilador do ponto funciona com energia solar?" (orientação 13) | s | n | "Acho que o ventilador deveria ligar de 28 °C para cima, e não acima de 30." | Não mudei o limite, mas calculei o efeito com os mesmos dados do INMET: com 28 °C, o ventilador ficaria ligado 692 h por ano (contra 332 h), o solar precisaria de painel de 200 W e bateria de 100 Ah, e o custo em 10 anos subiria para R$ 5.500 (contra R$ 3.150). Ainda sai mais barato que a ligação nova (R$ 6.271). O resultado está no README, e o limite é uma constante em `calculos.py`, fácil de trocar. |
| 3 | Opção 1, pergunta: "é melhor ir de ônibus ou de carro?" (orientação 15) | s | s | "Dois ventiladores não ajudam muito em um ponto cheio." | Registrei como limitação no README: dois ventiladores de 20 W atendem um abrigo comum. Para pontos muito cheios, seria preciso mais ventiladores, e o painel e a bateria teriam de ser recalculados na mesma proporção. |

**Resumo:** as 3 situações foram entendidas, e 2 de 3 foram consideradas úteis. A orientação que não foi considerada útil (situação 2) recebeu uma crítica à regra, e não ao texto: a pessoa preferia o ventilador ligando mais cedo.
