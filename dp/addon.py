import asyncio
import traceback

import dico
import dico_command
from .components import DP_INFO_SELECT, DPE_INFO_SELECT
from .infos import get_front_page, get_bot_info, get_sys_info, get_full_info
from .pager import Pager
from .pyeval import PYEval
from .utils import delete_wait


def interaction_check(message_id, prefix):
    def wrap(inter: dico.Interaction):
        return inter.data.custom_id.startswith(prefix) and inter.data.custom_id.endswith(str(message_id))
    return wrap


class DPAddon(dico_command.Addon, name="dp"):
    command_name = "dp"

    async def addon_check(self, ctx):
        owner_ids = await self.bot.get_owners()
        return ctx.author.id in owner_ids

    @dico_command.command(command_name)
    async def dp(self, ctx: dico_command.Context):
        info = DP_INFO_SELECT.copy()
        info.custom_id += str(ctx.id)
        msg = await ctx.reply(get_front_page(self.bot, ctx), component=dico.ActionRow(info))

        while not self.bot.websocket_closed:
            try:
                interaction: dico.Interaction = await self.bot.wait("interaction_create", check=interaction_check(ctx.id, "dpinfo"), timeout=30)
                await interaction.create_response(dico.InteractionResponse(callback_type=dico.InteractionCallbackType.DEFERRED_UPDATE_MESSAGE, data={}))
                if interaction.data.values[0] == "main":
                    await msg.edit(content=get_front_page(self.bot, ctx))
                elif interaction.data.values[0] == "bot":
                    await msg.edit(content=get_bot_info(self.bot, ctx.guild_id))
                elif interaction.data.values[0] == "sys":
                    await msg.edit(content=get_sys_info())
            except asyncio.TimeoutError:
                break
        info.disabled = True
        await msg.edit(component=dico.ActionRow(info))

    @dp.subcommand("bot")
    async def dp_bot(self, ctx: dico_command.Context):
        await ctx.reply(get_bot_info(self.bot, ctx.guild_id))

    @dp.subcommand("sys")
    async def dp_sys(self, ctx: dico_command.Context):
        await ctx.reply(get_sys_info())

    @dp.subcommand("py")
    async def dp_py(self, ctx: dico_command.Context, *, src: str):
        ev = PYEval(ctx, self.bot, src)
        delete_button = dico.Button(style=dico.ButtonStyles.DANGER, emoji="🗑️", custom_id="trash")
        try:
            resp = await ev.evaluate()
            str_resp = [f"Result {i}:\n{x}" for i, x in enumerate(resp, start=1)] if len(resp) > 1 else [*map(str, resp)]
            pages = []
            for x in str_resp:
                if len(x) > 2000:
                    while len(x) > 2000:
                        pages.append(x[:2000])
                        x = x[2000:]
                    pages.append(x)
                else:
                    pages.append(x)
            if len(pages) == 1:
                return await delete_wait(self.bot, ctx, content=str(pages[0]))
            pager = Pager(self.bot, ctx.channel, ctx.author, pages, reply=ctx, extra_button=delete_button, timeout=60)
            async for _ in pager.start():
                await pager.message.delete()
                break
        except Exception as ex:
            tb = ''.join(traceback.format_exception(type(ex), ex, ex.__traceback__))
            tb = ("..." + tb[-1997:]) if len(tb) > 2000 else tb
            await delete_wait(self.bot, ctx, content=tb)


class DPEAddon(dico_command.Addon, name="dpe"):
    command_name = "dpe"

    async def addon_check(self, ctx):
        owner_ids = await self.bot.get_owners()
        return ctx.author.id in owner_ids

    @dico_command.command(command_name)
    async def dpe(self, ctx: dico_command.Context):
        info = DPE_INFO_SELECT.copy()
        info.custom_id += str(ctx.id)
        msg = await ctx.reply(embed=get_front_page(self.bot, ctx, embed=True), component=dico.ActionRow(info))

        while not self.bot.websocket_closed:
            try:
                interaction: dico.Interaction = await self.bot.wait("interaction_create", check=interaction_check(ctx.id, "dpeinfo"), timeout=30)
                await interaction.create_response(dico.InteractionResponse(callback_type=dico.InteractionCallbackType.DEFERRED_UPDATE_MESSAGE, data={}))
                if interaction.data.values[0] == "main":
                    await msg.edit(embed=get_front_page(self.bot, ctx, embed=True))
                elif interaction.data.values[0] == "bot":
                    await msg.edit(embed=get_bot_info(self.bot, ctx.guild_id, embed=True, timestamp=ctx.timestamp))
                elif interaction.data.values[0] == "sys":
                    await msg.edit(embed=get_sys_info(embed=True, timestamp=ctx.timestamp))
                elif interaction.data.values[0] == "full":
                    await msg.edit(embed=get_full_info(self.bot, ctx))
            except asyncio.TimeoutError:
                break
        info.disabled = True
        await msg.edit(component=dico.ActionRow(info))

    @dpe.subcommand("bot")
    async def dpe_bot(self, ctx: dico_command.Context):
        await ctx.reply(embed=get_bot_info(self.bot, ctx.guild_id, embed=True, timestamp=ctx.timestamp))

    @dpe.subcommand("sys")
    async def dpe_sys(self, ctx: dico_command.Context):
        await ctx.reply(embed=get_sys_info(embed=True, timestamp=ctx.timestamp))

    @dpe.subcommand("full")
    async def dpe_full(self, ctx: dico_command.Context):
        await ctx.reply(embed=get_full_info(self.bot, ctx))
