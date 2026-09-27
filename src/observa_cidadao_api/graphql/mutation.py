from typing import Annotated

import strawberry

from observa_cidadao_api.core.seguranca import criar_token
from observa_cidadao_api.graphql.contexto import Info
from observa_cidadao_api.graphql.permissoes import EstaAutenticado
from observa_cidadao_api.graphql.types.acompanhamento import Acompanhamento
from observa_cidadao_api.graphql.types.usuario import Sessao, Usuario
from observa_cidadao_api.services import acompanhamentos, usuarios
from observa_cidadao_api.services.acompanhamentos import TAMANHO_MAXIMO_ANOTACAO
from observa_cidadao_api.services.usuarios import TAMANHO_MINIMO_SENHA


@strawberry.type
class Mutation:

    @strawberry.mutation(description="Cadastra um usuário e já devolve uma sessão autenticada")
    async def cadastrar_usuario(
        self,
        info: Info,
        nome: str,
        email: str,
        senha: Annotated[
            str, strawberry.argument(description=f"Mínimo de {TAMANHO_MINIMO_SENHA} caracteres")
        ],
    ) -> Sessao:
        usuario = await usuarios.cadastrar_usuario(info.context.sessao, nome, email, senha)
        return Sessao(token=criar_token(usuario.id), usuario=Usuario.do_modelo(usuario))

    @strawberry.mutation(description="Autentica com e-mail e senha e devolve uma sessão")
    async def login(self, info: Info, email: str, senha: str) -> Sessao:
        usuario = await usuarios.autenticar(info.context.sessao, email, senha)
        return Sessao(token=criar_token(usuario.id), usuario=Usuario.do_modelo(usuario))

    @strawberry.mutation(
        description="Passa a acompanhar um senador; o código é validado no Senado Federal",
        permission_classes=[EstaAutenticado],
    )
    async def acompanhar_senador(
        self,
        info: Info,
        codigo_senador: Annotated[
            int, strawberry.argument(description="Código do senador, por exemplo 6335")
        ],
        anotacao: Annotated[
            str | None,
            strawberry.argument(description=f"Até {TAMANHO_MAXIMO_ANOTACAO} caracteres"),
        ] = None,
    ) -> Acompanhamento:
        modelo = await acompanhamentos.acompanhar_senador(
            info.context.sessao, info.context.usuario.id, codigo_senador, anotacao
        )
        return Acompanhamento.do_modelo(modelo)

    @strawberry.mutation(
        description="Altera a anotação de um acompanhamento do usuário autenticado",
        permission_classes=[EstaAutenticado],
    )
    async def atualizar_acompanhamento(
        self,
        info: Info,
        id: int,
        anotacao: Annotated[
            str | None,
            strawberry.argument(description="Nova anotação; nulo ou vazio remove a anotação"),
        ],
    ) -> Acompanhamento:
        modelo = await acompanhamentos.atualizar_acompanhamento(
            info.context.sessao, info.context.usuario.id, id, anotacao
        )
        return Acompanhamento.do_modelo(modelo)

    @strawberry.mutation(
        description="Deixa de acompanhar um senador; retorna verdadeiro quando removido",
        permission_classes=[EstaAutenticado],
    )
    async def remover_acompanhamento(self, info: Info, id: int) -> bool:
        await acompanhamentos.remover_acompanhamento(
            info.context.sessao, info.context.usuario.id, id
        )
        return True
