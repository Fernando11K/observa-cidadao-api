import strawberry
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext

from observa_cidadao_api.core.database import obter_sessao
from observa_cidadao_api.core.seguranca import ler_usuario_id_do_token
from observa_cidadao_api.models import UsuarioModelo


class Contexto(BaseContext):
    def __init__(self, sessao: AsyncSession, usuario: UsuarioModelo | None):
        super().__init__()
        self.sessao = sessao
        self.usuario = usuario


Info = strawberry.Info[Contexto, None]


async def obter_contexto(
    request: Request, sessao: AsyncSession = Depends(obter_sessao)
) -> Contexto:
    return Contexto(sessao=sessao, usuario=await _usuario_do_cabecalho(request, sessao))


async def _usuario_do_cabecalho(
    request: Request, sessao: AsyncSession
) -> UsuarioModelo | None:
    esquema, _, token = request.headers.get("Authorization", "").partition(" ")
    if esquema.lower() != "bearer" or not token:
        return None

    usuario_id = ler_usuario_id_do_token(token)
    if usuario_id is None:
        return None

    return await sessao.get(UsuarioModelo, usuario_id)
