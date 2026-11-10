"""Classe Registro: um serviço ou orientação útil ao passageiro de ônibus.

Cada registro é o "dado" guardado dentro de um nó da lista encadeada.
As validações ficam aqui para que nenhum registro inválido entre na lista.
"""

import unicodedata

TAMANHO_MAXIMO_TEXTO = 600


def normalizar(texto):
    """Deixa o texto em minúsculas e sem acentos, para comparar e ordenar.
    Ex.: "Ônibus" e "onibus" ficam iguais."""
    sem_acento = unicodedata.normalize("NFD", str(texto))
    sem_acento = "".join(letra for letra in sem_acento if unicodedata.category(letra) != "Mn")
    return " ".join(sem_acento.lower().split())


def validar_id(valor):
    """Aceita só inteiros positivos (1, 2, 3...). Texto como "12" também vale."""
    if isinstance(valor, bool):
        raise ValueError("O ID deve ser um número inteiro positivo.")
    try:
        numero = int(str(valor).strip())
    except ValueError:
        raise ValueError("O ID deve ser um número inteiro positivo.") from None
    if numero <= 0:
        raise ValueError("O ID deve ser um número inteiro positivo.")
    return numero


def validar_texto(valor, nome_campo):
    """Campo de texto obrigatório: não pode ficar vazio nem ser longo demais."""
    texto = " ".join(str(valor or "").split())
    if not texto:
        raise ValueError(f"O campo {nome_campo} não pode ficar vazio.")
    if len(texto) > TAMANHO_MAXIMO_TEXTO:
        raise ValueError(f"O campo {nome_campo} passou de {TAMANHO_MAXIMO_TEXTO} caracteres.")
    return texto


def validar_requisitos(valor):
    """Aceita uma lista ou um texto separado por ponto e vírgula.
    Lista vazia é permitida (serviço que não pede documento)."""
    if isinstance(valor, str):
        valor = valor.split(";")
    return [" ".join(item.split()) for item in valor if str(item).strip()]


class Registro:
    """Um serviço ou orientação ao cidadão."""

    CAMPOS_EDITAVEIS = ("titulo", "categoria", "descricao", "requisitos", "local", "fonte")

    def __init__(self, id, titulo, categoria, descricao, requisitos, local, fonte=""):
        self.id = validar_id(id)
        self.titulo = validar_texto(titulo, "título")
        self.categoria = validar_texto(categoria, "categoria")
        self.descricao = validar_texto(descricao, "descrição")
        self.requisitos = validar_requisitos(requisitos)
        self.local = validar_texto(local, "local")
        self.fonte = " ".join(str(fonte or "").split())

    def atualizar(self, **campos):
        """Troca os campos informados. O ID nunca muda, porque é a chave do registro.
        Valida tudo antes de alterar: se um campo for inválido, nada é alterado."""
        for nome in campos:
            if nome not in self.CAMPOS_EDITAVEIS:
                raise ValueError(f"O campo {nome} não pode ser alterado.")

        novos = {}
        for nome, valor in campos.items():
            if nome == "requisitos":
                novos[nome] = validar_requisitos(valor)
            elif nome == "fonte":
                novos[nome] = " ".join(str(valor or "").split())
            else:
                rotulos = {"titulo": "título", "descricao": "descrição"}
                novos[nome] = validar_texto(valor, rotulos.get(nome, nome))

        for nome, valor in novos.items():
            setattr(self, nome, valor)

    def para_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "categoria": self.categoria,
            "descricao": self.descricao,
            "requisitos": list(self.requisitos),
            "local": self.local,
            "fonte": self.fonte,
        }

    @classmethod
    def de_dict(cls, dados):
        return cls(
            dados["id"], dados["titulo"], dados["categoria"], dados["descricao"],
            dados.get("requisitos", []), dados["local"], dados.get("fonte", ""),
        )

    def __repr__(self):
        return f"Registro(id={self.id}, titulo={self.titulo!r})"
