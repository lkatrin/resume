from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import (QVBoxLayout, QLabel, QLineEdit,
                             QComboBox, QPushButton, QMessageBox, QFormLayout,
                             QSpacerItem, QSizePolicy)
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression
from factory_bd import connect_to_db
import pymysql.cursors
import re  # Для проверки email


class Ui_EditCustomerForm:
    def __init__(self):
        super().__init__()
        self.db = connect_to_db()
        self.company_map = {}
        self.person_map = {}

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setStyleSheet("""
            background-color: rgb(181, 213, 202);
            font-family: 'MS Shell Dlg 2';
        """)

        main_layout = QVBoxLayout(Form)
        main_layout.setContentsMargins(20, 10, 20, 20)
        main_layout.setSpacing(15)

        # Заголовок
        self.header = QLabel("РЕДАКТИРОВАНИЕ ЗАКАЗЧИКА")
        self.header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: black;
                padding: 10px 0;
                font-family: 'MS Shell Dlg 2';
            }
        """)
        self.header.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.header)

        # Форма
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        form_layout.setContentsMargins(10, 0, 10, 0)


        customer_label = QLabel("Выберите заказчика:")
        customer_label.setStyleSheet("""
            QLabel {
                color: black;
                font-family: 'MS Shell Dlg 2';
            }
        """)
        self.customer_combo = QComboBox()
        self.customer_combo.currentIndexChanged.connect(self.load_customer_data)
        self.customer_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border-radius: 3px;
                padding: 5px;
                border: 1px solid #ccc;
                color: black;
                font-family: 'MS Shell Dlg 2';
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #ccc;
                border-left-style: solid;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                selection-background-color: rgb(224, 169, 175);
                border: 1px solid #ccc;
                color: black;
                font-family: 'MS Shell Dlg 2';
            }
        """)
        form_layout.addRow(customer_label, self.customer_combo)

        company_label = QLabel("Название компании:")
        company_label.setStyleSheet("""
            QLabel {
                color: black;
                font-family: 'MS Shell Dlg 2';
            }
        """)
        self.company_edit = QLineEdit()
        self.company_edit.setPlaceholderText("Введите название компании")
        self.company_edit.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border-radius: 3px;
                padding: 5px;
                border: 1px solid #ccc;
                color: black;
                font-family: 'MS Shell Dlg 2';
            }
        """)
        form_layout.addRow(company_label, self.company_edit)

        surname_label = QLabel("Фамилия:")
        surname_label.setStyleSheet("""
            QLabel {
                color: black;
                font-family: 'MS Shell Dlg 2';
            }
        """)
        self.surname_edit = QLineEdit()
        self.surname_edit.setPlaceholderText("Введите фамилию")
        self.surname_edit.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border-radius: 3px;
                padding: 5px;
                border: 1px solid #ccc;
                color: black;
                font-family: 'MS Shell Dlg 2';
            }
        """)
        form_layout.addRow(surname_label, self.surname_edit)

        name_label = QLabel("Имя:")
        name_label.setStyleSheet("""
            QLabel {
                color: black;
                font-family: 'MS Shell Dlg 2';
            }
        """)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите имя")
        self.name_edit.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border-radius: 3px;
                padding: 5px;
                border: 1px solid #ccc;
                color: black;
                font-family: 'MS Shell Dlg 2';
            }
        """)
        form_layout.addRow(name_label, self.name_edit)

        patronymic_label = QLabel("Отчество:")
        patronymic_label.setStyleSheet("""
            QLabel {
                color: black;
                font-family: 'MS Shell Dlg 2';
            }
        """)
        self.patronymic_edit = QLineEdit()
        self.patronymic_edit.setPlaceholderText("Введите отчество")
        self.patronymic_edit.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border-radius: 3px;
                padding: 5px;
                border: 1px solid #ccc;
                color: black;
                font-family: 'MS Shell Dlg 2';
            }
        """)
        form_layout.addRow(patronymic_label, self.patronymic_edit)

        phone_label = QLabel("Телефон:")
        phone_label.setStyleSheet("""
            QLabel {
                color: black;
                font-family: 'MS Shell Dlg 2';
            }
        """)
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("+7XXXXXXXXXX")
        phone_validator = QRegularExpressionValidator(
            QRegularExpression("[+]{0,1}[0-9]{0,15}"), self.phone_edit)
        self.phone_edit.setValidator(phone_validator)
        self.phone_edit.textChanged.connect(self.format_phone_number)
        self.phone_edit.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border-radius: 3px;
                padding: 5px;
                border: 1px solid #ccc;
                color: black; 
                font-family: 'MS Shell Dlg 2';
            }
        """)
        form_layout.addRow(phone_label, self.phone_edit)

        email_label = QLabel("Email:")
        email_label.setStyleSheet("""
            QLabel {
                color: black;
                font-family: 'MS Shell Dlg 2';
            }
        """)
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("example@mail.com")
        self.email_edit.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border-radius: 3px;
                padding: 5px;
                border: 1px solid #ccc;
                color: black;
                font-family: 'MS Shell Dlg 2';
            }
        """)
        form_layout.addRow(email_label, self.email_edit)

        login_label = QLabel("Логин:")
        login_label.setStyleSheet("""
            QLabel {
                color: black;
                font-family: 'MS Shell Dlg 2';
            }
        """)
        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("Придумайте логин")
        self.login_edit.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border-radius: 3px;
                padding: 5px;
                border: 1px solid #ccc;
                color: black;
                font-family: 'MS Shell Dlg 2';
            }
        """)
        form_layout.addRow(login_label, self.login_edit)

        password_label = QLabel("Пароль:")
        password_label.setStyleSheet("""
            QLabel {
                color: black;
                font-family: 'MS Shell Dlg 2';
            }
        """)
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Придумайте пароль")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border-radius: 3px;
                padding: 5px;
                border: 1px solid #ccc;
                color: black;
                font-family: 'MS Shell Dlg 2';
            }
        """)
        form_layout.addRow(password_label, self.password_edit)

        main_layout.addLayout(form_layout)
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.save_btn = QPushButton("Сохранить изменения")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(224, 169, 175);
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                font-family: 'MS Shell Dlg 2';
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgb(200, 149, 155);
            }
        """)
        self.save_btn.clicked.connect(self.save_customer)
        main_layout.addWidget(self.save_btn)

        self.load_customers()

    def load_customers(self):
        """Загружает заказчиков с типом отображаемой информации"""
        if not self.db:
            print("Ошибка: нет подключения к базе данных.")
            return

        try:
            with self.db.cursor(pymysql.cursors.DictCursor) as cursor:
                query = "SELECT id, company_name, surname, name, patronymic, id_type_customer FROM customer"
                cursor.execute(query)
                customers = cursor.fetchall()

                self.customer_combo.clear()
                self.customer_combo.addItem("Выберите заказчика", None)

                for customer in customers:
                    if customer['id_type_customer'] == 1:  # Компания
                        display_name = customer['company_name']
                        self.company_map[display_name] = customer['id']
                    elif customer['id_type_customer'] == 2:  # Физическое лицо
                        display_name = f"{customer['surname']} {customer['name']} {customer['patronymic']}"
                        self.person_map[display_name] = customer['id']

                    self.customer_combo.addItem(display_name, customer['id'])

        except pymysql.Error as e:
            print(f"Ошибка загрузки заказчиков: {e}")
            QMessageBox.critical(None, "Ошибка", f"Ошибка при загрузке заказчиков: {e}")

    def load_customer_data(self):
        """Загружает данные по выбранному заказчику"""
        customer_id = self.customer_combo.currentData()
        if not customer_id:
            return

        try:
            with self.db.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("""
                    SELECT company_name, surname, name, patronymic, phone, email, login, password, id_type_customer
                    FROM customer WHERE id = %s
                """, (customer_id,))
                customer_data = cursor.fetchone()

                if customer_data:
                    # Поля формы
                    self.company_edit.setText(customer_data.get('company_name', ''))
                    self.surname_edit.setText(customer_data.get('surname', ''))
                    self.name_edit.setText(customer_data.get('name', ''))
                    self.patronymic_edit.setText(customer_data.get('patronymic', ''))
                    self.phone_edit.setText(customer_data.get('phone', ''))
                    self.email_edit.setText(customer_data.get('email', ''))
                    self.login_edit.setText(customer_data.get('login', ''))
                    self.password_edit.setText(customer_data.get('password', ''))

                    # Блокировка поля "Название компании" для физ. лиц
                    if customer_data['id_type_customer'] == 2:
                        self.company_edit.setEnabled(False)
                    else:
                        self.company_edit.setEnabled(True)

        except pymysql.Error as e:
            print(f"Ошибка загрузки данных заказчика: {e}")
            QMessageBox.critical(None, "Ошибка", f"Ошибка при загрузке данных заказчика: {e}")

    def format_phone_number(self):
        text = self.phone_edit.text()
        if not text.startswith('+') and text:
            self.phone_edit.setText('+' + text)

    def validate_fields(self):
        """Проверка заполнения полей и соответствия шаблонам"""
        errors = []

        # Проверка на пустые поля
        if not self.surname_edit.text().strip():
            errors.append("Фамилия не может быть пустой.")
        if not self.name_edit.text().strip():
            errors.append("Имя не может быть пустым.")
        if not self.phone_edit.text().strip():
            errors.append("Телефон не может быть пустым.")
        if not self.email_edit.text().strip():
            errors.append("Email не может быть пустым.")
        if not self.login_edit.text().strip():
            errors.append("Логин не может быть пустым.")
        if not self.password_edit.text().strip():
            errors.append("Пароль не может быть пустым.")

        # Проверка телефона
        phone = self.phone_edit.text().strip()
        if phone and not re.match(r"^\+\d{10,15}$", phone):
            errors.append("Телефон должен начинаться с '+' и содержать от 10 до 15 цифр.")

        # Проверка email
        email = self.email_edit.text().strip()
        if email and not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            errors.append("Некорректный формат email.")

        # Если есть ошибки
        if errors:
            QMessageBox.warning(None, "Ошибка", "\n".join(errors))
            return False

        return True

    def save_customer(self):
        """Сохранение измененной информации"""
        customer_id = self.customer_combo.currentData()
        if not customer_id:
            QMessageBox.warning(None, "Ошибка", "Выберите заказчика для редактирования.")
            return

        # Проверяем поля перед сохранением
        if not self.validate_fields():
            return

        data = {
            'company': self.company_edit.text().strip(),
            'surname': self.surname_edit.text().strip(),
            'name': self.name_edit.text().strip(),
            'patronymic': self.patronymic_edit.text().strip(),
            'phone': self.phone_edit.text().strip(),
            'email': self.email_edit.text().strip(),
            'login': self.login_edit.text().strip(),
            'password': self.password_edit.text().strip()
        }

        try:
            with self.db.cursor() as cursor:
                query = """
                    UPDATE customer SET
                        company_name = %s,
                        surname = %s,
                        name = %s,
                        patronymic = %s,
                        phone = %s,
                        email = %s,
                        login = %s,
                        password = %s
                    WHERE id = %s
                """
                cursor.execute(query, (
                    data['company'], data['surname'], data['name'], data['patronymic'],
                    data['phone'], data['email'], data['login'], data['password'], customer_id))
                self.db.commit()

                QMessageBox.information(None, "Успех", "Данные заказчика успешно сохранены.")

        except pymysql.Error as e:
            print(f"Ошибка при сохранении данных заказчика: {e}")
            QMessageBox.critical(None, "Ошибка", f"Ошибка при сохранении данных заказчика: {e}")


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_EditCustomerForm()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())