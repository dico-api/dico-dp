import dico


SYS_BUTTON = dico.Button(style=dico.ButtonStyles.DANGER, label="System Info", custom_id="sys")
BOT_BUTTON = dico.Button(style=dico.ButtonStyles.PRIMARY, label="Bot Info", custom_id="bot")

DP_INFO_SELECT = dico.SelectMenu(custom_id="dpinfo",
                                 options=[
                                     dico.SelectOption(label="Main Panel", value="main"),
                                     dico.SelectOption(label="System Info", value="sys"),
                                     dico.SelectOption(label="Bot Info", value="bot")
                                 ])

DPE_INFO_SELECT = dico.SelectMenu(custom_id="dpeinfo",
                                  options=[
                                      dico.SelectOption(label="Main Panel", value="main"),
                                      dico.SelectOption(label="System Info", value="sys"),
                                      dico.SelectOption(label="Bot Info", value="bot"),
                                      dico.SelectOption(label="Full Info", value="full")
                                  ])
