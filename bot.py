import asyncio, sqlite3, time, re, os, random, string
from datetime import datetime, timedelta
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

BT = "9014541706:AAHIghnZbsTbmFgXiuGS9Q1Sq9sV6no1s0w"
CD = "2202 2092 3280 2644"
SP = "@spoff_id"

db = sqlite3.connect('bot.db', check_same_thread=False); c = db.cursor()
c.execute('CREATE TABLE IF NOT EXISTS u (id INTEGER PRIMARY KEY, n TEXT, b INTEGER DEFAULT 0, m INTEGER DEFAULT 0)'); db.commit()
sd = {}; dp = Dispatcher()
class S(StatesGroup): w = State()

def adu(s): return s in ["administrator", "creator"]
def gu(i, n):
    c.execute("INSERT OR IGNORE INTO u (id, n) VALUES (?, ?)", (i, n)); db.commit()
    c.execute("SELECT b, m FROM u WHERE id = ?", (i,)); return c.fetchone()
def ub(i, a): c.execute("UPDATE u SET b = b + ? WHERE id = ?", (a, i)); db.commit()
def um(i): c.execute("UPDATE u SET m = m + 1 WHERE id = ?", (i,)); db.commit()

def mk(): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📜 Правила", callback_data="r"), InlineKeyboardButton(text="🏆 Топ", callback_data="t")],[InlineKeyboardButton(text="👤 Профиль", callback_data="p"), InlineKeyboardButton(text="🛒 Магазин", callback_data="sh")],[InlineKeyboardButton(text="📜 Команды", callback_data="cmd"), InlineKeyboardButton(text="🆘 Поддержка", url=f"https://t.me/{SP[1:]}")]])
def sk(): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⭐ Звёзды", callback_data="bs"), InlineKeyboardButton(text="💎 Premium", callback_data="bp")],[InlineKeyboardButton(text="⬅ Назад", callback_data="bk")]])
def stk(): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="50 — 89₽", callback_data="pay_50")],[InlineKeyboardButton(text="100 — 165₽", callback_data="pay_100")],[InlineKeyboardButton(text="150 — 245₽", callback_data="pay_150")],[InlineKeyboardButton(text="Своё", callback_data="cs")],[InlineKeyboardButton(text="⬅ Назад", callback_data="sh")]])
def pk(): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="3 мес — 1350₽", callback_data="pm_3")],[InlineKeyboardButton(text="6 мес — 1900₽", callback_data="pm_6")],[InlineKeyboardButton(text="1 год — 3100₽", callback_data="pm_12")],[InlineKeyboardButton(text="⬅ Назад", callback_data="sh")]])

@dp.message(Command("start", "help"))
async def st(m: Message): gu(m.from_user.id, m.from_user.username or ""); await m.answer("Привет! Выбирай:", reply_markup=mk())

@dp.callback_query(F.data == "r")
async def c_r(c: CallbackQuery): await c.message.answer("📜 <b>Правила:</b>\n1. Без спама.\n2. Без рекламы.\n3. Уважайте друг друга.", parse_mode="HTML"); await c.answer()

@dp.callback_query(F.data == "cmd")
async def c_cmd(c: CallbackQuery): await c.message.answer("📜 <b>Команды:</b>\n/mute /unmute /ban /unban /kick /unkick /tab /wan1 /reward /top /profile /rules /id /ping /coin /dice /ball /roll /fact /joke /love /gay /time /weather /anime /short /calc /password /qr /translate /news /meme /8ball /pick /reverse /clap /vaporwave /spoiler", parse_mode="HTML"); await c.answer()

@dp.callback_query(F.data == "sh")
async def c_sh(c: CallbackQuery): await c.message.edit_text("Магазин:", reply_markup=sk()); await c.answer()

@dp.callback_query(F.data == "bk")
async def c_bk(c: CallbackQuery): await c.message.edit_text("Привет! Выбирай:", reply_markup=mk()); await c.answer()

@dp.callback_query(F.data == "bs")
async def c_bs(c: CallbackQuery): await c.message.edit_text("Выбери звёзды (Сначала оплата!):", reply_markup=stk()); await c.answer()

@dp.callback_query(F.data.startswith("pay_"))
async def c_py(c: CallbackQuery): await c.message.edit_text(f"Выбрано <b>{c.data.split('_')[1]} звёзд</b>.\nКарта:\n<code>{CD}</code>\n\nЧек {SP}", parse_mode="HTML"); await c.answer()

@dp.callback_query(F.data == "cs")
async def c_cs(c: CallbackQuery, s: FSMContext): await s.set_state(S.w); await c.message.edit_text("Введи кол-во (50-10000):"); await c.answer()

@dp.message(S.w)
async def p_cs(m: Message, s: FSMContext):
    if not m.text.isdigit(): return await m.answer("Только число:")
    st = int(m.text)
    if st < 50 or st > 10000: return await m.answer("50-10000:")
    await s.clear(); r = round(st * 1.65)
    await m.answer(f"<b>{st} звёзд</b> — <b>{r}₽</b>\nКарта:\n<code>{CD}</code>\n\nЧек {SP}", parse_mode="HTML")

