import sys
import pymysql
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication
from authorization_ui_form import Ui_Form
from main_menu import MainWindow

"""Запуск происходит с этого файла!"""


class CustomMessageBox(QtWidgets.QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QMessageBox {
                background-color: rgb(181, 213, 202);
                font-family: "MS Shell Dlg 2";
                font-size: 12pt;
                color: rgb(0, 0, 0);
            }
            QMessageBox QLabel {
                color: rgb(0, 0, 0);
                font-size: 12pt;
            }
            QMessageBox QPushButton {
                background-color: rgb(224, 169, 175);
                border: none;
                border-radius: 6px;
                font-size: 12pt;
                color: rgb(0, 0, 0);
                padding: 5px 10px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: rgb(200, 150, 155);
            }
        """)


class AuthorizationWindow(QtWidgets.QWidget):
    def __init__(self, allowed_roles, main_window_class):
        super().__init__()
        self.allowed_roles = allowed_roles
        self.main_window_class = main_window_class

        self.ui = Ui_Form()
        self.ui.setupUi(self)
        # Подключение к бд
        self.connection = pymysql.connect(
            host="fatima6p.beget.tech",
            user="fatima6p_orange",
            password="password",
            database="fatima6p_orange"
        )
        self.cursor = self.connection.cursor()
        self.current_user = None

        self.ui.pushButton_login.clicked.connect(self.authorize)

    # Получаем информацию в зависимости от пользователя, который вошел
    def get_user_from_db(self, username, password):
        worker_query = """
            SELECT 'worker' as user_type, w.id, w.login, 
                   r.role_name, w.id_role,
                   w.surname, w.name, w.patronymic  # Добавляем ФИО
            FROM worker w
            JOIN role r ON w.id_role = r.id
            WHERE w.login = %s AND w.password = %s
        """
        self.cursor.execute(worker_query, (username, password))
        worker = self.cursor.fetchone()

        if worker:
            return worker

        customer_query = """
            SELECT 'customer' as user_type, c.id, c.login,
                   tc.name_type_customer, c.id_type_customer,
                   c.surname, c.name, c.patronymic  # Добавляем ФИО
            FROM customer c
            JOIN type_customer tc ON c.id_type_customer = tc.id
            WHERE c.login = %s AND c.password = %s
        """
        self.cursor.execute(customer_query, (username, password))
        return self.cursor.fetchone()



    def authorize(self):
        try:
            username = self.ui.lineEdit_username.text()
            password = self.ui.lineEdit_password.text()

            if not username or not password:
                self.show_error_message("Заполните все поля")
                return

            user = self.get_user_from_db(username, password)

            if not user:
                self.show_error_message("Неверные данные")
                return

            self.current_user = {
                'type': user[0],
                'id': user[1],
                'login': user[2],
                'role': user[3],
                'role_id': user[4],
                'surname': user[5],
                'name': user[6],
                'patronymic': user[7]
            }


            self.main_window = self.main_window_class(user_data=self.current_user)
            self.main_window.show()

            self.close()

        except Exception as e:
            print(f"Ошибка авторизации: {str(e)}")
            self.show_error_message("Ошибка системы")

    def show_error_message(self, message):
        msg = CustomMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        msg.setWindowTitle("Ошибка")
        msg.setText(message)
        msg.exec()

    def closeEvent(self, event):
        self.cursor.close()
        self.connection.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    authorization = AuthorizationWindow(
        allowed_roles={
            'workers': [1],  # ID разрешенных ролей для сотрудников
            'customers': [1, 2]  # ID разрешенных типов для заказчиков
        },
        main_window_class=MainWindow
    )
    authorization.show()
    sys.exit(app.exec())