# dp
Simple debugger and tester for dico-command.

## Installation
```
pip install -U dico-dp
```

## Usage

```py
bot = dico_command.Bot(...)
...
bot.load_module("dp")
```

## Commands

### dp
Base command.

- dp cache - Shows current bot cache storage info.
- dp py [code] - Executes python code.

### dpe
Base command but with embed UI.
