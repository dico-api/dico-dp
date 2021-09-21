import asyncio

import dico
import dico_command
from .components import DP_INFO_SELECT, DPE_INFO_SELECT
from .infos import get_front_page, get_bot_info, get_sys_info, get_full_info


def interaction_check(message_id, prefix):
    def wrap(inter: dico.Interaction):
        return inter.data.custom_id.startswith(prefix) and inter.data.custom_id.endswith(str(message_id))
    return wrap


class DPAddon(dico_command.Addon, name="dp"):
    command_name = "dp"

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


class DPEAddon(dico_command.Addon, name="dpe"):
    command_name = "dpe"

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
