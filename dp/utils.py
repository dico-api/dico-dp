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
