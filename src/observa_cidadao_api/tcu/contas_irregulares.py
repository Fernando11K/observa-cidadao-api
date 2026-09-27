import httpx

from observa_cidadao_api.cache import HORA, em_cache
from observa_cidadao_api.tcu.nomes import normalizar_nome

URL_CONTAS_IRREGULARES = (
    "https://certidoes.apps.tcu.gov.br/api/publico/responsaveis-contas-irregulares"
)


async def buscar_contas_irregulares(nome_completo: str | None) -> list[dict]:
    # Sem filtro a API devolve a base inteira (cerca de 24 MB).
    if not nome_completo or not nome_completo.strip():
        return []

    nome = normalizar_nome(nome_completo)
    registros = await _registros_por_nome(nome_completo.strip())

    # A busca do TCU casa trechos do nome; só nomes idênticos são mantidos.
    return [r for r in registros if normalizar_nome(r.get("nome") or "") == nome]


@em_cache(segundos=12 * HORA)
async def _registros_por_nome(nome_completo: str) -> list[dict]:
    async with httpx.AsyncClient(timeout=15) as cliente:
        resposta = await cliente.post(URL_CONTAS_IRREGULARES, json={"parteNome": nome_completo})
    resposta.raise_for_status()
    return resposta.json()
