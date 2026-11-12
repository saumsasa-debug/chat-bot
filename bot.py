import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = "9092732678:AAF3pd_k9ANlSnCB-T2kJ0Oc_YJNlVXDxYw"
WEB_APP_URL = "https://chat-bot-iszv.onrender.com/v7"

dp = Dispatcher()

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { background: #121212; color: white; font-family: sans-serif; text-align: center; padding: 20px; }
        .card { background: #1e1e1e; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .btn { background: #4CAF50; color: white; padding: 15px; border: none; border-radius: 5px; width: 100%; margin: 5px 0; font-size: 16px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🎰 KAZINO MINE</h2>
        <h3>Баланс: 15000</h3>
    </div>
    
    <div class="card">
        <h2>Игры</h2>
        <button class="btn" onclick="alert('Игра Слоты (в разработке)')">🎰 Слоты</button>
        <button class="btn" onclick="alert('Игра Кости (в разработке)')">🎲 Кости</button>
        <button class="btn" onclick="alert('Игра Мины (в разработке)')">💣 Мины</button>
        <button class="btn" onclick="alert('Игра Блэкджек (в разработке)')">🃏 Блэкджек</button>
    </div>
    
    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        alert("Скрипт загружен! Кнопки должны работать.");
    </script>
</body>
</html>
"""

async def app_page(request): 
    return web.Response(text=HTML, content_type='text/html')

async def handle_ping(request): 
    return web.Response(text="OK")

async def main():
    bot = Bot(token=BOT_TOKEN)
    app = web.Application()
    app.router.add_get('/', handle_ping)
    app.router.add_get('/v7', app_page)
    runner = web.AppRunner(app); await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000); await site.start()
    
    print("Bot Started!")
    await dp.start_polling(bot)

@dp.message(Command("start"))
async def cmd_start(m: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🚀 Открыть", web_app=WebAppInfo(url=f"{WEB_APP_URL}"))]])
    await m.answer("Нажми кнопку:", reply_markup=kb)

if __name__ == "__main__": 
    asyncio.run(main())
