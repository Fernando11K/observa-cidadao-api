import strawberry
from strawberry.fastapi import GraphQLRouter

from observa_cidadao_api.graphql.type import Senador
from observa_cidadao_api.senado.senadores import buscar_senador


@strawberry.type
class Query:

    @strawberry.field
    async def senador(self, codigo: int) -> Senador | None:
        return await buscar_senador(codigo)


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)
