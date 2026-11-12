import asyncio, sqlite3, random, json
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = "9092732678:AAF3pd_k9ANlSnCB-T2kJ0Oc_YJNlVXDxYw"
ADMIN_PASS = "3421"
WEB_APP_URL = "https://chat-bot-iszv.onrender.com/v3" # Обновили версию для сброса кэша

db = sqlite3.connect('casino.db', check_same_thread=False)
c = db.cursor()
c.execute('CREATE TABLE IF NOT EXISTS u (id INTEGER PRIMARY KEY, bal INTEGER DEFAULT 15000, refs INTEGER DEFAULT 0, time INTEGER DEFAULT 0)')
c.execute('CREATE TABLE IF NOT EXISTS promo (code TEXT PRIMARY KEY, reward INTEGER)')
db.commit()

def get_u(uid):
    c.execute("INSERT OR IGNORE INTO u (id) VALUES (?)", (uid,)); db.commit()
    c.execute("SELECT bal, refs, time FROM u WHERE id=?", (uid,)); return c.fetchone()
def add_b(uid, amt): c.execute("UPDATE u SET bal = bal + ? WHERE id=?", (amt, uid)); db.commit()

dp = Dispatcher()

HTML = """
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1"><script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
body{background:#121212;color:#fff;font-family:sans-serif;margin:0;padding:15px;padding-bottom:70px;text-align:center}
.card{background:#1e1e1e;border-radius:10px;padding:15px;margin-bottom:15px}
.btn{background:#4CAF50;color:#fff;border:none;padding:10px;border-radius:5px;width:100%;margin:5px 0;font-size:16px}
.inp{background:#333;color:#fff;border:none;padding:10px;width:80%;border-radius:5px;text-align:center;font-size:16px}
.menu{position:fixed;bottom:0;left:0;width:100%;background:#1e1e1e;display:flex;justify-content:space-around;padding:10px 0;border-top:1px solid #333}
.menu-btn{background:none;border:none;color:#aaa;font-size:12px;cursor:pointer}
.hidden{display:none}
.slots{font-size:40px;margin:15px 0}
.grid{display:grid;grid-template-columns:repeat(4, 1fr);gap:5px;margin:10px 0}
.cell{background:#333;height:50px;display:flex;align-items:center;justify-content:center;font-size:24px;cursor:pointer;border-radius:5px}
.cell.safe{background:#4CAF50}
.cell.boom{background:#e91e63}
</style></head><body>
<div id="view-main">
<div class="card"><h2>🎰 KAZINO MINE</h2><h3>Баланс: <span id="bal">0</span></h3></div>
<div class="card"><h2>Слоты</h2><div class="slots" id="slot">🍒|🍋|🍊</div>
<input class="inp" id="bet" type="number" value="100" placeholder="Ставка (до 1 000 000)"><br>
<label style="display:block;margin:10px 0;"><input type="checkbox" id="fast"> Быстро (2 сек)</label>
<button class="btn" onclick="spin()">СТАРТ</button></div>
<div class="card"><h2>🎲 Кости</h2><button class="btn" onclick="dice()">Кинуть кубик (x2)</button><div id="dice-res" style="font-size:30px;margin:10px 0;"></div></div>
</div>

<div id="view-mines" class="hidden"><div class="card"><h2>💣 Минное поле</h2>
<button class="btn" onclick="startMines(2, 'x2')">x2 (2 бомбы)</button>
<button class="btn" onclick="startMines(4, 'x4')">x4 (4 бомбы)</button>
<button class="btn" onclick="startMines(6, 'x6')">x6 (6 бомб)</button>
<input class="inp" id="mine-bet" type="number" placeholder="Ставка"><button class="btn" onclick="startMines(0, 'custom')">Старт</button>
<div class="grid" id="mines-grid"></div><p id="mines-res"></p></div></div>

<div id="view-chance" class="hidden"><div class="card"><h2>🎡 Шанс</h2>
<button class="btn" onclick="playChance(10)">10%</button><button class="btn" onclick="playChance(20)">20%</button><button class="btn" onclick="playChance(50)">50%</button>
<button class="btn" onclick="playChance(85)">85%</button>
<input class="inp" id="chance-bet" type="number" placeholder="Ставка"><button class="btn" onclick="playCustomChance()">Старт (свой%)</button>
<input class="inp" id="chance-custom" type="number" placeholder="Свой % (10-85)"><div id="chance-res" style="font-size:30px;margin:10px 0;"></div></div></div>

<div id="view-prof" class="hidden"><div class="card"><h2>Профиль</h2><p>Баланс: <span id="p-bal">0</span></p><p>В игре: <span id="p-time">0</span> мин.</p><p>Друзей: <span id="p-ref">0</span></p></div></div>

<div id="view-earn" class="hidden"><div class="card"><h2>Заработок</h2><p>Пригласи друга и получи 5000 монет!</p><button class="btn" onclick="share()">Отправить ссылку</button></div></div>

<div id="view-set" class="hidden"><div class="card"><h2>Настройки</h2>
<p>Цвет темы:</p>
<button class="btn" style="background:#000" onclick="theme('black')">Черный</button>
<button class="btn" style="background:#ff69b4" onclick="theme('pink')">Розовый</button>
<button class="btn" style="background:#e91e63" onclick="theme('red')">Красный</button>
<button class="btn" style="background:#ffeb3b;color:#000" onclick="theme('yellow')">Желтый</button>
<button class="btn" style="background:#2196F3" onclick="theme('blue')">Синий</button>
<button class="btn" style="background:#9C27B0" onclick="theme('purple')">Фиолетовый</button>
<p>Промокод:</p><input class="inp" id="promo"><button class="btn" onclick="actPromo()">Активировать</button>
<p>Канал: <a href="https://t.me/kazino_mine" style="color:#4CAF50">@kazino_mine</a></p>
<button class="btn" style="background:#555;margin-top:20px;" onclick="admin()">Админ-панель</button></div></div>

<div class="menu">
<button class="menu-btn" onclick="nav('main')">🎰 Играть</button>
<button class="menu-btn" onclick="nav('mines')">💣 Мины</button>
<button class="menu-btn" onclick="nav('chance')">🎡 Шанс</button>
<button class="menu-btn" onclick="nav('earn')">💸 Заработок</button>
<button class="menu-btn" onclick="nav('set')">⚙️ Настройки</button>
</div>
<script>
let tg=window.Telegram.WebApp; tg.expand();
let uid = tg.initDataUnsafe?.user?.id || 12345;
let balance = 15000;
let currentMines = 0; let minesActive = false;

function updateUI(){ document.getElementById('bal').innerText=balance; document.getElementById('p-bal').innerText=balance; }
function nav(id){ document.querySelectorAll('div[id^="view-"]').forEach(el=>el.classList.add('hidden')); document.getElementById('view-'+id).classList.remove('hidden'); }

function spin(){
    let bet = parseInt(document.getElementById('bet').value) || 100;
    if(bet>balance) return alert('Недостаточно монет!');
    let time = document.getElementById('fast').checked ? 2000 : 6000;
    let icons = ['🍒','🍋','🍊','7️⃣','💎','🔔','🍀'];
    let interval = setInterval(()=>{ document.getElementById('slot').innerText = icons[Math.floor(Math.random()*icons.length)]+'|'+icons[Math.floor(Math.random()*icons.length)]+'|'+icons[Math.floor(Math.random()*icons.length)]; }, 100);
    setTimeout(()=>{
        clearInterval(interval);
        let r1=icons[Math.floor(Math.random()*icons.length)], r2=icons[Math.floor(Math.random()*icons.length)], r3=icons[Math.floor(Math.random()*icons.length)];
        document.getElementById('slot').innerText = r1+'|'+r2+'|'+r3;
        if(r1===r2 && r2===r3){ balance += bet*5; alert('ДЖЕКПОТ! +'+bet*5); }
        else if(r1===r2||r2===r3||r1===r3){ balance += bet*2; alert('Пара! +'+bet*2); }
        else { balance -= bet; alert('Мимо! -'+bet); }
        updateUI();
    }, time);
}

function dice(){
    let icons=['⚀','⚁','⚂','⚃','⚄','⚅'];
    let r1=icons[Math.floor(Math.random()*6)], r2=icons[Math.floor(Math.random()*6)];
    document.getElementById('dice-res').innerText=r1+' '+r2;
    if(r1===r2){ balance+=100; alert('Выигрыш 100!'); } else { balance-=100; alert('Проигрыш 100!'); }
    updateUI();
}

function startMines(bombs, mode){
    let bet = parseInt(document.getElementById('mine-bet').value) || 100;
    if(bet>balance) return alert('Недостаточно монет!');
    minesActive = true; currentMines = bombs;
    document.getElementById('mines-grid').innerHTML = '';
    document.getElementById('mines-res').innerText = '';
    for(let i=0; i<16; i++){
        let cell = document.createElement('div');
        cell.className = 'cell'; cell.innerText = '❓';
        cell.onclick = () => checkMine(cell, bet, bombs, mode);
        document.getElementById('mines-grid').appendChild(cell);
    }
    balance -= bet;
    updateUI();
}

function checkMine(cell, bet, bombs, mode){
    if(!minesActive) return;
    let isBomb = Math.random() < (bombs / 16);
    if(isBomb){ cell.className='cell boom'; cell.innerText='💣'; alert('БУМ! Ты проиграл.'); minesActive=false; }
    else {
        cell.className='cell safe'; cell.innerText='💎';
        let mult = mode === 'x2' ? 2 : mode === 'x4' ? 4 : 6;
        let win = bet * mult;
        balance += win;
        alert('Ты выиграл ' + win + '!');
        updateUI(); minesActive=false;
    }
}

function playChance(percent){
    let bet = parseInt(document.getElementById('chance-bet').value) || 100;
    if(bet>balance) return alert('Недостаточно монет!');
    let winChance = Math.random() * 100;
    if(winChance <= percent){ 
        let win = bet * (100/percent);
        balance += win; alert('Победа! Ты выиграл ' + Math.round(win));
    } else { alert('Проигрыш!'); balance -= bet; }
    updateUI();
}

function playCustomChance(){
    let percent = parseInt(document.getElementById('chance-custom').value);
    if(percent < 10 || percent > 85) return alert('Шанс от 10 до 85%');
    playChance(percent);
}

function share(){ alert('Ссылка: https://t.me/kazino_mine_bot?start='+uid); }
function theme(color){ document.body.style.background = color; }
function actPromo(){ let p = document.getElementById('promo').value; fetch('/api/promo', {method:'POST', body:JSON.stringify({uid, code:p})}).then(r=>r.json()).then(d=>{alert(d.msg); if(d.reward) { balance+=d.reward; updateUI(); } }); }
function admin(){ let p = prompt('Введите пароль:'); if(p === '3421'){ let act = prompt('1. Выдать монеты\\n2. Создать промокод'); if(act==='1'){ let u=prompt('Введи @username'); let a=prompt('Кол-во монет'); alert('Монеты выданы (заглушка)'); } else if(act==='2'){ let c=prompt('Промокод'); let r=prompt('Сумма'); alert('Промокод создан (заглушка)'); } } else { alert('Неверный пароль'); } }
updateUI();
</script></body></html>
"""

