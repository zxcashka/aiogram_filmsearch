from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InputMedia, InlineKeyboardMarkup, CallbackQuery
from kinopoisk_api import Api
import sqlite3
import datetime
import middlewares


con = sqlite3.connect("database/users.db")
cur = con.cursor()
# PROXY_URL = 'http://proxy.server:3128'

API_TOKEN = '6035467232:AAElF9cyxhsJXH2w8pfBaYUJhPNki5RGr1I'
bot = Bot(token=API_TOKEN)  # proxy=PROXY_URL
dp = Dispatcher(bot)


def caption(cor):
    return '\n'.join([f'Название: {cor[0]}',
                      f'Год выпуска: {cor[1]}',
                      f'Рейтинг: {cor[2]}',
                      # f'Жанры: {", ".join(search[integer].genres)}',
                      # f'Страны: {", ".join(search[integer].countries)}',
                      f'Длительность: {cor[3]}'])


def message_details(search, info, integer, param):
    id = info[integer]['id']
    if param == 'id':
        return id
    if param == 'photo':
        return search.get_pic300x(id)
    if param == 'info':
        return info[integer]['name'], info[integer]['year'], \
               info[integer]['rate'], info[integer]['duration']


def keytrone(id, param):
    button_1 = types.InlineKeyboardButton("Дальше >>", callback_data="+1")
    button_2 = types.InlineKeyboardButton("<< Назад", callback_data="-1")
    button_3 = types.InlineKeyboardButton("Смотреть", url=f'https://www.sspoisk.ru/film/{id}/')
    keyboard = InlineKeyboardMarkup()
    if param == '1':
        keyboard.add(button_1)
        keyboard.add(button_2)
        keyboard.add(button_3)
        return keyboard
    if param == '2':
        keyboard.add(button_1)
        keyboard.add(button_3)
        return keyboard
    if param == '3':
        keyboard.add(button_2)
        keyboard.add(button_3)
        return keyboard


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    global con, cur

    i = cur.execute(f'select id from users_bot').fetchall()
    me_id = int(i[-1][0]) + 1
    your_name = message.from_user.username
    your_id = message.from_user.id

    f = True
    for j in range(1, len(i) + 1):
        k = cur.execute(f'select name from users_bot where id={j}').fetchall()
        if your_name == k[0][0]:
            f = False
            break
    if f:
        cur.execute(f'''INSERT INTO 
                            users_bot (id, user_id, name)
                        VALUES 
                            ({me_id}, '{your_id}', '{your_name}');''')
        con.commit()

    await message.answer(f'👋  Привет! Меня зовут Film Search.'
                         f'\n\n🔎  С моей помощью ты можешь искать интересующие тебя фильмы и сериалы,'
                         f' смотреть их совершенно бесплатно.\n\n'
                         f'❗ Как пользоваться? Просто напиши мне название'
                         f', а дальше поработаю я!')


@dp.message_handler(commands=['commerce'])
async def send_welcome(message: types.Message):
    await message.answer(f'Напиши мне в личные сообщения: @deadcurseed')


@dp.message_handler()
async def test_key(message: types.Message):

    integer = 0

    try:
        search = Api(message.text)
        info = search.get_info()

        bot_message = await bot.send_photo(chat_id=message.chat.id, photo=message_details(search, info, integer, 'photo'),
                                           caption=f'По вашему запросу я нашел {len(info)} '
                                           f'фильмов/сериалов.'
                                           f'\nСтраница: {integer + 1}'
                                           f'\n\n{caption(message_details(search, info, integer, "info"))}',
                                           reply_markup=keytrone(message_details(search, info, integer, 'id'), '2'))
        print(str(info))
        cur.execute(f'''INSERT INTO 
                            message_info (message_id, integer, message, who, date_time)
                        VALUES 
                            ({bot_message.message_id}, 0, '{message.text}', '{message.from_user.username}', 
                            '{datetime.datetime.now()}');''')
        con.commit()
        cur.execute(f'''INSERT INTO 
                                    dictionary (message_id, dict)
                                VALUES 
                                    ({bot_message.message_id}, "{str(info)}");''')
        con.commit()
    except IndexError:

        cur.execute(f'''INSERT INTO 
                            raskumar (mes_id, message, who, data_time)
                        VALUES 
                            ({message.message_id}, '{message.text}', '{message.from_user.username}', 
                            '{datetime.datetime.now()}');''')
        con.commit()

        await message.answer(f'Я не смог ничего найти :(')


