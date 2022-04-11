# pip install beautifulsoup4 lxml requests wheel

import csv
import json
import os.path
import re
import fnmatch

from bs4 import BeautifulSoup
from datetime import datetime

shop_url = 'https://e-zoo.by'


def get_current_date():
    """ Определяем текущую дату.
     Determine the current date. """
    cur_date = datetime.now().strftime("%d_%m_%Y")
    return cur_date


def get_work_patch(category, product, start_dir):
    """ Загружаем страницы с товарами из каталога.
    We load pages with criminals from the catalog. """
    if category == 1 and product == 3:
        os.chdir(f"{start_dir}""/ezoo/data/cats/dry_food")
    if category == 1 and product == 4:
        os.chdir(f"{start_dir}""/ezoo/data/cats/canned_food")
    if category == 1 and product == 5:
        os.chdir(f"{start_dir}""/ezoo/data/cats/napolniteli")
    if category == 2 and product == 3:
        os.chdir(f"{start_dir}""/ezoo/data/dogs/dry_food")
    if category == 2 and product == 4:
        os.chdir(f"{start_dir}""/ezoo/data/dogs/canned_food")

    work_path = str(os.getcwd())
    return work_path


def get_pages_count(work_path):
    """ Подсчитываем сколько страниц с товарами в категориях.
    We count how many pages with products in categories. """
    pages_count = len(fnmatch.filter(os.listdir(work_path), '*.html'))
    return pages_count


def create_csv_file(cur_date):
    with open(f"data_{cur_date}.csv", "w", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                "Наименование товара",
                "Описание товара",
                "Упаковка",
                "Цена",
                "Размер скидки",
                "Ссылка"
            )
        )


def get_product_name(item):
    product_name = item.find("div", class_="cart__title h3").find("span").text.strip()
    return product_name


def get_product_article(item):
    product_article = item.find("p", class_="product-item-preview-text").text.strip()
    return product_article


def get_product_pack(item):
    try:
        product_pack = item.find("p", class_="product-item-list-proposal__pack").text.strip()
    except AttributeError:
        product_pack = 0
    return product_pack


def get_new_price(item):
    try:
        product_new_price = item.find("div", class_="cart__price-field-content").contents[1]
        product_new_price = re.sub("<span class=\"cart__price\">", "", product_new_price)
        product_new_price = re.sub(" руб</span>", "", product_new_price)
        product_new_price = float(product_new_price)
    except AttributeError:
        product_new_price = 0
    except ValueError:
        product_new_price = 0
    return product_new_price


def get_old_price(item):
    try:
        product_old_price = item.find("div", class_="cart__price-field-content").contents[3]
        product_old_price = re.sub("<span class=\"cart__old-price\">", "", product_old_price)
        product_old_price = re.sub(" руб</span>", "", product_old_price)
        product_old_price = float(product_old_price)
    except IndexError:
        product_old_price = 0
    return product_old_price


def get_disabled(item):
    try:
        product_disabled = item.find("span", class_="stiker stiker_netu").text
    except AttributeError:
        product_disabled = 0
    return product_disabled


def count_discount(product_new_price, product_old_price):
    try:
        discount = round(100 - (product_new_price * 100) / product_old_price)
    except ZeroDivisionError:
        discount = 0
    return discount


def get_product_url(item):
    product_url = f'{item.find("div", class_="cart__title h3").find("a", href=True).attrs["href"]}'
    return product_url


def collect_data(pages_count, work_dir, cur_date):
    data = []

    for page in range(1, pages_count + 1):
        with open(f"{work_dir}/page_{page}.html", "r") as file:
            src = file.read()

        soup = BeautifulSoup(src, "html.parser")
        items_cards = soup.find_all("div", class_="catalog__item js-catalog-item")

        for item in items_cards:
            product_name = get_product_name(item)
            # product_article = get_product_article(item)
            # product_pack = get_product_pack(item)
            product_new_price = get_new_price(item)
            product_old_price = get_old_price(item)
            discount = count_discount(product_new_price, product_old_price)
            product_url = get_product_url(item)
            # product_disabled = get_disabled(item)

            data.append(
                {"product_name": product_name,
                 # "product_article": product_article,
                 # "product_pack": product_pack,
                 "product_new_price": product_new_price,
                 "product_old_price": product_old_price,
                 "discount": discount,
                 # "disabled": product_disabled,
                 "product_url": product_url
                 }
            )

            with open(f"{work_dir}/data_{cur_date}.csv", "a", encoding="utf8", newline=None) as file:
                writer = csv.writer(file)

                writer.writerow(
                    (
                        product_name,
                        # product_article,
                        # product_pack,
                        product_new_price,
                        product_old_price,
                        discount,
                        product_url
                    )
                )

        print(f"[INFO] Обрабатываем страницу {page}/{pages_count}")
    with open(f"{work_dir}/data_{cur_date}.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def get_discount(cur_date, work_dir):
    discount_data = []

    with open(f"{work_dir}/data_{cur_date}.json", "r", encoding="utf-8") as file:
        items = json.load(file)

        for i in items:
            if 25 < i.get('discount') < 90 and i.get('disabled') != 0:
                product_name = i.get('product_name')
                # product_article = i.get('product_article')
                product_new_price = i.get('product_new_price')
                discount = i.get('discount')
                product_url = i.get('product_url')

                discount_data.append(
                    {"product_name": product_name,
                     # "product_article": product_article,
                     "product_new_price": product_new_price,
                     "discount": discount,
                     "product_url": product_url
                     }
                )
    print('Всего найдено товаров со скидкой', len(discount_data))

    with open(f"{work_dir}/discount_{cur_date}.json", "w", encoding="utf-8") as file:
        json.dump(discount_data, file, indent=4, ensure_ascii=False)


def main(shop_category, shop_product):
    starting_dir = str(os.getcwd())

    working_dir = get_work_patch(shop_category, shop_product, starting_dir)

    pages_count = get_pages_count(working_dir)
    print("[INFO] ""Найдено страниц для обработки:", pages_count, "\n" "--------")
    create_csv_file(get_current_date())
    collect_data(pages_count, working_dir, get_current_date())
    get_discount(get_current_date(), working_dir)


if __name__ == '__main__':
    main(1, 3)
