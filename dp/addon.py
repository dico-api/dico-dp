import asyncio
import traceback

import dico
import dico_command
from .components import DP_INFO_SELECT, DPE_INFO_SELECT
from .infos import get_front_page, get_bot_info, get_sys_info, get_full_info, get_cache_info, get_addons_info
from .pager import Pager
from .pyeval import PYEval
from .utils import delete_wait, resolve_route, receive_interaction,interaction_check


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
                interaction: dico.Interaction = await receive_interaction(ctx, "dpinfo")
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

    @dp.subcommand("cache")
    async def dp_cache(self, ctx: dico_command.Context):
        # await ctx.reply(get_cache_info(self.bot))
        delete_button = dico.Button(style=dico.ButtonStyles.DANGER, label="Reset", emoji="🗑️", custom_id=f"trash{ctx.id}")
        msg = await ctx.reply(get_cache_info(self.bot), components=[dico.ActionRow(delete_button)])
        try:
            interaction = await receive_interaction(ctx, "trash")
            options = [dico.SelectOption(label=x, value=x) for x in self.bot.cache.available_cache_types if x != "guild_cache"]
            select_cache = dico.SelectMenu(custom_id=f"cachesel{ctx.id}", options=[dico.SelectOption(label="All", value="all"), *options])
            resp = dico.InteractionResponse(dico.InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
                                            dico.InteractionApplicationCommandCallbackData(
                                                content="Select cache to reset",
                                                flags=64,
                                                components=[dico.ActionRow(select_cache)]
                                            ))
            await interaction.create_response(resp)
            try:
                select_resp: dico.Interaction = await receive_interaction(ctx, "cachesel")
                selected = select_resp.data.values[0]
                yes_button = dico.Button(style=dico.ButtonStyles.SUCCESS, emoji="⭕", custom_id=f"confy{msg.id}")
                no_button = dico.Button(style=dico.ButtonStyles.DANGER, emoji="❌", custom_id=f"confn{msg.id}")
                resp = dico.InteractionResponse(callback_type=dico.InteractionCallbackType.UPDATE_MESSAGE,
                                                data=dico.InteractionApplicationCommandCallbackData(
                                                    content=f"Are you sure want to reset {selected} cache?",
                                                    flags=64,
                                                    components=[dico.ActionRow(yes_button, no_button)]))
                await select_resp.create_response(resp)
                yes_button.disabled = True
                no_button.disabled = True
                try:
                    inter: dico.Interaction = await self.bot.wait("interaction_create",
                                                                  check=interaction_check(msg.id, "conf"), timeout=30)
                    if inter.data.custom_id.startswith("confy"):
                        self.bot.cache.reset(selected if selected != "all" else None)
                        resp = dico.InteractionResponse(
                            callback_type=dico.InteractionCallbackType.UPDATE_MESSAGE,
                            data=dico.InteractionApplicationCommandCallbackData(content="Successfully cleared cache.",
                                                                                flags=64,
                                                                                components=[dico.ActionRow(yes_button, no_button)])
                        )
                        await inter.create_response(resp)
                    else:
                        resp = dico.InteractionResponse(
                            callback_type=dico.InteractionCallbackType.UPDATE_MESSAGE,
                            data=dico.InteractionApplicationCommandCallbackData(content="Cancelled cache reset.",
                                                                                flags=64,
                                                                                components=[dico.ActionRow(yes_button, no_button)])
                        )
                        await inter.create_response(resp)
                except asyncio.TimeoutError:
                    await select_resp.edit_original_response(content="Cancelled cache reset.", components=[dico.ActionRow(yes_button, no_button)])
            except asyncio.TimeoutError:
                select_cache.disabled = True
                await interaction.edit_original_response(components=[dico.ActionRow(select_cache)])
        except asyncio.TimeoutError:
            pass
        delete_button.disabled = True
        await msg.edit(components=[dico.ActionRow(delete_button)])

    @dp.subcommand("addon")
    async def dp_addon(self, ctx: dico_command.Context, option: str = None, addon: str = "dp"):
        if not option:
            return await ctx.reply(get_addons_info(self.bot))
        if option not in ["load", "unload", "reload"]:
            return await ctx.reply(f"Invalid option `{option}`. Must be one of `load`, `unload`, `reload`.")
        try:
            resolved = resolve_route(addon) if addon != "dp" else ["dp"]
            if not resolved:
                return await ctx.reply("No addons to reload found.")
        except ValueError as ex:
            return await ctx.reply(str(ex))
        action = {"load": self.bot.load_module, "unload": self.bot.unload_module, "reload": self.bot.reload_module}[option]
        resp = []
        if resolved:
            for x in resolved:
                try:
                    action(x)
                    resp.append(f"✅ `{x}`")
                except Exception as e:
                    resp.append(f"❌ `{x}` - `{e}`")
        await ctx.reply("\n".join(resp))

    @dp.subcommand("py")
    async def dp_py(self, ctx: dico_command.Context, *, src: str):
        delete_button = dico.Button(style=dico.ButtonStyles.DANGER, emoji="🗑️", custom_id="trash")
        try:
            ev = PYEval(ctx, self.bot, src)
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
                interaction: dico.Interaction = await receive_interaction(ctx.id, "dpeinfo")
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