@dp.callback_query_handler(text='+1')
async def plus(query: CallbackQuery):

    integer = (cur.execute(f'select integer from message'
                           f'_info where message_id={query.message.message_id}').fetchall())[0][0]
    txt = (cur.execute(f'select message from message'
                       f'_info where message_id={query.message.message_id}').fetchall())[0][0]
    search = Api(txt)
    info = dict((cur.execute(f'select dict from dictionary '
                        f'where message_id={query.message.message_id}').fetchall())[0][0])

    if integer + 1 < len(info) - 1:
        integer += 1
        cur.execute(f"""UPDATE message_info
                              SET integer = {integer}
                              WHERE message_id == {query.message.message_id}""")
        con.commit()

        filr = InputMedia(media=message_details(search, info, integer, 'photo'),
                          caption=f'По вашему запросу я нашел {len(info)} '
                          f'фильмов/сериалов.'
                          f'\nСтраница: {integer + 1}'
                          f'\n\n{caption(message_details(search, info, integer, "info"))}')

        await query.message.edit_media(filr, reply_markup=keytrone(message_details(search, info, integer, 'id'), '1'))
    else:
        if integer + 1 == len(search.get_info()) - 1:
            integer += 1
            cur.execute(f"""UPDATE message_info
                                          SET integer = {integer}
                                          WHERE message_id == {query.message.message_id}""")
            con.commit()

        filr = InputMedia(media=message_details(search, integer, 'photo'),
                          caption=f'По вашему запросу я нашел {len(search.get_info())} '
                          f'фильмов/сериалов.'
                          f'\nСтраница: {integer + 1}'
                          f'\n\n{caption(message_details(search, integer, "info"))}')

        await query.message.edit_media(filr, reply_markup=keytrone(message_details(search, integer, 'id'), '3'))


@dp.callback_query_handler(text='-1')
async def minus(query: CallbackQuery):

    integer = (cur.execute(f'select integer from message'
                           f'_info where message_id={query.message.message_id}').fetchall())[0][0]
    txt = (cur.execute(f'select message from message'
                       f'_info where message_id={query.message.message_id}').fetchall())[0][0]

    search = Api(txt)

    if integer > 1:
        integer -= 1
        cur.execute(f"""UPDATE message_info
                                      SET integer = {integer}
                                      WHERE message_id == {query.message.message_id}""")
        con.commit()

        filr = InputMedia(media=message_details(search, integer, 'photo'),
                          caption=f'По вашему запросу я нашел {len(search.get_info())} '
                          f'фильмов/сериалов.'
                          f'\nСтраница: {integer + 1}'
                          f'\n\n{caption(message_details(search, integer, "info"))}')

        await query.message.edit_media(filr, reply_markup=keytrone(message_details(search, integer, 'id'), '1'))
    else:
        if integer == 1:
            integer -= 1
            cur.execute(f"""UPDATE message_info
                                          SET integer = {integer}
                                          WHERE message_id == {query.message.message_id}""")
            con.commit()

        filr = InputMedia(media=message_details(search, integer, 'photo'),
                          caption=f'По вашему запросу я нашел {len(search.get_info())} '
                          f'фильмов/сериалов.'
                          f'\nСтраница: {integer + 1}'
                          f'\n\n{caption(message_details(search, integer, "info"))}')

        await query.message.edit_media(filr, reply_markup=keytrone(message_details(search, integer, 'id'), '2'))


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("commerce", "По коммерческим вопросам"),
    ])

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=set_default_commands, skip_updates=False)