@dp.callback_query(F.data == "bp")
async def c_bp(c: CallbackQuery): await c.message.edit_text("Выбери Premium:", reply_markup=pk()); await c.answer()

@dp.callback_query(F.data.startswith("pm_"))
async def c_pm(c: CallbackQuery): await c.message.edit_text(f"Premium.\nКарта:\n<code>{CD}</code>\n\nЧек {SP}", parse_mode="HTML"); await c.answer()

@dp.message(Command("top"))
async def c_top(m: Message):
    c.execute("SELECT n, b FROM u ORDER BY b DESC LIMIT 10"); rows = c.fetchall(); t = "🏆 <b>Топ:</b>\n"
    for i, (u, b) in enumerate(rows, 1): t += f"{i}. @{u} — {b}\n"
    await m.answer(t, parse_mode="HTML")

@dp.callback_query(F.data == "t")
async def c_t(c: CallbackQuery): await c_top(c.message); await c.answer()

@dp.message(Command("profile"))
async def c_p(m: Message): b, ms = gu(m.from_user.id, m.from_user.username or ""); await m.answer(f"👤 ID: <code>{m.from_user.id}</code>\nМонеты: {b}\nСообщений: {ms}", parse_mode="HTML")

@dp.callback_query(F.data == "p")
async def c_pp(c: CallbackQuery): b, ms = gu(c.from_user.id, c.from_user.username or ""); await c.message.answer(f"👤 ID: <code>{c.from_user.id}</code>\nМонеты: {b}\nСообщений: {ms}", parse_mode="HTML"); await c.answer()

@dp.message(Command("mute"))
async def c_mu(m: Message):
    if m.chat.type == ChatType.PRIVATE: return
    mem = await m.chat.get_member(m.from_user.id)
    if not adu(mem.status) or not m.reply_to_message: return
    await m.chat.restrict(m.reply_to_message.from_user.id, ChatPermissions(can_send_messages=False)); await m.reply("🔇 Замучен.")

@dp.message(Command("unmute"))
async def c_un(m: Message):
    if m.chat.type == ChatType.PRIVATE: return
    mem = await m.chat.get_member(m.from_user.id)
    if not adu(mem.status) or not m.reply_to_message: return
    await m.chat.restrict(m.reply_to_message.from_user.id, ChatPermissions(can_send_messages=True)); await m.reply("🔊 Размучен.")

@dp.message(Command("ban"))
async def c_ba(m: Message):
    if m.chat.type == ChatType.PRIVATE: return
    mem = await m.chat.get_member(m.from_user.id)
    if not adu(mem.status) or not m.reply_to_message: return
    await m.chat.ban(m.reply_to_message.from_user.id); await m.reply("⛔ Забанен.")

@dp.message(Command("unban"))
async def c_ub(m: Message):
    if m.chat.type == ChatType.PRIVATE: return
    mem = await m.chat.get_member(m.from_user.id)
    if not adu(mem.status) or not m.reply_to_message: return
    await m.chat.unban(m.reply_to_message.from_user.id); await m.reply("✅ Разбанен.")

@dp.message(Command("tab"))
async def c_tb(m: Message):
    if m.chat.type == ChatType.PRIVATE: return
    mem = await m.chat.get_member(m.from_user.id)
    if not adu(mem.status): return
    await m.delete()
    for i in range(1, 50):
        try: await m.chat.delete_message(m.message_id - i)
        except: pass

@dp.message(Command("wan1"))
async def c_w(m: Message):
    c.execute("SELECT n, m FROM u ORDER BY m DESC LIMIT 1"); r = c.fetchone()
    if r: await m.answer(f"🥇 @{r[0]} (сообщений: {r[1]})")

@dp.message(Command("reward"))
async def c_rw(m: Message):
    a = m.text.split()
    if len(a) < 3 or not a[1].isdigit(): return await m.answer("Формат: /reward 100 @user")
    am = int(a[1])
    if am < 10 or am > 1000: return await m.answer("10-1000.")
    b, _ = gu(m.from_user.id, m.from_user.username or "")
    if b < am: return await m.answer("Мало монет.")
    t = m.reply_to_message.from_user.id if m.reply_to_message else None
    if not t and a[2].startswith("@"):
        c.execute("SELECT id FROM u WHERE n = ?", (a[2][1:],)); r = c.fetchone()
        if r: t = r[0]
    if not t: return await m.answer("Укажи @user.")
    ub(m.from_user.id, -am); ub(t, am); await m.answer(f"✅ {am} монет.")

