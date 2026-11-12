import asyncio, sqlite3, random, time
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = "9092732678:AAF3pd_k9ANlSnCB-T2kJ0Oc_YJNlVXDxYw"
WEB_APP_URL = "https://chat-bot-iszv.onrender.com"

dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(m: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Заходи и выигрывай", web_app=WebAppInfo(url=f"{WEB_APP_URL}/app"))]
    ])
    await m.answer("Добро пожаловать в казино! Нажми кнопку ниже, чтобы открыть меню:", reply_markup=kb)

# HTML для Mini App (интерфейс)
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { background-color: #1a1a1a; color: #fff; font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .header { text-align: center; margin-bottom: 20px; }
        .balance { font-size: 24px; font-weight: bold; color: #ffd700; }
        .card { background: #2a2a2a; border-radius: 10px; padding: 15px; margin-bottom: 15px; text-align: center; }
        .btn { background: #4CAF50; color: white; border: none; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 5px; width: 80%; }
        .btn:hover { background: #45a049; }
        .slots { font-size: 30px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎰 KAZINO MINE</h1>
        <p>Твой баланс: <span class="balance" id="balance">1000</span> монет</p>
    </div>
    <div class="card">
        <h2>🎰 Слоты</h2>
        <div class="slots" id="slot-result">🍒 | 🍋 | 🍊</div>
        <button class="btn" onclick="playSlots(100)">Крутить за 100</button>
        <button class="btn" onclick="playSlots(500)">Крутить за 500</button>
    </div>
    <div class="card">
        <h2>🎲 Рулетка</h2>
        <button class="btn" onclick="playRoulette(100, 'red')">Красное (x2)</button>
        <button class="btn" onclick="playRoulette(100, 'black')">Черное (x2)</button>
    </div>
    <script>
        let tg = window.Telegram.WebApp;
        tg.expand();
        let userBalance = 1000; // В реальном приложении баланс подтягивается с сервера
        
        function updateBalance(newBal) {
            userBalance = newBal;
            document.getElementById('balance').innerText = userBalance;
        }

        function playSlots(bet) {
            if (userBalance < bet) return alert("Недостаточно монет!");
            // Здесь должен быть запрос к серверу через tg.sendData
            let res = ["🍒", "🍋", "🍊", "7️⃣"];
            let s1 = res[Math.floor(Math.random()*res.length)];
            let s2 = res[Math.floor(Math.random()*res.length)];
            let s3 = res[Math.floor(Math.random()*res.length)];
            document.getElementById('slot-result').innerText = s1 + " | " + s2 + " | " + s3;
            // Заглушка для начисления
            if (s1 === s2 && s2 === s3) updateBalance(userBalance + bet * 5);
            else updateBalance(userBalance - bet);
        }

        function playRoulette(bet, color) {
            if (userBalance < bet) return alert("Недостаточно монет!");
            let win = Math.random() > 0.5 ? color : (color === 'red' ? 'black' : 'red');
            if (win === color) updateBalance(userBalance + bet);
            else updateBalance(userBalance - bet);
        }
    </script>
</body>
</html>
"""

async def handle_ping(request): return web.Response(text="OK")
async def handle_app(request): return web.Response(text=HTML_PAGE, content_type='text/html')

async def main():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    app.router.add_get('/app', handle_app)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()
    
    bot = Bot(token=BOT_TOKEN)
    print("Bot Started!")
    await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())
