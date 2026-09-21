import strawberry
from datetime import date



@strawberry.type
class Legislatura:
    numero: int
    data_inicio: date
    data_fim: date | None

@strawberry.type
class Exercicio:
    data_inicio: date
    data_fim: date
    causa_afastamento: str | None


@strawberry.type
class Mandato:
    id: int
    uf: str
    data_nascimento: str
    legislaturas: list[Legislatura]
    exercicios: list[Exercicio]
    email: str

#@strawberry.type
#class Senador:
#    id: int
#    nome: str
#    nome_parlamentar: str
#    data_nascimento: date
#    partidoAtual: str
#    email: str
#    idade: int
#    uf: str
#    url_foto: str
#    mandatos: list[Mandato]


@strawberry.type
class Senador:
    id: int | None = None
    nome: str | None = None
    nome_parlamentar: str | None = None
    data_nascimento: date | None = None
    partidoAtual: str | None = None
    email: str | None = None
    idade: int | None = None
    uf: str | None = None
    url_foto: str | None = None
    mandatos: list[Mandato] | None = None