# pip install aiogram apscheduler

import json
import random
import garfild_v2_correct_data
import garfild_v2_site_data_download
import gavrik_v2_correct_data
import gavrik_v2_site_data_download
import ezoo_v2_correct_data
import ezoo_v2_site_data_download
import os

from time import sleep
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hbold, hlink
from apscheduler.schedulers.asyncio import AsyncIOScheduler


def get_bot_token():
    try:
        from bot_token import token2 as token
        b_token = token
        print("Bot token local find!")
    except ModuleNotFoundError:
        print("Bot token local not find!", "\n", "Get token from Heroku vars")
        b_token = os.environ.get('TOKEN_KEY')

    print("\n", "Enjoy!")
    return b_token


bot = Bot(token=get_bot_token(), parse_mode=types.ParseMode.HTML)
scheduler = AsyncIOScheduler()
starting_dir = str(os.getcwd())
dp = Dispatcher(bot)
start_date = datetime.now().strftime("%d.%m.%Y")
start_time = datetime.now().strftime("%H:%M:%S")

print("Бот запущен!", start_date, start_time)


@dp.message_handler(commands='update_data')
async def data_update(commands="update_data"):

    garfild_v2_site_data_download.main()
    os.chdir(starting_dir)
    gavrik_v2_site_data_download.main()
    os.chdir(starting_dir)
    ezoo_v2_site_data_download.main()
    os.chdir(starting_dir)


@dp.message_handler(commands='start')
async def start(message: types.Message):
    start_messge = f'Привет, <b>{message.from_user.first_name}</b> Для кого будем искать корм?'
    start_buttons = ['Для Котов', 'Для Собак']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)

    await message.answer(start_messge, reply_markup=keyboard, parse_mode='html')


@dp.message_handler(commands='user_info')
async def start(message: types.Message):
    start_messge = f'{message}'

    await message.answer(start_messge, parse_mode='html')


@dp.message_handler(Text(equals='Для Котов'))
async def get_data_cat(message: types.Message):
    start_buttons = ['Сухой корм для котов', 'Консервы для котов', 'Наполнители для туалета', 'Выбрать питомца']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)

    await message.answer('Чем будем кормить вашего Котика?', reply_markup=keyboard)


@dp.message_handler(Text(equals='Для Собак'))
async def get_data_dog(message: types.Message):
    start_buttons = ['Сухой корм для собак', 'Консервы для собак', 'Выбрать питомца']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)

    await message.answer('Чем будем кормить вашего Песика?', reply_markup=keyboard)


@dp.message_handler(Text(equals='Выбрать питомца'))
async def get_data_start(message: types.Message):
    start_buttons = ['Для Котов', 'Для Собак']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)

    await message.answer('Для кого будем искать корм?', reply_markup=keyboard)


@dp.message_handler(Text(equals='Сухой корм для котов'))
async def get_data_cats_dry_food(message: types.Message):
    await message.answer('Please waiting...')

    try:
        garfild_v2_correct_data.main(1, 3)
        os.chdir(starting_dir)
        gavrik_v2_correct_data.main(1, 3)
        os.chdir(starting_dir)
        ezoo_v2_correct_data.main(1, 3)
        os.chdir(starting_dir)

        set_current_date = datetime.now().strftime("%d.%m.%Y")
        set_current_time = datetime.now().strftime("%H:%M:%S")
        cur_date = datetime.now().strftime("%d_%m_%Y")

        with open(f"{starting_dir}/garfild/data/cats/dry_food/discount_{cur_date}.json") as file1, \
                open(f"{starting_dir}/gavrik/data/cats/dry_food/discount_{cur_date}.json") as file2, \
                open(f"{starting_dir}/ezoo/data/cats/dry_food/discount_{cur_date}.json") as file3:
            data_garfild = json.load(file1)
            data_garvik = json.load(file2)
            data_ezoo = json.load(file3)
            os.chdir(starting_dir)

        data = data_garfild + data_garvik + data_ezoo
        print(set_current_date, set_current_time, 'Выдаем результаты поиска сухие корма для кошек', len(data))

        if (len(data)) > 0:
            for index, item in enumerate(data):
                card = f'{hbold("Наименование товара: ")}{hlink(item.get("product_name"), item.get("product_url"))}\n' \
                       f'{hbold("Скидка: ")}{item.get("discount")}%\n' \
                       f'{hbold("Цена: ")}{item.get("product_new_price")} BYN🔥\n' \

                if index % 20 == 0:
                    sleeptime = random.randint(1, 5)
                    sleep(sleeptime)

                await message.answer(card, disable_web_page_preview=True)
        else:
            await message.answer("Упс..., товаров с скидкой не нашли (")
    except FileNotFoundError:
        await message.answer("Попробуй позже, идет обновление информации (")


