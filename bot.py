import asyncio, sqlite3, random, json, os
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = "9092732678:AAF3pd_k9ANlSnCB-T2kJ0Oc_YJNlVXDxYw"
CARD = "2202 2092 3280 2644"
ADMIN_PASS = "3421"
WEB_APP_URL = "https://chat-bot-iszv.onrender.com"

db = sqlite3.connect('casino.db', check_same_thread=False)
c = db.cursor()
# Изменили DEFAULT 1000 на 15000
c.execute('CREATE TABLE IF NOT EXISTS u (id INTEGER PRIMARY KEY, bal INTEGER DEFAULT 15000, refs INTEGER DEFAULT 0, time INTEGER DEFAULT 0)')
c.execute('CREATE TABLE IF NOT EXISTS promo (code TEXT PRIMARY KEY, reward INTEGER)')
db.commit()

def get_u(uid):
    c.execute("INSERT OR IGNORE INTO u (id) VALUES (?)", (uid,)); db.commit()
    c.execute("SELECT bal, refs, time FROM u WHERE id=?", (uid,)); return c.fetchone()
def add_b(uid, amt): c.execute("UPDATE u SET bal = bal + ? WHERE id=?", (amt, uid)); db.commit()

dp = Dispatcher()

# --- HTML Mini App ---
HTML = """
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1"><script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
body{background:#121212;color:#fff;font-family:sans-serif;margin:0;padding:15px;padding-bottom:70px;text-align:center}
.card{background:#1e1e1e;border-radius:10px;padding:15px;margin-bottom:15px}
.btn{background:#4CAF50;color:#fff;border:none;padding:10px;border-radius:5px;width:100%;margin:5px 0;font-size:16px}
.inp{background:#333;color:#fff;border:none;padding:10px;width:80%;border-radius:5px;text-align:center;font-size:16px}
.menu{position:fixed;bottom:0;left:0;width:100%;background:#1e1e1e;display:flex;justify-content:space-around;padding:10px 0}
.menu-btn{background:none;border:none;color:#aaa;font-size:12px;cursor:pointer}
.menu-btn.active{color:#4CAF50}
.hidden{display:none}
.slots{font-size:40px;margin:15px 0}
</style></head><body>
<div id="view-main">
<div class="card"><h2>🎰 KAZINO MINE</h2><h3>Баланс: <span id="bal">0</span></h3></div>
<div class="card"><h2>Слоты</h2><div class="slots" id="slot">🍒|🍋|🍊</div>
<input class="inp" id="bet" type="number" value="100"><br>
<label><input type="checkbox" id="fast"> Быстро (2 сек)</label><br>
<button class="btn" onclick="spin()">СТАРТ</button></div>
</div>
<div id="view-prof" class="hidden"><div class="card"><h2>Профиль</h2><p>Баланс: <span id="p-bal">0</span></p><p>В игре: <span id="p-time">0</span> мин.</p><p>Друзей: <span id="p-ref">0</span></p></div></div>
<div id="view-earn" class="hidden"><div class="card"><h2>Заработок</h2><p>Пригласи друга и получи 5000 монет!</p><button class="btn" onclick="share()">Отправить ссылку</button></div></div>
<div id="view-sell" class="hidden"><div class="card"><h2>Продажа</h2><p>Купить монеты:</p>
<button class="btn" onclick="buy(1000,10)">1000 монет - 10₽</button>
<button class="btn" onclick="buy(5000,50)">5000 монет - 50₽</button>
<input class="inp" id="c-buy" type="number" placeholder="Свое кол-во"><button class="btn" onclick="buyCustom()">Купить</button>
<p id="pay-info" class="hidden">Перевод на карту: 2202 2092 3280 2644</p></div></div>
<div id="view-set" class="hidden"><div class="card"><h2>Настройки</h2><p>Тема:</p>
<button class="btn" style="background:#000" onclick="theme('black')">Черный</button><button class="btn" style="background:#ff69b4" onclick="theme('pink')">Розовый</button>
<p>Промокод:</p><input class="inp" id="promo"><button class="btn" onclick="actPromo()">Активировать</button>
<p>Канал: <a href="https://t.me/kazino_mine" style="color:#4CAF50">@kazino_mine</a></p>
<button class="btn" style="background:#e91e63" onclick="admin()">Админ-панель</button></div></div>
<div class="menu">
<button class="menu-btn" onclick="nav('main')">🎰 Играть</button>
<button class="menu-btn" onclick="nav('prof')">👤 Профиль</button>
<button class="menu-btn" onclick="nav('earn')">💸 Заработок</button>
<button class="menu-btn" onclick="nav('sell')">🛒 Продажа</button>
<button class="menu-btn" onclick="nav('set')">⚙️ Настройки</button>
</div>
<script>
let tg=window.Telegram.WebApp; tg.expand();
let uid = tg.initDataUnsafe?.user?.id || 12345;
let balance = 15000; // Изменили стартовый баланс на 15000
function updateUI(){ document.getElementById('bal').innerText=balance; document.getElementById('p-bal').innerText=balance; }
function nav(id){ document.querySelectorAll('div[id^="view-"]').forEach(el=>el.classList.add('hidden')); document.getElementById('view-'+id).classList.remove('hidden'); }
function spin(){
    let bet = parseInt(document.getElementById('bet').value) || 100;
    if(bet>balance) return alert('Недостаточно монет!');
    let time = document.getElementById('fast').checked ? 2000 : 6000;
    let icons = ['🍒','🍋','🍊','7️⃣','💎'];
    let interval = setInterval(()=>{ document.getElementById('slot').innerText = icons[Math.floor(Math.random()*icons.length)]+'|'+icons[Math.floor(Math.random()*icons.length)]+'|'+icons[Math.floor(Math.random()*icons.length)]; }, 100);
    setTimeout(()=>{
        clearInterval(interval);
        let r1=icons[Math.floor(Math.random()*icons.length)], r2=icons[Math.floor(Math.random()*icons.length)], r3=icons[Math.floor(Math.random()*icons.length)];
        document.getElementById('slot').innerText = r1+'|'+r2+'|'+r3;
        if(r1===r2 && r2===r3){ balance += bet*5; alert('ДЖЕКПОТ! +'+bet*5); }
        else if(r1===r2||r2===r3||r1===r3){ balance += bet*2; alert('Пара! +'+bet*2); }
        else { balance -= bet; alert('Мимо! -'+bet); }
        updateUI();
        fetch('/api/spin', {method:'POST', body:JSON.stringify({uid, bet, win:(r1===r2&&r2===r3)||(r1===r2||r2===r3||r1===r3)})});
    }, time);
}
function share(){ alert('Ссылка: https://t.me/kazino_mine_bot?start='+uid); }
function buy(c, p){ document.getElementById('pay-info').classList.remove('hidden'); alert('Переведите '+p+'₽ на карту и нажмите "Оплатил"'); fetch('/api/pay', {method:'POST', body:JSON.stringify({uid, coins:c, rub:p})}); }
function buyCustom(){ let c=parseInt(document.getElementById('c-buy').value); if(c) buy(c, c*0.01); }
function theme(color){ document.body.style.background = color; }
function actPromo(){ let p = document.getElementById('promo').value; fetch('/api/promo', {method:'POST', body:JSON.stringify({uid, code:p})}).then(r=>r.json()).then(d=>{alert(d.msg); balance+=d.reward; updateUI();}); }
function admin(){ let p = prompt('Введите пароль:'); if(p === '3421'){ alert('Админка (в разработке)'); } else { alert('Неверный пароль'); } }
updateUI();
</script></body></html>
"""

