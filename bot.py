import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = "9092732678:AAHLWCp60TTdfYGdr1_FR3md1kn1F5xj-pU"
WEB_APP_URL = "https://chat-bot-iszv.onrender.com/v8"

dp = Dispatcher()

HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { background: #121212; color: white; font-family: sans-serif; margin: 0; padding: 15px; padding-bottom: 80px; text-align: center; }
        .card { background: #1e1e1e; border-radius: 10px; padding: 15px; margin-bottom: 15px; }
        .btn { background: #4CAF50; color: white; border: none; padding: 10px; border-radius: 5px; width: 100%; margin: 5px 0; font-size: 16px; cursor: pointer; }
        .inp { background: #333; color: white; border: none; padding: 10px; width: 80%; border-radius: 5px; text-align: center; font-size: 16px; margin: 5px 0; }
        .menu { position: fixed; bottom: 0; left: 0; width: 100%; background: #1e1e1e; display: flex; justify-content: space-around; padding: 10px 0; }
        .menu-btn { background: none; border: none; color: #aaa; font-size: 12px; cursor: pointer; }
        .hidden { display: none; }
        .slots { font-size: 40px; margin: 15px 0; }
        .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; margin: 10px 0; }
        .cell { background: #333; height: 50px; display: flex; align-items: center; justify-content: center; font-size: 24px; cursor: pointer; border-radius: 5px; }
        .cell.safe { background: #4CAF50; }
        .cell.boom { background: #e91e63; }
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
        <button class="btn" onclick="nav('mines')">💣 Мины</button>
        <button class="btn" onclick="nav('bj')">🃏 Блэкджек</button>
    </div>
</div>

<div id="view-slots" class="hidden">
    <div class="card">
        <h2>🎰 Слоты</h2>
        <div class="slots" id="slot">🍒|🍋|🍊</div>
        <input class="inp" id="slot-bet" type="number" value="100"><br>
        <label><input type="checkbox" id="fast"> Быстро</label><br>
        <button class="btn" onclick="spin()">СТАРТ</button>
        <button class="btn" style="background:#555" onclick="nav('main')">⬅ Назад</button>
    </div>
</div>

<div id="view-dice" class="hidden">
    <div class="card">
        <h2>🎲 Кости</h2>
        <div id="dice-res" style="font-size:40px;margin:20px 0;"></div>
        <input class="inp" id="dice-bet" type="number" value="100">
        <button class="btn" onclick="dice()">Кинуть</button>
        <button class="btn" style="background:#555" onclick="nav('main')">⬅ Назад</button>
    </div>
</div>

<div id="view-mines" class="hidden">
    <div class="card">
        <h2>💣 Мины</h2>
        <button class="btn" onclick="startMines(2, 2)">x2 (2 бомбы)</button>
        <button class="btn" onclick="startMines(4, 4)">x4 (4 бомбы)</button>
        <button class="btn" onclick="startMines(6, 6)">x6 (6 бомб)</button>
        <input class="inp" id="mine-bet" type="number" value="100">
        <button class="btn" onclick="startMines(0, 1)">Старт</button>
        <div class="grid" id="mines-grid"></div>
        <p id="mines-res"></p>
        <button class="btn" id="btn-take" onclick="takeMines()" disabled>💰 Забрать</button>
        <button class="btn" style="background:#555" onclick="nav('main')">⬅ Назад</button>
    </div>
</div>

<div id="view-bj" class="hidden">
    <div class="card">
        <h2>🃏 Блэкджек</h2>
        <p>Дилер: <span id="bj-dealer">-</span></p>
        <p>Ты: <span id="bj-player">0</span></p>
        <input class="inp" id="bj-bet" type="number" value="100">
        <button class="btn" id="bj-start" onclick="startBJ()">Старт</button>
        <button class="btn" id="bj-hit" onclick="hitBJ()" disabled>Взять</button>
        <button class="btn" id="bj-stand" onclick="standBJ()" disabled>Стоп</button>
        <button class="btn" style="background:#555" onclick="nav('main')">⬅ Назад</button>
    </div>
</div>

<div id="view-prof" class="hidden">
    <div class="card">
        <h2>👤 Профиль</h2>
        <p>ID: <span id="p-id">0</span></p>
        <p>Баланс: <span id="p-bal">0</span></p>
        <button class="btn" style="background:#555" onclick="nav('main')">⬅ Назад</button>
    </div>
</div>

<div id="view-earn" class="hidden">
    <div class="card">
        <h2>💸 Заработок</h2>
        <p>Пригласи друга и получи 5000!</p>
        <button class="btn" onclick="alert('Ссылка скопирована!')">Отправить ссылку</button>
        <button class="btn" style="background:#555" onclick="nav('main')">⬅ Назад</button>
    </div>
</div>

<div id="view-set" class="hidden">
    <div class="card">
        <h2>⚙️ Настройки</h2>
        <button class="btn" onclick="admin()">Админ-панель</button>
        <button class="btn" style="background:#555" onclick="nav('main')">⬅ Назад</button>
    </div>
</div>

<div class="menu">
    <button class="menu-btn" onclick="nav('main')">🏠 Меню</button>
    <button class="menu-btn" onclick="nav('prof')">👤 Профиль</button>
    <button class="menu-btn" onclick="nav('earn')">💸 Заработок</button>
    <button class="menu-btn" onclick="nav('set')">⚙️ Настройки</button>
</div>

<script>
    let tg = window.Telegram.WebApp;
    tg.expand();
    let balance = 15000;
    let uid = tg.initDataUnsafe?.user?.id || 12345;
    let minesActive = false, minesBet = 0, minesMult = 0, minesOpened = 0;
    let bjPlayer = 0, bjDealer = 0, bjPlaying = false;

    document.getElementById('username').innerText = tg.initDataUnsafe?.user?.first_name || "Игрок";
    document.getElementById('p-id').innerText = uid;

    function updateUI() { 
        document.getElementById('bal').innerText = Math.floor(balance); 
        document.getElementById('p-bal').innerText = Math.floor(balance);
    }
    function nav(id) { 
        document.querySelectorAll('div[id^="view-"]').forEach(el => el.classList.add('hidden')); 
        document.getElementById('view-' + id).classList.remove('hidden'); 
    }

    function spin() {
        let bet = parseInt(document.getElementById('slot-bet').value) || 100;
        if(bet > balance) return alert('Мало монет!');
        let time = document.getElementById('fast').checked ? 2000 : 6000;
        let icons = ['🍒','🍋','🍊','7️⃣','💎'];
        let interval = setInterval(() => {
            document.getElementById('slot').innerText = icons[Math.floor(Math.random()*icons.length)] + '|' + icons[Math.floor(Math.random()*icons.length)] + '|' + icons[Math.floor(Math.random()*icons.length)];
        }, 100);
        setTimeout(() => {
            clearInterval(interval);
            let r1 = icons[Math.floor(Math.random()*icons.length)], r2 = icons[Math.floor(Math.random()*icons.length)], r3 = icons[Math.floor(Math.random()*icons.length)];
            document.getElementById('slot').innerText = r1 + '|' + r2 + '|' + r3;
            if(r1===r2 && r2===r3) { balance += bet*5; alert('ДЖЕКПОТ! +' + bet*5); }
            else if(r1===r2 || r2===r3 || r1===r3) { balance += bet*2; alert('Пара! +' + bet*2); }
            else { balance -= bet; alert('Мимо! -' + bet); }
            updateUI();
        }, time);
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

    function startMines(bombs, mult) {
        minesBet = parseInt(document.getElementById('mine-bet').value) || 100;
        if(minesBet > balance) return alert('Мало монет!');
        minesActive = true; minesOpened = 0; minesMult = mult;
        document.getElementById('mines-grid').innerHTML = '';
        document.getElementById('btn-take').disabled = false;
        for(let i=0; i<16; i++) {
            let cell = document.createElement('div');
            cell.className = 'cell'; cell.innerText = '❓';
            cell.dataset.safe = Math.random() > (bombs / 16) ? 'true' : 'false';
            cell.onclick = () => checkMine(cell);
            document.getElementById('mines-grid').appendChild(cell);
        }
        balance -= minesBet; updateUI();
    }

    function checkMine(cell) {
        if(!minesActive || cell.classList.contains('safe') || cell.classList.contains('boom')) return;
        if(cell.dataset.safe === 'true') {
            cell.className = 'cell safe'; cell.innerText = '💎';
            minesOpened++;
        } else {
            cell.className = 'cell boom'; cell.innerText = '💣';
            alert('БУМ!'); minesActive = false; document.getElementById('btn-take').disabled = true;
        }
    }

    function takeMines() {
        if(!minesActive || minesOpened === 0) return;
        let win = minesBet * (minesMult + minesOpened * 0.5);
        balance += win; alert('Забрал ' + Math.floor(win));
        minesActive = false; document.getElementById('btn-take').disabled = true;
        updateUI();
    }

    function startBJ() {
        if(bjPlaying) return;
        let bet = parseInt(document.getElementById('bj-bet').value) || 100;
        if(bet > balance) return alert('Мало монет!');
        balance -= bet; updateUI();
        bjPlayer = Math.floor(Math.random()*10)+2; bjDealer = Math.floor(Math.random()*10)+2;
        document.getElementById('bj-player').innerText = bjPlayer;
        document.getElementById('bj-dealer').innerText = bjDealer;
        bjPlaying = true;
        document.getElementById('bj-start').disabled = true;
        document.getElementById('bj-hit').disabled = false;
        document.getElementById('bj-stand').disabled = false;
        if(bjPlayer === 21) standBJ();
    }

    function hitBJ() {
        bjPlayer += Math.floor(Math.random()*10)+2;
        document.getElementById('bj-player').innerText = bjPlayer;
        if(bjPlayer > 21) { alert('Перебор!'); bjPlaying = false; document.getElementById('bj-start').disabled = false; }
    }

    function standBJ() {
        while(bjDealer < 17) bjDealer += Math.floor(Math.random()*10)+2;
        document.getElementById('bj-dealer').innerText = bjDealer;
        let bet = parseInt(document.getElementById('bj-bet').value);
        if(bjDealer > 21 || bjPlayer > bjDealer) { balance += bet*2; alert('Победа!'); }
        else if(bjPlayer === bjDealer) { balance += bet; alert('Ничья'); }
        else { alert('Дилер победил'); }
        bjPlaying = false; updateUI();
        document.getElementById('bj-start').disabled = false;
        document.getElementById('bj-hit').disabled = true;
        document.getElementById('bj-stand').disabled = true;
    }

    function admin() {
        let p = prompt('Пароль:');
        if(p === '3421') {
            let act = prompt('1 - Выдать монеты\n2 - Забрать монеты\n3 - Промокод\n4 - Рассылка');
            alert('Действие ' + act + ' (заглушка)');
        }
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
    app.router.add_get('/v8', app_page)
    runner = web.AppRunner(app); await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000); await site.start()
    print("Bot Started!"); await dp.start_polling(bot)

@dp.message(Command("start"))
async def cmd_start(m: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🚀 Заходи и выигрывай", web_app=WebAppInfo(url=f"{WEB_APP_URL}"))]])
    await m.answer("Добро пожаловать!", reply_markup=kb)

if __name__ == "__main__": asyncio.run(main())
