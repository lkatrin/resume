from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import (QVBoxLayout, QLabel, QLineEdit,
                             QComboBox, QPushButton, QMessageBox, QFormLayout,
                             QSpacerItem, QSizePolicy)
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression
from factory_bd import connect_to_db


class Ui_Form:
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setStyleSheet("""
            background-color: rgb(181, 213, 202);
            font-family: 'MS Shell Dlg 2';
        """)

        main_layout = QVBoxLayout(Form)
        main_layout.setContentsMargins(20, 10, 20, 20)
        main_layout.setSpacing(15)

        self.header = QLabel("РЕГИСТРАЦИЯ ЗАКАЗЧИКА")
        self.header.setStyleSheet("""
            QLabel {
                font-size: 18pt;
                font-weight: bold;
                color: black;
                padding: 10px 0;
                font-family: 'MS Shell Dlg 2';
            }
        """)
        self.header.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.header)

        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        form_layout.setContentsMargins(10, 0, 10, 0)

        type_label = QLabel("Тип заказчика:")
        type_label.setStyleSheet("""
            QLabel {
                color: black;
                font-family: 'MS Shell Dlg 2';
            }
        """)
        self.type_combo = QComboBox()
        self.type_combo.addItem("Юридическое лицо", 1)
        self.type_combo.addItem("Физическое лицо", 2)
        self.type_combo.currentIndexChanged.connect(self.toggle_company_field)
        self.type_combo.setStyleSheet("""
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
        form_layout.addRow(type_label, self.type_combo)

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

        self.register_btn = QPushButton("Зарегистрировать")
        self.register_btn.setStyleSheet("""
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
        self.register_btn.clicked.connect(self.register_customer)
        main_layout.addWidget(self.register_btn)

        self.toggle_company_field()

    def format_phone_number(self):
        """Позволяет вводить номер по формату"""
        text = self.phone_edit.text()
        if not text.startswith('+') and text:
            self.phone_edit.setText('+' + text)

    def toggle_company_field(self):
        if self.type_combo.currentData() == 2:
            self.company_edit.setEnabled(False)
            self.company_edit.clear()
        else:
            self.company_edit.setEnabled(True)

    def register_customer(self):
        data = {
            'type_id': self.type_combo.currentData(),
            'company': self.company_edit.text().strip(),
            'surname': self.surname_edit.text().strip(),
            'name': self.name_edit.text().strip(),
            'patronymic': self.patronymic_edit.text().strip(),
            'phone': self.phone_edit.text().strip(),
            'email': self.email_edit.text().strip(),
            'login': self.login_edit.text().strip(),
            'password': self.password_edit.text().strip()
        }

        if not data['phone'].startswith('+'):
            data['phone'] = '+' + data['phone']

        # Проверка данных
        errors = []
        if data['type_id'] == 1 and not data['company']:
            errors.append("Укажите название компании для юр. лица")
        if not data['surname']:
            errors.append("Укажите фамилию")
        if not data['name']:
            errors.append("Укажите имя")
        if not data['phone'] or len(data['phone']) < 5:
            errors.append("Некорректный номер телефона")
        if not data['email'] or '@' not in data['email']:
            errors.append("Некорректный email")
        if not data['login']:
            errors.append("Укажите логин")
        if not data['password']:
            errors.append("Укажите пароль")

        if errors:
            QMessageBox.warning(None, "Ошибка", "\n".join(errors))
            return

        if self.check_login_exists(data['login']):
            QMessageBox.warning(None, "Ошибка", "Этот логин уже занят")
            return

        try:
            conn = connect_to_db()
            if not conn:
                raise Exception("Не удалось подключиться к базе данных")

            cursor = conn.cursor()

            query = """
                INSERT INTO customer (
                    company_name, surname, name, patronymic,
                    login, password, phone, email, id_type_customer
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                data['company'] if data['type_id'] == 1 else '',
                data['surname'],
                data['name'],
                data['patronymic'],
                data['login'],
                data['password'],
                data['phone'],
                data['email'],
                data['type_id']
            )

            cursor.execute(query, values)
            conn.commit()

            QMessageBox.information(None, "Успех",
                                    "Заказчик успешно зарегистрирован!")
            self.clear_form()

        except Exception as e:
            QMessageBox.critical(None, "Ошибка",
                                 f"Ошибка при сохранении данных: {str(e)}")
        finally:
            if 'conn' in locals():
                cursor.close()
                conn.close()

    def check_login_exists(self, login):
        try:
            conn = connect_to_db()
            if not conn:
                return True

            cursor = conn.cursor()

            # Проверка в таблице customer
            cursor.execute("SELECT id FROM customer WHERE login = %s", (login,))
            if cursor.fetchone() is not None:
                return True  # Логин найден в customer

            # Проверка в таблице worker
            cursor.execute("SELECT id FROM worker WHERE login = %s", (login,))
            return cursor.fetchone() is not None  # Возвращает True, если найден в worker

        except Exception as e:
            print(f"Ошибка проверки логина: {e}")
            return True  # При ошибке считаем логин существующим
        finally:
            if 'conn' in locals():
                cursor.close()
                conn.close()

    def clear_form(self):
        """Очищение полей после добавления заказчика"""
        self.type_combo.setCurrentIndex(0)
        self.company_edit.clear()
        self.surname_edit.clear()
        self.name_edit.clear()
        self.patronymic_edit.clear()
        self.phone_edit.clear()
        self.email_edit.clear()
        self.login_edit.clear()
        self.password_edit.clear()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())