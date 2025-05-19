from PyQt6.QtCore import QTime
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QTimeEdit, QComboBox, QMessageBox
from database import update_train, delete_user

class AddDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить поезд")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()
        self.name_edit = QLineEdit()
        self.departure_time_edit = QTimeEdit()
        self.arrival_time_edit = QTimeEdit()
        self.route_edit = QLineEdit()
        self.platform_edit = QLineEdit()
        self.path_edit = QLineEdit()

        layout.addWidget(QLabel("Название"))
        layout.addWidget(self.name_edit)
        layout.addWidget(QLabel("Время отправления"))
        layout.addWidget(self.departure_time_edit)
        layout.addWidget(QLabel("Время прибытия"))
        layout.addWidget(self.arrival_time_edit)
        layout.addWidget(QLabel("Маршрут"))
        layout.addWidget(self.route_edit)

        self.status_edit = QComboBox()
        self.status_edit.addItems(["Вовремя", "Опаздывает"])
        layout.addWidget(QLabel("Статус"))
        layout.addWidget(self.status_edit)

        self.schedule_edit = QComboBox()
        self.schedule_edit.addItems(["Каждый день", "По будним", "По выходным"])
        layout.addWidget(QLabel("Расписание по дням"))
        layout.addWidget(self.schedule_edit)

        self.direction_edit = QComboBox()
        self.direction_edit.addItems(["Из Москвы", "В Москву", "Не указано"])
        layout.addWidget(QLabel("Направление"))
        layout.addWidget(self.direction_edit)

        layout.addWidget(QLabel("Платформа"))
        layout.addWidget(self.platform_edit)

        layout.addWidget(QLabel("Путь"))
        layout.addWidget(self.path_edit)

        buttons_layout = QHBoxLayout()
        btn_add = QPushButton("Добавить")
        btn_add.clicked.connect(self.accept)
        buttons_layout.addWidget(btn_add)

        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(btn_cancel)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)


class EditDialog(QDialog):
    def __init__(self, train_id, name, departure_time, arrival_time, route, status, schedule, platform, path, direction):
        super().__init__()
        self.setWindowTitle("Редактировать поезд")
        self.setGeometry(100, 100, 300, 200)
        layout = QVBoxLayout()
        self.name_edit = QLineEdit(name)
        self.departure_time_edit = QTimeEdit()
        self.departure_time_edit.setDisplayFormat("HH:mm")
        self.departure_time_edit.setTime(QTime.fromString(departure_time, "HH:mm"))
        self.arrival_time_edit = QTimeEdit()
        self.arrival_time_edit.setDisplayFormat("HH:mm")
        self.arrival_time_edit.setTime(QTime.fromString(arrival_time, "HH:mm"))
        self.route_edit = QLineEdit(route)
        self.platform_edit = QLineEdit(platform)
        self.path_edit = QLineEdit(path)
        self.train_id = train_id

        layout.addWidget(QLabel("Название"))
        layout.addWidget(self.name_edit)
        layout.addWidget(QLabel("Время отправления"))
        layout.addWidget(self.departure_time_edit)
        layout.addWidget(QLabel("Время прибытия"))
        layout.addWidget(self.arrival_time_edit)
        layout.addWidget(QLabel("Маршрут"))
        layout.addWidget(self.route_edit)

        self.status_edit = QComboBox()
        self.status_edit.addItems(["Вовремя", "Опаздывает", "Отменена"])
        self.status_edit.setCurrentText(status)
        layout.addWidget(QLabel("Статус"))
        layout.addWidget(self.status_edit)

        self.schedule_edit = QComboBox()
        self.schedule_edit.addItems(["Каждый день", "По будним", "По выходным"])
        self.schedule_edit.setCurrentText(schedule)
        layout.addWidget(QLabel("Расписание по дням"))
        layout.addWidget(self.schedule_edit)

        self.direction_edit = QComboBox()
        self.direction_edit.addItems(["Из Москвы", "В Москву", "Не указано"])
        self.direction_edit.setCurrentText(direction)
        layout.addWidget(QLabel("Направление"))
        layout.addWidget(self.direction_edit)


        layout.addWidget(QLabel("Платформа"))
        layout.addWidget(self.platform_edit)

        layout.addWidget(QLabel("Путь"))
        layout.addWidget(self.path_edit)

        buttons_layout = QHBoxLayout()
        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.save_data)
        buttons_layout.addWidget(btn_save)
        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(btn_cancel)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def save_data(self):
        # Сбор данных из полей ввода
        name = self.name_edit.text()
        departure_time = self.departure_time_edit.time().toString("HH:mm")
        arrival_time = self.arrival_time_edit.time().toString("HH:mm")
        route = self.route_edit.text()
        status = self.status_edit.currentText()
        schedule = self.schedule_edit.currentText()
        platform = self.platform_edit.text()
        path = self.path_edit.text()
        direction = self.status_edit.currentText()

        # Обновление данных в базе данных
        update_train(self.train_id, name, departure_time, arrival_time, route, status, schedule, platform, path, direction)

        # Закрытие диалогового окна
        self.accept()


class DeleteUserDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Удалить пользователя")
        self.setGeometry(100, 100, 250, 150)
        layout = QVBoxLayout()

        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addWidget(QLabel("Имя пользователя"))
        layout.addWidget(self.username_edit)
        layout.addWidget(QLabel("Пароль"))
        layout.addWidget(self.password_edit)

        buttons_layout = QHBoxLayout()
        delete_button = QPushButton("Удалить")
        delete_button.clicked.connect(self.confirm_delete)
        buttons_layout.addWidget(delete_button)

        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def confirm_delete(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        if delete_user(username, password):
            QMessageBox.information(self, "Успех", "Пользователь удален.")
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверное имя пользователя или пароль.")