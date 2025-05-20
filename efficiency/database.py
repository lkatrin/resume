import sqlite3

class Database:
    def __init__(self, db_name="app.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL,
                            role TEXT NOT NULL CHECK (role IN ('admin', 'user')),
                            security_question TEXT,
                            security_answer TEXT
                        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS employees (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            position TEXT NOT NULL
                        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS ratings (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            employee_id INTEGER NOT NULL,
                            rated_by INTEGER NOT NULL,
                            professional_skills INTEGER,
                            teamwork INTEGER,
                            initiative INTEGER,
                            time_management INTEGER,
                            responsibility INTEGER,
                            comments TEXT,
                            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (employee_id) REFERENCES employees(id),
                            FOREIGN KEY (rated_by) REFERENCES users(id)
                        )''')
        self.conn.commit()

    def add_user(self, username, password, role, question, answer):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password, role, security_question, security_answer) VALUES (?, ?, ?, ?, ?)",
                (username, password, role, question, answer)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def authenticate_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, role FROM users WHERE username = ? AND password = ?", (username, password))
        return cursor.fetchone()

    def add_employee(self, name, position):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO employees (name, position) VALUES (?, ?)", (name, position))
        self.conn.commit()

    def delete_employee_by_name(self, name):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM employees WHERE name = ?", (name,))
        self.conn.commit()

    def edit_employee(self, old_name, new_name, new_position):
        cursor = self.conn.cursor()
        if new_name and new_position:
            cursor.execute("UPDATE employees SET name = ?, position = ? WHERE name = ?", (new_name, new_position, old_name))
        elif new_name:
            cursor.execute("UPDATE employees SET name = ? WHERE name = ?", (new_name, old_name))
        elif new_position:
            cursor.execute("UPDATE employees SET position = ? WHERE name = ?", (new_position, old_name))
        self.conn.commit()

    def get_employees(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM employees")
        employees = cursor.fetchall()
        print(f"Fetched employees: {employees}")  # Проверка, что сотрудники извлекаются из базы данных
        return employees

    def add_rating(self, employee_id, rated_by, ratings, comments):
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO ratings (
                            employee_id, rated_by, professional_skills, teamwork, initiative,
                            time_management, responsibility, comments
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                        (employee_id, rated_by, ratings['professional_skills'], ratings['teamwork'],
                         ratings['initiative'], ratings['time_management'], ratings['responsibility'], comments))
        self.conn.commit()

    def calculate_effectiveness(self, employee_id):
        weights = {
            'professional_skills': 0.4,
            'teamwork': 0.2,
            'initiative': 0.2,
            'time_management': 0.1,
            'responsibility': 0.1
        }
        cursor = self.conn.cursor()
        cursor.execute('''SELECT professional_skills, teamwork, initiative, time_management, responsibility
                          FROM ratings WHERE employee_id = ?''', (employee_id,))
        ratings = cursor.fetchall()
        if not ratings:
            return 0

        total_score = 0
        for rating in ratings:
            total_score += sum(r * weights[key] for r, key in zip(rating, weights.keys()))
        effectiveness = total_score / len(ratings)
        return effectiveness

    def get_rating_history(self):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT employees.name, raters.username, professional_skills, teamwork, initiative, 
                          time_management, responsibility, comments, date
                          FROM ratings
                          JOIN employees ON ratings.employee_id = employees.id
                          JOIN users AS raters ON ratings.rated_by = raters.id
                          ORDER BY date DESC''')
        return cursor.fetchall()

    def get_employee_statistics(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT e.name, 
                   (r.professional_skills * 0.4 + r.teamwork * 0.2 + r.initiative * 0.2 +
                    r.time_management * 0.1 + r.responsibility * 0.1) AS effectiveness
            FROM employees e
            JOIN (
                SELECT employee_id, professional_skills, teamwork, initiative, time_management, responsibility
                FROM ratings
                WHERE id IN (
                    SELECT MAX(id) FROM ratings GROUP BY employee_id
                )
            ) r ON e.id = r.employee_id
            ORDER BY effectiveness DESC
        ''')
        return cursor.fetchall()

    def get_employee_id_by_name(self, name):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM employees WHERE name = ?", (name,))
        result = cursor.fetchone()
        return result[0] if result else None

    def delete_employee(self, employee_id):
        # Получить имя сотрудника по его ID, а затем удалить его
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM employees WHERE id = ?", (employee_id,))
        employee = cursor.fetchone()
        if employee:
            self.delete_employee_by_name(employee[0])  # Вызов метода удаления по имени
            return True
        return False

    def get_rating_history(self):
        """
        Получает историю оценок.
        """
        cursor = self.conn.cursor()
        cursor.execute('''SELECT employees.name, 
                                 raters.username, 
                                 json_object(
                                     'professional_skills', professional_skills,
                                     'teamwork', teamwork,
                                     'initiative', initiative,
                                     'time_management', time_management,
                                     'responsibility', responsibility
                                 ) AS ratings,
                                 comments, 
                                 date
                          FROM ratings
                          JOIN employees ON ratings.employee_id = employees.id
                          JOIN users AS raters ON ratings.rated_by = raters.id
                          ORDER BY date DESC''')
        return cursor.fetchall()

    def get_employee_ratings(self, employee_id):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT raters.username, 
                                 professional_skills || ', ' || teamwork || ', ' || initiative || ', ' || 
                                 time_management || ', ' || responsibility AS ratings, 
                                 comments, date
                          FROM ratings
                          JOIN users AS raters ON ratings.rated_by = raters.id
                          WHERE ratings.employee_id = ?
                          ORDER BY date DESC''', (employee_id,))
        return cursor.fetchall()

    def add_rating(self, employee_id, rated_by, ratings, comments):
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO ratings (
                            employee_id, rated_by, professional_skills, teamwork, initiative,
                            time_management, responsibility, comments
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (employee_id, rated_by, ratings['professional_skills'], ratings['teamwork'],
                        ratings['initiative'], ratings['time_management'], ratings['responsibility'], comments))
        self.conn.commit()

    def get_employee_statistics_last(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                employees.name,
                (professional_skills * 0.4 + teamwork * 0.2 + initiative * 0.2 +
                 time_management * 0.1 + responsibility * 0.1) AS current_score
            FROM ratings
            JOIN employees ON ratings.employee_id = employees.id
            WHERE ratings.date = (
                SELECT MAX(date) 
                FROM ratings AS sub_ratings 
                WHERE sub_ratings.employee_id = ratings.employee_id
            )
            GROUP BY employees.id
            ORDER BY current_score DESC
        ''')
        return cursor.fetchall()

    def get_current_and_previous_effectiveness(self, employee_id):
        """
        Возвращает текущую и предыдущую эффективность сотрудника.
        Если запись одна, предыдущая эффективность будет None.
        """
        weights = {
            'professional_skills': 0.4,
            'teamwork': 0.2,
            'initiative': 0.2,
            'time_management': 0.1,
            'responsibility': 0.1
        }

        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT professional_skills, teamwork, initiative, time_management, responsibility
            FROM ratings
            WHERE employee_id = ?
            ORDER BY date DESC
            LIMIT 2
        ''', (employee_id,))
        ratings = cursor.fetchall()

        if not ratings:
            return None, None  # Нет данных

        # Рассчитываем эффективность
        def calculate_score(rating):
            return sum(r * weights[key] for r, key in zip(rating, weights.keys()))

        current_score = calculate_score(ratings[0])  # Последняя запись
        previous_score = calculate_score(ratings[1]) if len(ratings) > 1 else None  # Предыдущая запись

        return current_score, previous_score

    def get_security_question(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT security_question FROM users WHERE username = ?", (username,))
        return cursor.fetchone()

    def verify_security_answer(self, username, answer):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ? AND security_answer = ?", (username, answer))
        return cursor.fetchone()

    def update_password(self, username, new_password):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
        self.conn.commit()