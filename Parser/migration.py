import pyodbc
import mysql.connector
from mysql.connector import Error

# Конфигурация подключения к Access
access_conn_str = (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    r'DBQ=C:/Users/sasha/OneDrive/Рабочий стол/СУБД/Новая папка/test.accdb;' 
)

# Конфигурация подключения к MySQL
mysql_config = {
    'host' : 'localhost',
    'port' : 3306,
    'user' : 'root',
    'database' : 'champ', 
    'charset' : 'utf8'
}

# Список таблиц для переноса
tables = [
    'Clubs', 'Players', 'Seasons',
    'Teams_lineups', 'Matches', 
    'Player_stats', 'Staff'
]

def migrate_table(table_name):
    try:
        # Подключение к Access
        access_conn = pyodbc.connect(access_conn_str)
        access_cursor = access_conn.cursor()
        
        # Подключение к MySQL
        mysql_conn = mysql.connector.connect(**mysql_config)
        mysql_cursor = mysql_conn.cursor()
        
        # Получение данных из Access
        access_cursor.execute(f'SELECT * FROM {table_name}')
        rows = access_cursor.fetchall()
        
        if not rows:
            print(f"Таблица {table_name} пуста")
            return
        
        # Получение названий столбцов
        columns = [column[0] for column in access_cursor.description]
        columns_str = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(columns))
        
        # Очистка таблицы в MySQL перед вставкой
        mysql_cursor.execute(f'DELETE FROM {table_name}')
        
        # Вставка данных в MySQL
        insert_query = f"""
            INSERT INTO {table_name} ({columns_str})
            VALUES ({placeholders})
        """
        
        for row in rows:
            # Конвертация специальных типов данных
            converted_row = []
            for value in row:
                if isinstance(value, bytes):
                    # Обработка двоичных данных
                    converted_row.append(value.decode('latin1'))
                elif hasattr(value, 'strftime'):
                    # Конвертация даты/времени в строку
                    converted_row.append(value.strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    converted_row.append(value)
            
            mysql_cursor.execute(insert_query, converted_row)
        
        mysql_conn.commit()
        print(f"Перенесено {len(rows)} записей в таблицу {table_name}")
        
    except Error as e:
        print(f"Ошибка при работе с таблицей {table_name}: {e}")
    finally:
        # Закрытие соединений
        access_cursor.close()
        access_conn.close()
        mysql_cursor.close()
        mysql_conn.close()

# Перенос всех таблиц
if __name__ == "__main__":
    for table in tables:
        print(f"Начало переноса таблицы {table}...")
        migrate_table(table)
    print("Миграция данных завершена!")