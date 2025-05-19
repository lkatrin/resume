import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def create_connection():
    """ Создает соединение с базой данных SQLite """
    try:
        conn = sqlite3.connect('app_database.sqlite')
        return conn
    except sqlite3.Error as e:
        print(e)

def create_tables():
    """ Создает таблицы в базе данных, если они не существуют """
    conn = create_connection()
    try:
        cursor = conn.cursor()
        # Таблица для данных о поездах
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                departure_time TEXT NOT NULL,
                arrival_time TEXT NOT NULL,
                route TEXT NOT NULL,
                status TEXT NOT NULL,
                schedule TEXT NOT NULL,
                platform TEXT,
                path TEXT,
                direction TEXT
            )
        ''')

        # Таблица для данных пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

def add_train(name, departure_time, arrival_time, route, status, schedule, platform, path, direction):
    conn = create_connection()
    if conn:
        try:
            sql = ''' INSERT INTO trains(name, departure_time, arrival_time, route, status, schedule, platform, path, direction) VALUES(?,?,?,?,?,?,?,?,?) '''
            cur = conn.cursor()
            cur.execute(sql, (name, departure_time, arrival_time, route, status, schedule, platform, path, direction))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении поезда: {e}")
        finally:
            conn.close()

def update_train(train_id, name, departure_time, arrival_time, route, status, schedule, platform, path, direction):
    conn = create_connection()
    if conn:
        try:
            sql = ''' UPDATE trains SET name = ?, departure_time = ?, arrival_time = ?, route = ?, status = ?, schedule = ?, platform = ?, path = ?, direction = ? WHERE id = ? '''
            cur = conn.cursor()
            # Преобразование train_id в целое число для избежания ошибок
            cur.execute(sql, (name, departure_time, arrival_time, route, status,  schedule, platform, path, direction, int(train_id)))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении поезда: {e}")
        finally:
            conn.close()

def delete_train(id):
    """ Удаляет поезд из таблицы trains """
    conn = create_connection()
    if conn:
        try:
            sql = 'DELETE FROM trains WHERE id = ?'
            cur = conn.cursor()
            cur.execute(sql, (id,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при удалении поезда: {e}")
        finally:
            conn.close()

def get_all_trains():
    conn = create_connection()
    trains = []
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM trains")
            rows = cur.fetchall()
            print(rows)
            for row in rows:
                trains.append({'id': row[0], 'name': row[1], 'departure_time': row[2], 'arrival_time': row[3], 'route': row[4], 'status': row[5], 'schedule': row[6], 'platform': row[7], 'path': row[8], 'direction': row[9]})
        except sqlite3.Error as e:
            print(f"Ошибка при получении данных: {e}")
        finally:
            conn.close()
    return trains

def add_user(username, password):
    """ Добавляет нового пользователя в базу данных """
    conn = create_connection()
    try:
        cursor = conn.cursor()
        password_hash = generate_password_hash(password)
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при добавлении пользователя: {e}")
    finally:
        if conn:
            conn.close()

def check_user(username, password):
    """ Проверяет учетные данные пользователя """
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user[0], password):
            return True
        return False
    except sqlite3.Error as e:
        print(f"Ошибка при проверке пользователя: {e}")
    finally:
        if conn:
            conn.close()

def train_exists(name, departure_time, arrival_time, route):
    """ Проверяет, существует ли уже поезд с такими данными """
    conn = create_connection()
    if conn:
        try:
            sql = ''' SELECT * FROM trains WHERE name = ? AND departure_time = ? AND arrival_time = ? AND route = ? '''
            cur = conn.cursor()
            cur.execute(sql, (name, departure_time, arrival_time, route))
            if cur.fetchone():
                return True
            return False
        except sqlite3.Error as e:
            print(f"Ошибка при проверке существующего поезда: {e}")
        finally:
            conn.close()
    return False

def delete_user(username, password):
    """ Удаляет пользователя, если пароль верный """
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Проверка пароля пользователя
            cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            if user and check_password_hash(user[0], password):
                # Удаление пользователя, если пароль подтвержден
                cursor.execute("DELETE FROM users WHERE username = ?", (username,))
                conn.commit()
                return True  # Возвращаем True, если удаление прошло успешно
            return False  # Возвращаем False, если пароль неверный
        except sqlite3.Error as e:
            print(f"Ошибка при удалении пользователя: {e}")
            return False
        finally:
            conn.close()

