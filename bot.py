# pip install aiogram apscheduler

import json
import random
import time

import garfild_correct_data
import garfild_site_data_download
import gavrik_correct_data
import gavrik_site_data_download
import ezoo_correct_data
import ezoo_site_data_download
import zoobazar_site_data_download
import zoobazar_correct_data
import os

from time import sleep
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hbold, hlink
from apscheduler.schedulers.asyncio import AsyncIOScheduler


def get_bot_token():
    try:
        from bot_token import token2 as token
        print("Bot token local find!")
    except ModuleNotFoundError:
        token = os.environ.get('TOKEN_KEY')
        print("Bot token local not find!", "\n", "Get token from Heroku vars")

    print("\n", "Enjoy!")
    return token


bot = Bot(token=get_bot_token(), parse_mode=types.ParseMode.HTML)
scheduler = AsyncIOScheduler()
starting_dir = str(os.getcwd())
dp = Dispatcher(bot)
start_date = datetime.now().strftime("%d.%m.%Y")
start_time = datetime.now().strftime("%H:%M:%S")

print("Бот запущен!", start_date, start_time)


@dp.message_handler(commands='update_data')
async def data_update(message: types.Message):

    start_job_time = time.perf_counter()

    await garfild_site_data_download.main()
    os.chdir(starting_dir)
    await gavrik_site_data_download.main()
    os.chdir(starting_dir)
    await ezoo_site_data_download.main()
    os.chdir(starting_dir)
    await zoobazar_site_data_download.main()
    os.chdir(starting_dir)

    stop_job_time = time.perf_counter()

    working_time = stop_job_time - start_job_time
    print("Затрачено времени:", str(timedelta(seconds=working_time)))
    os.chdir(starting_dir)
    print(datetime.now())

    working_time_message = f'На обработку затрачено времени: <b>{str(timedelta(seconds=working_time))}</b>'
    try:
        await message.answer(working_time_message, parse_mode='html')
    except AttributeError:
        await bot.send_message(66377435, working_time_message, parse_mode='html')


@dp.message_handler(commands='start')
async def start(message: types.Message):
    start_message = f'Привет, <b>{message.from_user.first_name}</b> Для кого будем искать корм?'
    start_buttons = ['Для Котов', 'Для Собак']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)

    await message.answer(start_message, reply_markup=keyboard, parse_mode='html')


@dp.message_handler(commands='user_info')
async def start(message: types.Message):
    start_message = f'Привет, <b>{message.from_user.first_name}</b>.' '\n' \
                   f'Твой ID: <b>{message.from_user.id}</b>'

    await message.answer(start_message, parse_mode='html')


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
        await start_collect_data(1, 3)

        set_current_date = datetime.now().strftime("%d.%m.%Y")
        set_current_time = datetime.now().strftime("%H:%M:%S")

        data = await get_cards('cats', 'dry_food')
        print(f'{set_current_date}, {set_current_time}, Выдаем результаты поиска сухие корма для кошек, {len(data)}, '
              f'для {message.from_user.first_name}')

        if (len(data)) > 0:
            for index, item in enumerate(data):
                card = f'{hbold("Наименование товара: ")}{hlink(item.get("product_name"), item.get("product_url"))}\n' \
                       f'{hbold("Скидка: ")}{item.get("discount")}%\n' \
                       f'{hbold("Цена: ")}{item.get("product_new_price")} BYN🔥\n' \

                if index % 20 == 0:
                    sleep_time = random.randint(1, 5)
                    sleep(sleep_time)

                await message.answer(card, disable_web_page_preview=True)
        else:
            await message.answer("Упс..., товаров с скидкой не нашли (")
    except FileNotFoundError:
        await message.answer("Попробуй позже, идет обновление информации (")


@dp.message_handler(Text(equals='Сухой корм для собак'))
async def get_data_dogs_dry_food(message: types.Message):
    await message.answer('Please waiting...')

    try:
        await start_collect_data(2, 3)

        set_current_date = datetime.now().strftime("%d.%m.%Y")
        set_current_time = datetime.now().strftime("%H:%M:%S")

        data = await get_cards('dogs', 'dry_food')

        print(f'{set_current_date}, {set_current_time}, Выдаем результаты поиска сухие корма для собак, {len(data)}, '
              f'для {message.from_user.first_name}')
        if (len(data)) > 0:
            for index, item in enumerate(data):
                card = f'{hbold("Наименование товара: ")}{hlink(item.get("product_name"), item.get("product_url"))}\n' \
                       f'{hbold("Скидка: ")}{item.get("discount")}%\n' \
                       f'{hbold("Цена: ")}{item.get("product_new_price")} BYN🔥\n' \

                if index % 20 == 0:
                    sleep_time = random.randint(1, 5)
                    sleep(sleep_time)

                await message.answer(card, disable_web_page_preview=True)
        else:
            await message.answer("Упс..., товаров с скидкой не нашли (")
    except FileNotFoundError:
        await message.answer("Попробуй позже, идет обновление информации (")


