# get players in the team

from bs4 import BeautifulSoup
import pyodbc
import requests
import mysql.connector
from mysql.connector import Error

URL = 'https://www.euro-football.ru'

# config for connection to MySql server
config = {

    'host' : 'localhost',
    'port' : 3310,
    'user' : 'root',
    'database' : 'Chemp', 
    'charset' : 'utf8'

}


def get_info(url, team_id):

    final_lineup = []

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        team_name_elm = soup.find('div', class_ = 'team-header__name')

        team_name = team_name_elm.find('h1', class_ = 'team-header__name-title').text

        # print(name)

        all_players = soup.find_all('div', class_ = 'team-staff__table')

        for players in all_players:

            player_position = players.find('div', class_ = 'team-staff__header').text
            player_rows = players.find_all('tbody')

            # print(player_position)

            for rows in player_rows:

                row = rows.find_all('tr')
    
                for r in row:

                    # Извлекаем элементы с проверкой на наличие
                    number_elem = r.find('td', class_ = 'team-staff-amplua__number')
                    national_elem = r.find('img')
                    name_elem = r.find('td', class_ = 'team-staff-amplua__name')
                    age_elem = r.find('td', class_ = 'team-staff-amplua__age')
                    height_elem = r.find('td', class_ = 'team-staff-amplua__growth')
                    weight_elem = r.find('td', class_ = 'team-staff-amplua__weight')

                    # Безопасно получаем текст или значение по умолчанию
                    player_number = int(number_elem.text.strip()) if (number_elem and number_elem.text.strip().isdigit()) else 0
                    player_nationality = national_elem.get('title') if national_elem else 'N/A'
                    player_name = str(name_elem.text).replace('\n', '').replace('\t', ' ') if name_elem else 'N/A'
                    player_age = int(age_elem.text.strip()) if (age_elem and age_elem.text.strip().isdigit()) else 0
                    player_height = int(height_elem.text.strip()) if (height_elem and height_elem.text.strip()) else 0
                    player_weight = int(weight_elem.text.strip()) if (weight_elem and weight_elem.text.strip()) else 0

                    for item in [(team_id, team_name, player_position, player_number, player_nationality, player_name, player_age, player_height, player_weight)]:
                        final_lineup.append(item)
                    # print(name, player_position, player_number, player_nationality, player_name, player_age, player_height, player_weight)
    else:
        print('Страница не загрузилась!')

    print("Данные получены!")

    return final_lineup


def get_url_teams():

    f_url = []
    final_name = []
    url = 'https://www.euro-football.ru/champ/spain/la-liga/teams'
    data = "Дата не указана"

    response = requests.get(url)

    if response.status_code == 200:

        soup = BeautifulSoup(response.text, 'lxml')
        all_teams = soup.find_all('div', class_ = 'turnir-team__snippet')

        for teams in all_teams:
            href_elem = teams.find('a')
            href = href_elem.get('href')
            full_url = URL + href
            f_url.append(full_url)

            # print(f_url)

        for clubs in all_teams:
            
            name_object = clubs.find('div', 'turnir-team-snippet__title')
            name_club = name_object.text if name_object else 'Имя не найдено'
            name_str = str(name_club).replace('\n', '')
            adress_object = clubs.find('div', 'turnir-team-snippet__city')
            adress_club = adress_object.text if adress_object else 'Имя не найдено'

            lis = clubs.find_all('li')

            # get year from li without class
            for li in lis:
                if "Дата основания" in li.text:
                    data = int(li.span.text)
                    break
                
            for item in [(name_str, adress_club, data)]:
                final_name.append(item)
    else:
        print('Страница не загрузилась!')
    
    return f_url, final_name


def get_teams_lineup(url):

    f_url = []
    href = None
    responce = requests.get(url)

    if responce.status_code == 200:
        
        soup = BeautifulSoup(responce.text, 'lxml')
        lineup_elem = soup.find('ul', class_ = 'team-menu')
        all_lineups = lineup_elem.find_all('li')

        for lineups in all_lineups:

            if 'Состав' in lineups.text:
                href = lineups.a.get('href')

                if href:
                    full_url = URL + href
                    f_url.append(full_url)
                else:
                    print('Ссылка не найдена!')
                    return ""
                break

        # print(full_url)
    else:
        print('Страница не загрузилась!')

    return f_url


