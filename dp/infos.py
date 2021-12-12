import datetime
import platform

import dico
import dico_command
import psutil
from dico.utils import rgb

from . import __version__
from .utils import parse_bytesize, parse_second

try:
    from dico_interaction import __version__ as __inter_version__
except ImportError:
    __inter_version__ = None

privileged = ["GUILD_MEMBERS", "GUILD_PRESENCES"]


def get_front_page(bot, ctx, embed: bool = False):
    py_version = platform.python_version()
    py_platform = platform.platform()
    process = psutil.Process()
    start_time = int(process.create_time())
    if embed:
        inter_ver = f"\ndico-interaction `{__inter_version__}`" if __inter_version__ else ""
        intents = [k for k, v in bot.intents.values.items() if v in bot.intents]

        embed = dico.Embed(title=f"dp {__version__} Panel",
                           description=f"dico `{dico.__version__}`\ndico-command `{dico_command.__version__}`{inter_ver}\n"
                                       f"Python `{py_version}` in `{py_platform}`",
                           color=rgb(225, 225, 225),
                           timestamp=ctx.timestamp)
        embed.set_author(name=ctx.member.nick if ctx.member else ctx.author.username, icon_url=ctx.author.avatar_url())
        embed.add_field(name="Privileged Intents",
                        value=f"{', '.join([f'`{x}`' for x in intents if x in privileged])}\n"
                              f"For more info, please run `{ctx.prefix}dpe bot` or select `Bot Info`.",
                        inline=False)
        embed.add_field(name="Process Start Time",
                        value=f"<t:{start_time}:R>. (<t:{start_time}> ~)\n"
                              f"For more info, please run `{ctx.prefix}dpe sys` or select `System Info`.")
        return embed
    else:
        inter_ver = f"dico-interaction is installed and the version is `{__inter_version__}`.\n" if __inter_version__ else ""
        start_time = int(process.create_time())
        sharded_info = f"This guild is on shard `{bot.get_shard_id(ctx.guild_id) if ctx.guild_id else 0}`.\n" if bot.shards else ""
        return f"dp `{__version__}`, with dico `{dico.__version__}` and dico-command `{dico_command.__version__}` " \
            f"on Python `{py_version}` in `{py_platform}`.\n{inter_ver}" \
            f"This bot was started <t:{start_time}:R>. (<t:{start_time}> ~)\n{sharded_info}\n" \
            f"Run `{ctx.prefix}dp bot` or select `Bot Info` for more information with this bot.\n" \
            f"Run `{ctx.prefix}dp sys` or select `System Info` for more information with hardware."


def get_sys_info(embed: bool = False, timestamp: datetime.datetime = None):
    process = psutil.Process()
    memory = psutil.virtual_memory()
    uptime_sys = (datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())).total_seconds()
    uptime_bot = (datetime.datetime.now() - datetime.datetime.fromtimestamp(process.create_time())).total_seconds()
    if embed:
        embed = dico.Embed(title=f"System Information",
                           color=rgb(225, 225, 225),
                           timestamp=timestamp)
        embed.add_field(name="CPU Usage",
                        value=f"Total: `{psutil.cpu_percent()}`%\n"
                              f"Per thread: `{'`% | `'.join([str(x) for x in psutil.cpu_percent(percpu=True)])}`%\n"
                              f"Bot process: `{process.cpu_percent()}`%",
                        inline=False)
        embed.add_field(name="RAM Usage",
                        value=f"Total: `{memory.percent}`% ({parse_bytesize(memory.used)}/{parse_bytesize(memory.total)})\n"
                              f"Bot process: (Physical: `{round(process.memory_percent('rss'), 2)}`% | "
                              f"Virtual: `{round(process.memory_percent('vms'), 2)}`%)",
                        inline=False)
        embed.add_field(name="Uptime", value=f"System: {parse_second(round(uptime_sys))} | Bot: {parse_second(round(uptime_bot))}", inline=False)
        return embed
    else:
        return f"Current CPU load is `{psutil.cpu_percent()}`%.\n" \
               f"This bot is using `{process.cpu_percent()}`% of CPU.\n" \
               f"Current RAM usage is `{memory.percent}`%. ({parse_bytesize(memory.used)}/{parse_bytesize(memory.total)})\n" \
               f"This bot is using `{round(process.memory_percent('rss'), 2)}`% of physical memory " \
               f"and `{round(process.memory_percent('vms'), 2)}`% of virtual memory.\n" \
               f"System is online for {parse_second(round(uptime_sys))} and bot is online for {parse_second(round(uptime_bot))}."


