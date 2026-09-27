from collections.abc import AsyncIterator
from pathlib import Path

from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from observa_cidadao_api.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.database_url)
fabrica_de_sessoes = async_sessionmaker(engine, expire_on_commit=False)


async def criar_tabelas() -> None:
    _criar_pasta_do_sqlite()

    from observa_cidadao_api import (
        models,  # noqa: F401  registra os modelos no metadata
    )

    async with engine.begin() as conexao:
        await conexao.run_sync(Base.metadata.create_all)


async def obter_sessao() -> AsyncIterator[AsyncSession]:
    async with fabrica_de_sessoes() as sessao:
        yield sessao


def _criar_pasta_do_sqlite() -> None:
    url = make_url(settings.database_url)
    if url.get_backend_name() == "sqlite" and url.database and url.database != ":memory:":
        Path(url.database).parent.mkdir(parents=True, exist_ok=True)
