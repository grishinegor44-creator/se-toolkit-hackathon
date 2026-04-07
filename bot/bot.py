"""
CocktailBot entry point.
Supports two run modes:
  - normal: starts aiogram polling (default)
  - cli-test: runs a simple REPL for handler testing without real Telegram
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import settings
from bot.handlers import commands_router, messages_router

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    logger.info("Starting CocktailBot…")

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(commands_router)
    dp.include_router(messages_router)

    logger.info("Bot started. Polling for updates…")
    await dp.start_polling(bot)


def cli_test() -> None:
    """
    Simple CLI test mode — runs intent detection without Telegram.
    Useful for verifying handler logic without a live bot token.
    Usage: python -m bot.bot cli-test
    """
    from bot.services.intent import detect_intent

    print("CocktailBot CLI test mode. Type messages to test intent detection.")
    print("Type 'quit' to exit.\n")
    while True:
        try:
            text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if text.lower() in ("quit", "exit", "q"):
            break
        result = detect_intent(text)
        print(f"Intent: {result.intent}")
        if result.name:
            print(f"  Name: {result.name}")
        if result.ingredients:
            print(f"  Ingredients: {result.ingredients}")
        print()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cli-test":
        cli_test()
    else:
        asyncio.run(main())
