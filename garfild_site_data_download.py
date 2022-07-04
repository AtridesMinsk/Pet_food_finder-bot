import os.path
import aiohttp
import asyncio
import aiofiles
import shutil
import random

from bs4 import BeautifulSoup
from datetime import timedelta, datetime
from time import sleep

shop_url = 'https://garfield.by/stock.html'


async def delete_old_data():
    """ Удаляет папку с устаревшими данными.
    Deletes the stale data folder. """
    try:
        shutil.rmtree("garfild/data")
    except FileNotFoundError:
        pass


async def create_dir():
    """ Создаем каталоги для загрузки страниц сайта.
     We create directories for loading site pages. """
    if not os.path.exists("garfild/data"):
        os.mkdir("garfild/data")
    if not os.path.exists("garfild/data/cats"):
        os.mkdir("garfild/data/cats")
    if not os.path.exists("garfild/data/dogs"):
        os.mkdir("garfild/data/dogs")
    if not os.path.exists("garfild/data/cats/dry_food"):
        os.mkdir("garfild/data/cats/dry_food")
    if not os.path.exists("garfild/data/dogs/dry_food"):
        os.mkdir("garfild/data/dogs/dry_food")
    if not os.path.exists("garfild/data/cats/canned_food"):
        os.mkdir("garfild/data/cats/canned_food")
    if not os.path.exists("garfild/data/dogs/canned_food"):
        os.mkdir("garfild/data/dogs/canned_food")
    if not os.path.exists("garfild/data/cats/napolniteli"):
        os.mkdir("garfild/data/cats/napolniteli")


def get_headers():
    """ Задаем параметры заголовков для веб запросов.
     Setting header parameters for web requests. """
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                  "*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/96.0.4664.93 Safari/537.36"
    }
    return headers


async def get_url(pet, chapter):

    headers = get_headers()

    async with aiohttp.ClientSession() as session:
        start_url = shop_url

        response = await session.get(url=shop_url, headers=headers, ssl=False)
        soup = BeautifulSoup(await response.text(), 'lxml')

        pets_url = []
        pets_url_description = []

        for i in soup.find("ul", class_="item-selected-list").findAll('a', href=True):
            link = start_url + str(i.get('href'))
            pets_url.append(link)
            link_text = i.text
            pets_url_description.append(link_text)

        index_pets_url = pets_url_description.index(pet)

        pets_url, pets_url_description = pets_url[index_pets_url], pets_url_description[index_pets_url]

        response = await session.get(url=pets_url, headers=headers, ssl=False)
        soup = BeautifulSoup(await response.text(), 'lxml')

        chapters_urls = []
        chapters_urls_description = []

        for i in soup.find("ul", class_="root-item").findAll('a', href=True):
            link = start_url + str(i.get('href'))
            chapters_urls.append(link)
            link_text = i.text
            chapters_urls_description.append(link_text)
            print(link_text)

        try:
            index_cr_url = chapters_urls_description.index(chapter)
        except ValueError:
            index_cr_url = 2

        chapters_urls, chapters_urls_description = chapters_urls[index_cr_url], chapters_urls_description[index_cr_url]

        url = chapters_urls

        return [index_pets_url, index_cr_url, url]


async def get_pages_count(headers, url):
    """ Подсчитываем сколько страниц с товарами в категориях.
    We count how many pages with products in categories. """
    async with aiohttp.ClientSession() as session:
        try:
            response = await session.get(url=url, headers=headers, ssl=False)
            soup = BeautifulSoup(await response.text(), 'lxml')
            pages_count = int(soup.find("div", class_="bx_pagination_page").find_all("a")[-2].text)
        except AttributeError:
            pages_count = 1
    return pages_count


async def get_urls_list(category, pages_count):
    list_urls = []
    for i in range(1, pages_count + 1):
        download_url = f'{category}?PAGEN_1={i}'
        list_urls.append(download_url)
    return list_urls


async def get_site_data(headers, category, product, start_dir, url, url_count):
    async with aiohttp.ClientSession() as session:

        if category == 'Для кошек' and product == 'Сухой корм':
            os.chdir(f"{start_dir}""/garfild/data/cats/dry_food")
        if category == 'Для кошек' and product == 'Наполнители':
            os.chdir(f"{start_dir}""/garfild/data/cats/napolniteli")
        if category == 'Для кошек' and product == 'Консервы':
            os.chdir(f"{start_dir}""/garfild/data/cats/canned_food")
        if category == 'Для собак' and product == 'Сухой корм':
            os.chdir(f"{start_dir}""/garfild/data/dogs/dry_food")
        if category == 'Для собак' and product == 'Консервы':
            os.chdir(f"{start_dir}""/garfild/data/dogs/canned_food")

        workdir = str(os.getcwd())

        print(f"[INFO] Page loading, {url}")
        response = await session.get(url=url, headers=headers, ssl=False)
        async with aiofiles.open(f"{workdir}/page_{url_count}.html", "w", encoding="utf-8") as file:
            await file.write(await response.text())
            await file.close()
        sleep(0.1)
        print("[INFO] Page saved", f"{workdir}/page_{url_count}.html")


async def main():
    await delete_old_data()
    await create_dir()
    headers = get_headers()
    starting_dir = str(os.getcwd())

    shop_category = ['Для кошек', 'Для кошек', 'Для кошек', 'Для собак', 'Для собак']
    shop_product = ['Сухой корм', 'Наполнители', 'Консервы', 'Сухой корм', 'Консервы']

    for category, product in zip(shop_category, shop_product):
        url = await get_url(category, product)
        link_url = url[2]
        pages_count = await get_pages_count(headers, link_url)
        print("Найдено", pages_count, "страниц из:", product, category)
        urls = await get_urls_list(link_url, pages_count)
        urls_counts = [i for i in range(1, len(urls) + 1)]
        tasks = [asyncio.ensure_future(get_site_data(headers, category, product, starting_dir, url, number))
                 for url, number in zip(urls, urls_counts)]
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    start_job_time = int(datetime.now().strftime("%H_%M_%S"))

    asyncio.run(main())

    stop_job_time = int(datetime.now().strftime("%H_%M_%S"))
    working_time = stop_job_time - start_job_time
    print("Затрачено времени:", str(timedelta(seconds=working_time)))