@dp.message(F.text & ~F.text.startswith("/"))
async def c_as(m: Message):
    if m.chat.type == ChatType.PRIVATE: return
    mem = await m.chat.get_member(m.from_user.id)
    if adu(mem.status): return
    gu(m.from_user.id, m.from_user.username or ""); um(m.from_user.id)
    if re.search(r"(https?://|t\.me/|@[a-zA-Z0-9_]{5,})", m.text):
        try: await m.delete(); return await m.answer(f"{m.from_user.first_name}, ссылки запрещены!")
        except: pass
    u = m.from_user.id; n = time.time()
    if u not in sd: sd[u] = []
    sd[u] = [x for x in sd[u] if n - x < 5]; sd[u].append(n)
    if len(sd[u]) > 5:
        try: await m.chat.restrict(u, ChatPermissions(can_send_messages=False), until_date=int(n) + 600); await m.answer("🚫 Флуд."); sd[u] = []
        except: pass
    else: ub(u, 1)

@dp.message(Command("coin"))
async def c_co(m: Message): await m.answer(f"Монетка: {random.choice(['Орёл 🦅', 'Решка 🪙'])}")
@dp.message(Command("dice"))
async def c_di(m: Message): await m.answer_dice(emoji="🎲")
@dp.message(Command("ball"))
async def c_bl(m: Message): await m.answer(f"🎱 {random.choice(['Да', 'Нет', 'Возможно', 'Спроси позже'])}")
@dp.message(Command("roll"))
async def c_ro(m: Message): await m.answer(f"🎲 Выпало: {random.randint(1, 100)}")
@dp.message(Command("fact"))
async def c_fa(m: Message): await m.answer(f"💡 {random.choice(['Мед не портится.', 'Осьминог имеет три сердца.', 'Венера вращается по часовой.'])}")
@dp.message(Command("joke"))
async def c_jo(m: Message): await m.answer(f"😂 {random.choice(['Программист ставит два стакана...', 'Я не ленивый, я в энергосберегающем режиме.'])}")
@dp.message(Command("time"))
async def c_ti(m: Message): await m.answer(f"⏰ {time.strftime('%H:%M:%S')}")
@dp.message(Command("id"))
async def c_id(m: Message): await m.reply(f"ID: <code>{m.reply_to_message.from_user.id if m.reply_to_message else m.from_user.id}</code>", parse_mode="HTML")
@dp.message(Command("ping"))
async def c_pi(m: Message): await m.answer("🏓 Понг!")
@dp.message(Command("gay"))
async def c_ga(m: Message): await m.answer(f"🌈 {m.reply_to_message.from_user.first_name} гей на {random.randint(1, 100)}%" if m.reply_to_message else "Ответь!")
@dp.message(Command("love"))
async def c_lo(m: Message): await m.answer(f"❤️ Совместимость: {random.randint(1, 100)}%" if m.reply_to_message else "Ответь!")
@dp.message(Command("weather"))
async def c_we(m: Message): await m.answer("☀️ Погода: +25°C, солнечно.")
@dp.message(Command("anime"))
async def c_an(m: Message): await m.answer("🍥 Аниме: Наруто, Атака Титанов, Ван-Пис.")
@dp.message(Command("short"))
async def c_sh(m: Message): await m.answer("✂️ Сокращатель ссылок в разработке.")
@dp.message(Command("calc"))
async def c_ca(m: Message): await m.answer("🧮 Калькулятор в разработке.")
@dp.message(Command("password"))
async def c_pa(m: Message): await m.answer(f"🔑 Пароль: {''.join(random.choices(string.ascii_letters + string.digits, k=12))}")
@dp.message(Command("qr"))
async def c_qr(m: Message): await m.answer("🔳 QR-код в разработке.")
@dp.message(Command("translate"))
async def c_tr(m: Message): await m.answer("🌐 Переводчик в разработке.")
@dp.message(Command("news"))
async def c_ne(m: Message): await m.answer("📰 Новости: Всё хорошо!")
@dp.message(Command("meme"))
async def c_me(m: Message): await m.answer("🖼 Мем: [Картинка]")
@dp.message(Command("8ball"))
async def c_8b(m: Message): await m.answer(f"🎱 {random.choice(['Да', 'Нет', 'Возможно', 'Точно да', 'Точно нет'])}")
@dp.message(Command("pick"))
async def c_pk(m: Message): await m.answer(f"🎲 Выбор: {random.choice(['Вариант 1', 'Вариант 2', 'Вариант 3'])}")
@dp.message(Command("reverse"))
async def c_re(m: Message): await m.answer(f"🔄 {m.text[9:][::-1] if len(m.text) > 9 else 'Напиши текст'}")
@dp.message(Command("clap"))
async def c_cl(m: Message): await m.answer("👏👏👏")
@dp.message(Command("vaporwave"))
async def c_va(m: Message): await m.answer("Ｖ Ａ Ｐ Ｏ Ｒ Ｗ Ａ Ｖ Ｅ")
@dp.message(Command("spoiler"))
async def c_sp(m: Message): await m.answer("||Скрытый текст||", parse_mode="MarkdownV2")

async def hp(r): return web.Response(text="OK")
async def mn():
    app = web.Application(); app.router.add_get('/', hp); rn = web.AppRunner(app); await rn.setup()
    st = web.TCPSite(rn, '0.0.0.0', 10000); await st.start(); print("Web Started")
    b = Bot(token=BT); print("Bot Started!"); await dp.start_polling(b)

if __name__ == "__main__": asyncio.run(mn())
