import csv
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
import os

INPUT_CSV = "correct_profile_links.csv"
OUTPUT_CSV = "profiles_data.csv"
BASE_DOMAIN = "https://www.mywsba.org"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def get_total_profiles():
    """Подсчитывает общее количество профилей для обработки"""
    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        return sum(1 for _ in f) - 1  # Вычитаем заголовок


def parse_profile(url):
    """Парсит данные профиля"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        name_spans = soup.find_all('span', class_='name')
        names_data = [span.get_text(strip=True) for span in name_spans if span.get_text(strip=True)]

        return names_data if names_data else ["No name data found"]

    except requests.exceptions.RequestException as e:
        return [f"Error: {str(e)}"]
    except Exception as e:
        return [f"Parsing error: {str(e)}"]


def process_profiles():
    total_profiles = get_total_profiles()
    processed = 0
    success_count = 0
    error_count = 0

    # Проверяем существование файла для дозаписи
    file_exists = os.path.isfile(OUTPUT_CSV)

    with open(INPUT_CSV, 'r', encoding='utf-8') as infile, \
            open(OUTPUT_CSV, 'a' if file_exists else 'w', newline='', encoding='utf-8') as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Записываем заголовки только если файл новый
        if not file_exists:
            writer.writerow(['Profile URL', 'Name Data'])

        # Пропускаем заголовок
        next(reader, None)

        for row in reader:
            if not row:
                continue

            processed += 1
            profile_url = row[0]

            if not profile_url.startswith('http'):
                profile_url = urljoin(BASE_DOMAIN, profile_url)

            # Обновляем прогресс в терминале
            print(f"\rОбработано: {processed}/{total_profiles} | Успешно: {success_count} | Ошибки: {error_count}",
                  end="")

            names_data = parse_profile(profile_url)

            for name in names_data:
                writer.writerow([name])

            if "Error" not in names_data[0] and "No name data" not in names_data[0]:
                success_count += 1
            else:
                error_count += 1

            time.sleep(1.5)

    # Финальный вывод
    print(f"\nОбработка завершена!")
    print(f"Всего профилей: {total_profiles}")
    print(f"Успешно обработано: {success_count}")
    print(f"С ошибками: {error_count}")
    print(f"Результаты сохранены в {OUTPUT_CSV}")


if __name__ == "__main__":
    process_profiles()