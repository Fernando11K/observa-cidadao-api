import httpx

from observa_cidadao_api.cache import HORA, em_cache
from observa_cidadao_api.tcu.nomes import normalizar_nome

URL_PEDIDOS_CONGRESSO = "https://contas.tcu.gov.br/ords/api/publica/scn/pedidos_congresso"
LIMITE_PAGINAS = 100


async def buscar_solicitacoes(nome_parlamentar: str | None) -> list[dict]:
    if not nome_parlamentar:
        return []

    nome = normalizar_nome(nome_parlamentar)
    return [
        pedido
        for pedido in await _todos_os_pedidos()
        if pedido.get("autor") and normalizar_nome(pedido["autor"]) == nome
    ]


@em_cache(segundos=12 * HORA)
async def _todos_os_pedidos() -> list[dict]:
    """A API não aceita filtros, então a base inteira é baixada e mantida em cache."""
    pedidos: list[dict] = []
    url: str | None = URL_PEDIDOS_CONGRESSO

    # Os links de paginação vêm em http e redirecionam para https.
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as cliente:
        for _ in range(LIMITE_PAGINAS):
            if not url:
                break
            resposta = await cliente.get(url)
            resposta.raise_for_status()
            pagina = resposta.json()

            itens = pagina.get("items", [])
            if not itens:
                break
            pedidos.extend(itens)

            proxima = pagina.get("next")
            url = proxima.get("$ref") if isinstance(proxima, dict) else proxima

    return pedidos
