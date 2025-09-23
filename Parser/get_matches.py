import pandas as pd
import re
import pyodbc
from bs4 import BeautifulSoup
from datetime import datetime


def get_matches():
        # Загрузка HTML содержимого
    with open('links.txt', 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Парсинг стадионов с использованием регулярных выражений
    stadiums = {}
    stadium_box = soup.find('div', {'id': 'box_stadiums'})
    for a in stadium_box.find_all('a'):
        onclick = a.get('onclick', '')
        stadium_id_match = re.search(r"filtersData\('stadium','(\d+)'\)", onclick)
        if stadium_id_match:
            stadium_id = stadium_id_match.group(1)
            stadium_name = a.text.strip()
            stadiums[stadium_id] = stadium_name

    # Парсинг матчей с названиями команд
    matches = []

    for tour_block in soup.find_all('div', class_='live_comptt_bd'):
        tour = tour_block.find('div', class_='cmp_stg_ttl').text.strip()

        for game in tour_block.find_all('div', class_='game_block'):
            # Извлечение названий команд
            try:
                home_name = game.find('div', class_='ht').find('span').text.strip()
            except AttributeError:
                home_name = 'Unknown Home Team'

            try:
                away_name = game.find('div', class_='at').find('span').text.strip()
            except AttributeError:
                away_name = 'Unknown Away Team'

            # Стадион
            stadium_id = game.get('dt-st', '')
            stadium = stadiums.get(stadium_id, 'Unknown Stadium')

            # Дата и время
            status = game.find('div', class_='status')
            date_time = status.text.strip() if status else ''
            if 'Завершен' in date_time:
                match_date, match_time = 'Завершен', 'Завершен'
            else:
                date_time_parts = date_time.split(', ') if ', ' in date_time else ['', '']
                match_date = date_time_parts[0].replace('.', '/') if date_time_parts[0] else ''
                match_time = date_time_parts[1] if len(date_time_parts) > 1 else ''

            # Счет
            try:
                home_score = int(game.find('div', class_='ht').find('div', class_='gls').text.strip())
                away_score = int(game.find('div', class_='at').find('div', class_='gls').text.strip())
            except (AttributeError, ValueError) as e:
                home_score = '0'
                away_score = '0'
                print(f"Ошибка обработки счёта: {e}")

            matches.append({
                'Home_team': home_name,
                'Away_team': away_name,
                'Season_id': 1,
                'Match_date': match_date,
                'Match_time': match_time,
                'Stadium': stadium,
                'Home_score': home_score,
                'Away_score': away_score
            })

    # Создание DataFrame
    df = pd.DataFrame(matches)

    df['Match_date'] = df['Match_date'].apply(
    lambda x: f"{x}/25" if len(x.split('/')) == 2 else x
    )

    # Конвертируем в datetime
    df['Match_date'] = pd.to_datetime(
        df['Match_date'], 
        format='%d/%m/%y', 
        errors='coerce'
    )

    # Конвертация времени
    df['Match_time'] = pd.to_datetime(
        df['Match_time'], 
        format='%H:%M', 
        errors='coerce'
    ).dt.strftime('%H:%M')  # Сохраняем как строку HH:MM

    # Экспорт в CSV
    df.to_csv('matches_with_team_names.csv', index=False, sep=';', encoding='utf-8-sig')
    print("Данные успешно сохранены в matches_with_team_names.csv")


get_matches()


# 1. Подключение к базе Access
db_path = r'C:\Users\sasha\OneDrive\Рабочий стол\СУБД\Новая папка\test.accdb'  # Укажите реальный путь
conn_str = (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    r'DBQ=' + db_path + ';'
)

try:
    conn = pyodbc.connect(conn_str)
except pyodbc.Error as e:
    print(f"Ошибка подключения: {e}")
    exit()

# 2. Выгрузка данных из таблицы Clubs
query = """
SELECT 
    Club_id, 
    Nazvn AS club_name
FROM Clubs;
"""

clubs_df = pd.read_sql(query, conn)
conn.close()

# Доработанная функция нормализации с заменой сокращений
def normalize_name(name):
    # Словарь замен для сокращений
    replacements = {
        r'\bатлетик б\b': 'атлетик',
        r'\bатлетико м\b': 'атлетико мадрид',
        r'\bреал вальядолид\b': 'вальядолид',  # Удаляем "Реал"
        r'\bр вальядолид\b': 'вальядолид',    # Для сокращенных вариантов
        r'\bвальядолид\b': 'вальядолид'       # Явное указание
    }
    
    # Базовые преобразования
    normalized = (
        str(name).strip().lower()
        .translate(str.maketrans('ё', 'е'))
        .replace("-", " ")
        .replace(".", "")
        .replace("  ", " ")
    )
    
    # Применяем замену сокращений
    for pattern, replacement in replacements.items():
        normalized = re.sub(pattern, replacement, normalized)

    return normalized

# Создаем все варианты названий
clubs_df['normalized'] = clubs_df.apply(
    lambda x: [normalize_name(x[col]) for col in ['club_name'] if x[col]],
    axis=1
)

# 4. Сопоставление с данными с сайта
matches_df = pd.read_csv('matches_with_team_names.csv', sep=';')

def find_club_id(search_name):
    normalized = normalize_name(search_name)
    for _, row in clubs_df.iterrows():
        if normalized in row['normalized']:
            return row['Club_id']
    return None

# Применяем к обеим командам
matches_df['Home_club_id'] = matches_df['Home_team'].apply(find_club_id)
matches_df['Away_club_id'] = matches_df['Away_team'].apply(find_club_id)

# 5. Проверка и экспорт

matches_df.to_csv('final_matches.csv', index=False, sep=';', encoding='utf-8-sig')




# Подключение к базе Access
db_path = r'C:\Users\sasha\OneDrive\Рабочий стол\СУБД\Новая папка\test.accdb'
conn_str = (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    r'DBQ=' + db_path + ';'
)

matches_df = pd.read_csv(
    'final_matches.csv', 
    sep=';', 
    parse_dates=['Match_date'],
    dtype={'Home_club_id': 'Int64', 'Away_club_id': 'Int64'}
)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    query = """
    INSERT INTO Matches (
        Home_club_id, 
        Away_club_id,
        Season_id, 
        Match_date,
        Match_time, 
        Stadium, 
        Home_score, 
        Away_score
    ) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """

    data_to_insert = []
    for idx, row in matches_df.iterrows():
        # Валидация ID клубов
        if pd.isnull(row['Home_club_id']) or pd.isnull(row['Away_club_id']):
            print(f"Пропуск строки {idx}: отсутствует ID клуба")
            continue
        
        # Дата
        match_date = row['Match_date'].date() if not pd.isnull(row['Match_date']) else None
        
        # Время
        try:
            match_time = datetime.strptime(row['Match_time'], "%H:%M").time()
        except:
            match_time = None
        
        data_to_insert.append((
            int(row['Home_club_id']),
            int(row['Away_club_id']),
            1,
            match_date,
            match_time,
            str(row['Stadium']),
            int(row['Home_score']),
            int(row['Away_score'])
        ))

    # Пакетная вставка
    batch_size = 100
    for i in range(0, len(data_to_insert), batch_size):
        cursor.executemany(query, data_to_insert[i:i+batch_size])
        conn.commit()

    print(f"Успешно: {len(data_to_insert)} записей")

except Exception as e:
    print("Ошибка:", str(e))
    if 'conn' in locals():
        conn.rollback()
finally:
    if 'conn' in locals():
        conn.close()

