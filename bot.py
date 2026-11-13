import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = "9092732678:AAFmhciWXZCY_fETo2kgitaR8rLWF2tmuak"
WEB_APP_URL = "https://chat-bot-iszv.onrender.com/v14"

dp = Dispatcher()

HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { background: #121212; color: white; font-family: sans-serif; margin: 0; padding: 15px; text-align: center; }
        .card { background: #1e1e1e; border-radius: 10px; padding: 15px; margin-bottom: 15px; }
        .btn { background: #4CAF50; color: white; border: none; padding: 10px; border-radius: 5px; width: 100%; margin: 5px 0; font-size: 16px; cursor: pointer; }
        .inp { background: #333; color: white; border: none; padding: 10px; width: 80%; border-radius: 5px; text-align: center; font-size: 16px; margin: 5px 0; }
    </style>
</head>
<body>

<div id="view-main">
    <div class="card">
        <h2>🎰 KAZINO MINE</h2>
        <h3>Привет, <span id="username">Игрок</span>!</h3>
        <h3>Баланс: <span id="bal">0</span></h3>
    </div>
    <div class="card">
        <h2>Игры</h2>
        <button class="btn" onclick="nav('slots')">🎰 Слоты</button>
        <button class="btn" onclick="nav('dice')">🎲 Кости</button>
        <button class="btn" onclick="nav('roulette')">🎡 Рулетка</button>
    </div>
</div>

<div id="view-slots" style="display:none;">
    <div class="card">
        <h2>🎰 Слоты</h2>
        <div id="slot-res" style="font-size:40px;margin:15px 0;">🍒|🍋|🍊</div>
        <input class="inp" id="slot-bet" type="number" value="100"><br>
        <button class="btn" onclick="spin()">Крутить</button>
        <button class="btn" style="background:#555" onclick="nav('main')">⬅ Назад</button>
    </div>
</div>

<div id="view-dice" style="display:none;">
    <div class="card">
        <h2>🎲 Кости</h2>
        <div id="dice-res" style="font-size:40px;margin:20px 0;"></div>
        <input class="inp" id="dice-bet" type="number" value="100">
        <button class="btn" onclick="dice()">Кинуть</button>
        <button class="btn" style="background:#555" onclick="nav('main')">⬅ Назад</button>
    </div>
</div>

<div id="view-roulette" style="display:none;">
    <div class="card">
        <h2>🎡 Рулетка</h2>
        <p>Выбери цвет:</p>
        <button class="btn" style="background:#e91e63" onclick="roulette('red')">Красное</button>
        <button class="btn" style="background:#333" onclick="roulette('black')">Черное</button>
        <input class="inp" id="roul-bet" type="number" value="100">
        <button class="btn" style="background:#555" onclick="nav('main')">⬅ Назад</button>
    </div>
</div>

<script>
    let tg = window.Telegram.WebApp;
    tg.expand();
    let balance = 15000;
    let uid = tg.initDataUnsafe?.user?.id || 12345;

    document.getElementById('username').innerText = tg.initDataUnsafe?.user?.first_name || "Игрок";

    function updateUI() { 
        document.getElementById('bal').innerText = Math.floor(balance); 
    }
    function nav(id) { 
        document.getElementById('view-main').style.display = 'none';
        document.getElementById('view-slots').style.display = 'none';
        document.getElementById('view-dice').style.display = 'none';
        document.getElementById('view-roulette').style.display = 'none';
        document.getElementById('view-' + id).style.display = 'block'; 
    }

    function spin() {
        let bet = parseInt(document.getElementById('slot-bet').value) || 100;
        if(bet > balance) return alert('Мало монет!');
        let icons = ['🍒','🍋','🍊','7️⃣','💎'];
        let r1 = icons[Math.floor(Math.random()*icons.length)], r2 = icons[Math.floor(Math.random()*icons.length)], r3 = icons[Math.floor(Math.random()*icons.length)];
        document.getElementById('slot-res').innerText = r1 + '|' + r2 + '|' + r3;
        if(r1===r2 && r2===r3) { balance += bet*5; alert('ДЖЕКПОТ! +' + bet*5); }
        else if(r1===r2 || r2===r3 || r1===r3) { balance += bet*2; alert('Пара! +' + bet*2); }
        else { balance -= bet; alert('Мимо! -' + bet); }
        updateUI();
    }

    function dice() {
        let bet = parseInt(document.getElementById('dice-bet').value) || 100;
        if(bet > balance) return alert('Мало монет!');
        let icons = ['⚀','⚁','⚂','⚃','⚄','⚅'];
        let r1 = icons[Math.floor(Math.random()*6)], r2 = icons[Math.floor(Math.random()*6)];
        document.getElementById('dice-res').innerText = r1 + ' ' + r2;
        if(r1===r2) { balance += bet; alert('Выигрыш!'); }
        else { balance -= bet; alert('Проигрыш!'); }
        updateUI();
    }

    function roulette(color) {
        let bet = parseInt(document.getElementById('roul-bet').value) || 100;
        if(bet > balance) return alert('Мало монет!');
        let win = Math.random() > 0.5 ? 'red' : 'black';
        if(win === color) { balance += bet; alert('Победа! +' + bet); }
        else { balance -= bet; alert('Проигрыш! -' + bet); }
        updateUI();
    }

    updateUI();
</script>
</body>
</html>
"""

async def app_page(request): return web.Response(text=HTML, content_type='text/html')
async def handle_ping(request): return web.Response(text="OK")

async def main():
    bot = Bot(token=BOT_TOKEN)
    app = web.Application()
    app.router.add_get('/', handle_ping)
    app.router.add_get('/v14', app_page)
    runner = web.AppRunner(app); await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000); await site.start()
    print("Bot Started!"); await dp.start_polling(bot)

@dp.message(Command("start"))
async def cmd_start(m: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🚀 Заходи и выигрывай", web_app=WebAppInfo(url=f"{WEB_APP_URL}"))]])
    await m.answer("Добро пожаловать!", reply_markup=kb)

if __name__ == "__main__": asyncio.run(main())
