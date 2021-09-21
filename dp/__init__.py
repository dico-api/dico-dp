"""
dp, simple debugger and tester for dico-command.
"""

__version__ = "0.0.1"

from .addon import DPAddon, DPEAddon


def load(bot):
    bot.load_addons(DPAddon, DPEAddon)


def unload(bot):
    bot.unload_addons(DPAddon, DPEAddon)
