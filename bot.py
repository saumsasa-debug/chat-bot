import asyncio, sqlite3, time, re, os, random
from datetime import datetime, timedelta
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from aiogram.enums import ChatType

BOT_TOKEN = "9014541706:AAHIghnZbsTbmFgXiuGS9Q1Sq9sV6no1s0w"
CARD = "2202 2092 3280 2644"
SUPPORT = "@Amoert822"

conn = sqlite3.connect('bot.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, balance INTEGER DEFAULT 0, messages INTEGER DEFAULT 0)')
conn.commit()

spam_db = {} 
dp = Dispatcher()

def is_admin(status): return status in ["administrator", "creator"]

def get_user(user_id, username):
    c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    c.execute("SELECT balance, messages FROM users WHERE user_id = ?", (user_id,))
    return c.fetchone()

def update_bal(user_id, amount):
    c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()

def update_msg(user_id):
    c.execute("UPDATE users SET messages = messages + 1 WHERE user_id = ?", (user_id,))
    conn.commit()

def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📜 Правила", callback_data="m_rules"), InlineKeyboardButton(text="🏆 Топ", callback_data="m_top")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="m_prof"), InlineKeyboardButton(text="🛒 Магазин", callback_data="m_shop")],
        [InlineKeyboardButton(text="🆘 Поддержка", url=f"https://t.me/{SUPPORT[1:]}")]
    ])

def shop_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Купить звёзды", callback_data="buy_stars"), InlineKeyboardButton(text="💎 Купить Premium", callback_data="buy_prem")],
        [InlineKeyboardButton(text="⬅ Назад", callback_data="back_main")]
    ])

def stars_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="50 звёзд — 89 ₽", callback_data="pay_50")],
        [InlineKeyboardButton(text="100 звёзд — 165 ₽", callback_data="pay_100")],
        [InlineKeyboardButton(text="150 звёзд — 245 ₽", callback_data="pay_150")],
        [InlineKeyboardButton(text="⬅ Назад", callback_data="m_shop")]
    ])

def prem_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="3 мес — 1350 ₽", callback_data="prem_3")],
        [InlineKeyboardButton(text="6 мес — 1900 ₽", callback_data="prem_6")],
        [InlineKeyboardButton(text="1 год — 3100 ₽", callback_data="prem_12")],
        [InlineKeyboardButton(text="⬅ Назад", callback_data="m_shop")]
    ])

@dp.message(Command("start", "help"))
async def cmd_start(m: Message):
    get_user(m.from_user.id, m.from_user.username or "")
    await m.answer("Привет! Я бот для чата. Выбирай:", reply_markup=main_kb())

@dp.message(Command("rules"))
async def cmd_rules(m: Message):
    await m.answer("📜 <b>Правила чата:</b>\n1. Без спама и флуда.\n2. Без рекламы.\n3. Уважайте друг друга.", parse_mode="HTML")

@dp.callback_query(F.data == "m_rules")
async def cb_rules(c: CallbackQuery):
    await c.message.answer("📜 <b>Правила чата:</b>\n1. Без спама и флуда.\n2. Без рекламы.\n3. Уважайте друг друга.", parse_mode="HTML")
    await c.answer()

@dp.callback_query(F.data == "m_shop")
async def cb_shop(c: CallbackQuery):
    await c.message.edit_text("Добро пожаловать в магазин! Что тебя интересует?", reply_markup=shop_kb())
    await c.answer()

@dp.callback_query(F.data == "back_main")
async def cb_back(c: CallbackQuery):
    await c.message.edit_text("Привет! Я бот для чата. Выбирай:", reply_markup=main_kb())
    await c.answer()

@dp.callback_query(F.data == "buy_stars")
async def cb_stars(c: CallbackQuery):
    await c.message.edit_text("Выбери количество звёзд (⚠️ Сначала оплата, потом выдача!):", reply_markup=stars_kb())
    await c.answer()

@dp.callback_query(F.data.startswith("pay_"))
async def cb_pay_stars(c: CallbackQuery):
    stars = c.data.split("_")[1]
    await c.message.edit_text(f"Вы выбрали <b>{stars} звёзд</b>.\nПереведите сумму на карту:\n<code>{CARD}</code>\n\nПосле перевода напишите {SUPPORT} — пришлите чек.", parse_mode="HTML")
    await c.answer()

@dp.callback_query(F.data == "buy_prem")
async def cb_prem(c: CallbackQuery):
    await c.message.edit_text("Выбери срок Premium (⚠️ Сначала оплата, потом выдача!):", reply_markup=prem_kb())
    await c.answer()

@dp.callback_query(F.data.startswith("prem_"))
async def cb_prem_pay(c: CallbackQuery):
    await c.message.edit_text(f"Вы выбрали Premium.\nПереведите сумму на карту:\n<code>{CARD}</code>\n\nПосле перевода напишите {SUPPORT} — пришлите чек.", parse_mode="HTML")
    await c.answer()

