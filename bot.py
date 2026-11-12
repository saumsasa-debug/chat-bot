import asyncio, sqlite3, random, time
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

BOT_TOKEN = "9092732678:AAF3pd_k9ANlSnCB-T2kJ0Oc_YJNlVXDxYw"
SUPPORT = "@spoff_id"
CHANNEL_URL = "https://t.me/kazino_mine"

db = sqlite3.connect('casino.db', check_same_thread=False)
c = db.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, balance INTEGER DEFAULT 1000, last_bonus INTEGER DEFAULT 0, last_sub_bonus INTEGER DEFAULT 0)')
db.commit()

dp = Dispatcher()
class Promo(StatesGroup):
    wait_code = State()

def get_bal(uid):
    c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (uid,)); db.commit()
    c.execute("SELECT balance, last_bonus, last_sub_bonus FROM users WHERE user_id = ?", (uid,))
    return c.fetchone()

def add_bal(uid, amt):
    c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amt, uid)); db.commit()

def start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Заходи и выигрывай", callback_data="open_menu")]
    ])

def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎰 Слоты", callback_data="slots"), InlineKeyboardButton(text="🎲 Рулетка", callback_data="roulette")],
        [InlineKeyboardButton(text="🪙 Монетка", callback_data="coin"), InlineKeyboardButton(text="🎁 Бонус", callback_data="bonus")],
        [InlineKeyboardButton(text="🔥 +1000 за подписку", callback_data="sub_bonus")],
        [InlineKeyboardButton(text="🎟 Промокод", callback_data="promo"), InlineKeyboardButton(text="🔗 Наш канал", url=CHANNEL_URL)],
        [InlineKeyboardButton(text="🆘 Поддержка", url=f"https://t.me/{SUPPORT[1:]}")]
    ])

@dp.message(Command("start"))
async def cmd_start(m: Message):
    get_bal(m.from_user.id)
    text = "👋 <b>Привет! Это казино, где можно играть без денег!</b> 🤤\n\nНа старте мы даем тебе <b>1000 монет</b>. Жми кнопку ниже, чтобы начать!"
    await m.answer(text, reply_markup=start_kb(), parse_mode="HTML")

@dp.callback_query(F.data == "open_menu")
async def cb_open_menu(c: CallbackQuery):
    bal, _, _ = get_bal(c.from_user.id)
    # Вот то самое меню-витрина, которое ты просил
    text = (
        f"<b>🎰 Добро пожаловать в KAZINO MINE</b>\n\n"
        f"💰 <b>Твой баланс:</b> {bal} монет\n"
        f"🏆 <b>Статус:</b> Новичок (уровень 1)\n\n"
        f"<b>📈 Твоя статистика:</b>\n"
        f"├ Игр сыграно: 0\n"
        f"├ Выиграно: 0 монет\n"
        f"└ Проиграно: 0 монет\n\n"
        f"<b>⚡️ Доступные действия:</b>\n"
        f"Выбирай игру ниже и испытай удачу! Не забудь забрать бонус."
    )
    await c.message.edit_text(text, reply_markup=main_kb(), parse_mode="HTML")
    await c.answer()

# --- ИГРЫ ---
@dp.callback_query(F.data == "slots")
async def cb_slots(c: CallbackQuery): await c.message.answer("Напиши /slots [ставка] в чат, чтобы играть."); await c.answer()

@dp.message(Command("slots"))
async def cmd_slots(m: Message):
    args = m.text.split()
    if len(args) < 2 or not args[1].isdigit(): return await m.answer("Формат: /slots 100")
    bet = int(args[1])
    bal, _, _ = get_bal(m.from_user.id)
    if bal < bet: return await m.answer("Недостаточно монет.")
    add_bal(m.from_user.id, -bet)
    slots = [random.choice(["🍒", "🍋", "🍊", "7️⃣"]) for _ in range(3)]
    res = " | ".join(slots)
    if slots[0] == slots[1] == slots[2]:
        add_bal(m.from_user.id, bet * 5); await m.answer(f"🎰 {res}\n\n🔥 ДЖЕКПОТ! +{bet * 5} монет!")
    elif slots[0] == slots[1] or slots[1] == slots[2] or slots[0] == slots[2]:
        add_bal(m.from_user.id, bet * 2); await m.answer(f"🎰 {res}\n\n✅ Пара! +{bet * 2} монет!")
    else: await m.answer(f"🎰 {res}\n\n❌ Мимо. -{bet} монет.")

async def handle_ping(request): return web.Response(text="Casino Bot is Live!")
async def main():
    app = web.Application(); app.router.add_get('/', handle_ping); runner = web.AppRunner(app); await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000); await site.start()
    bot = Bot(token=BOT_TOKEN); print("Bot Started!"); await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())
