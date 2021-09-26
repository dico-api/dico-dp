import typing
import asyncio
import dico
import dico_command


class Pager:
    next_emoji = "➡"
    prev_emoji = "⬅"

    def __init__(self,
                 bot: dico_command.Bot,
                 channel: dico.Channel,
                 author: dico.User,
                 pages: typing.List[typing.Union[str, dico.Embed]],
                 extra_button: dico.Button = None,
                 *, is_embed: bool = False,
                 reply: dico.Message = None,
                 timeout: int = 30):
        self.bot = bot
        self.channel = channel
        self.author = author
        self.pages = pages
        self.extra_button = extra_button
        self.is_embed = is_embed
        self.reply = reply
        self.timeout = timeout
        self.current = 0
        self.message = None  # Should be set later.

    @property
    def __max_page(self):
        return len(self.pages) - 1

    @property
    def current_page(self):
        return self.current + 1

    def next(self):
        self.current = self.current + 1 if self.current + 1 <= self.__max_page else 0
        return self.pages[self.current]

    def prev(self):
        self.current = self.current - 1 if self.current - 1 >= 0 else self.__max_page
        return self.pages[self.current]

    @property
    def page_button(self):
        return dico.Button(style=2, label=f"Page {self.current_page}/{len(self.pages)}", custom_id=f"pages{self.message.id}", disabled=True)

    def current_action_row(self, disabled: bool = False):
        next_button = dico.Button(style=1, label="Next", custom_id=f"next{self.message.id}", emoji=self.next_emoji, disabled=disabled)
        prev_button = dico.Button(style=1, label="Prev", custom_id=f"prev{self.message.id}", emoji=self.prev_emoji, disabled=disabled)
        buttons = [prev_button, self.page_button, next_button]
        if self.extra_button:
            if not self.extra_button.custom_id.endswith(str(self.message.id)):
                self.extra_button.custom_id += str(self.message.id)
            if disabled:
                self.extra_button.disabled = True
            else:
                self.extra_button.disabled = False
            buttons.append(self.extra_button)
        return dico.ActionRow(*buttons)

    async def start_flatten(self):
        return_list = []
        async for x in self.start():
            return_list.append(x)
        return return_list

    async def start(self):
        func = self.channel.send if not self.reply else self.reply.reply
        self.message = await func(content=self.pages[0] if not self.is_embed else None, embed=self.pages[0] if self.is_embed else None)
        await self.message.edit(component=self.current_action_row())

        while not self.bot.websocket_closed:
            try:
                interaction: dico.Interaction = await self.bot.wait(
                    "interaction_create",
                    check=lambda inter: int(inter.author) == int(self.author.id),
                    timeout=self.timeout
                )

                await interaction.create_response(dico.InteractionResponse(callback_type=dico.InteractionCallbackType.DEFERRED_UPDATE_MESSAGE, data={}))

                if interaction.data.custom_id.startswith("next"):
                    page = self.next()
                    await self.message.edit(content=page if not self.is_embed else None,
                                            embed=page if self.is_embed else None,
                                            component=self.current_action_row())

                elif interaction.data.custom_id.startswith("prev"):
                    page = self.prev()
                    await self.message.edit(content=page if not self.is_embed else None,
                                            embed=page if self.is_embed else None,
                                            component=self.current_action_row())

                else:
                    yield self.current_page

            except asyncio.TimeoutError:
                break
        await self.message.edit(component=self.current_action_row(disabled=True))