@dp.message(Command("top"))
async def cmd_top(m: Message):
    c.execute("SELECT username, balance FROM users ORDER BY balance DESC LIMIT 10")
    rows = c.fetchall()
    text = "🏆 <b>Топ по монетам:</b>\n"
    for i, (u, b) in enumerate(rows, 1): text += f"{i}. @{u} — {b}\n"
    await m.answer(text, parse_mode="HTML")

@dp.callback_query(F.data == "m_top")
async def cb_top(c: CallbackQuery):
    c.execute("SELECT username, balance FROM users ORDER BY balance DESC LIMIT 10")
    rows = c.fetchall()
    text = "🏆 <b>Топ по монетам:</b>\n"
    for i, (u, b) in enumerate(rows, 1): text += f"{i}. @{u} — {b}\n"
    await c.message.answer(text, parse_mode="HTML")
    await c.answer()

@dp.message(Command("profile"))
async def cmd_profile(m: Message):
    bal, msg = get_user(m.from_user.id, m.from_user.username or "")
    await m.answer(f"👤 <b>Профиль:</b>\nID: <code>{m.from_user.id}</code>\nМонеты: {bal}\nСообщений: {msg}", parse_mode="HTML")

@dp.callback_query(F.data == "m_prof")
async def cb_profile(c: CallbackQuery):
    bal, msg = get_user(c.from_user.id, c.from_user.username or "")
    await c.message.answer(f"👤 <b>Профиль:</b>\nID: <code>{c.from_user.id}</code>\nМонеты: {bal}\nСообщений: {msg}", parse_mode="HTML")
    await c.answer()

@dp.message(Command("coin"))
async def cmd_coin(m: Message):
    await m.answer(f"Монетка: {random.choice(['Орёл 🦅', 'Решка 🪙'])}")

@dp.message(Command("dice"))
async def cmd_dice(m: Message):
    await m.answer_dice(emoji="🎲")

@dp.message(Command("ball"))
async def cmd_ball(m: Message):
    answers = ["Да", "Нет", "Возможно", "Спроси позже", "Однозначно да", "Даже не думай"]
    await m.answer(f"🎱 Шар говорит: {random.choice(answers)}")

@dp.message(Command("roll"))
async def cmd_roll(m: Message):
    await m.answer(f"🎲 Выпало: {random.randint(1, 100)}")

@dp.message(Command("fact"))
async def cmd_fact(m: Message):
    facts = ["Мед не портится.", "Осьминог имеет три сердца.", "Венера вращается против часовой стрелки."]
    await m.answer(f"💡 Факт: {random.choice(facts)}")

@dp.message(Command("joke"))
async def cmd_joke(m: Message):
    jokes = ["Программист ставит на ночь два стакана: один с водой (если захочет пить), второй пустой (если не захочет).", "Я не ленивый, я в энергосберегающем режиме."]
    await m.answer(f"😂 {random.choice(jokes)}")

@dp.message(Command("time"))
async def cmd_time(m: Message):
    await m.answer(f"⏰ Время: {time.strftime('%H:%M:%S')}")

@dp.message(Command("id"))
async def cmd_id(m: Message):
    if m.reply_to_message: await m.reply(f"ID пользователя: <code>{m.reply_to_message.from_user.id}</code>", parse_mode="HTML")
    else: await m.reply(f"Твой ID: <code>{m.from_user.id}</code>", parse_mode="HTML")

@dp.message(Command("ping"))
async def cmd_ping(m: Message):
    await m.answer("🏓 Понг! Я на месте.")

@dp.message(Command("gay"))
async def cmd_gay(m: Message):
    if not m.reply_to_message: return await m.answer("Ответь на сообщение!")
    await m.answer(f"🌈 {m.reply_to_message.from_user.first_name} гей на {random.randint(1, 100)}%")

@dp.message(Command("love"))
async def cmd_love(m: Message):
    if not m.reply_to_message: return await m.answer("Ответь на сообщение!")
    await m.answer(f"❤️ Совместимость: {random.randint(1, 100)}%")

# --- КИК, БАН, МУТ ---
def parse_time(time_str):
    if time_str.endswith("s"): return timedelta(seconds=int(time_str[:-1]))
    if time_str.endswith("m"): return timedelta(minutes=int(time_str[:-1]))
    if time_str.endswith("h"): return timedelta(hours=int(time_str[:-1]))
    return None

async def get_target(m: Message, args):
    target_id = None
    if m.reply_to_message: target_id = m.reply_to_message.from_user.id
    elif len(args) > 0 and args[0].startswith("@"):
        c.execute("SELECT user_id FROM users WHERE username = ?", (args[0][1:],))
        res = c.fetchone()
        if res: target_id = res[0]
    return target_id

