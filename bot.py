import asyncio, sqlite3, time, re, os
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ChatType

BOT_TOKEN = "9014541706:AAHIghnZbsTbmFgXiuGS9Q1Sq9sV6no1s0w"

conn = sqlite3.connect('bot.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, balance INTEGER DEFAULT 0)')
conn.commit()

spam_db = {} 
dp = Dispatcher()

def is_admin(status): return status in ["administrator", "creator"]
def check_user(user_id, username):
    c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
def add_balance(user_id, amount):
    c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
def get_balance(user_id):
    c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    res = c.fetchone()
    return res[0] if res else 0

def get_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📜 Правила", callback_data="btn_rules"), InlineKeyboardButton(text="🏆 Топ чата", callback_data="btn_top")],
        [InlineKeyboardButton(text="👤 Мой профиль", callback_data="btn_profile"), InlineKeyboardButton(text="🆘 Помощь", callback_data="btn_help")]
    ])

@dp.message(Command("start", "help"))
async def cmd_start(m: Message):
    await m.answer("Привет! Я бот для чата. Нажми на кнопку ниже.", reply_markup=get_main_kb())

@dp.callback_query(F.data == "btn_rules")
async def cb_rules(c: CallbackQuery):
    await c.message.answer("📜 <b>Правила чата:</b>\n1. Без спама.\n2. Без рекламы.", parse_mode="HTML")
    await c.answer()

@dp.callback_query(F.data == "btn_top")
async def cb_top(c: CallbackQuery):
    c_db = conn.cursor(); c_db.execute("SELECT username, balance FROM users ORDER BY balance DESC LIMIT 10")
    rows = c_db.fetchall(); text = "🏆 <b>Топ:</b>\n"
    for i, (u, b) in enumerate(rows, 1): text += f"{i}. @{u} — {b} монет\n"
    await c.message.answer(text or "Пусто", parse_mode="HTML"); await c.answer()

@dp.callback_query(F.data == "btn_profile")
async def cb_profile(c: CallbackQuery):
    check_user(c.from_user.id, c.from_user.username or "")
    await c.message.answer(f"👤 Твой ID: <code>{c.from_user.id}</code>\nБаланс: {get_balance(c.from_user.id)}", parse_mode="HTML")
    await c.answer()

@dp.callback_query(F.data == "btn_help")
async def cb_help(c: CallbackQuery):
    await c.message.answer("🆘 /reward 10-1000 @user — перевод\n/top — топ\n/mute — мут (реплай)", parse_mode="HTML")
    await c.answer()

@dp.message(Command("reward"))
async def cmd_reward(m: Message):
    if m.chat.type == ChatType.PRIVATE: return await m.answer("Только в чате.")
    args = m.text.split()
    if len(args) < 3 or not args[1].isdigit(): return await m.answer("Формат: /reward 100 @user")
    amount = int(args[1])
    if amount < 10 or amount > 1000: return await m.answer("Сумма 10-1000.")
    check_user(m.from_user.id, m.from_user.username or "")
    target_id = m.reply_to_message.from_user.id if m.reply_to_message else None
    if not target_id and args[2].startswith("@"):
        c_db = conn.cursor(); c_db.execute("SELECT user_id FROM users WHERE username = ?", (args[2][1:],))
        res = c_db.fetchone()
        if res: target_id = res[0]
        else: return await m.answer("Не найден. Пусть напишет в чат.")
    if not target_id: return await m.answer("Укажи @user или реплай.")
    if get_balance(m.from_user.id) < amount: return await m.answer("Мало монет.")
    add_balance(m.from_user.id, -amount); add_balance(target_id, amount)
    await m.answer(f"✅ Переведено {amount} монет.")

@dp.message(Command("top"))
async def cmd_top(m: Message):
    c_db = conn.cursor(); c_db.execute("SELECT username, balance FROM users ORDER BY balance DESC LIMIT 10")
    rows = c_db.fetchall(); text = "🏆 <b>Топ:</b>\n"
    for i, (u, b) in enumerate(rows, 1): text += f"{i}. @{u} — {b}\n"
    await m.answer(text or "Пусто", parse_mode="HTML")

@dp.message(Command("mute"))
async def cmd_mute(m: Message):
    if m.chat.type == ChatType.PRIVATE: return
    member = await m.chat.get_member(m.from_user.id)
    if not is_admin(member.status) or not m.reply_to_message: return
    await m.chat.restrict(m.reply_to_message.from_user.id, can_send_messages=False)
    await m.reply("Замучен.")

@dp.message(F.text & ~F.text.startswith("/"))
async def anti_spam(m: Message):
    if m.chat.type == ChatType.PRIVATE: return
    member = await m.chat.get_member(m.from_user.id)
    if is_admin(member.status): return
    check_user(m.from_user.id, m.from_user.username or "")
    if re.search(r"(https?://|t\.me/|@[a-zA-Z0-9_]{5,})", m.text):
        try:
            await m.delete(); return await m.answer(f"{m.from_user.first_name}, ссылки запрещены!")
        except: pass
    user_id = m.from_user.id; now = time.time()
    if user_id not in spam_db: spam_db[user_id] = []
    spam_db[user_id] = [t for t in spam_db[user_id] if now - t < 5]; spam_db[user_id].append(now)
    if len(spam_db[user_id]) > 5:
        try:
            await m.chat.restrict(user_id, can_send_messages=False, until_date=int(now) + 600)
            await m.answer(f"🚫 {m.from_user.first_name} замучен за флуд.")
            spam_db[user_id] = []
        except: pass
    else: add_balance(user_id, 1)

async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def main():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()
    print("Web server started on port 10000")
    
    bot = Bot(token=BOT_TOKEN)
    print("Bot started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
