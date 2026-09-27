import strawberry
from graphql import GraphQLError
from strawberry.exceptions import StrawberryGraphQLError
from strawberry.fastapi import GraphQLRouter
from strawberry.types import ExecutionContext

from observa_cidadao_api.graphql.contexto import obter_contexto
from observa_cidadao_api.graphql.mutation import Mutation
from observa_cidadao_api.graphql.query import Query
from observa_cidadao_api.services.erros import ErroDeNegocio

ERROS_ESPERADOS = (ErroDeNegocio, StrawberryGraphQLError)


class Schema(strawberry.Schema):
    def process_errors(
        self, errors: list[GraphQLError], execution_context: ExecutionContext | None = None
    ) -> None:
        # Erros de negócio e de permissão são respostas esperadas; só os inesperados vão para o log.
        inesperados = [
            e for e in errors if not isinstance(e.original_error, ERROS_ESPERADOS)
        ]
        super().process_errors(inesperados, execution_context)


schema = Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema, context_getter=obter_contexto)