@dp.message(Command("kick"))
async def cmd_kick(m: Message):
    if m.chat.type == ChatType.PRIVATE: return
    member = await m.chat.get_member(m.from_user.id)
    if not is_admin(member.status): return
    args = m.text.split()[1:]
    target_id = await get_target(m, args)
    if not target_id: return await m.answer("Ответь на сообщение или укажи @user.")
    
    time_str = args[-1] if not args[-1].startswith("@") else "10m"
    delta = parse_time(time_str) or timedelta(minutes=10)
    until_date = datetime.now() + delta
    
    await m.chat.restrict(target_id, ChatPermissions(can_send_messages=False), until_date=until_date)
    await m.answer(f"🔇 Пользователь замучен на {time_str}.")

@dp.message(Command("unkick"))
async def cmd_unkick(m: Message):
    if m.chat.type == ChatType.PRIVATE: return
    member = await m.chat.get_member(m.from_user.id)
    if not is_admin(member.status): return
    args = m.text.split()[1:]
    target_id = await get_target(m, args)
    if not target_id: return await m.answer("Ответь на сообщение или укажи @user.")
    await m.chat.restrict(target_id, ChatPermissions(can_send_messages=True))
    await m.answer("🔊 Пользователь размучен.")

@dp.message(Command("ban"))
async def cmd_ban(m: Message):
    if m.chat.type == ChatType.PRIVATE: return
    member = await m.chat.get_member(m.from_user.id)
    if not is_admin(member.status): return
    args = m.text.split()[1:]
    target_id = await get_target(m, args)
    if not target_id: return await m.answer("Ответь на сообщение или укажи @user.")
    await m.chat.ban(target_id)
    await m.answer("⛔ Пользователь забанен.")

@dp.message(Command("unban"))
async def cmd_unban(m: Message):
    if m.chat.type == ChatType.PRIVATE: return
    member = await m.chat.get_member(m.from_user.id)
    if not is_admin(member.status): return
    args = m.text.split()[1:]
    target_id = await get_target(m, args)
    if not target_id: return await m.answer("Ответь на сообщение или укажи @user.")
    await m.chat.unban(target_id)
    await m.answer("✅ Пользователь разбанен.")

@dp.message(Command("mute"))
async def cmd_mute(m: Message):
    if m.chat.type == ChatType.PRIVATE: return
    member = await m.chat.get_member(m.from_user.id)
    if not is_admin(member.status) or not m.reply_to_message: return
    await m.chat.restrict(m.reply_to_message.from_user.id, ChatPermissions(can_send_messages=False))
    await m.reply("🔇 Замучен.")

@dp.message(Command("tab"))
async def cmd_tab(m: Message):
    if m.chat.type == ChatType.PRIVATE: return
    member = await m.chat.get_member(m.from_user.id)
    if not is_admin(member.status): return
    await m.delete()
    for i in range(1, 50):
        try: await m.chat.delete_message(m.message_id - i)
        except: pass

@dp.message(Command("wan1"))
async def cmd_wan1(m: Message):
    c.execute("SELECT username, messages FROM users ORDER BY messages DESC LIMIT 1")
    res = c.fetchone()
    if res: await m.answer(f"🥇 Самый активный в чате: @{res[0]} (сообщений: {res[1]})")

@dp.message(Command("reward"))
async def cmd_reward(m: Message):
    args = m.text.split()
    if len(args) < 3 or not args[1].isdigit(): return await m.answer("Формат: /reward 100 @user")
    amount = int(args[1])
    if amount < 10 or amount > 1000: return await m.answer("Сумма 10-1000.")
    bal, _ = get_user(m.from_user.id, m.from_user.username or "")
    if bal < amount: return await m.answer("Мало монет.")
    target_id = m.reply_to_message.from_user.id if m.reply_to_message else None
    if not target_id and args[2].startswith("@"):
        c.execute("SELECT user_id FROM users WHERE username = ?", (args[2][1:],))
        res = c.fetchone()
        if res: target_id = res[0]
    if not target_id: return await m.answer("Укажи @user или реплай.")
    update_bal(m.from_user.id, -amount); update_bal(target_id, amount)
    await m.answer(f"✅ Переведено {amount} монет.")

@dp.message(F.text & ~F.text.startswith("/"))
async def anti_spam(m: Message):
    if m.chat.type == ChatType.PRIVATE: return
    member = await m.chat.get_member(m.from_user.id)
    if is_admin(member.status): return
    
    get_user(m.from_user.id, m.from_user.username or "")
    update_msg(m.from_user.id)
    
    if re.search(r"(https?://|t\.me/|@[a-zA-Z0-9_]{5,})", m.text):
        try:
            await m.delete(); return await m.answer(f"{m.from_user.first_name}, ссылки запрещены!")
        except: pass
    user_id = m.from_user.id; now = time.time()
    if user_id not in spam_db: spam_db[user_id] = []
    spam_db[user_id] = [t for t in spam_db[user_id] if now - t < 5]; spam_db[user_id].append(now)
    if len(spam_db[user_id]) > 5:
        try:
            await m.chat.restrict(user_id, ChatPermissions(can_send_messages=False), until_date=int(now) + 600)
            await m.answer(f"🚫 {m.from_user.first_name} замучен за флуд.")
            spam_db[user_id] = []
        except: pass
    else: update_bal(user_id, 1)

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
