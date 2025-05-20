from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from database import Database
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.config import Config


class StatisticsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bonus_logic_text = (
            "Логика премий:\n"
            " - Эффективность < 5.0: Нет премии (0%)\n"
            " - 5.0 ≤ Эффективность < 7.0: 10% премии\n"
            " - 7.0 ≤ Эффективность < 9.0: 20% премии\n"
            " - Эффективность ≥ 9.0: 30% премии\n"
        )

    def on_enter(self):
        # Вызываем метод refresh_statistics() только после того, как экран загружен
        Clock.schedule_once(self.refresh_statistics)

    def refresh_statistics(self, *args):
        self.ids.statistics_list.clear_widgets()  # Очистка старых данных

        # Добавляем логику премий в статистику
        self.ids.statistics_list.add_widget(Label(
            text=self.bonus_logic_text,
            size_hint_y=None,
            height=150,
            font_size=18
        ))

        # Получаем статистику сотрудников из базы
        stats = db.get_employee_statistics()

        if not stats:
            # Если статистика пуста, отображаем сообщение
            self.ids.statistics_list.add_widget(Label(
                text="Нет доступных статистических данных",
                size_hint_y=None,
                height=40,
                font_size=18,
                color=(1, 0, 0, 1)  # Красный текст
            ))
            return

        # Создание списка с рейтингами и премиями
        for rank, stat in enumerate(stats, start=1):
            emp_name, avg_score = stat  # Данные сотрудника
            bonus = self.calculate_bonus(avg_score)  # Расчет премии

            # Добавляем информацию в список
            self.ids.statistics_list.add_widget(Label(
                text=f"{rank}. {emp_name} - Эффективность: {avg_score:.2f} - Премия: {bonus}%",
                size_hint_y=None,
                height=40,
                font_size=18
            ))

    def calculate_bonus(self, effectiveness):
        """
        Рассчитывает процент премии на основе эффективности.
        """
        if effectiveness < 5.0:
            return 0  # Нет премии
        elif 5.0 <= effectiveness < 7.0:
            return 10  # 10% премии
        elif 7.0 <= effectiveness < 9.0:
            return 20  # 20% премии
        else:  # 9.0 и выше
            return 30  # 30% премии


# Ограничение размера окна
Config.set('graphics', 'resizable', False)  # Запрещаем изменять размер
Config.set('graphics', 'width', '350')
Config.set('graphics', 'height', '550')


# Загрузка kv-файлов
Builder.load_file("login.kv")
Builder.load_file("register.kv")
Builder.load_file("recovery.kv")
Builder.load_file("admin.kv")
Builder.load_file("user.kv")
Builder.load_file("admin_rating.kv")
Builder.load_file("statistics.kv")
Builder.load_file("admin_employee_management.kv")

# Создание экземпляра базы данных
db = Database()

class LoginScreen(Screen):
    def login(self):
        username = self.ids.username.text
        password = self.ids.password.text
        user = db.authenticate_user(username, password)

        # Очистка полей после использования
        self.ids.username.text = ""
        self.ids.password.text = ""

        if user:
            user_id, role = user
            App.get_running_app().user_id = user_id
            App.get_running_app().user_role = role
            self.manager.current = 'admin' if role == 'admin' else 'user'
        else:
            self.ids.error.text = "Неверное имя пользователя или пароль"

    def go_to_register(self):
        self.manager.current = 'register'


class RegisterScreen(Screen):
    def register(self):
        username = self.ids.username.text
        password = self.ids.password.text
        role = self.ids.role.text
        question = self.ids.security_question.text
        answer = self.ids.security_answer.text

        self.ids.username.text = ""
        self.ids.password.text = ""
        self.ids.role.text = ""
        self.ids.security_question.text = ""
        self.ids.security_answer.text = ""

        if db.add_user(username, password, role, question, answer):
            self.manager.current = 'login'
        else:
            self.ids.error.text = "Имя пользователя уже существует"


