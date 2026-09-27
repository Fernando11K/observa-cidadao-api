from typing import Any

import strawberry
from strawberry.permission import BasePermission


class EstaAutenticado(BasePermission):
    message = "É necessário estar autenticado. Envie o cabeçalho Authorization: Bearer <token>."
    error_extensions = {"code": "NAO_AUTENTICADO"}

    def has_permission(self, source: Any, info: strawberry.Info, **kwargs: Any) -> bool:
        return info.context.usuario is not None