@dp.message_handler(Text(equals='Консервы для котов'))
async def get_data_cats_canned_food(message: types.Message):
    await message.answer('Please waiting...')

    try:
        await start_collect_data(1, 4)

        set_current_date = datetime.now().strftime("%d.%m.%Y")
        set_current_time = datetime.now().strftime("%H:%M:%S")

        data = await get_cards('cats', 'canned_food')
        print(f'{set_current_date}, {set_current_time}, Выдаем результаты поиска консервы для кошек, {len(data)}, '
              f'для {message.from_user.first_name}')

        if (len(data)) > 0:
            for index, item in enumerate(data):
                card = f'{hbold("Наименование товара: ")}{hlink(item.get("product_name"), item.get("product_url"))}\n' \
                       f'{hbold("Скидка: ")}{item.get("discount")}%\n' \
                       f'{hbold("Цена: ")}{item.get("product_new_price")} BYN🔥\n' \

                if index % 20 == 0:
                    sleep_time = random.randint(1, 5)
                    sleep(sleep_time)

                await message.answer(card, disable_web_page_preview=True)
        else:
            await message.answer("Упс..., товаров с скидкой не нашли (")
    except FileNotFoundError:
        await message.answer("Попробуй позже, идет обновление информации (")


@dp.message_handler(Text(equals='Консервы для собак'))
async def get_data_cats_canned_food(message: types.Message):
    await message.answer('Please waiting...')

    try:
        await start_collect_data(2, 4)

        set_current_date = datetime.now().strftime("%d.%m.%Y")
        set_current_time = datetime.now().strftime("%H:%M:%S")

        data = await get_cards('dogs', 'canned_food')
        print(f'{set_current_date}, {set_current_time}, Выдаем результаты поиска консервы для собак, {len(data)}, '
              f'для {message.from_user.first_name}')

        if (len(data)) > 0:
            for index, item in enumerate(data):
                card = f'{hbold("Наименование товара: ")}{hlink(item.get("product_name"), item.get("product_url"))}\n' \
                       f'{hbold("Скидка: ")}{item.get("discount")}%\n' \
                       f'{hbold("Цена: ")}{item.get("product_new_price")} BYN🔥\n' \

                if index % 20 == 0:
                    sleep_time = random.randint(1, 5)
                    sleep(sleep_time)

                await message.answer(card, disable_web_page_preview=True)
        else:
            await message.answer("Упс..., товаров с скидкой не нашли (")
    except FileNotFoundError:
        await message.answer("Попробуй позже, идет обновление информации (")


@dp.message_handler(Text(equals='Наполнители для туалета'))
async def get_data_cats_napolniteli(message: types.Message):
    await message.answer('Please waiting...')

    try:
        await start_collect_data(1, 5)

        set_current_date = datetime.now().strftime("%d.%m.%Y")
        set_current_time = datetime.now().strftime("%H:%M:%S")

        data = await get_cards('cats', 'napolniteli')

        print(f'{set_current_date}, {set_current_time}, Выдаем результаты поиска Наполнители для кошек, {len(data)},'
              f' для {message.from_user.first_name}')
        if (len(data)) > 0:
            for index, item in enumerate(data):
                card = f'{hbold("Наименование товара: ")}{hlink(item.get("product_name"), item.get("product_url"))}\n' \
                       f'{hbold("Скидка: ")}{item.get("discount")}%\n' \
                       f'{hbold("Цена: ")}{item.get("product_new_price")} BYN🔥\n' \

                if index % 20 == 0:
                    sleep_time = random.randint(1, 5)
                    sleep(sleep_time)

                await message.answer(card, disable_web_page_preview=True)
        else:
            await message.answer("Упс..., товаров с скидкой не нашли (")
    except FileNotFoundError:
        await message.answer("Попробуй позже, идет обновление информации (")


async def start_collect_data(pet, category):
    garfild_correct_data.main(pet, category)
    os.chdir(starting_dir)
    gavrik_correct_data.main(pet, category)
    os.chdir(starting_dir)
    ezoo_correct_data.main(pet, category)
    os.chdir(starting_dir)
    zoobazar_correct_data.main(pet, category)
    os.chdir(starting_dir)


async def get_cards(pet, category):
    cur_date = datetime.now().strftime("%d_%m_%Y")

    with open(f"{starting_dir}/garfild/data/{pet}/{category}/discount_{cur_date}.json") as file1, \
            open(f"{starting_dir}/gavrik/data/{pet}/{category}//discount_{cur_date}.json") as file2, \
            open(f"{starting_dir}/ezoo/data/{pet}/{category}//discount_{cur_date}.json") as file3, \
            open(f"{starting_dir}/zoobazar/data/{pet}/{category}//discount_{cur_date}.json") as file4:
        data_garfild = json.load(file1)
        data_garvik = json.load(file2)
        data_ezoo = json.load(file3)
        data_zoobazar = json.load(file4)
        os.chdir(starting_dir)

    data = data_garfild + data_garvik + data_ezoo + data_zoobazar
    return data


def schedule_jobs():
    """
    Для cron нужно обязательно указывать timezone, а для interval не нужно указание timezone!
    Cron requires a timezone, interval does not need a timezone!
    """
    print("Запускаем расписание на старт обновления данных с сайта каждый день c 08:00, 13:00, 22:00 UTC+3")

    scheduler.add_job(data_update, 'date', run_date=datetime.now(), timezone="Europe/Minsk", args=(dp,))
    scheduler.add_job(data_update, 'cron', day_of_week='0-6', hour=8, minute=00, timezone="Europe/Minsk", args=(dp,))
    scheduler.add_job(data_update, 'cron', day_of_week='0-6', hour=13, minute=00, timezone="Europe/Minsk", args=(dp,))
    scheduler.add_job(data_update, 'cron', day_of_week='0-6', hour=20, minute=00, timezone="Europe/Minsk", args=(dp,))


def main():
    schedule_jobs()
    scheduler.start()
    executor.start_polling(dp)


if __name__ == '__main__':
    main()