class AdminScreen(Screen):
    def on_enter(self):
        self.refresh_employee_list()
        self.ids.employee_name.text = ""
        self.ids.employee_position.text = ""

    def refresh_employee_list(self):
        self.ids.employee_list.clear_widgets()
        employees = db.get_employees()
        for employee in employees:
            label = Label(text=f"{employee[1]} ({employee[2]})", size_hint_y=None, height=40)
            self.ids.employee_list.add_widget(label)
        self.ids.employee_list.height = self.ids.employee_list.minimum_height

    def add_employee(self):
        name = self.ids.employee_name.text
        position = self.ids.employee_position.text

        if name and position:
            db.add_employee(name, position)  # Операция в базе данных
        else:
            print("Имя или должность пусты")  # Для отладки

        # Очистка полей после нажатия на кнопку
        self.ids.employee_name.text = ""
        self.ids.employee_position.text = ""

        self.refresh_employee_list()


class UserScreen(Screen):
    selected_employee = None

    def on_enter(self):
        self.refresh_employee_list()
        self.ids.selected_employee.text = "Сотрудник не выбран"
        self.ids.effectiveness.text = ""
        self.ids.previous_effectiveness.text = ""  # Сброс предыдущей эффективности
        self.ids.history_list.clear_widgets()

    def refresh_employee_list(self):
        self.ids.employee_list.clear_widgets()
        employees = db.get_employees()
        for employee in employees:
            btn = Button(
                text=f"{employee[1]} ({employee[2]})",
                size_hint_y=None, height=60,
                background_normal='', background_color=(0.95, 0.95, 0.95, 1),  # Светлый фон для кнопок
                color=(0.2, 0.6, 0.8, 1),  # Цвет текста для читаемости
                on_press=lambda btn, emp=employee: self.select_employee(emp)
            )
            self.ids.employee_list.add_widget(btn)
        self.ids.employee_list.height = self.ids.employee_list.minimum_height

    def select_employee(self, employee):
        self.selected_employee = employee
        self.ids.selected_employee.text = f"Выбран: {employee[1]} ({employee[2]})"

        # Сброс данных эффективности при выборе нового сотрудника
        self.ids.effectiveness.text = ""
        self.ids.previous_effectiveness.text = ""

        self.refresh_history()

    def refresh_history(self):
        if not self.selected_employee:
            return
        employee_id = self.selected_employee[0]
        history = db.get_employee_ratings(employee_id)

        self.ids.history_list.clear_widgets()
        for record in history:
            rater_name, ratings, comments, date = record
            comment_label = Label(
                text=f"{date} by {rater_name}\nОценки: {ratings}\nКомментарии: {comments}",
                size_hint_y=None,
                height=140,  # Увеличена высота записи для длинных комментариев
                text_size=(self.ids.history_list.width - 30, None),  # Устанавливаем ширину для переносов
                valign='top',  # Выравнивание текста по верхнему краю
                halign='left',  # Горизонтальное выравнивание
            )
            self.ids.history_list.add_widget(comment_label)
        self.ids.history_list.height = self.ids.history_list.minimum_height

    def show_effectiveness(self):
        if self.selected_employee:
            employee_id = self.selected_employee[0]
            current_effectiveness, previous_effectiveness = db.get_current_and_previous_effectiveness(employee_id)

            # Обновляем текущую эффективность
            if current_effectiveness is not None:
                self.ids.effectiveness.text = f"Текущая эффективность: {current_effectiveness:.2f}"
            else:
                self.ids.effectiveness.text = "Текущая эффективность: N/A"

            # Обновляем прошлую эффективность
            if previous_effectiveness is not None:
                self.ids.previous_effectiveness.text = f"Прошлая эффективность: {previous_effectiveness:.2f}"
            else:
                self.ids.previous_effectiveness.text = "Прошлая эффективность: N/A"
        else:
            self.ids.effectiveness.text = "Не выбран сотрудник"
            self.ids.previous_effectiveness.text = ""


