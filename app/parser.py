import os
import requests
import re

import pandas as pd
from dotenv import load_dotenv
from lxml import html

from db import save_to_db, parse_prices

load_dotenv()

DIR = os.getenv('UPLOAD_DIR')
os.makedirs(DIR, exist_ok=True)


def file_parser(bot, message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    file_path = os.path.join(DIR, message.document.file_name)
    with open(file_path, 'wb') as f:
        f.write(downloaded_file)

    df = pd.read_excel(file_path)

    response = "📄 Содержимое файла:\n\n"
    for i, row in df.iterrows():
        response += f"📦 <b>{row['title']}</b>\n"
        response += f"🔗 <a href=\"{row['url']}\">{row['url']}</a>\n"
        response += f"📍 XPath: <code>{row['xpath']}</code>\n\n"

    save_to_db(df)

    return response


def price_parser():
    try:
        df = parse_prices()
        response = "💰 Средние цены:\n\n"

        for i, row in df.iterrows():
            title, url, xpath = row["title"], row["url"], row["xpath"]

            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                  "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                }
                r = requests.get(url, timeout=5, headers=headers)

                tree = html.fromstring(r.content)
                price_raw = tree.xpath(xpath)

                if not price_raw:
                    raise ValueError("Элемент не найден по XPath")

                price_text = price_raw[0].text_content().strip()
                print(price_text)
                price = float(re.sub(r"[^\d.]", "", price_text.replace(",", ".")))

                response += f"📦 <b>{title}</b>\n💲 Цена: <code>{price:.2f}</code>\n\n"

            except Exception as e:
                response += f"📦 <b>{title}</b>\n❌ Ошибка: {e}\n\n"

    except Exception as e:
        response = f"❌ Ошибка загрузки БД: {e}"

    return response

    return response