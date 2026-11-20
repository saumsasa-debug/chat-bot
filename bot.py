import asyncio, sqlite3, urllib.parse
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

BOT_TOKEN = "9116065800:AAHENWeP6vSK-xL7Q4hJkZmycA5XGIqZ0No"
ADMIN_PASS = "3421"
ADMIN_USER = "@spoff_id"

db = sqlite3.connect('ai.db', check_same_thread=False)
c = db.cursor()
# Ставим 5 запросов по умолчанию
c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, reqs INTEGER DEFAULT 5)')
c.execute('CREATE TABLE IF NOT EXISTS promos (code TEXT PRIMARY KEY, reqs INTEGER, uses INTEGER DEFAULT 0)')
db.commit()

dp = Dispatcher()

class Adm(StatesGroup):
    wait_pass = State()
    promo_name = State()
    promo_reqs = State()
    give_user = State()
    give_amount = State()

class UserPromo(StatesGroup):
    wait_code = State()

def get_reqs(uid):
    c.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (uid,)); db.commit()
    c.execute("SELECT reqs FROM users WHERE id=?", (uid,)); return c.fetchone()[0]

def add_reqs(uid, amt):
    c.execute("UPDATE users SET reqs = reqs + ? WHERE id=?", (amt, uid)); db.commit()

def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎨 Нарисовать", callback_data="draw")],
        [InlineKeyboardButton(text="➕ Купить запросы", callback_data="buy"), InlineKeyboardButton(text="🎟 Промокод", callback_data="enter_promo")],
        [InlineKeyboardButton(text="💸 Заработать", callback_data="ref"), InlineKeyboardButton(text="🆘 Поддержка", url=f"https://t.me/{ADMIN_USER[1:]}")]
    ])

def adm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Выдать запросы", callback_data="adm_give")],
        [InlineKeyboardButton(text="🎟 Создать промокод", callback_data="adm_promo")],
        [InlineKeyboardButton(text="🔨 Забанить юзера", callback_data="adm_ban")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="adm_msg")],
        [InlineKeyboardButton(text="⬅ Выход", callback_data="back_main")]
    ])

@dp.message(Command("start"))
async def cmd_start(m: Message, state: FSMContext):
    await state.clear()
    reqs = get_reqs(m.from_user.id)
    await m.answer(f"👋 Привет! У тебя {reqs} запросов на генерацию.\nВыбери действие:", reply_markup=main_kb())

@dp.callback_query(F.data == "back_main")
async def cb_back(c: CallbackQuery, state: FSMContext):
    await state.clear()
    reqs = get_reqs(c.from_user.id)
    await c.message.edit_text(f"👋 Главное меню. У тебя {reqs} запросов.\nВыбери действие:", reply_markup=main_kb())
    await c.answer()

@dp.callback_query(F.data == "enter_promo")
async def cb_enter_promo(c: CallbackQuery, state: FSMContext):
    await c.message.edit_text("Введи промокод (например: BONUS):")
    await state.set_state(UserPromo.wait_code)
    await c.answer()

@dp.message(UserPromo.wait_code)
async def process_promo(m: Message, state: FSMContext):
    code = m.text.strip().upper()
    c.execute("SELECT reqs, uses FROM promos WHERE code=?", (code,))
    res = c.fetchone()
    if res:
        reqs, uses = res
        add_reqs(m.from_user.id, reqs)
        c.execute("UPDATE promos SET uses = uses + 1 WHERE code=?", (code,)); db.commit()
        await m.answer(f"✅ Промокод активирован! Ты получил {reqs} запросов.")
    else:
        await m.answer("❌ Неверный или просроченный промокод.")
    await state.clear()
    await cmd_start(m, state)

# --- АДМИНКА ---
@dp.message(Command("admin"))
async def cmd_admin(m: Message, state: FSMContext):
    await m.answer("Введи пароль:")
    await state.set_state(Adm.wait_pass)