class AdminRatingScreen(Screen):
    def on_pre_enter(self):
        self.refresh_employee_list()
        self.clear_inputs()
        self.adjust_input_width()  # Новый метод для регулировки ширины полей

    def refresh_employee_list(self):
        employees = db.get_employees()
        self.ids.employee_spinner.values = [f"{emp[1]} ({emp[2]})" for emp in employees]

    def save_rating(self):
        # Извлекаем имя сотрудника из спиннера
        employee_name = self.ids.employee_spinner.text.split(" (")[0]
        employee_id = db.get_employee_id_by_name(employee_name)

        if employee_id:
            # Собираем оценки из полей ввода
            try:
                ratings = {
                    'professional_skills': int(self.ids.professional_skills.text or 0),
                    'teamwork': int(self.ids.teamwork.text or 0),
                    'initiative': int(self.ids.initiative.text or 0),
                    'time_management': int(self.ids.time_management.text or 0),
                    'responsibility': int(self.ids.responsibility.text or 0)
                }
                comments = self.ids.comments.text.strip()

                # Сохраняем оценки в базу данных
                db.add_rating(employee_id, App.get_running_app().user_id, ratings, comments)

                # Обновляем интерфейс после успешного сохранения
                self.ids.success_message.text = "Оценка успешно сохранена!"
                Clock.schedule_once(lambda dt: setattr(self.ids, 'success_message.text', ""), 2)  # Очистка сообщения через 2 сек.
                self.clear_inputs()

            except ValueError:
                self.ids.success_message.text = "Пожалуйста, введите корректные числа для всех оценок!"
        else:
            self.ids.success_message.text = "Пожалуйста, выберите действующего сотрудника!"

    def clear_inputs(self):
        # Очистка всех полей ввода
        self.ids.professional_skills.text = ""
        self.ids.teamwork.text = ""
        self.ids.initiative.text = ""
        self.ids.time_management.text = ""
        self.ids.responsibility.text = ""
        self.ids.comments.text = ""

    def adjust_input_width(self):
        # Уменьшаем ширину полей для ввода числовых значений
        self.ids.professional_skills.width = 100
        self.ids.teamwork.width = 100
        self.ids.initiative.width = 100
        self.ids.time_management.width = 100
        self.ids.responsibility.width = 100
        # Поле для комментариев оставляем без изменений, так как оно должно быть широким

        # Применяем выравнивание текста в полях для оценки
        self.ids.professional_skills.text_align = 'left'
        self.ids.teamwork.text_align = 'left'
        self.ids.initiative.text_align = 'left'
        self.ids.time_management.text_align = 'left'
        self.ids.responsibility.text_align = 'left'


from kivy.clock import Clock


class StatisticsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bonus_logic_text = (
            "Логика премий:\n"
            "\n"
            " - Эффективность < 5.0: Нет премии (0%)\n"
            "\n"
            " - 5.0 ≤ Эффективность < 7.0: 10% премии\n"
            "\n"
            " - 7.0 ≤ Эффективность < 9.0: 20% премии\n"
            "\n"
            " - Эффективность ≥ 9.0: 30% премии\n"
        )

    def on_enter(self):
        # Вызываем метод refresh_statistics() только после того, как экран загружен
        Clock.schedule_once(self.refresh_statistics)

    def refresh_statistics(self, *args):
        self.ids.statistics_list.clear_widgets()  # Очистка старых данных

        # Добавляем логику премий в статистику
        self.ids.statistics_list.add_widget(Label(
            text=self.bonus_logic_text,
            size_hint_y=None,
            height=400,
            font_size=32,
            color=(0, 1, 0, 1),
            halign='left',
        ))

        # Получаем статистику сотрудников из базы
        stats = db.get_employee_statistics()

        if not stats:
            # Если статистика пуста, отображаем сообщение
            self.ids.statistics_list.add_widget(Label(
                text="Нет доступных статистических данных",
                size_hint_y=None,
                height=40,
                font_size=30,
                color=(1, 0, 0, 1), # Красный текст
                halign='left'
            ))
            return

        # Создание списка с рейтингами и премиями
        for rank, stat in enumerate(stats, start=1):
            emp_name, avg_score = stat  # Данные сотрудника
            bonus = self.calculate_bonus(avg_score)  # Расчет премии

            grid_layout = GridLayout(cols=2, spacing=20, size_hint_y=None, height=60, row_default_height=40,
                                     row_force_default=True)

            # Добавляем данные о сотруднике в GridLayout
            grid_layout.add_widget(Label(
                text=f"{rank}. {emp_name}",
                font_size=36,
                halign='left',  # Выравнивание по левому краю
                size_hint_x=None,
                width=300,
                text_size=(300, None)  # Устанавливаем размер текста, чтобы он мог перенести
            ))

            grid_layout.add_widget(Label(
                text=f"Эффективность: {avg_score:.2f}\nБонус: {bonus}%",
                font_size=36,
                halign='left',  # Выравнивание по левому краю
                size_hint_x=None,
                width=280,
                text_size=(280, None)  # Устанавливаем размер текста
            ))

            # Добавляем созданный GridLayout в список
            self.ids.statistics_list.add_widget(grid_layout)


    def calculate_bonus(self, effectiveness):
        """
        Рассчитывает процент премии на основе эффективности.
        """
        if effectiveness < 5.0:
            return 0  # Нет премии
        elif 5.0 <= effectiveness < 7.0:
            return 10  # 10% премии
        elif 7.0 <= effectiveness < 9.0:
            return 20  # 20% премии
        else:  # 9.0 и выше
            return 30  # 30% премии