@dp.message_handler(Text(equals='Сухой корм для собак'))
async def get_data_dogs_dry_food(message: types.Message):
    await message.answer('Please waiting...')

    try:
        garfild_v2_correct_data.main(2, 3)
        os.chdir(starting_dir)
        gavrik_v2_correct_data.main(2, 3)
        os.chdir(starting_dir)
        ezoo_v2_correct_data.main(2, 3)
        os.chdir(starting_dir)

        set_current_date = datetime.now().strftime("%d.%m.%Y")
        set_current_time = datetime.now().strftime("%H:%M:%S")
        cur_date = datetime.now().strftime("%d_%m_%Y")

        with open(f"{starting_dir}/garfild/data/dogs/dry_food/discount_{cur_date}.json") as file1, \
                open(f"{starting_dir}/gavrik/data/dogs/dry_food/discount_{cur_date}.json") as file2, \
                open(f"{starting_dir}/ezoo/data/dogs/dry_food/discount_{cur_date}.json") as file3:
            data_garfild = json.load(file1)
            data_garvik = json.load(file2)
            data_ezoo = json.load(file3)
            os.chdir(starting_dir)

        data = data_garfild + data_garvik + data_ezoo
        print(set_current_date, set_current_time, 'Выдаем результаты поиска сухие корма для собак', len(data))
        if (len(data)) > 0:
            for index, item in enumerate(data):
                card = f'{hbold("Наименование товара: ")}{hlink(item.get("product_name"), item.get("product_url"))}\n' \
                       f'{hbold("Скидка: ")}{item.get("discount")}%\n' \
                       f'{hbold("Цена: ")}{item.get("product_new_price")} BYN🔥\n' \

                if index % 20 == 0:
                    sleeptime = random.randint(1, 5)
                    sleep(sleeptime)

                await message.answer(card, disable_web_page_preview=True)
        else:
            await message.answer("Упс..., товаров с скидкой не нашли (")
    except FileNotFoundError:
        await message.answer("Попробуй позже, идет обновление информации (")


@dp.message_handler(Text(equals='Консервы для котов'))
async def get_data_cats_canned_food(message: types.Message):
    await message.answer('Please waiting...')

    try:
        garfild_v2_correct_data.main(1, 4)
        os.chdir(starting_dir)
        gavrik_v2_correct_data.main(1, 4)
        os.chdir(starting_dir)
        ezoo_v2_correct_data.main(1, 4)
        os.chdir(starting_dir)

        set_current_date = datetime.now().strftime("%d.%m.%Y")
        set_current_time = datetime.now().strftime("%H:%M:%S")
        cur_date = datetime.now().strftime("%d_%m_%Y")

        with open(f"{starting_dir}/garfild/data/cats/canned_food/discount_{cur_date}.json") as file1, \
                open(f"{starting_dir}/gavrik/data/cats/canned_food/discount_{cur_date}.json") as file2, \
                open(f"{starting_dir}/ezoo/data/cats/canned_food/discount_{cur_date}.json") as file3:
            data_garfild = json.load(file1)
            data_garvik = json.load(file2)
            data_ezoo = json.load(file3)
            os.chdir(starting_dir)

        data = data_garfild + data_garvik + data_ezoo
        print(set_current_date, set_current_time, 'Выдаем результаты поиска консервы для кошек', len(data))

        if (len(data)) > 0:
            for index, item in enumerate(data):
                card = f'{hbold("Наименование товара: ")}{hlink(item.get("product_name"), item.get("product_url"))}\n' \
                       f'{hbold("Скидка: ")}{item.get("discount")}%\n' \
                       f'{hbold("Цена: ")}{item.get("product_new_price")} BYN🔥\n' \

                if index % 20 == 0:
                    sleeptime = random.randint(1, 5)
                    sleep(sleeptime)

                await message.answer(card, disable_web_page_preview=True)
        else:
            await message.answer("Упс..., товаров с скидкой не нашли (")
    except FileNotFoundError:
        await message.answer("Попробуй позже, идет обновление информации (")


