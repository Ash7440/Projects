import requests
import pyodbc
from bs4 import BeautifulSoup


def safe_int(value, default=0):
    """Безопасно конвертирует строку в целое число, возвращает default при ошибке."""
    try:
        return int(value) if value.strip() != '' else default
    except (ValueError, AttributeError):
        return default


def site_info():
    url = "https://soccer365.ru/?"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Referer": "https://soccer365.ru/competitions/16/players/",
    }

    teams_ids = [
        "6902",
        "296",
        "3",
        "12",
        "14",
        "30",
        "36",
        "752",
        "7030",
        "8546",
        "89",
        "114",
        "322",
        "31",
        "126",
        "203",
        "143",
        "259",
        "230",
        "195"
    ]

    players_with_stats = []
    team_id = 0

    for cl_value in teams_ids:

        team_id += 1
        params = {
            "c": "competitions",
            "a": "tab_tablesorter_players",
            "cp_ss": "4359275",
            "cl": cl_value,
            "page": "0",
            "size": "50"
        }


        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            try:
                data = response.json()

                # Обрабатываем каждую строку отдельно
                for row in data['rows']:
                    html_row = "".join(row)
                    soup = BeautifulSoup(html_row, 'lxml')

                    # Извлекаем имя
                    name_elem = soup.find('span')
                    name = name_elem.text.strip() if name_elem else "N/A"

                    # Извлекаем позицию
                    position_elem = soup.find('br')
                    position_raw = position_elem.next_sibling.strip() if position_elem else ""
                    position = safe_int(
                        position_raw.split(" ")[0].replace('#', '') 
                        if " " in position_raw 
                        else "0"
                    )

                    # Извлекаем статистику
                    stats = [stat.text.strip() for stat in soup.find_all('td', class_='al_c')]

                    # Проверяем, что статистика содержит достаточно элементов
                    if len(stats) >= 13:
                        players_with_stats.append({
                            'team_id': team_id,
                            'name': name,
                            'position': position,
                            'goals': safe_int(stats[0]), 
                            'assists': safe_int(stats[1]),
                            'games': safe_int(stats[2]),
                            'yellow_cards': safe_int(stats[10]),
                            'red_cards': safe_int(stats[12])
                        })

                # print(players_with_stats)

            except Exception as e:
                print("Ошибка:", e)
        else:
            print("Request failed. Status code:", response.status_code)

    # try:
    #     with open("stat.txt", 'w', encoding='utf-8') as file:
    #         for player in players_with_stats:
    #             # print(player)
    #             file.write(f'{player}\n')
    # except IOError as e:
    #     print(f'Ошибка записи в файл: {e}')
    # finally:
    #     file.close()
    #     print('Запись данных в блокнот закончена!')
        
    return players_with_stats


def  db_info():
    db_players_dict = {}
    try:
        conn = pyodbc.connect(
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=C:\Users\sasha\OneDrive\Рабочий стол\СУБД\Новая папка\test.accdb'
        )
        cursor = conn.cursor()

        # SQL-запрос для вставки определенных полей
        sql = '''SELECT Player_id, Club_id, Player_number, Season_id 
            FROM Teams_lineups
            WHERE Season_id = ?'''

        cursor.execute(sql, (1,))
        db_players = cursor.fetchall()

        for row in db_players:
            key = (row.Club_id, row.Player_number)
            db_players_dict[key] = (row.Player_id, row.Season_id)

        conn.commit()
        print("Данные успешно выгружены!")

    except pyodbc.Error as e:
        print(f"Ошибка при работе с Access: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()
        
    return db_players_dict


def update_player_stats(db_players, site_players, season_id=1):
    try:
        conn = pyodbc.connect(
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=C:\Users\sasha\OneDrive\Рабочий стол\СУБД\Новая папка\test.accdb'
        )
        cursor = conn.cursor()

        for player in site_players:
            team_id = player['team_id']
            position = player['position']
            key = (team_id, position)
            
            # Ищем Player_id и Season_id в словаре из БД
            if key in db_players:
                player_id, season_id_db = db_players[key]
                
                # Проверяем, совпадает ли Season_id
                if season_id_db != season_id:
                    print(f"Игрок {player['name']} принадлежит другому сезону!")
                    continue
                
                # SQL-запрос для вставки данных
                sql = '''
                    INSERT INTO Player_stats (
                        Player_id, Club_id, Season_id, 
                        Games_played, Goals, Assists, 
                        Yellow_cards, Red_cards
                    ) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                '''
                params = (
                    player_id, 
                    team_id, 
                    season_id,
                    player.get('games', 0), 
                    player.get('goals', 0), 
                    player.get('assists', 0),
                    player.get('yellow_cards', 0), 
                    player.get('red_cards', 0)
                )
                
                cursor.execute(sql, params)
                print(f"Данные для игрока {player['name']} добавлены!")

        conn.commit()
        print("Все данные успешно обновлены!")

    except pyodbc.Error as e:
        print(f"Ошибка при работе с Access: {e}")
        conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()



db_players = db_info()
site_players = site_info()

update_player_stats(db_players, site_players)