class AdminEmployeeManagementScreen(Screen):
    selected_employee = None

    def on_enter(self):
        self.refresh_employee_list()
        self.ids.selected_employee.text = ""
        self.ids.new_employee_name.text = ""
        self.ids.employee_position.text = ""

    def refresh_employee_list(self):
        self.ids.employee_list.clear_widgets()
        employees = db.get_employees()
        for employee in employees:
            btn = Button(
                text=f"{employee[1]} ({employee[2]})",
                size_hint_y=None, height=60,
                background_normal='', background_color=(0.95, 0.95, 0.95, 1),  # Светлый фон для кнопок
                color=(0.2, 0.6, 0.8, 1),  # Цвет текста для читаемости
                on_press=lambda btn, emp=employee: self.select_employee(emp)
            )
            self.ids.employee_list.add_widget(btn)
        self.ids.employee_list.height = self.ids.employee_list.minimum_height

    def select_employee(self, employee):
        self.selected_employee = employee
        self.ids.selected_employee.text = f"Выбран: {employee[1]} ({employee[2]})"

    def edit_employee(self):
        if self.selected_employee:
            old_name = self.selected_employee[1]
            new_name = self.ids.new_employee_name.text
            new_position = self.ids.employee_position.text

            if new_name or new_position:
                db.edit_employee(old_name, new_name, new_position)  # Операция в базе данных

            # Очистка полей после редактирования
            self.ids.new_employee_name.text = ""
            self.ids.employee_position.text = ""
            self.selected_employee = None
            self.ids.selected_employee.text = "Выбранный сотрудник: None"

        self.refresh_employee_list()

    def delete_employee(self):
        if self.selected_employee:
            employee_id = self.selected_employee[0]
            db.delete_employee(employee_id)  # Операция в базе данных

            # Очистка выбора после удаления
            self.selected_employee = None
            self.ids.selected_employee.text = "Выбранный сотрудник: None"

        self.refresh_employee_list()

class PasswordRecoveryScreen(Screen):
    def fetch_question(self):
        username = self.ids.username.text.strip()  # Удаляем лишние пробелы
        if not username:
            self.ids.question.text = "Пожалуйста, введите ваше имя пользователя"
            return

        # Запрашиваем вопрос из базы данных
        question = db.get_security_question(username)
        if question:
            self.ids.question.text = f"Секретный вопрос: {question[0]}"
        else:
            self.ids.question.text = "Пользователь не найден"

    def reset_password(self):
        username = self.ids.username.text.strip()
        answer = self.ids.answer.text.strip()  # Теперь это поле существует
        new_password = self.ids.new_password.text.strip()  # Мы можем теперь получить новый пароль

        if not username or not answer or not new_password:
            self.ids.error.text = "AВсе поля обязательны для заполнения"
            return

        if db.verify_security_answer(username, answer):
            db.update_password(username, new_password)
            self.manager.current = 'login'
        else:
            self.ids.error.text = "Неверный ответ"

class MainApp(App):
    user_id = None
    user_role = None

    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(PasswordRecoveryScreen(name='recovery'))
        sm.add_widget(AdminScreen(name='admin'))
        sm.add_widget(UserScreen(name='user'))
        sm.add_widget(AdminRatingScreen(name='admin_rating'))
        sm.add_widget(StatisticsScreen(name='statistics'))
        sm.add_widget(AdminEmployeeManagementScreen(name='admin_employee_management'))
        sm.current = 'login'
        return sm

    def get_employee_names(self):
        """
        Возвращает список имен сотрудников из базы данных.
        """
        employees = db.get_employees()  # Получаем всех сотрудников из базы
        return [employee[1] for employee in employees]  # Извлекаем только имена


if __name__ == '__main__':
    MainApp().run()