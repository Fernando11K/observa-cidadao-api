import asyncio
import functools
import time
from collections import OrderedDict
from collections.abc import Awaitable, Callable, Hashable
from typing import Any

HORA = 60 * 60


def em_cache(segundos: float, maximo_de_entradas: int = 1024):
    """Guarda em memória o resultado de uma função assíncrona, pelos argumentos, por `segundos`.

    Exceções não são guardadas. Chamadas simultâneas com os mesmos argumentos aguardam
    uma única execução da função. O valor devolvido é compartilhado entre as chamadas
    e não deve ser modificado.
    """

    def decorador(funcao: Callable[..., Awaitable[Any]]):
        entradas: OrderedDict[Hashable, tuple[float, Any]] = OrderedDict()
        travas: dict[Hashable, asyncio.Lock] = {}

        def valor_valido(chave: Hashable) -> tuple[bool, Any]:
            entrada = entradas.get(chave)
            if entrada and entrada[0] > time.monotonic():
                return True, entrada[1]
            return False, None

        @functools.wraps(funcao)
        async def envoltorio(*args: Hashable) -> Any:
            encontrado, valor = valor_valido(args)
            if encontrado:
                return valor

            trava = travas.setdefault(args, asyncio.Lock())
            try:
                async with trava:
                    encontrado, valor = valor_valido(args)
                    if encontrado:
                        return valor

                    valor = await funcao(*args)
                    entradas[args] = (time.monotonic() + segundos, valor)
                    entradas.move_to_end(args)
                    while len(entradas) > maximo_de_entradas:
                        entradas.popitem(last=False)
                    return valor
            finally:
                if travas.get(args) is trava:
                    del travas[args]

        envoltorio.limpar_cache = entradas.clear
        return envoltorio

    return decorador
