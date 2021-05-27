import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL, echo=True)
meta = MetaData()

people = Table(
    'Users',
    meta,
    Column('chatid', Integer(), nullable=False),
    Column('currency', String(), nullable=False),
    Column('price', String())
)

user_status = Table(
    "UserStatus",
    meta,
    Column('chatid', Integer(), nullable=False),
    Column('status', String())
)

meta.create_all(engine)
conn = engine.connect()


async def find_chat_id(chat_id):
    user = user_status.select().where(user_status.c.chatid == chat_id)
    result = conn.execute(user)
    false_list = []
    if result.all() == false_list:
        add = user_status.insert().values(chatid=chat_id, status="0_null")
        conn.execute(add)
        text = "Ваш id сохранен"
    else:
        text = "Ваш id уже сохранен"
    return text


async def process_status_update(chat_id, status):
    status_exist = True
    update = user_status.update().where(user_status.c.chatid == chat_id).values(status=status)
    conn.execute(update)
    return status_exist


async def process_rate_update(chat_id, currency, rate):
    status_exist = True
    update = people.update().where(people.c.chatid == chat_id, people.c.currency == currency).values(price=rate)
    conn.execute(update)
    return status_exist


async def find_user_status(chat_id):
    command = user_status.select().where(user_status.c.chatid == chat_id)
    result = conn.execute(command)
    done_data = result.all()
    return done_data[0].status


async def id_for_parser():
    com = user_status.select()
    result = conn.execute(com)
    list_id = []
    for i in result.all():
        list_id.append(i.chatid)
    return list_id


async def edit_cur_list(data, chat_id):
    search_exist = True

    word = people.select().where(people.c.currency == data, people.c.chatid == chat_id)
    result = conn.execute(word)

    list_result = []
    if result.all() == list_result:
        search_exist = False

    if search_exist:
        del_word = people.delete().where(people.c.currency == data, people.c.chatid == chat_id)
        conn.execute(del_word)
        answer = f"{data} удалена"
    elif not search_exist:
        insrt = people.insert().values(chatid=chat_id, currency=data, price="-1")
        conn.execute(insrt)
        answer = f"{data} добавлена"
    else:
        answer = f"{data} уже есть"

    return answer


async def search_currency(chat_id):
    all_users = people.select().where(people.c.chatid == chat_id)
    result = conn.execute(all_users)

    return result.all()
