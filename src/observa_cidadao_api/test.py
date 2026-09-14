import strawberry
from strawberry.fastapi import GraphQLRouter


@strawberry.type
class User:
    name: str
    age: int
    sexo: str | None =None


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(name="Patrick", sexo = "Masculino", age=100)

    @strawberry.field
    def users(self, sexo: str) -> list[User]:
        usuarios = [
                  User(name="Patrick", sexo="Masculino", age=200),
            User(name="Fernando", sexo="Masculino", age=26),
            User(name="Ferreira", sexo="Masculino", age=16),
                    User(name="Julia", sexo="Feminino", age=14),
            User(name="Roberta", sexo="Feminino", age=17)
        ]
        return list(filter(lambda u: u.sexo == sexo ,usuarios))

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)
