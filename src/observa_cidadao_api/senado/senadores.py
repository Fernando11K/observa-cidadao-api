from observa_cidadao_api.graphql.type import Senador
import httpx
import json

URL_SENADO = "https://legis.senado.leg.br/dadosabertos/senador"


async def buscar_senador(codigo: int) -> Senador | None:

    async with httpx.AsyncClient() as cliente:

        resposta = await cliente.get(f"{URL_SENADO}/{codigo}?v=6",
            headers={
                "Accept": "application/json"
            },
            timeout=10
        )

        resposta.raise_for_status()

        dados = resposta.json()

        return converter_senador(dados)


def converter_senador(dados: dict) -> Senador | None:
    identificao = dados["DetalheParlamentar"]["Parlamentar"]["IdentificacaoParlamentar"]
    #print(json.dumps(dados, indent=4, ensure_ascii=False))

    return Senador(nome=identificao["NomeCompletoParlamentar"],)