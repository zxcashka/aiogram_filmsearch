from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InputMedia, InlineKeyboardMarkup, CallbackQuery
from kinopoisk_api import KP
import sqlite3
import datetime
import middlewares


con = sqlite3.connect("database/users.db")
cur = con.cursor()

# tok = cur.execute(f'select token from tokens').fetchall()
# integer = 1
# dey = datetime.datetime.today().day

PROXY_URL = 'http://proxy.server:3128'

API_TOKEN = '6231406899:AAEQHIzb2hC9Ms6JopVvjmn2D_-0HcwAdPI'
kinopoisk = KP(token='85aa2c68-4303-421c-9b5a-82e3061306db')

button_1 = types.InlineKeyboardButton("Дальше >>", callback_data="+1")
button_2 = types.InlineKeyboardButton("<< Назад", callback_data="-1")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


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
        cur.execute(f'''INSERT INTO users_bot (id)
                              VALUES ({me_id});''')
        con.commit()
        cur.execute(f"""UPDATE users_bot
                              SET user_id = "{your_id}"
                              WHERE id == {me_id}""")
        con.commit()
        cur.execute(f"""UPDATE users_bot
                      SET name = "{your_name}"
                      WHERE id == {me_id}""")
        con.commit()
        cur.execute(f"""UPDATE users_bot
                              SET mesage_count = 0
                              WHERE id == {me_id}""")
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
    global button_1

    integer = 0

    try:
        search = kinopoisk.search(''.join(message.text.split()))
        film_id = search[integer].kp_id
        button_3 = types.InlineKeyboardButton("Смотреть", url=f'https://www.sspoisk.ru/film/{film_id}/')
        keyboard2 = InlineKeyboardMarkup()
        keyboard2.add(button_1)
        keyboard2.add(button_3)
        if search[integer].duration < '01:10':
            search[integer].duration = 'Сериал'
        if search[integer].kp_rate == 'null':
            search[integer].kp_rate = 'Нет рейтинга'
        text = '\n'.join([f'Название: {search[integer].ru_name}',
                             f'Год выпуска: {search[integer].year}',
                             f'Рейтинг: {search[integer].kp_rate}',
                             f'Жанры: {", ".join(search[integer].genres)}',
                             f'Страны: {", ".join(search[integer].countries)}',
                             f'Длительность: {search[integer].duration}'])
        bot_message = await bot.send_photo(chat_id=message.chat.id, photo=search[integer].poster,
                             caption=f'По вашему запросу я нашел {len(search)} фильмов/сериалов.\n\n{text}',
                             reply_markup=keyboard2)

        cur.execute(f'''INSERT INTO message_info (message_id)
                                      VALUES ({bot_message.message_id});''')
        con.commit()
        cur.execute(f"""UPDATE message_info
                                      SET integer = 0
                                      WHERE message_id == {bot_message.message_id}""")
        con.commit()
        cur.execute(f"""UPDATE message_info
                              SET message = "{message.text}"
                              WHERE message_id == {bot_message.message_id}""")
        con.commit()
        cur.execute(f"""UPDATE message_info
                                      SET who = "{message.from_user.username}"
                                      WHERE message_id == {bot_message.message_id}""")
        con.commit()
        cur.execute(f"""UPDATE message_info
                                      SET date_time = "{datetime.datetime.now()}"
                                      WHERE message_id == {bot_message.message_id}""")
        con.commit()
        integer = (cur.execute(f'select mesage_count from users_bot'
                               f' where user_id={message.from_user.id}').fetchall())[0][0]
        integer += 1
        cur.execute(f"""UPDATE users_bot
                                      SET mesage_count = {integer}
                                      WHERE user_id == {message.from_user.id}""")
        con.commit()
        if integer % 3 == 0:
            text = str('''​​​Инструкция для всех новичков❕ 
            Как получить бонус до 25.000₽❔
            
            🇷🇺Легальная Букмекерская контора
            👉  MELBET.RU (https://tracker.partnersmelbet.ru/link?btag=26233898_243233)
            
            Промокод: PODAROK999
            
            Вносим депозит и сумма удваивается (до 25.000 RUB)🎁
            Скачать приложение на ANDROID (https://tracker.partnersmelbet.ru/link?btag=26233898_243233)
            Скачать приложение на iOS (https://tracker.partnersmelbet.ru/link?btag=26233898_243233)''')
            await bot.send_video(chat_id=message.chat.id,
                                 video=open('video/Реклама Melbet pre roll.mp4', 'rb'),
                                 caption=text)
    except IndexError:

        cur.execute(f'''INSERT INTO raskumar (mes_id)
                                              VALUES ({message.message_id});''')
        con.commit()
        cur.execute(f"""UPDATE raskumar
                                      SET message = "{message.text}"
                                      WHERE mes_id == {message.message_id}""")
        con.commit()
        cur.execute(f"""UPDATE raskumar
                                              SET who = "{message.from_user.username}"
                                              WHERE mes_id == {message.message_id}""")
        con.commit()
        cur.execute(f"""UPDATE raskumar
                                              SET data_time = "{datetime.datetime.now()}"
                                              WHERE mes_id == {message.message_id}""")
        con.commit()

        await message.answer(f'Я не смог ничего найти :(')


