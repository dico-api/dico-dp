import os
import asyncio

import dico


def parse_bytesize(bytesize: float):
    gb = round(bytesize / (1024 * 1024 * 1024), 1)
    if gb < 1:
        mb = round(bytesize / (1024 * 1024), 1)
        if mb < 1:
            return f"{bytesize}KB"
        return f"{mb}MB"
    return f"{gb}GB"


def parse_second(time: int):
    parsed_time = ""
    day = time // (24 * 60 * 60)
    time -= day * (24 * 60 * 60)
    hour = time // (60 * 60)
    time -= hour * (60 * 60)
    minute = time // 60
    time -= minute * 60
    if day:
        parsed_time += f"{day} day{'s' if day != 1 else ''} "
    if hour:
        parsed_time += f"{hour} hours "
    if minute:
        parsed_time += f"{minute} minutes "
    parsed_time += f"{time} seconds"
    return parsed_time


async def delete_wait(bot, ctx, content=None, embed=None):
    delete_button = dico.Button(style=dico.ButtonStyles.DANGER, emoji="🗑️", custom_id="trash")
    delete_button.custom_id += str(ctx.id)
    msg = await ctx.reply(content, embed=embed, component=dico.ActionRow(delete_button))
    try:
        await bot.wait("interaction_create",
                       check=lambda inter: int(inter.author) == int(ctx.author.id) and inter.data.custom_id == delete_button.custom_id,
                       timeout=60)
        await msg.delete()
    except asyncio.TimeoutError:
        delete_button.disabled = True
        await msg.edit(component=dico.ActionRow(delete_button))


def resolve_route(route: str, extension: str = ".py", sep: str = "."):
    extension = extension if extension.startswith(".") else f".{extension}"
    was_py_file = route.endswith(extension)
    initial_route = route[:-len(extension)] if was_py_file else route
    initial_route = initial_route.replace(sep, '/')
    if "*" not in initial_route:
        if was_py_file:
            return [initial_route.replace("/", sep)]
        elif os.path.isdir(initial_route):
            files = [x for x in os.listdir(initial_route)]
            if "__init__.py" in files:
                return [initial_route.replace("/", sep)]
            files = [x for x in files if x.endswith(extension) or "__init__.py" in os.listdir(os.path.join(initial_route, x))]
            files = [x[:-len(extension)] if x.endswith(extension) else x for x in files]
            return [f"{initial_route.replace('/', sep)}.{x}" for x in files]
        elif os.path.isfile(initial_route+extension):
            return [initial_route.replace("/", sep)]
        else:
            return []
    buf = ""
    for x in initial_route.split("/"):
        if x != "*":
            buf += f"{x}/"
            continue
        if initial_route[-1] != "*":
            raise ValueError(f"`*` can only be used at the end of a route.")
        if os.path.isdir(buf):
            files = [x for x in os.listdir(buf)]
            files = [x for x in files if
                     x.endswith(extension) or (not was_py_file and "__init__.py" in os.listdir(os.path.join(buf, x)))]
            files = [x[:-len(extension)] if x.endswith(extension) else x for x in files]
            return [f"{buf.replace('/', sep)}{x}" for x in files]
        else:
            return []


def interaction_check(message_id, prefix):
    def wrap(inter: dico.Interaction):
        return inter.type.message_component and inter.data.custom_id.startswith(prefix) and inter.data.custom_id.endswith(str(message_id))
    return wrap


async def receive_interaction(ctx, prefix):
    while not ctx.client.websocket_closed:
        interaction: dico.Interaction = await ctx.client.wait("interaction_create", check=interaction_check(ctx.id, prefix), timeout=30)
        if interaction.author.id != ctx.author.id:
            resp = dico.InteractionResponse(dico.InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
                                            dico.InteractionApplicationCommandCallbackData(
                                                content="You are not authorized to use this.",
                                                flags=64
                                            ))
            ctx.client.loop.create_task(interaction.create_response(resp))
            continue
        return interaction
