from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
                             QLabel, QHBoxLayout, QLineEdit, QPushButton)
from factory_bd import get_orders


class OrderItemWidget(QWidget):
    def __init__(self, order_data, bg_color, parent=None):
        super().__init__(parent)
        self.setup_ui(order_data, bg_color)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed
        )

    def setup_ui(self, order, bg_color):
        self.setMinimumHeight(100)
        self.setStyleSheet(f"background-color: {bg_color}; border-radius: 5px;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.setSpacing(5)

        # Верхняя строка
        top_layout = QHBoxLayout()
        self.order_number = QLabel(f"Заказ №{order['order_id']}")
        self.order_number.setStyleSheet("font-weight: bold; font-size: 14px; color: black;")

        self.order_date = QLabel(order['order_date'])
        self.order_date.setStyleSheet("font-size: 12px; color: black;")

        top_layout.addWidget(self.order_number)
        top_layout.addStretch()
        top_layout.addWidget(self.order_date)
        main_layout.addLayout(top_layout)

        # Информация о заказе
        self.company_info = QLabel(order['company'])
        self.company_info.setStyleSheet("font-size: 12px; color: black;")
        main_layout.addWidget(self.company_info)

        self.customer_name = QLabel(f"Заказчик: {order['customer_name']}")
        self.customer_name.setStyleSheet("font-size: 12px; color: black;")
        main_layout.addWidget(self.customer_name)

        # Нижняя строка
        bottom_layout = QHBoxLayout()
        self.products_count = QLabel(f"Количество: {order['total_products']}")
        self.products_count.setStyleSheet("font-size: 12px; color: black;")

        self.status_label = QLabel(f"Статус: {order['status_name']}")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 12px; color: black;")
        self.status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight |
                                       QtCore.Qt.AlignmentFlag.AlignBottom)

        bottom_layout.addWidget(self.products_count)
        bottom_layout.addWidget(self.status_label)
        main_layout.addLayout(bottom_layout)


class Ui_Form:
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setStyleSheet("background-color: rgb(181, 213, 202);")

        main_layout = QVBoxLayout(Form)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Заголовок
        self.header = QLabel("МОИ ЗАКАЗЫ (м)")
        self.header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: black;
                padding: 8px;
                background-color: rgb(181, 213, 202);
                border-radius: 5px;
            }
        """)
        main_layout.addWidget(self.header)

        # Поисковая строка
        search_layout = QHBoxLayout()
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Поиск заказов...")
        self.search_field.setStyleSheet("background-color: white; border-radius: 3px;")

        self.search_btn = QPushButton("Найти")
        self.search_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(224, 169, 175);
                color: black;
                padding: 5px 15px;
                border-radius: 3px;
            }
        """)

        search_layout.addWidget(self.search_field)
        search_layout.addWidget(self.search_btn)
        main_layout.addLayout(search_layout)

        # Список заказов
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: white;
                border-radius: 5px;
                border: 1px solid #ddd;
            }
            QListWidget::item {
                border: none;
                margin-bottom: 5px;
            }
        """)
        main_layout.addWidget(self.list_widget)

        self.list_widget.resizeEvent = self.handle_resize
        self.load_orders()

    def handle_resize(self, event):
        """Обновление размеров элементов при изменении окна"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item_widget = self.list_widget.itemWidget(item)
            if item_widget:
                new_width = self.list_widget.width() - 20
                item.setSizeHint(QtCore.QSize(new_width, 100))
        super(QListWidget, self.list_widget).resizeEvent(event)

    def load_orders(self):
        orders = get_orders()
        self.list_widget.clear()

        colors = ["rgb(255, 252, 214)", "rgb(209, 238, 252)"]

        for idx, order in enumerate(orders):
            bg_color = colors[idx % 2]
            item_widget = OrderItemWidget(order, bg_color)

            item = QListWidgetItem()
            item.setSizeHint(QtCore.QSize(
                self.list_widget.width() - 20,
                100
            ))

            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, item_widget)