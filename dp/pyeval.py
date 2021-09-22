import types
from typing import Callable, Awaitable, Any, List

from dico_command import Bot, Context


class PYEval:
    def __init__(self, ctx, bot, src):
        self.ctx = ctx
        self.bot = bot
        self.src = src
        self.coro = self.compile(src)

    @staticmethod
    def compile(code) -> Callable[[Bot, Context], Awaitable[Any]]:
        if code.startswith("```py") and code.endswith("```"):
            code = code.lstrip("```py\n")
            code = code.rstrip('```')
        if len(code.split('\n')) == 1 and not code.startswith("return") and not code.startswith("del") and not code.startswith("raise"):
            code = f"return {code}"
        code = '\n'.join([f'    {x}' for x in code.split('\n')])
        code = f"async def evaluate_this(bot, ctx):\n{code}"
        exec(compile(code, "<string>", "exec"))
        return eval("evaluate_this")

    async def evaluate(self) -> List[Any]:
        results = []
        coro = self.coro(self.bot, self.ctx)
        if isinstance(coro, types.AsyncGeneratorType):
            async for x in coro:
                results.append(x)
        else:
            results.append(await coro)
        return results