@dp.callback_query_handler(text='+1')
async def plus(query: CallbackQuery):
    global button_1, button_2

    integer = (cur.execute(f'select integer from message'
                           f'_info where message_id={query.message.message_id}').fetchall())[0][0]
    txt = (cur.execute(f'select message from message'
                           f'_info where message_id={query.message.message_id}').fetchall())[0][0]
    search = kinopoisk.search(''.join(txt.split()))

    if integer + 1 < len(search) - 1:
        integer += 1
        cur.execute(f"""UPDATE message_info
                              SET integer = {integer}
                              WHERE message_id == {query.message.message_id}""")
        con.commit()
        film_id = search[integer].kp_id
        button_3 = types.InlineKeyboardButton("Смотреть", url=f'https://www.sspoisk.ru/film/{film_id}/')
        keyboard = InlineKeyboardMarkup()
        keyboard.add(button_1)
        keyboard.add(button_2)
        keyboard.add(button_3)
        if search[integer].duration < '01:10':
            search[integer].duration = 'Сериал'
        if search[integer].kp_rate == 'null':
            search[integer].kp_rate = 'Нет рейтинга'

        filr = InputMedia(media=search[integer].poster, caption='\n'.join([f'Название: {search[integer].ru_name}',
                             f'Год выпуска: {search[integer].year}',
                             f'Рейтинг: {search[integer].kp_rate}',
                             f'Жанры: {", ".join(search[integer].genres)}',
                             f'Страны: {", ".join(search[integer].countries)}',
                             f'Длительность: {search[integer].duration}']))
        await query.message.edit_media(filr, reply_markup=keyboard)
    else:
        if integer + 1 == len(search) - 1:
            integer += 1
            cur.execute(f"""UPDATE message_info
                                          SET integer = {integer}
                                          WHERE message_id == {query.message.message_id}""")
            con.commit()
        film_id = search[integer].kp_id
        button_3 = types.InlineKeyboardButton("Смотреть", url=f'https://www.sspoisk.ru/film/{film_id}/')
        keyboard3 = InlineKeyboardMarkup()
        keyboard3.add(button_2)
        keyboard3.add(button_3)
        if search[integer].duration < '01:10':
            search[integer].duration = 'Сериал'
        if search[integer].kp_rate == 'null':
            search[integer].kp_rate = 'Нет рейтинга'

        filr = InputMedia(media=search[integer].poster, caption='\n'.join([f'Название: {search[integer].ru_name}',
                                                                           f'Год выпуска: {search[integer].year}',
                                                                           f'Рейтинг: {search[integer].kp_rate}',
                                                                           f'Жанры: {", ".join(search[integer].genres)}',
                                                                           f'Страны: {", ".join(search[integer].countries)}',
                                                                           f'Длительность: {search[integer].duration}']))
        await query.message.edit_media(filr, reply_markup=keyboard3)


@dp.callback_query_handler(text='-1')
async def minus(query: CallbackQuery):
    global button_1, button_2

    integer = (cur.execute(f'select integer from message'
                           f'_info where message_id={query.message.message_id}').fetchall())[0][0]
    txt = (cur.execute(f'select message from message'
                       f'_info where message_id={query.message.message_id}').fetchall())[0][0]
    search = kinopoisk.search(''.join(txt.split()))

    if integer > 1:
        integer -= 1
        cur.execute(f"""UPDATE message_info
                                      SET integer = {integer}
                                      WHERE message_id == {query.message.message_id}""")
        con.commit()
        film_id = search[integer].kp_id
        button_3 = types.InlineKeyboardButton("Смотреть", url=f'https://www.sspoisk.ru/film/{film_id}/')
        keyboard = InlineKeyboardMarkup()
        keyboard.add(button_1)
        keyboard.add(button_2)
        keyboard.add(button_3)
        if search[integer].duration < '01:10':
            search[integer].duration = 'Сериал'
        if search[integer].kp_rate == 'null':
            search[integer].kp_rate = 'Нет рейтинга'
        filr = InputMedia(media=search[integer].poster,
                          caption='\n'.join([f'Название: {search[integer].ru_name}',
                                             f'Год выпуска: {search[integer].year}',
                                             f'Рейтинг: {search[integer].kp_rate}',
                                             f'Жанры: {", ".join(search[integer].genres)}',
                                             f'Страны: {", ".join(search[integer].countries)}',
                                             f'Длительность: {search[integer].duration}']))
        await query.message.edit_media(filr, reply_markup=keyboard)
    else:
        if integer == 1:
            integer -= 1
            cur.execute(f"""UPDATE message_info
                                          SET integer = {integer}
                                          WHERE message_id == {query.message.message_id}""")
            con.commit()
        film_id = search[integer].kp_id
        button_3 = types.InlineKeyboardButton("Смотреть", url=f'https://www.sspoisk.ru/film/{film_id}/')
        keyboard2 = InlineKeyboardMarkup()
        keyboard2.add(button_1)
        keyboard2.add(button_3)
        if search[integer].duration < '01:10':
            search[integer].duration = 'Сериал'
        if search[integer].kp_rate == 'null':
            search[integer].kp_rate = 'Нет рейтинга'
        text = '\n'.join([f'Название: {search[integer].ru_name}',
                             f'Год выпуска: {search[integer].year}',
                             f'Рейтинг: {search[integer].kp_rate}',
                             f'Жанры: {", ".join(search[integer].genres)}',
                             f'Страны: {", ".join(search[integer].countries)}',
                             f'Длительность: {search[integer].duration}',])
        filr = InputMedia(media=search[integer].poster,
                          caption=f'По вашему запросу я нашел {len(search)} фильмов.\n\n{text}')
        await query.message.edit_media(filr, reply_markup=keyboard2)


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("commerce", "По коммерческим вопросам"),
    ])

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=set_default_commands, skip_updates=False)