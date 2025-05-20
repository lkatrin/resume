import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QStackedWidget, QWidget,
                             QVBoxLayout, QListWidget, QHBoxLayout, QLabel, QPushButton, QDialog)
from PyQt6 import QtCore, QtGui
from list_orders_manager import Ui_Form as Ui_ListOrdersForm
from myorder_customer import Ui_Form as Ui_MyOrderCustomer
from new_order import Ui_Form as Ui_NewOrder
from customer_registration import Ui_Form as Ui_CustomerRegistration
from orders_without_manager import Ui_Form as Ui_WithoutManager
from new_order_client import Ui_Form as Ui_NewOrder2
from customer_redaction import Ui_EditCustomerForm as Ui_CustomerRedaction


def set_global_font(app):
    font = QtGui.QFont("MS Shell Dlg 2", 9)
    app.setFont(font)


class ProfileDialog(QDialog):
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Профиль")
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            background-color: rgb(181, 213, 202);
            font-family: 'MS Shell Dlg 2';
        """)
        self.orders_form = None  # Будем хранить ссылку на форму заказов

        if parent:
            parent_geometry = parent.geometry()
            x = parent_geometry.center().x() - self.width() // 2
            y = parent_geometry.center().y() - self.height() // 2
            self.move(x, y)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_label = QLabel("Информация о профиле")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: black;
            padding: 10px;
        """)
        layout.addWidget(title_label)

        # Отображение информации о пользователе
        if user_data:
            print("Отладка: Данные пользователя получены в ProfileDialog:", user_data)
            full_name = f"{user_data['surname']} {user_data['name']} {user_data['patronymic']}"
            self.add_info_field(layout, "ФИО:", full_name)
            self.add_info_field(layout, "Логин:", user_data['login'])
            self.add_info_field(layout, "Роль:", user_data['role'])
        else:
            print("Отладка: Данные пользователя отсутствуют (Гость)")
            self.add_info_field(layout, "Статус:", "Гость")

        close_btn = QPushButton("Закрыть")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(224, 169, 175);
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px;
                font-family: 'MS Shell Dlg 2';
            }
            QPushButton:hover {
                background-color: rgb(200, 149, 155);
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def add_info_field(self, layout, label_text, value_text):
        """Добавляет поле с информацией в layout"""
        field_layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setStyleSheet("font-size: 14px; font-weight: bold; color: black;")
        value = QLabel(value_text)
        value.setStyleSheet("font-size: 14px; color: black;")
        field_layout.addWidget(label)
        field_layout.addWidget(value)
        layout.addLayout(field_layout)


class MainWindow(QMainWindow):
    def __init__(self, user_data=None):
        super().__init__()
        self.user_data = user_data
        self.setWindowTitle("Главное меню")
        self.resize(700, 700)
        self.setStyleSheet("""
            background-color: rgb(181, 213, 202);
            font-family: 'MS Shell Dlg 2';
        """)
        print(f"Открыто главное окно для пользователя: {self.user_data}")

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Левое меню
        left_menu = QWidget()
        left_menu.setFixedWidth(165)
        left_layout = QVBoxLayout(left_menu)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(15)

        logo_label = QLabel()
        logo_pixmap = QtGui.QPixmap("logo-01.jpg")
        logo_label.setPixmap(logo_pixmap.scaled(120, 150,
                                                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                                QtCore.Qt.TransformationMode.SmoothTransformation))
        logo_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(logo_label)

        # Кнопка Профиль
        self.profile_btn = QPushButton()
        self.profile_btn.setStyleSheet("""
                           QPushButton {
                               background-color: rgb(224, 169, 175);
                               color: white;
                               font-weight: bold;
                               border-radius: 5px;
                               padding: 8px;
                               font-family: 'MS Shell Dlg 2';
                           }
                           QPushButton:hover {
                               background-color: rgb(200, 149, 155);
                           }
                       """)
        self.profile_btn.setFixedHeight(40)

        # Устанавливаем текст кнопки
        if self.user_data:
            full_name = f"{self.user_data['surname']} {self.user_data['name']}"
            self.profile_btn.setText(full_name)
        else:
            self.profile_btn.setText("Гость")

        self.profile_btn.clicked.connect(self.show_profile)
        left_layout.addWidget(self.profile_btn)

        # Навигация
        nav_label = QLabel("Навигация")
        nav_label.setStyleSheet("font-size: 16px; font-weight: bold; color: black; padding: 5px;")
        left_layout.addWidget(nav_label)

        # Список меню
        self.menu_list = QListWidget()
        self.menu_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border-radius: 5px;
                color: black;
            }
            QListWidget::item {
                padding: 8px;
            }
            QListWidget::item:selected {
                background-color: rgb(224, 169, 175);
                color: white;
            }
        """)

        # Определение пунктов меню в зависимости от роли
        if self.user_data and self.user_data['type'] == 'customer':
            self.menu_items = ["Создать заказ", "Мои заказы"]
        else:
            self.menu_items = [
                "Список заказов",
                "Создание заказа",
                "Не назначенные заказы",
                "Регистрация заказчика",
                "Редактирование заказчика"
            ]
        self.menu_list.addItems(self.menu_items)
        left_layout.addWidget(self.menu_list)

        # Область контента
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)

        main_layout.addWidget(left_menu)
        main_layout.addWidget(content_area)

        # Инициализация форм
        self.init_forms(self.menu_items)
        self.menu_list.currentRowChanged.connect(self.switch_form)

    def show_profile(self):
        print("Отладка: Кнопка профиля нажата")
        print("Отладка: Данные пользователя в show_profile:", self.user_data)
        self.profile_dialog = ProfileDialog(self.user_data, self)
        self.profile_dialog.exec()

    def init_forms(self, menu_items):
        """Инициализирует только необходимые формы в зависимости от роли"""
        for item in menu_items:
            if item == "Список заказов":
                self.orders_widget = QWidget()
                self.orders_form = Ui_ListOrdersForm(user_data=self.user_data)  # Передача данных пользователя
                self.orders_form.setupUi(self.orders_widget)
                self.stacked_widget.addWidget(self.orders_widget)

            elif item == "Создание заказа":
                self.new_order_widget = QWidget()
                self.new_order_form = Ui_NewOrder(user_data=self.user_data)
                self.new_order_form.setupUi(self.new_order_widget)
                self.stacked_widget.addWidget(self.new_order_widget)
            elif item == "Создать заказ":
                self.new_order_widget = QWidget()
                self.new_order_form = Ui_NewOrder2(user_data=self.user_data)
                self.new_order_form.setupUi(self.new_order_widget)
                self.stacked_widget.addWidget(self.new_order_widget)
            elif item == "Мои заказы":
                self.my_orders_widget = QWidget()
                self.my_orders_form = Ui_MyOrderCustomer(user_data=self.user_data)
                self.my_orders_form.setupUi(self.my_orders_widget)
                self.stacked_widget.addWidget(self.my_orders_widget)
            elif item == "Не назначенные заказы":
                self.without_manager_widget = QWidget()
                self.without_manager_form = Ui_WithoutManager(
                    user_data=self.user_data,
                    on_assignment_callback=self.update_orders_list)  # Передаем callback
                self.without_manager_form.setupUi(self.without_manager_widget)
                self.stacked_widget.addWidget(self.without_manager_widget)

            elif item == "Регистрация заказчика":
                self.registration_widget = QWidget()
                self.registration_form = Ui_CustomerRegistration()
                self.registration_form.setupUi(self.registration_widget)
                self.stacked_widget.addWidget(self.registration_widget)

            elif item == "Редактирование заказчика":
                self.redaction_widget = QWidget()
                self.redaction_form = Ui_CustomerRedaction()
                self.redaction_form.setupUi(self.redaction_widget)
                self.stacked_widget.addWidget(self.redaction_widget)

    def switch_form(self, index):
        self.stacked_widget.setCurrentIndex(index)

        if 0 <= index < len(self.menu_items):
            current_item = self.menu_items[index]

            # Для клиента
            if current_item == "Мои заказы" and hasattr(self, 'my_orders_form'):
                self.my_orders_form.load_orders()

            # Для менеджера
            if current_item == "Список заказов" and hasattr(self, 'orders_form'):
                self.orders_form.load_orders()

    def update_orders_list(self):
        """Обновляет список заказов менеджера"""
        if self.orders_form:
            self.orders_form.load_orders()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    set_global_font(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())