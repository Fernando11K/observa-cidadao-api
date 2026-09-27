from datetime import datetime

import strawberry

from observa_cidadao_api.graphql.types.datas import em_utc
from observa_cidadao_api.models import UsuarioModelo


@strawberry.type(description="Usuário cadastrado na API")
class Usuario:
    id: int = strawberry.field(description="Identificador do usuário")
    nome: str = strawberry.field(description="Nome do usuário")
    email: str = strawberry.field(description="E-mail usado no login")
    criado_em: datetime = strawberry.field(description="Data e hora do cadastro, em UTC")

    @classmethod
    def do_modelo(cls, modelo: UsuarioModelo) -> "Usuario":
        return cls(
            id=modelo.id,
            nome=modelo.nome,
            email=modelo.email,
            criado_em=em_utc(modelo.criado_em),
        )


@strawberry.type(description="Sessão autenticada: token de acesso e dados do usuário")
class Sessao:
    token: str = strawberry.field(
        description="Token JWT; envie no cabeçalho Authorization: Bearer <token>"
    )
    usuario: Usuario = strawberry.field(description="Usuário autenticado")
