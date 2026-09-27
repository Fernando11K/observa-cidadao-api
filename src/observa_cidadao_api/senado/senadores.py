from observa_cidadao_api.cache import HORA, em_cache
from observa_cidadao_api.senado.cliente import como_lista, obter_json


@em_cache(segundos=12 * HORA)
async def listar_senadores_em_exercicio() -> list[dict]:
    dados = await obter_json("lista/atual", versao=4)
    parlamentares = dados["ListaParlamentarEmExercicio"].get("Parlamentares", {})
    return como_lista(parlamentares.get("Parlamentar"))


@em_cache(segundos=12 * HORA)
async def buscar_detalhe_senador(codigo: int) -> dict | None:
    dados = await obter_json(str(codigo), versao=6)
    return dados["DetalheParlamentar"].get("Parlamentar")


@em_cache(segundos=12 * HORA)
async def buscar_mandatos_senador(codigo: int) -> list[dict]:
    dados = await obter_json(f"{codigo}/mandatos", versao=5)
    parlamentar = dados["MandatoParlamentar"].get("Parlamentar", {})
    return como_lista(parlamentar.get("Mandatos", {}).get("Mandato"))
