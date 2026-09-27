from datetime import date

import httpx

URL_SENADO = "https://legis.senado.leg.br/dadosabertos/senador"


async def obter_json(caminho: str, versao: int) -> dict:
    async with httpx.AsyncClient(headers={"Accept": "application/json"}, timeout=10) as cliente:
        resposta = await cliente.get(f"{URL_SENADO}/{caminho}", params={"v": versao})
    resposta.raise_for_status()
    return resposta.json()


def como_lista(valor: list | dict | None) -> list:
    """A API do Senado devolve um objeto em vez de lista quando há um único item."""
    if valor is None:
        return []
    if isinstance(valor, dict):
        return [valor]
    return valor


def inteiro(valor: str | None) -> int | None:
    return int(valor) if valor else None


def data_iso(valor: str | None) -> date | None:
    return date.fromisoformat(valor) if valor else None