@dp.message(Adm.wait_pass)
async def check_pass(m: Message, state: FSMContext):
    if m.text == ADMIN_PASS:
        await m.answer("✅ Админ-панель:", reply_markup=adm_kb())
    else:
        await m.answer("❌ Неверный пароль.")
    await state.clear()

@dp.callback_query(F.data == "adm_give")
async def cb_adm_give(c: CallbackQuery, state: FSMContext):
    await c.message.edit_text("Введи @username пользователя (без @):")
    await state.set_state(Adm.give_user)
    await c.answer()

@dp.message(Adm.give_user)
async def adm_give_user(m: Message, state: FSMContext):
    uname = m.text.strip().replace("@", "")
    await state.update_data(uname=uname)
    await m.answer("Сколько запросов выдать?")
    await state.set_state(Adm.give_amount)

@dp.message(Adm.give_amount)
async def adm_give_amount(m: Message, state: FSMContext):
    if not m.text.isdigit(): return await m.answer("Число:")
    amt = int(m.text)
    data = await state.get_data()
    uname = data['uname']
    c.execute("SELECT id FROM users WHERE username=?", (uname,))
    res = c.fetchone()
    if res:
        add_reqs(res[0], amt)
        await m.answer(f"✅ Выдано {amt} запросов пользователю @{uname}.")
    else:
        await m.answer("❌ Пользователь не найден в базе (пусть нажмет /start).")
    await state.clear()

@dp.callback_query(F.data == "adm_ban")
async def cb_adm_ban(c: CallbackQuery):
    await c.answer("Функция бана (нужен ID или @username)", show_alert=True)

@dp.callback_query(F.data == "adm_msg")
async def cb_adm_msg(c: CallbackQuery):
    await c.answer("Функция рассылки в разработке", show_alert=True)

@dp.callback_query(F.data == "adm_promo")
async def cb_adm_promo(c: CallbackQuery, state: FSMContext):
    await c.message.edit_text("Введи название промокода (латиницей):")
    await state.set_state(Adm.promo_name)
    await c.answer()

@dp.message(Adm.promo_name)
async def adm_promo_name(m: Message, state: FSMContext):
    code = m.text.strip().upper()
    await state.update_data(code=code)
    await m.answer("Сколько запросов должен выдавать промокод?")
    await state.set_state(Adm.promo_reqs)

@dp.message(Adm.promo_reqs)
async def adm_promo_reqs(m: Message, state: FSMContext):
    if not m.text.isdigit(): return await m.answer("Введи число:")
    reqs = int(m.text)
    data = await state.get_data()
    c.execute("INSERT OR REPLACE INTO promos (code, reqs) VALUES (?, ?)", (data['code'], reqs))
    db.commit()
    await m.answer(f"✅ Промокод <code>{data['code']}</code> создан на {reqs} запросов!", parse_mode="HTML")
    await state.clear()

# --- ГЕНЕРАЦИЯ ---
@dp.callback_query(F.data == "draw")
async def cb_draw(c: CallbackQuery):
    await c.message.answer("Отправь мне текст, и я нарисую картинку:")

@dp.message(F.text & ~F.text.startswith("/"))
async def handle_prompt(m: Message, state: FSMContext):
    if await state.get_state() == UserPromo.wait_code:
        return
    reqs = get_reqs(m.from_user.id)
    if reqs <= 0:
        return await m.answer("❌ У тебя закончились запросы! Купи их в меню или активируй промокод.")
    
    await m.answer("🎨 Рисую, подожди 10-15 секунд...")
    add_reqs(m.from_user.id, -1)
    try:
        encoded = urllib.parse.quote(m.text)
        # Изменили модель на flux для лучшего качества
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model=flux"
        await m.answer_photo(photo=url, caption=f"Твой запрос: {m.text}")
    except Exception as e:
        await m.answer(f"❌ Ошибка: {e}")

async def handle_ping(request): return web.Response(text="OK")

async def main():
    bot = Bot(token=BOT_TOKEN)
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app); await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000); await site.start()
    print("Bot Started!")
    await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())
