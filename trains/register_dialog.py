from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QApplication
from database import add_user

class RegisterDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация пользователя")
        self.setGeometry(100, 100, 200, 150)

        self.setStyleSheet("background-color: #f0f0f0;")  # Фон диалога

        layout = QVBoxLayout()

        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        self.register_button = QPushButton("Зарегистрироваться")
        self.register_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 10px; }"
                                           "QPushButton:hover { background-color: #45a049; }")  # Стиль кнопки
        self.register_button.clicked.connect(self.register)

        layout.addWidget(QLabel("Имя пользователя"))
        layout.addWidget(self.username_edit)
        layout.addWidget(QLabel("Пароль"))
        layout.addWidget(self.password_edit)
        layout.addWidget(self.register_button)

        self.setGeometry(100, 100, 200, 150)  # Устанавливаем размер
        self.center_on_screen()  # Центрируем окно

        self.setLayout(layout)

    def register(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        if username and password:
            add_user(username, password)
            QMessageBox.information(self, "Регистрация", "Пользователь успешно зарегистрирован.")
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Имя пользователя и пароль не могут быть пустыми")

    def center_on_screen(self):
        """ Центрирует окно на экране """
        center_point = QApplication.primaryScreen().geometry().center()
        frame_geo = self.frameGeometry()
        frame_geo.moveCenter(center_point)
        self.move(frame_geo.topLeft())