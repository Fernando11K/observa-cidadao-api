from datetime import date

import strawberry

from observa_cidadao_api.senado.cliente import como_lista, data_iso, inteiro


@strawberry.type(description="Legislatura que compõe um mandato")
class Legislatura:
    numero: int | None = strawberry.field(description="Número da legislatura")
    data_inicio: date | None = strawberry.field(description="Data de início da legislatura")
    data_fim: date | None = strawberry.field(description="Data de término da legislatura")

    @classmethod
    def da_api(cls, dados: dict) -> "Legislatura":
        return cls(
            numero=inteiro(dados.get("NumeroLegislatura")),
            data_inicio=data_iso(dados.get("DataInicio")),
            data_fim=data_iso(dados.get("DataFim")),
        )


@strawberry.type(description="Período de exercício efetivo do mandato")
class Exercicio:
    data_inicio: date | None = strawberry.field(description="Data de início do exercício")
    data_fim: date | None = strawberry.field(
        description="Data de término do exercício; nulo se não informada pelo Senado"
    )
    causa_afastamento: str | None = strawberry.field(
        description="Descrição da causa do afastamento, quando houver"
    )

    @classmethod
    def da_api(cls, dados: dict) -> "Exercicio":
        return cls(
            data_inicio=data_iso(dados.get("DataInicio")),
            data_fim=data_iso(dados.get("DataFim")),
            causa_afastamento=dados.get("DescricaoCausaAfastamento"),
        )


@strawberry.type(description="Filiação partidária do senador durante o mandato")
class Partido:
    sigla: str = strawberry.field(description="Sigla do partido")
    nome: str = strawberry.field(description="Nome do partido")
    data_filiacao: date | None = strawberry.field(description="Data de filiação ao partido")
    data_desfiliacao: date | None = strawberry.field(
        description="Data de desfiliação; nulo se não informada pelo Senado"
    )

    @classmethod
    def da_api(cls, dados: dict) -> "Partido":
        return cls(
            sigla=dados["Sigla"],
            nome=dados["Nome"],
            data_filiacao=data_iso(dados.get("DataFiliacao")),
            data_desfiliacao=data_iso(dados.get("DataDesfiliacao")),
        )


@strawberry.type(description="Mandato do senador")
class Mandato:
    id: int | None = strawberry.field(description="Código do mandato no Senado Federal")
    uf: str | None = strawberry.field(description="UF do mandato")
    participacao: str | None = strawberry.field(
        description="Descrição da participação do parlamentar no mandato"
    )
    legislaturas: list[Legislatura] = strawberry.field(
        description="Primeira e segunda legislaturas do mandato, quando informadas"
    )
    exercicios: list[Exercicio] = strawberry.field(
        description="Períodos de exercício do mandato"
    )
    partidos: list[Partido] = strawberry.field(
        description="Partidos associados ao mandato"
    )

    @classmethod
    def da_api(cls, dados: dict) -> "Mandato":
        return cls(
            id=inteiro(dados.get("CodigoMandato")),
            uf=dados.get("UfParlamentar"),
            participacao=dados.get("DescricaoParticipacao"),
            legislaturas=[
                Legislatura.da_api(legislatura)
                for chave in ("PrimeiraLegislaturaDoMandato", "SegundaLegislaturaDoMandato")
                if (legislatura := dados.get(chave))
            ],
            exercicios=[
                Exercicio.da_api(exercicio)
                for exercicio in como_lista(dados.get("Exercicios", {}).get("Exercicio"))
            ],
            partidos=[
                Partido.da_api(partido)
                for partido in como_lista(dados.get("Partidos", {}).get("Partido"))
            ],
        )
