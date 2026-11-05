"""Classe Orientacao: representa UMA orientação da base de conhecimento
(um registro do arquivo data/base_conhecimento.json)."""

AVISO = "Aviso: este assistente NÃO é um canal oficial da Prefeitura ou da SPTrans."


class Orientacao:
    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave  # lista de textos
        self.resposta = resposta
        self.documentos = documentos          # lista de textos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    def exibir(self):
        """Mostra a orientação na tela, com fonte, data e o aviso de canal não oficial."""
        print()
        print(f">> {self.titulo}  [{self.categoria}]")
        print(self.resposta)
        print("Documentos necessários:")
        for documento in self.documentos:
            print(f"  - {documento}")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print(AVISO)
