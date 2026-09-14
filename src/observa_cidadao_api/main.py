from fastapi import FastAPI

from .test import graphql_app

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
