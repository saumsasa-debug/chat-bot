import asyncio, sqlite3, datetime
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

BOT_TOKEN = "9160721343:AAG0guycCUJ5uyvXr7waRtjcqZVnZmpn7nA"
WEB_APP_URL = "https://chat-bot-iszv.onrender.com/anon"
ADMIN_PASS = "3421"

db = sqlite3.connect('anon.db', check_same_thread=False)
c = db.cursor()
c.execute('CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, uid INTEGER, uname TEXT, msg TEXT, time TEXT)')
db.commit()

dp = Dispatcher()
waiting_users = [] # Очередь ожидания
active_chats = {}  # Связки: user_id -> partner_id

class AdminState(StatesGroup):
    wait_pass = State()

HTML = """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1"><script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>body{background:#121212;color:#fff;font-family:sans-serif;text-align:center;padding:15px}.card{background:#1e1e1e;border-radius:10px;padding:15px;margin-bottom:15px}.btn{background:#4CAF50;color:#fff;border:none;padding:10px;border-radius:5px;width:100%;margin:5px 0;font-size:16px}</style></head><body>
<div class="card"><h2>Анонимный чат</h2><button class="btn" onclick="alert('Поиск...')">🔍 Начать диалог</button></div>
</body></html>"""

async def app_page(request): return web.Response(text=HTML, content_type='text/html')
async def handle_ping(request): return web.Response(text="OK")

@dp.message(Command("start"))
async def cmd_start(m: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Открыть чат", web_app=WebAppInfo(url=f"{WEB_APP_URL}"))]])
    await m.answer("Добро пожаловать! Жми кнопку:", reply_markup=kb)

@dp.message(Command("admin"))
async def cmd_admin(m: Message, state: FSMContext):
    await m.answer("Пароль:")
    await state.set_state(AdminState.wait_pass)

@dp.message(AdminState.wait_pass)
async def check_pass(m: Message, state: FSMContext):
    if m.text == ADMIN_PASS:
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📜 Последние 20 сообщений", callback_data="admin_logs")]])
        await m.answer("Админ-панель:", reply_markup=kb)
    else:
        await m.answer("Неверный пароль")
    await state.clear()

@dp.callback_query(F.data == "admin_logs")
async def show_logs(c):
    c_db = db.cursor()
    c_db.execute("SELECT uname, msg, time FROM logs ORDER BY id DESC LIMIT 20")
    rows = c_db.fetchall()
    text = "📜 <b>Последние сообщения:</b>\n\n"
    for r in rows:
        text += f"👤 {r[0]} | 🕒 {r[2]}\n💬 {r[1]}\n\n"
    await c.message.answer(text or "Пусто", parse_mode="HTML")

@dp.message(F.text & ~F.text.startswith("/"))
async def handle_chat(m: Message):
    if m.chat.type != "private": return
    
    # Логируем
    c.execute("INSERT INTO logs (uid, uname, msg, time) VALUES (?, ?, ?, ?)", 
              (m.from_user.id, m.from_user.username or m.from_user.first_name, m.text, datetime.datetime.now().strftime("%H:%M:%S")))
    db.commit()

    # Логика связывания (упрощенная)
    if m.from_user.id in active_chats:
        partner = active_chats[m.from_user.id]
        try:
            await m.bot.send_message(partner, f"Аноним: {m.text}")
        except:
            pass
    else:
        if m.from_user.id not in waiting_users:
            waiting_users.append(m.from_user.id)
            await m.answer("🔍 Ищем собеседника...")
        else:
            # Нашли пару
            if len(waiting_users) >= 2:
                user1 = waiting_users.pop(0)
                user2 = m.from_user.id
                active_chats[user1] = user2
                active_chats[user2] = user1
                await m.bot.send_message(user1, "✅ Собеседник найден! Пиши.")
                await m.answer("✅ Собеседник найден! Пиши.")

async def main():
    bot = Bot(token=BOT_TOKEN)
    app = web.Application()
    app.router.add_get('/', handle_ping)
    app.router.add_get('/anon', app_page)
    runner = web.AppRunner(app); await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000); await site.start()
    print("Bot Started!")
    await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())
