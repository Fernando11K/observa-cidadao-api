from datetime import date

import strawberry

from observa_cidadao_api.graphql.types.mandato import Mandato
from observa_cidadao_api.graphql.types.tcu import ContaIrregularTcu, SolicitacaoTcu
from observa_cidadao_api.senado.cliente import data_iso, inteiro
from observa_cidadao_api.senado.senadores import buscar_mandatos_senador
from observa_cidadao_api.tcu.contas_irregulares import buscar_contas_irregulares
from observa_cidadao_api.tcu.solicitacoes import buscar_solicitacoes


@strawberry.type(description="Dados resumidos de um senador em exercício")
class SenadorResumo:
    codigo: int = strawberry.field(description="Código do parlamentar no Senado Federal")
    nome_parlamentar: str | None = strawberry.field(description="Nome parlamentar")
    nome: str | None = strawberry.field(description="Nome completo do parlamentar")
    partido: str | None = strawberry.field(description="Sigla do partido atual")
    uf: str | None = strawberry.field(description="UF do parlamentar")
    sexo: str | None = strawberry.field(description="Sexo do parlamentar: Masculino ou Feminino")
    url_foto: str | None = strawberry.field(description="URL da foto oficial")
    participacao: str | None = strawberry.field(
        description="Participação no mandato: Titular, 1º Suplente ou 2º Suplente"
    )
    fim_mandato: date | None = strawberry.field(description="Data de término do mandato atual")
    bloco: str | None = strawberry.field(description="Nome do bloco parlamentar")
    membro_mesa: bool = strawberry.field(description="Se é membro da Mesa Diretora do Senado")
    membro_lideranca: bool = strawberry.field(description="Se ocupa cargo de liderança")

    @classmethod
    def da_api(cls, dados: dict) -> "SenadorResumo | None":
        identificacao = dados.get("IdentificacaoParlamentar", {})
        mandato = dados.get("Mandato", {})
        codigo = inteiro(identificacao.get("CodigoParlamentar"))
        if codigo is None:
            return None
        return cls(
            codigo=codigo,
            nome_parlamentar=identificacao.get("NomeParlamentar"),
            nome=identificacao.get("NomeCompletoParlamentar"),
            partido=identificacao.get("SiglaPartidoParlamentar"),
            uf=identificacao.get("UfParlamentar"),
            sexo=identificacao.get("SexoParlamentar"),
            url_foto=identificacao.get("UrlFotoParlamentar"),
            participacao=mandato.get("DescricaoParticipacao"),
            fim_mandato=data_iso(
                mandato.get("SegundaLegislaturaDoMandato", {}).get("DataFim")
            ),
            bloco=(identificacao.get("Bloco") or {}).get("NomeBloco"),
            membro_mesa=identificacao.get("MembroMesa") == "Sim",
            membro_lideranca=identificacao.get("MembroLideranca") == "Sim",
        )


@strawberry.type(description="Senador, com dados do portal de dados abertos do Senado Federal")
class Senador:
    id: int = strawberry.field(description="Código do parlamentar no Senado Federal")
    nome: str | None = strawberry.field(description="Nome completo do parlamentar")
    nome_parlamentar: str | None = strawberry.field(description="Nome parlamentar")
    data_nascimento: date | None = strawberry.field(description="Data de nascimento")
    partido_atual: str | None = strawberry.field(description="Sigla do partido atual")
    email: str | None = strawberry.field(description="E-mail do parlamentar")
    idade: int | None = strawberry.field(
        description="Idade calculada a partir da data de nascimento"
    )
    uf: str | None = strawberry.field(description="UF do parlamentar")
    url_foto: str | None = strawberry.field(description="URL da foto oficial")

    @strawberry.field(
        description=(
            "Mandatos do parlamentar, na ordem retornada pelo Senado, buscados apenas quando "
            "solicitados. Nulo se o Senado estiver indisponível."
        )
    )
    async def mandatos(self) -> list[Mandato] | None:
        return [Mandato.da_api(m) for m in await buscar_mandatos_senador(self.id)]

    @strawberry.field(
        description=(
            "Solicitações ao TCU aprovadas no Congresso cujo autor tem o mesmo nome parlamentar "
            "do senador. Nulo se o TCU estiver indisponível."
        )
    )
    async def solicitacoes_tcu(self) -> list[SolicitacaoTcu] | None:
        return [SolicitacaoTcu.da_api(s) for s in await buscar_solicitacoes(self.nome_parlamentar)]

    @strawberry.field(
        description=(
            "Possíveis registros na lista de contas julgadas irregulares do TCU, encontrados por "
            "nome completo idêntico. Homônimos são possíveis: a correspondência não usa CPF. "
            "Nulo se o TCU estiver indisponível."
        )
    )
    async def contas_irregulares_tcu(self) -> list[ContaIrregularTcu] | None:
        return [ContaIrregularTcu.da_api(c) for c in await buscar_contas_irregulares(self.nome)]

    @classmethod
    def da_api(cls, codigo: int, dados: dict) -> "Senador":
        identificacao = dados.get("IdentificacaoParlamentar", {})
        data_nascimento = data_iso(
            dados.get("DadosBasicosParlamentar", {}).get("DataNascimento")
        )
        return cls(
            id=codigo,
            nome=identificacao.get("NomeCompletoParlamentar"),
            nome_parlamentar=identificacao.get("NomeParlamentar"),
            data_nascimento=data_nascimento,
            partido_atual=identificacao.get("SiglaPartidoParlamentar"),
            email=identificacao.get("EmailParlamentar"),
            idade=_idade(data_nascimento),
            uf=identificacao.get("UfParlamentar"),
            url_foto=identificacao.get("UrlFotoParlamentar"),
        )


def _idade(nascimento: date | None) -> int | None:
    if nascimento is None:
        return None
    hoje = date.today()
    return hoje.year - nascimento.year - (
        (hoje.month, hoje.day) < (nascimento.month, nascimento.day)
    )
