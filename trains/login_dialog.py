from PyQt6.QtWidgets import QDialog, QVBoxLayout, QApplication, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout
from database import check_user
from register_dialog import RegisterDialog

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход в систему")

        self.setStyleSheet("background-color: #f0f0f0;")

        layout = QVBoxLayout()

        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Войти")
        self.login_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 10px; }"
                                        "QPushButton:hover { background-color: #45a049; }")  # Стиль кнопки
        self.login_button.clicked.connect(self.attempt_login)

        self.register_button = QPushButton("Регистрация")
        self.register_button.setStyleSheet("QPushButton { background-color: #1E88E5; color: white; padding: 10px; }"
                                           "QPushButton:hover { background-color: #1565C0; }")  # Стиль кнопки
        self.register_button.clicked.connect(self.open_register_dialog)

        layout.addWidget(QLabel("Имя пользователя"))
        layout.addWidget(self.username_edit)
        layout.addWidget(QLabel("Пароль"))
        layout.addWidget(self.password_edit)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        self.setGeometry(100, 100, 200, 150)  # Устанавливаем размер
        self.center_on_screen()  # Центрируем окно

        self.setLayout(layout)

    def attempt_login(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        if check_user(username, password):
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Неправильное имя пользователя или пароль")

    def open_register_dialog(self):
        register_dialog = RegisterDialog()
        register_dialog.exec()

    def center_on_screen(self):
        """ Центрирует окно на экране """
        center_point = QApplication.primaryScreen().geometry().center()
        frame_geo = self.frameGeometry()
        frame_geo.moveCenter(center_point)
        self.move(frame_geo.topLeft())

    def reject(self):
        # Дополнительная логика при закрытии окна, если нужно
        super().reject()  # Закрывает диалог и возвращает отказ