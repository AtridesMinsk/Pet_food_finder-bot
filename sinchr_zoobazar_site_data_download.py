# pip install beautifulsoup4 lxml requests wheel

import os.path
import requests
import random
import shutil

from datetime import datetime
from datetime import timedelta
from bs4 import BeautifulSoup
from time import sleep

shop_url = 'https://zoobazar.by'


def get_current_date():
    """ Определяем текущую дату.
     Determine the current date. """
    cur_date = datetime.now().strftime("%d_%m_%Y")
    return cur_date


def get_current_time():
    """ Определяем текущее время.
     Determine the current time. """
    cur_time = datetime.now().strftime("%H_%M_%S")
    return cur_time


def delete_old_data():
    """ Удаляет папку с устаревшими данными.
    Deletes the stale data folder. """
    try:
        shutil.rmtree("zoobazar/data")
    except FileNotFoundError:
        pass


def create_dir():
    """ Создаем каталоги для загрузки страниц сайта.
     We create directories for loading site pages. """
    if not os.path.exists("zoobazar/data"):
        os.mkdir("zoobazar/data")
    if not os.path.exists("zoobazar/data/cats"):
        os.mkdir("zoobazar/data/cats")
    if not os.path.exists("zoobazar/data/dogs"):
        os.mkdir("zoobazar/data/dogs")
    if not os.path.exists("zoobazar/data/cats/dry_food"):
        os.mkdir("zoobazar/data/cats/dry_food")
    if not os.path.exists("zoobazar/data/dogs/dry_food"):
        os.mkdir("zoobazar/data/dogs/dry_food")
    if not os.path.exists("zoobazar/data/cats/canned_food"):
        os.mkdir("zoobazar/data/cats/canned_food")
    if not os.path.exists("zoobazar/data/dogs/canned_food"):
        os.mkdir("zoobazar/data/dogs/canned_food")
    if not os.path.exists("zoobazar/data/cats/napolniteli"):
        os.mkdir("zoobazar/data/cats/napolniteli")


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


def get_url(pet, chapter):
    """ Получаем ссылку на страницы каталогов товаров.
     We get a link to the product catalog pages. """
    start_url = shop_url

    r = requests.get(start_url)
    soup = BeautifulSoup(r.text, 'html.parser')

    pets_url = []
    pets_url_description = []

    for i in soup.find("div", class_="main-menu").findAll('a', href=True):
        link = start_url + str(i.get('href'))
        pets_url.append(link)
        link_text = i.text
        pets_url_description.append(link_text)

    index_pets_url = pets_url_description.index(pet)

    pets_url, pets_url_description = pets_url[index_pets_url], pets_url_description[index_pets_url]

    r = requests.get(pets_url)
    soup = BeautifulSoup(r.text, 'html.parser')

    chapters_urls = []
    chapters_urls_description = []

    for i in soup.findAll("div", class_="sections-child__item"):
        link = start_url + i.find('a', href=True).attrs['href']
        chapters_urls.append(link)
        link_text = i.text.strip()
        chapters_urls_description.append(link_text)

    index_cr_url = chapters_urls_description.index(chapter)
    chapters_urls, chapters_urls_description = chapters_urls[index_cr_url], chapters_urls_description[index_cr_url]

    url = chapters_urls
    return [index_pets_url, index_cr_url, url]


def get_pages_count(headers, url):
    """ Подсчитываем сколько страниц с товарами в категориях.
    We count how many pages with products in categories. """
    try:
        r = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        count = str(soup.find("pagination"))
        pages_count = str.replace(count, "<pagination :current-page=\"1\" :nav-num=\"2\" :", "")
        pages_count = pages_count.split(":")[0]
        pages_count = str.replace(pages_count, 'page-count="', '')
        pages_count = int(str.replace(pages_count, '"', ''))
    except AttributeError as error:
        print(error)
        pages_count = 1
    return pages_count


def get_pages(headers, url, pages_count, category, product, start_dir):
    """ Загружаем страницы с товарами из каталога.
    We load pages with criminals from the catalog. """
    if category == 'Для кошек' and product == 'Сухие корма':
        os.chdir(f"{start_dir}""/zoobazar/data/cats/dry_food")
    if category == 'Для кошек' and product == 'Наполнители':
        os.chdir(f"{start_dir}""/zoobazar/data/cats/napolniteli")
    if category == 'Для кошек' and product == 'Консервы':
        os.chdir(f"{start_dir}""/zoobazar/data/cats/canned_food")
    if category == 'Для собак' and product == 'Сухой корм':
        os.chdir(f"{start_dir}""/zoobazar/data/dogs/dry_food")
    if category == 'Для собак' and product == 'Консервы':
        os.chdir(f"{start_dir}""/zoobazar/data/dogs/canned_food")

    workdir = str(os.getcwd())

    for i in range(1, pages_count + 1):
        download_url = f"{url},&PAGEN_2={i}"
        print(f"[INFO] Page loading, {i}/{pages_count}, {download_url}")

        r = requests.get(url=download_url, headers=headers)

        with open(f"{workdir}/page_{i}.html", "w", encoding="utf-8") as file:
            file.write(r.text)

        # sleep_time = random.randint(1, 3)
        # sleep(sleep_time)


def get_site_data(headers, shop_category, shop_product, starting_dir):
    url = get_url(shop_category, shop_product)
    link_url = url[2]
    pages_count = get_pages_count(headers, link_url)
    print("Найдено", pages_count, "страниц из:", shop_product, shop_category)
    get_pages(headers, link_url, pages_count, shop_category, shop_product, starting_dir)
    print("*" * 20, shop_product, shop_category, "*" * 20)


def main():
    delete_old_data()
    create_dir()
    headers = get_headers()
    starting_dir = str(os.getcwd())

    shop_category = 'Кошки'
    shop_product = 'Сухие корма'

    get_site_data(headers, shop_category, shop_product, starting_dir)

    shop_category = 'Кошки'
    shop_product = 'Влажные корма'

    get_site_data(headers, shop_category, shop_product, starting_dir)

    shop_category = 'Кошки'
    shop_product = 'Наполнители'

    get_site_data(headers, shop_category, shop_product, starting_dir)

    shop_category = 'Собаки'
    shop_product = 'Сухие корма'

    get_site_data(headers, shop_category, shop_product, starting_dir)

    shop_category = 'Собаки'
    shop_product = 'Влажные корма'

    get_site_data(headers, shop_category, shop_product, starting_dir)


if __name__ == '__main__':
    start_job_time = int(datetime.now().strftime("%H_%M_%S"))

    main()

    stop_job_time = int(datetime.now().strftime("%H_%M_%S"))
    working_time = stop_job_time - start_job_time
    print("Затрачено времени:", str(timedelta(seconds=working_time)))