@dp.message_handler(Text(equals='Консервы для собак'))
async def get_data_cats_canned_food(message: types.Message):
    await message.answer('Please waiting...')

    try:
        garfild_v2_correct_data.main(2, 4)
        os.chdir(starting_dir)
        gavrik_v2_correct_data.main(2, 4)
        os.chdir(starting_dir)
        ezoo_v2_correct_data.main(2, 4)
        os.chdir(starting_dir)

        set_current_date = datetime.now().strftime("%d.%m.%Y")
        set_current_time = datetime.now().strftime("%H:%M:%S")
        cur_date = datetime.now().strftime("%d_%m_%Y")

        with open(f"{starting_dir}/garfild/data/dogs/canned_food/discount_{cur_date}.json") as file1, \
                open(f"{starting_dir}/gavrik/data/dogs/canned_food/discount_{cur_date}.json") as file2, \
                open(f"{starting_dir}/ezoo/data/dogs/canned_food/discount_{cur_date}.json") as file3:
            data_garfild = json.load(file1)
            data_garvik = json.load(file2)
            data_ezoo = json.load(file3)
            os.chdir(starting_dir)

        data = data_garfild + data_garvik + data_ezoo
        print(set_current_date, set_current_time, 'Выдаем результаты поиска консервы для собак', len(data))
        if (len(data)) > 0:
            for index, item in enumerate(data):
                card = f'{hbold("Наименование товара: ")}{hlink(item.get("product_name"), item.get("product_url"))}\n' \
                       f'{hbold("Скидка: ")}{item.get("discount")}%\n' \
                       f'{hbold("Цена: ")}{item.get("product_new_price")} BYN🔥\n' \

                if index % 20 == 0:
                    sleeptime = random.randint(1, 5)
                    sleep(sleeptime)

                await message.answer(card, disable_web_page_preview=True)
        else:
            await message.answer("Упс..., товаров с скидкой не нашли (")
    except FileNotFoundError:
        await message.answer("Попробуй позже, идет обновление информации (")


@dp.message_handler(Text(equals='Наполнители для туалета'))
async def get_data_cats_napolniteli(message: types.Message):
    await message.answer('Please waiting...')

    try:
        garfild_v2_correct_data.main(1, 5)
        os.chdir(starting_dir)
        gavrik_v2_correct_data.main(1, 5)
        os.chdir(starting_dir)
        ezoo_v2_correct_data.main(1, 5)
        os.chdir(starting_dir)

        set_current_date = datetime.now().strftime("%d.%m.%Y")
        set_current_time = datetime.now().strftime("%H:%M:%S")
        cur_date = datetime.now().strftime("%d_%m_%Y")

        with open(f"{starting_dir}/garfild/data/cats/napolniteli/discount_{cur_date}.json") as file1, \
                open(f"{starting_dir}/gavrik/data/cats/napolniteli/discount_{cur_date}.json") as file2, \
                open(f"{starting_dir}/ezoo/data/cats/napolniteli/discount_{cur_date}.json") as file3:
            data_garfild = json.load(file1)
            data_garvik = json.load(file2)
            data_ezoo = json.load(file3)
            os.chdir(starting_dir)

        data = data_garfild + data_garvik + data_ezoo
        print(set_current_date, set_current_time, 'Выдаем результаты поиска Наполнители для кошек', len(data))
        if (len(data)) > 0:
            for index, item in enumerate(data):
                card = f'{hbold("Наименование товара: ")}{hlink(item.get("product_name"), item.get("product_url"))}\n' \
                       f'{hbold("Скидка: ")}{item.get("discount")}%\n' \
                       f'{hbold("Цена: ")}{item.get("product_new_price")} BYN🔥\n' \

                if index % 20 == 0:
                    sleeptime = random.randint(1, 5)
                    sleep(sleeptime)

                await message.answer(card, disable_web_page_preview=True)
        else:
            await message.answer("Упс..., товаров с скидкой не нашли (")
    except FileNotFoundError:
        await message.answer("Попробуй позже, идет обновление информации (")


def schedule_jobs():
    """
    Для cron нужно обязательно указывать timezone, а для interval не нужно указание timezone!
    Cron requires a timezone, interval does not need a timezone!
    """
    # print("Запускаем расписание на старт обновления данных с сайта каждый день c 1:00 UTC+3")
    print("Запускаем расписание на старт обновления данных с сайта каждый час")

    # scheduler.add_job(data_update, 'cron', day_of_week='0-6', hour=1, minute=00, timezone="Europe/Minsk", args=(dp,))
    scheduler.add_job(data_update, 'interval', hours=1, args=(dp,))


def main():
    schedule_jobs()
    scheduler.start()
    executor.start_polling(dp)


if __name__ == '__main__':
    main()