def get_bot_info(bot, guild_id, embed: bool = False, timestamp: datetime.datetime = None):
    intents = [k for k, v in bot.intents.values.items() if v in bot.intents]
    cmds = len(bot.commands)
    addons = len(bot.addons)
    if embed:
        embed = dico.Embed(title=f"Bot Information",
                           color=rgb(225, 225, 225),
                           timestamp=timestamp)
        embed.add_field(name="Commands and Addons",
                        value=f"`{cmds}` Command{'s' if cmds > 1 else ''} | `{addons}` Addon{'s' if addons > 1 else ''}")
        embed.add_field(name="Guilds and Shards",
                        value=f"In {bot.guild_count} guilds.\n" + "Sharding is not enabled." if not bot.shard_count else
                        f"Total `{bot.shard_count}` shard{'s' if bot.shard_count > 1 else ''}. "
                        f"(This guild is on shard `{bot.get_shard_id(guild_id) if guild_id else 0}`.)",
                        inline=False)
        embed.add_field(name="Enabled Intents",
                        value=f"{', '.join([f'__`{x}`__' if x in privileged else f'`{x}`' for x in intents])}",
                        inline=False)
        return embed
    else:
        p_i = [f"`{x}` intent" for x in intents if x in privileged]
        if len(p_i) > 1:
            p_i[-1] = f"and {p_i[-1]}"
        shard_text = f" with `{bot.shard_count}` shard{'s' if bot.shard_count > 1 else ''}" if bot.shard_count else ""
        addon_text = f" and `{len(bot.addons)}` addon{'s' if len(bot.addons) > 1 else ''}" if bot.addons else ""
        privileged_text = f"For privileged intents, {(', ' if len(p_i) > 2 else ' ').join(p_i)} {'are' if len(p_i) > 1 else 'is'} enabled.\n"

        return f"This bot is in `{bot.guild_count}` guild{'s' if bot.guild_count > 1 else ''}{shard_text}.\n" \
               f"This bot has `{len(bot.commands)}` command{'s' if len(bot.commands) > 1 else ''}{addon_text}.\n\n" \
               f"Enabled intents: ```\n" \
               f"{', '.join(intents)}\n" \
               f"```{privileged_text}"


def get_full_info(bot, ctx):
    py_version = platform.python_version()
    py_platform = platform.platform()
    process = psutil.Process()
    memory = psutil.virtual_memory()
    uptime_sys = (datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())).total_seconds()
    uptime_bot = (datetime.datetime.now() - datetime.datetime.fromtimestamp(process.create_time())).total_seconds()
    inter_ver = f" | dico-interaction `{__inter_version__}`" if __inter_version__ else ""
    intents = [k for k, v in bot.intents.values.items() if v in bot.intents]

    embed = dico.Embed(title=f"dp {__version__} Panel",
                       description=f"dico `{dico.__version__}` | dico-command `{dico_command.__version__}`{inter_ver}\n"
                                   f"Python `{py_version}` in `{py_platform}`",
                       color=rgb(225, 225, 225),
                       timestamp=ctx.id.timestamp)
    embed.set_author(name=ctx.member.nick if ctx.member else ctx.author.username, icon_url=ctx.author.avatar_url())
    embed.add_field(name="Enabled Intents",
                    value=f"{', '.join([f'__`{x}`__' if x in privileged else f'`{x}`' for x in intents])}",
                    inline=False)
    embed.add_field(name="Shards",
                    value="Sharding is not enabled." if not bot.shard_count else
                    f"Total `{bot.shard_count}` shards. (This guild is on shard `{bot.get_shard_id(ctx.guild_id) if ctx.guild_id else 0}`.)",
                    inline=False)
    embed.add_field(name="CPU Usage",
                    value=f"Total: `{psutil.cpu_percent()}`%\n"
                          f"Per thread: `{'`% | `'.join([str(x) for x in psutil.cpu_percent(percpu=True)])}`%\n"
                          f"Bot process: `{process.cpu_percent()}`%",
                    inline=False)
    embed.add_field(name="RAM Usage",
                    value=f"Total: `{memory.percent}`% ({parse_bytesize(memory.used)}/{parse_bytesize(memory.total)})\n"
                          f"Bot process: (Physical: `{round(process.memory_percent('rss'), 2)}`% | "
                          f"Virtual: `{round(process.memory_percent('vms'), 2)}`%)",
                    inline=False)
    embed.add_field(name="Uptime",
                    value=f"System: {parse_second(round(uptime_sys))} | Bot: {parse_second(round(uptime_bot))}",
                    inline=False)
    return embed


def get_cache_info(bot, embed: bool = False):
    cache = bot.cache
    cache_info_dict = {}
    for x in cache.available_cache_types:
        if x == "guild_cache":
            continue
        storage = cache.get_storage(x)
        cache_info_dict[x] = {"size": storage.size, "max_size": storage.max_size}
    if not embed:
        max_size = sorted(map(lambda n: len(n)+4, cache_info_dict.keys()))[-1]
        texts = '\n'.join([f"{f'[ {k} ]'.ljust(max_size, ' ')} - {v['size']} / {v['max_size'] if v['max_size'] > 0 else '∞'}" for k, v in cache_info_dict.items()])
        return "This bot's cache info:\n" \
               f"```css\n{texts}\n```"


def get_addons_info(bot, embed: bool = False):
    if not embed:
        texts = []
        max_size = sorted(map(lambda n: len(n)+4, [x.name for x in bot.addons]))[-1]
        for addon in bot.addons:
            addon: dico_command.Addon
            commands = f"{len(addon.commands)} command{'s' if len(addon.commands) != 1 else ''}" if addon.commands else ""
            listeners = f"{len(addon.listeners)} listener{'s' if len(addon.listeners) != 1 else ''}" if addon.listeners else ""
            interactions = f"{len(addon.interactions)} interaction{'s' if len(addon.interactions) != 1 else ''}" if addon.interactions else ""
            callbacks = f"{len(addon.callbacks)} callback{'s' if len(addon.callbacks) != 1 else ''}" if addon.callbacks else ""
            autocompletes = f"{len(addon.autocompletes)} autocomplete{'s' if len(addon.autocompletes) != 1 else ''}" if addon.autocompletes else ""
            final_texts = [x for x in (commands, listeners, interactions, callbacks, autocompletes) if x]
            if len(final_texts) > 1:
                final_texts[-1] = f"and {final_texts[-1]}"
            texts.append(f"{f'[ {addon.name} ]'.ljust(max_size, ' ')} - {(', ' if len(final_texts) > 1 else ' ').join(final_texts)}")
        joined_texts = '\n'.join(texts)
        return f"```css\n{joined_texts}\n```"
