"""Classe Assistente: quem conversa com o passageiro.
Faz o atendimento, guarda o histórico e calcula os indicadores."""


class Assistente:
    def __init__(self, nome, base):
        self.nome = nome
        self.base = base      # objeto BaseConhecimento (composição)
        self.historico = []   # lista de atendimentos (dicionários)

    def perguntar(self):
        """Recebe uma dúvida em texto livre e mostra a melhor orientação + até 2 alternativas."""
        # TODO
        pass

    def navegar(self):
        """Lista categorias e orientações numeradas, com '0 para voltar'."""
        # TODO
        pass

    def registrar(self, origem, pergunta, orientacao, encontrou, ajudou, tentativas, tempo):
        """Salva um atendimento em data/historico.json."""
        # TODO
        pass

    def indicadores(self):
        """% encontrada, % ajudou, tempo médio, tentativas, facilidade, dúvidas sem solução."""
        # TODO
        pass

    def exportar_csv(self):
        """Exporta os atendimentos para data/atendimentos.csv com csv.DictWriter."""
        # TODO
        pass
