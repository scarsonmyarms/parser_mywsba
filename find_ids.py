import requests
from bs4 import BeautifulSoup
import time
import csv
import re

BASE_URL = "https://www.mywsba.org/PersonifyEbusiness/LegalDirectory.aspx"
OUTPUT_FILE = "itemtemplate_numbers.csv"


def extract_numbers_from_itemtemplates(soup):
    """Извлекает числа из тегов itemtemplate"""
    numbers = []
    item_templates = soup.find_all('itemtemplate')

    for item in item_templates:
        # Извлекаем текст и ищем числа
        text = item.get_text(strip=True)
        # Ищем все целые числа в тексте
        found_numbers = re.findall(r'\d+', text)
        if found_numbers:
            numbers.extend(found_numbers)

    return numbers


def scrape_page(page_number):
    params = {
        "ShowSearchResults": "TRUE",
        "LicenseType": "Lawyer",
        "EligibleToPractice": "Y",
        "Status": "Active",
        "Page": page_number
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return extract_numbers_from_itemtemplates(soup)

    except Exception as e:
        print(f"Ошибка при обработке страницы {page_number}: {e}")
        return []


def save_numbers(numbers, writer):
    """Сохраняет числа в CSV"""
    for num in numbers:
        writer.writerow([num])


def main():
    total_pages = 2

    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        for page in range(total_pages):
            print(f"Обрабатываю страницу {page + 1} из {total_pages}")
            numbers = scrape_page(page)

            if numbers:
                save_numbers(numbers, writer)

            # Задержка для соблюдения правил вежливости
            time.sleep(1.5)

            # Вывод прогресса
            if (page + 1) % 50 == 0:
                print(f"Обработано {page + 1} страниц, найдено {len(numbers)} чисел")

    print(f"Парсинг завершен. Результаты сохранены в {OUTPUT_FILE}")


if __name__ == "__main__":
    main()