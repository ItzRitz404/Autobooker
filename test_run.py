import asyncio
from main import AutoBooker

async def main():
    bot = AutoBooker()
    await bot.test_runner(headless=False)

if __name__ == "__main__":
    asyncio.run(main())