async def app_page(request): return web.Response(text=HTML, content_type='text/html')
async def api_promo(request):
    data = await request.json()
    c.execute("SELECT reward FROM promo WHERE code=?", (data['code'].upper(),))
    res = c.fetchone()
    if res:
        add_b(data['uid'], res[0])
        return web.json_response({"msg":"Промокод активирован!", "reward":res[0]})
    return web.json_response({"msg":"Неверный промокод", "reward":0})

async def handle_ping(request): return web.Response(text="OK")

async def main():
    global bot, ADMIN_ID
    bot = Bot(token=BOT_TOKEN)
    ADMIN_ID = 123456789 
    
    app = web.Application()
    app.router.add_get('/', handle_ping)
    app.router.add_get('/v3', app_page)
    app.router.add_post('/api/promo', api_promo)
    
    runner = web.AppRunner(app); await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000); await site.start()
    
    print("Server & Bot Started!")
    await dp.start_polling(bot)

@dp.message(Command("start"))
async def cmd_start(m: Message):
    args = m.text.split()
    if len(args) > 1 and args[1].isdigit():
        ref_id = int(args[1])
        if ref_id != m.from_user.id:
            add_b(ref_id, 5000) 
            try: await bot.send_message(ref_id, "🎉 По твоей ссылке зашел друг! +5000 монет.")
            except: pass
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🚀 Заходи и выигрывай", web_app=WebAppInfo(url=f"{WEB_APP_URL}"))]])
    await m.answer("Добро пожаловать в KAZINO MINE! Нажми кнопку ниже:", reply_markup=kb)

if __name__ == "__main__": asyncio.run(main())
