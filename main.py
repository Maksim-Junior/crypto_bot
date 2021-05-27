import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ParseMode
from dotenv import load_dotenv
from parser import CryptoParse
from db import find_chat_id, edit_cur_list, search_currency, process_status_update, find_user_status
from db import process_rate_update
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO)

load_dotenv()
TOKEN = os.getenv("TOKEN")
URL = os.getenv("URL")
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)

list_currency = [
    "BTC", "ETH", "USDT", "BNB", "ADA", "XRP", "DOGE", "DOT", "USDC", "ICP", "UNI", "BCH", "MATIC", "LTC",
    "LINK", "XLM", "SQL", "BUSD", "ETC", "VET", "THETA", "WBTC", "DREP", "EOS", "TRX", "FIL", "AAVE",
    "DAI", "XMR", "NEO", "KLAY", "MKR", "SHIB", "FTT", "XTZ", "BSV", "CRO", "MIOTA", "CAKE", "ALGO",
    "ATOM", "HT", "BTT", "LUNA", "KSM", "RUNE", "AVAX", "COMP", "HBAR", "LEO", "BTCB", "DASH", "EGLD",
    "UST", "TEL", "HOT", "XEM", "DCR", "ZEC", "YFI", "WAVES", "CEL", "CHZ", "SNX", "TFUEL", "SUSHI",
    "MANA", "ENJ", "ZIL", "REV", "NEXO", "PAX", "NEAR", "HNT", "STX", "BAT", "QTUM", "BTG", "TUSD",
    "ZEN", "GRT", "DGB", "NANO", "ONT", "ONE", "OMG", "HUSD", "CHSB", "SC", "BNT", "ZRX", "FTM", "UMA",
    "OKB", "RVN", "CELO", "ICX", "ANKR", "BAKE", "NXM",
]

inline_kb1 = InlineKeyboardMarkup()

for i in range(len(list_currency)):
    a = InlineKeyboardButton(f"{list_currency[i]}", callback_data=f"btn_{i}")
    inline_kb1.add(a)


@dp.message_handler(commands='listcurrency')
async def get_user_currency(message: types.Message):
    currency = await search_currency(message.chat.id)
    if currency:
        text = ''
        for cur in currency:
            text += f' {cur.currency} '
    else:
        text = 'У вас нет отслеживаемых валют.\nВы можете их выбрать по команде /addCurrency'
    await message.answer(text=text)


@dp.message_handler(commands='addcurrency')
async def send_search(message: types.Message):
    await message.answer(text="Выберите валюты, которые желаете отслеживать:", reply_markup=inline_kb1)


@dp.callback_query_handler(lambda c: c.data.startswith("btn"))
async def process_callback(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id
    button = callback_query.data
    data = button.split("_")[1]
    if data.isdigit():
        data = int(data)
    answer = await edit_cur_list(list_currency[data], chat_id)
    await bot.answer_callback_query(callback_query.id, text=answer)


@dp.message_handler(commands='addrate')
async def add_rate_to_currency(message: types.Message):
    all_currency = await search_currency(message.chat.id)
    if not all_currency:
        await message.answer(text="У вас нет отслеживаемых валют.\nВы можете их выбрать по команде /addCurrency")
    else:
        all_list = [currency.currency for currency in all_currency]
        inline_kb2 = InlineKeyboardMarkup()
        for cur in all_list:
            s = InlineKeyboardButton(f"{cur}", callback_data=f"cur_{cur}")
            inline_kb2.add(s)
        await message.answer(text="Выберите валюту, чтобы добавить к ней курс(за ед.),"
                                  " по которому вы ее купили:", reply_markup=inline_kb2)


@dp.callback_query_handler(lambda c: c.data.startswith("cur"))
async def callback_add_rate(callback_query: types.CallbackQuery):
    button = callback_query.data
    data = button.split("_")[1]
    await process_status_update(callback_query.from_user.id, f'1_{data}')
    await bot.send_message(callback_query.from_user.id, text=f"Укажите курс в долларах(за ед.),"
                                                             f" по которому вы купили {data}")


@dp.message_handler(commands='start')
async def send_search(message: types.Message):
    answer = 'Добро пожаловать!\nВозможности бота:\n' \
             '/addCurrency - добавить/удалить отслеживаемую валюту.\n' \
             '/listCurrency - посмотреть список отслеживаемых валют.\n' \
             '/addRate - добавление к выбранной валюте стоимость(за ед.), по которой вы ее преобрели.\n' \
             'Каждые 60 секунд бот отправляет данные по выбранным валютам.\n\n'
    text = await find_chat_id(message.chat.id)
    await message.answer(text=answer + text)


@dp.message_handler()
async def echo(message: types.Message):
    data = await find_user_status(message.chat.id)
    status, currency = data.split("_")
    if status == "1":
        if message.text.isdigit() or is_number(message.text):
            await process_rate_update(message.chat.id, currency, message.text)
            text = "Данные сохранены..."
            await process_status_update(message.chat.id, '0_null')
        else:
            text = 'Данные введены неверно. Если вы указываете дробное число, попробуйте разделять его точкой(".")'
    else:
        text = message.text

    await message.answer(text=text)


def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


async def scheduled(wait_for, parser):
    while True:
        await parser.parse()
        await asyncio.sleep(wait_for)


if __name__ == "__main__":
    parser = CryptoParse(url=URL, bot=bot)
    loop = asyncio.get_event_loop()
    loop.create_task(scheduled(60, parser))
    executor.start_polling(dp, skip_updates=True)
