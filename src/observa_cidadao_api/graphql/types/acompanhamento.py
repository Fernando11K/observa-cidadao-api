from datetime import datetime

import strawberry

from observa_cidadao_api.graphql.types.datas import em_utc
from observa_cidadao_api.graphql.types.senador import Senador
from observa_cidadao_api.models import AcompanhamentoModelo
from observa_cidadao_api.senado.senadores import buscar_detalhe_senador


@strawberry.type(description="Senador acompanhado pelo usuário autenticado")
class Acompanhamento:
    id: int = strawberry.field(description="Identificador do acompanhamento")
    codigo_senador: int = strawberry.field(description="Código do senador acompanhado")
    anotacao: str | None = strawberry.field(description="Anotação do usuário sobre o senador")
    criado_em: datetime = strawberry.field(description="Data e hora da criação, em UTC")
    atualizado_em: datetime = strawberry.field(
        description="Data e hora da última alteração, em UTC"
    )

    @strawberry.field(
        description="Dados do senador no Senado Federal, buscados apenas quando solicitados"
    )
    async def senador(self) -> Senador | None:
        dados = await buscar_detalhe_senador(self.codigo_senador)
        return Senador.da_api(self.codigo_senador, dados) if dados else None

    @classmethod
    def do_modelo(cls, modelo: AcompanhamentoModelo) -> "Acompanhamento":
        return cls(
            id=modelo.id,
            codigo_senador=modelo.codigo_senador,
            anotacao=modelo.anotacao,
            criado_em=em_utc(modelo.criado_em),
            atualizado_em=em_utc(modelo.atualizado_em),
        )
