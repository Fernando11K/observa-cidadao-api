from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from observa_cidadao_api.models import AcompanhamentoModelo
from observa_cidadao_api.senado.senadores import buscar_detalhe_senador
from observa_cidadao_api.services.erros import ErroDeNegocio

TAMANHO_MAXIMO_ANOTACAO = 1000


async def listar_acompanhamentos(
    sessao: AsyncSession, usuario_id: int
) -> Sequence[AcompanhamentoModelo]:
    resultado = await sessao.scalars(
        select(AcompanhamentoModelo)
        .where(AcompanhamentoModelo.usuario_id == usuario_id)
        .order_by(AcompanhamentoModelo.criado_em.desc(), AcompanhamentoModelo.id.desc())
    )
    return resultado.all()


async def acompanhar_senador(
    sessao: AsyncSession, usuario_id: int, codigo_senador: int, anotacao: str | None
) -> AcompanhamentoModelo:
    anotacao = _validar_anotacao(anotacao)

    ja_acompanha = await sessao.scalar(
        select(AcompanhamentoModelo.id).where(
            AcompanhamentoModelo.usuario_id == usuario_id,
            AcompanhamentoModelo.codigo_senador == codigo_senador,
        )
    )
    if ja_acompanha:
        raise _ja_acompanha()

    if await buscar_detalhe_senador(codigo_senador) is None:
        raise ErroDeNegocio(
            "Senador não encontrado no Senado Federal.", "SENADOR_NAO_ENCONTRADO"
        )

    acompanhamento = AcompanhamentoModelo(
        usuario_id=usuario_id, codigo_senador=codigo_senador, anotacao=anotacao
    )
    sessao.add(acompanhamento)
    try:
        await sessao.commit()
    except IntegrityError:
        await sessao.rollback()
        raise _ja_acompanha()
    await sessao.refresh(acompanhamento)
    return acompanhamento


async def atualizar_acompanhamento(
    sessao: AsyncSession, usuario_id: int, acompanhamento_id: int, anotacao: str | None
) -> AcompanhamentoModelo:
    acompanhamento = await _do_usuario(sessao, usuario_id, acompanhamento_id)
    acompanhamento.anotacao = _validar_anotacao(anotacao)
    await sessao.commit()
    await sessao.refresh(acompanhamento)
    return acompanhamento


async def remover_acompanhamento(
    sessao: AsyncSession, usuario_id: int, acompanhamento_id: int
) -> None:
    acompanhamento = await _do_usuario(sessao, usuario_id, acompanhamento_id)
    await sessao.delete(acompanhamento)
    await sessao.commit()


async def _do_usuario(
    sessao: AsyncSession, usuario_id: int, acompanhamento_id: int
) -> AcompanhamentoModelo:
    # Acompanhamentos de outros usuários são tratados como inexistentes.
    acompanhamento = await sessao.scalar(
        select(AcompanhamentoModelo).where(
            AcompanhamentoModelo.id == acompanhamento_id,
            AcompanhamentoModelo.usuario_id == usuario_id,
        )
    )
    if acompanhamento is None:
        raise ErroDeNegocio("Acompanhamento não encontrado.", "ACOMPANHAMENTO_NAO_ENCONTRADO")
    return acompanhamento


def _validar_anotacao(anotacao: str | None) -> str | None:
    if anotacao is None or not anotacao.strip():
        return None
    anotacao = anotacao.strip()
    if len(anotacao) > TAMANHO_MAXIMO_ANOTACAO:
        raise ErroDeNegocio(
            f"A anotação deve ter até {TAMANHO_MAXIMO_ANOTACAO} caracteres.", "DADOS_INVALIDOS"
        )
    return anotacao


def _ja_acompanha() -> ErroDeNegocio:
    return ErroDeNegocio("Você já acompanha este senador.", "JA_ACOMPANHA")