def insert_players(data, info):
    try:
        # Подключение к Access
        conn = pyodbc.connect(
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=C:\Users\sasha\OneDrive\Рабочий стол\СУБД\Новая папка\test.accdb'
        )
        cursor = conn.cursor()

        # SQL-запрос для вставки определенных полей
        sql = '''INSERT INTO Players (Player_id, Full_name, Age, Height, Weight, Nationality)
                 VALUES (?, ?, ?, ?, ?, ?)'''
        sql1 = '''INSERT INTO Clubs (Club_id, Nazvn, Address, Found_year)
                 VALUES (?, ?, ?, ?)'''
        sql2 = '''SELECT Season_id FROM Seasons'''
        sql3 = '''INSERT INTO Teams_lineups (Player_id, Clubs_id, Season_id, Player_number, Position)
                 VALUES (?, ?, ?, ?, ?)'''

        cursor.execute(sql2)
        seasons = cursor.fetchall()
        season_id = 1

        for club in info:
            club_id = club[0]
            club_name = club[1]
            club_address = club[2]
            club_date = club[3]

            cursor.execute(sql1, (club_id, club_name, club_address, club_date))

        # Выбираем нужные данные из кортежа
        for player in data:
            # Предполагаем структуру кортежа: 
            # (player_id, team_id, team_name, position, ...)
            player_id = player[0]
            club_i = player[1]
            player_position = player[3]
            player_number = player[4]
            nationality = player[5]
            player_name = player[6]
            age = player[7]
            height = player[8]
            weight = player[9]

            # Выполняем запрос
            cursor.execute(sql, (player_id, player_name, age, height, weight, nationality))
            cursor.execute(sql3, (player_id, club_i, season_id, player_number, player_position))

        

        print(seasons)
        # Сохраняем изменения
        conn.commit()
        print("Данные успешно записаны!")

    except pyodbc.Error as e:
        print(f"Ошибка при работе с Access: {e}")
    finally:
        if conn:
            conn.close()


def main():
    player_id = 1
    all_players = []
    all_info = []

    teams_urls, teams_info = get_url_teams()
    # print(teams_info)

    for team_id, (team_url, team_info) in enumerate(zip(teams_urls, teams_info), start=1):
    
        info = (team_id,) + team_info
        all_info.append(info)

        lineup_url = get_teams_lineup(team_url)
        for url in lineup_url:
            players = get_info(url, team_id)
            for player in players:
                # Создаем кортеж с player_id
                full_data = (player_id,) + player
                all_players.append(full_data)
                player_id += 1

    # print(all_info)
    
    # start_date, end_date = get_seasons()

    # Запись в Access
    insert_players(all_players, all_info)

    
    # try:
    #     connection = mysql.connector.connect(**config)
# 
    #     cursor = connection.cursor()
# 
    #     query = """
    #         INSERT INTO Players(team_name, player_position, player_number, player_nationality, player_name, player_age, player_height, player_weight)
    #         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    #     """
    #     for urls in url:
    #         url1 = get_teams_lineup(urls)
# 
    #         for url2 in url1:
    #             info = get_info(url2)
    #             cursor.executemany(query, info)
    #             
    #     connection.commit()
# 
    #     print("Данные успешно записаны!")
    # except Error as e:
    #     print(f"Ошика при работе с MySql: {e}")
    # finally:
    #     if 'connection' in locals() and connection.is_connected():
    #         cursor.close()
    #         connection.close()
    #         print("Соединение с MySQL закрыто")
    
    # try:
    #     with open("teams1.txt", "w",  encoding = "utf-8") as file:
# 
    #         for team_id, (team_url, team_info) in enumerate(zip(teams_urls, teams_info), start=1):
    # 
    #             info = (team_id,) + team_info
    #             all_info.append(info)
# 
    #             lineup_url = get_teams_lineup(team_url)
    #             for url in lineup_url:
    #                 players = get_info(url, team_id)
    #                 for player in players:
    #                     print(player)
    #                     Создаем кортеж с player_id
    #                     full_data = (player_id,) + player
    #                     all_players.append(full_data)
    #                     file.write(f'{all_players}\n')
    #                     player_id += 1
# 
    #                 #print(info)
    # except IOError as e:
    #     print(f'Ошибка записи в файл: {e}')
    # finally:
    #     file.close()
    #     print('Запись данных в блокнот закончена!')
 
main()