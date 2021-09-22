"""
dico
~~~~~~~~~~~~~~~~~~~~~~~~
Simple debugger and tester for dico-command.
:copyright: (c) 2021 dico-api
:license: MIT
"""

__version__ = "0.0.2"

from .addon import DPAddon, DPEAddon


def load(bot):
    bot.load_addons(DPAddon, DPEAddon)


def unload(bot):
    bot.unload_addons(DPAddon, DPEAddon)
