import asyncio

from config_reader import config
from on_polling import main as run_polling
from on_webhook import main as run_webhook

if __name__ == "__main__":
    if config.WEB_HOOK_MODE:
        run_webhook()
    else:
        asyncio.run(run_polling())
