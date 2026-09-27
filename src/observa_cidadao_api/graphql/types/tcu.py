from datetime import date, datetime, timedelta, timezone

import strawberry

FUSO_BRASILIA = timezone(timedelta(hours=-3))


@strawberry.type(description="Solicitação do Congresso Nacional ao Tribunal de Contas da União")
class SolicitacaoTcu:
    tipo: str | None = strawberry.field(description="Tipo da proposição, por exemplo REQ")
    numero: int | None = strawberry.field(description="Número da proposição")
    data_aprovacao: date | None = strawberry.field(
        description="Data de aprovação da solicitação no Congresso"
    )
    assunto: str | None = strawberry.field(description="Assunto da solicitação")
    autor: str | None = strawberry.field(description="Autor da solicitação")
    processo_tcu: str | None = strawberry.field(
        description="Número do processo que trata a solicitação no TCU"
    )
    link_proposicao: str | None = strawberry.field(
        description="Página da proposição no Senado ou na Câmara"
    )

    @classmethod
    def da_api(cls, dados: dict) -> "SolicitacaoTcu":
        return cls(
            tipo=dados.get("tipo"),
            numero=dados.get("numero"),
            data_aprovacao=_data_em_brasilia(dados.get("data_aprovacao")),
            assunto=_texto(dados.get("assunto")),
            autor=_texto(dados.get("autor")),
            processo_tcu=dados.get("processo_scn"),
            link_proposicao=dados.get("link_proposicao"),
        )


@strawberry.type(
    description="Registro na lista de responsáveis com contas julgadas irregulares pelo TCU"
)
class ContaIrregularTcu:
    nome: str = strawberry.field(description="Nome do responsável no TCU")
    uf: str | None = strawberry.field(
        description="UF do último endereço do responsável na Receita Federal"
    )
    municipio: str | None = strawberry.field(
        description="Município do último endereço do responsável na Receita Federal"
    )
    processo: str | None = strawberry.field(description="Número do processo no TCU")
    acordao: str | None = strawberry.field(description="Número do acórdão, quando informado")
    data_transito_em_julgado: date | None = strawberry.field(
        description="Data do trânsito em julgado da decisão"
    )
    link_deliberacoes: str | None = strawberry.field(
        description="Endereço das deliberações do processo"
    )
    link_acompanhamento: str | None = strawberry.field(
        description="Endereço de acompanhamento do processo"
    )

    @classmethod
    def da_api(cls, dados: dict) -> "ContaIrregularTcu":
        return cls(
            nome=dados["nome"],
            uf=dados.get("uf"),
            municipio=dados.get("municipio"),
            processo=dados.get("numeroProcessoFormatado"),
            acordao=dados.get("numeroAcordaoFormatado"),
            data_transito_em_julgado=_data_brasileira(dados.get("dataTransitoEmJulgado")),
            link_deliberacoes=dados.get("linkDeliberacoesProcesso"),
            link_acompanhamento=dados.get("linkAcompanhamentoProcesso"),
        )


def _data_em_brasilia(valor: str | None) -> date | None:
    if not valor:
        return None
    return datetime.fromisoformat(valor).astimezone(FUSO_BRASILIA).date()


def _data_brasileira(valor: str | None) -> date | None:
    return datetime.strptime(valor, "%d/%m/%Y").date() if valor else None


def _texto(valor: str | None) -> str | None:
    return valor.strip() if valor else None
