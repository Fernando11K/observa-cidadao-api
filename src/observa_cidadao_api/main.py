from fastapi import FastAPI

from observa_cidadao_api.graphql.query import graphql_app

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")
