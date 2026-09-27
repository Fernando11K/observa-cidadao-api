from typing import Annotated

import strawberry

from observa_cidadao_api.graphql.contexto import Info
from observa_cidadao_api.graphql.permissoes import EstaAutenticado
from observa_cidadao_api.graphql.types.acompanhamento import Acompanhamento
from observa_cidadao_api.graphql.types.senador import Senador, SenadorResumo
from observa_cidadao_api.graphql.types.usuario import Usuario
from observa_cidadao_api.senado.senadores import (
    buscar_detalhe_senador,
    listar_senadores_em_exercicio,
)
from observa_cidadao_api.services.acompanhamentos import listar_acompanhamentos


@strawberry.type
class Query:

    @strawberry.field(
        description="Lista os senadores em exercício, em ordem alfabética, com filtros opcionais"
    )
    async def senadores(
        self,
        uf: Annotated[
            str | None, strawberry.argument(description="Filtra pela UF, por exemplo DF")
        ] = None,
        partido: Annotated[
            str | None,
            strawberry.argument(description="Filtra pela sigla do partido, por exemplo PT"),
        ] = None,
    ) -> list[SenadorResumo]:
        senadores = [
            senador
            for dados in await listar_senadores_em_exercicio()
            if (senador := SenadorResumo.da_api(dados))
        ]
        if uf:
            senadores = [s for s in senadores if (s.uf or "").upper() == uf.strip().upper()]
        if partido:
            senadores = [
                s for s in senadores if (s.partido or "").upper() == partido.strip().upper()
            ]
        return sorted(senadores, key=lambda s: (s.nome_parlamentar or "").casefold())

    @strawberry.field(
        description="Busca um senador pelo código do Senado Federal; retorna nulo se o código não existir"
    )
    async def senador(
        self,
        codigo: Annotated[
            int, strawberry.argument(description="Código do parlamentar, por exemplo 6335")
        ],
    ) -> Senador | None:
        dados = await buscar_detalhe_senador(codigo)
        return Senador.da_api(codigo, dados) if dados else None

    @strawberry.field(
        description="Dados do usuário autenticado", permission_classes=[EstaAutenticado]
    )
    async def eu(self, info: Info) -> Usuario:
        return Usuario.do_modelo(info.context.usuario)

    @strawberry.field(
        description="Senadores acompanhados pelo usuário autenticado, do mais recente ao mais antigo",
        permission_classes=[EstaAutenticado],
    )
    async def acompanhamentos(self, info: Info) -> list[Acompanhamento]:
        modelos = await listar_acompanhamentos(info.context.sessao, info.context.usuario.id)
        return [Acompanhamento.do_modelo(modelo) for modelo in modelos]
