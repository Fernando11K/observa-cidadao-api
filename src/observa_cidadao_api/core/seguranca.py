from datetime import UTC, datetime, timedelta

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from observa_cidadao_api.core.config import settings

ALGORITMO = "HS256"

_hasher = PasswordHash.recommended()
# Verificado quando o e-mail não existe, para o login levar o mesmo tempo nos dois casos.
_HASH_FALSO = _hasher.hash("senha-falsa-para-tempo-constante")


def gerar_hash_senha(senha: str) -> str:
    return _hasher.hash(senha)


def verificar_senha(senha: str, senha_hash: str | None) -> bool:
    if senha_hash is None:
        _hasher.verify(senha, _HASH_FALSO)
        return False
    return _hasher.verify(senha, senha_hash)


def criar_token(usuario_id: int) -> str:
    expira_em = datetime.now(UTC) + timedelta(
        minutes=settings.token_expira_em_minutos
    )
    return jwt.encode(
        {"sub": str(usuario_id), "exp": expira_em}, settings.secret_key, algorithm=ALGORITMO
    )


def ler_usuario_id_do_token(token: str) -> int | None:
    try:
        dados = jwt.decode(token, settings.secret_key, algorithms=[ALGORITMO])
        return int(dados["sub"])
    except (InvalidTokenError, KeyError, ValueError):
        return None
