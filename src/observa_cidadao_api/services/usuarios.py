import re

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from observa_cidadao_api.core.seguranca import gerar_hash_senha, verificar_senha
from observa_cidadao_api.models import UsuarioModelo
from observa_cidadao_api.services.erros import ErroDeNegocio

TAMANHO_MINIMO_SENHA = 8
TAMANHO_MAXIMO_SENHA = 128
TAMANHO_MAXIMO_NOME = 120
TAMANHO_MAXIMO_EMAIL = 254
FORMATO_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


async def cadastrar_usuario(
    sessao: AsyncSession, nome: str, email: str, senha: str
) -> UsuarioModelo:
    nome = _validar_nome(nome)
    email = _validar_email(email)
    _validar_senha(senha)

    if await sessao.scalar(select(UsuarioModelo.id).where(UsuarioModelo.email == email)):
        raise _email_em_uso()

    usuario = UsuarioModelo(nome=nome, email=email, senha_hash=gerar_hash_senha(senha))
    sessao.add(usuario)
    try:
        await sessao.commit()
    except IntegrityError:
        await sessao.rollback()
        raise _email_em_uso()
    await sessao.refresh(usuario)
    return usuario


async def autenticar(sessao: AsyncSession, email: str, senha: str) -> UsuarioModelo:
    usuario = await sessao.scalar(
        select(UsuarioModelo).where(UsuarioModelo.email == email.strip().lower())
    )
    if not verificar_senha(senha, usuario.senha_hash if usuario else None):
        raise ErroDeNegocio("E-mail ou senha inválidos.", "CREDENCIAIS_INVALIDAS")
    return usuario


def _validar_nome(nome: str) -> str:
    nome = " ".join(nome.split())
    if not nome:
        raise ErroDeNegocio("Informe o nome.", "DADOS_INVALIDOS")
    if len(nome) > TAMANHO_MAXIMO_NOME:
        raise ErroDeNegocio(
            f"O nome deve ter até {TAMANHO_MAXIMO_NOME} caracteres.", "DADOS_INVALIDOS"
        )
    return nome


def _validar_email(email: str) -> str:
    email = email.strip().lower()
    if len(email) > TAMANHO_MAXIMO_EMAIL or not FORMATO_EMAIL.match(email):
        raise ErroDeNegocio("E-mail inválido.", "DADOS_INVALIDOS")
    return email


def _validar_senha(senha: str) -> None:
    if not TAMANHO_MINIMO_SENHA <= len(senha) <= TAMANHO_MAXIMO_SENHA:
        raise ErroDeNegocio(
            f"A senha deve ter entre {TAMANHO_MINIMO_SENHA} e {TAMANHO_MAXIMO_SENHA} caracteres.",
            "DADOS_INVALIDOS",
        )


def _email_em_uso() -> ErroDeNegocio:
    return ErroDeNegocio("Já existe um usuário com este e-mail.", "EMAIL_EM_USO")