async def app_page(request): return web.Response(text=HTML, content_type='text/html')
async def api_spin(request):
    data = await request.json()
    return web.json_response({"status":"ok"})
async def api_promo(request):
    data = await request.json()
    c.execute("SELECT reward FROM promo WHERE code=?", (data['code'].upper(),))
    res = c.fetchone()
    if res:
        add_b(data['uid'], res[0])
        return web.json_response({"msg":"Промокод активирован!", "reward":res[0]})
    return web.json_response({"msg":"Неверный промокод", "reward":0})
async def api_pay(request):
    data = await request.json()
    await bot.send_message(ADMIN_ID, f"💰 Оплата: {data['coins']} монет за {data['rub']}₽ от ID {data['uid']}")
    return web.json_response({"status":"ok"})

async def handle_ping(request): return web.Response(text="OK")

async def main():
    global bot, ADMIN_ID
    bot = Bot(token=BOT_TOKEN)
    ADMIN_ID = 123456789 
    
    app = web.Application()
    app.router.add_get('/', handle_ping)
    app.router.add_get('/app', app_page)
    app.router.add_post('/api/spin', api_spin)
    app.router.add_post('/api/promo', api_promo)
    app.router.add_post('/api/pay', api_pay)
    
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
            c.execute("UPDATE u SET refs = refs + 1 WHERE id=?", (ref_id,)); db.commit()
            try: await bot.send_message(ref_id, "🎉 По твоей ссылке зашел друг! +5000 монет.")
            except: pass

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Заходи и выигрывай", web_app=WebAppInfo(url=f"{WEB_APP_URL}/app"))]
    ])
    await m.answer("Добро пожаловать в KAZINO MINE! Нажми кнопку ниже, чтобы играть:", reply_markup=kb)

if __name__ == "__main__": asyncio.run(main())
