import csv
import re

BASE_PROFILE_URL = "https://www.mywsba.org/PersonifyEbusiness/LegalDirectory/LegalProfile.aspx?Usr_ID="
INPUT_CSV = "itemtemplate_numbers.csv"
OUTPUT_CSV = "correct_profile_links.csv"


def extract_number(raw_value):
    """Извлекает число из строки, независимо от формата"""
    # Удаляем все нецифровые символы
    cleaned = re.sub(r'[^\d]', '', str(raw_value))
    return cleaned if cleaned else None


def format_user_id(number):
    """Форматирует число в 12-значный ID с ведущими нулями"""
    return str(number).zfill(12) if number else None


def process_csv():
    profile_links = []

    with open(INPUT_CSV, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile)

        # Пропускаем заголовок, если он есть
        try:
            header = next(reader)
            if 'Extracted Number' not in str(header):
                # Если заголовок не содержит ожидаемых колонок, возвращаемся к началу файла
                infile.seek(0)
        except StopIteration:
            pass  # Файл пустой

        for row in reader:
            try:
                # Обрабатываем строки с разным количеством колонок
                raw_number = row[1] if len(row) > 1 else row[0]
                number = extract_number(raw_number)

                if number:
                    user_id = format_user_id(number)
                    profile_url = f"{BASE_PROFILE_URL}{user_id}"
                    profile_links.append(profile_url)
            except Exception as e:
                print(f"Ошибка обработки строки {row}: {str(e)}")
                continue

    # Сохраняем результаты
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['Profile URL'])
        writer.writerows([[link] for link in profile_links])

    print(f"Успешно обработано. Создано {len(profile_links)} корректных ссылок.")


if __name__ == "__main__":
    process_csv()