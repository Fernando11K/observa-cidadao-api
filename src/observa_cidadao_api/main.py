from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from observa_cidadao_api.core.config import settings
from observa_cidadao_api.core.database import criar_tabelas, engine
from observa_cidadao_api.graphql.schema import graphql_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    await criar_tabelas()
    yield
    await engine.dispose()


app = FastAPI(title="Observa Cidadão API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(graphql_app, prefix="/graphql")
