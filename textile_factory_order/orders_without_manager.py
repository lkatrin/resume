from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
                             QLabel, QHBoxLayout, QLineEdit, QPushButton, QMessageBox)
from factory_bd import get_orders_without_manager, assign_manager_to_order


class OrderItemWidget(QWidget):
    """Элемент списка"""
    def __init__(self, order_data, bg_color, parent=None):
        super().__init__(parent)
        self.order_data = order_data  # Сохраняем данные заказа
        self.setup_ui(order_data, bg_color)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed
        )

    def setup_ui(self, order, bg_color):
        self.setMinimumHeight(100)
        self.setStyleSheet(f"""
            background-color: {bg_color}; 
            border-radius: 5px;
            font-family: 'MS Shell Dlg 2';
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.setSpacing(5)

        top_layout = QHBoxLayout()
        self.order_number = QLabel(f"Заказ №{order['order_id']}")
        self.order_number.setStyleSheet("""
            font-weight: bold; 
            font-size: 14px; 
            color: black;
            font-family: 'MS Shell Dlg 2';
        """)

        self.order_date = QLabel(order['order_date'])
        self.order_date.setStyleSheet("""
            font-size: 12px; 
            color: black;
            font-family: 'MS Shell Dlg 2';
        """)

        top_layout.addWidget(self.order_number)
        top_layout.addStretch()
        top_layout.addWidget(self.order_date)
        main_layout.addLayout(top_layout)

        # Информация о заказе
        self.company_info = QLabel(order['company'])
        self.company_info.setStyleSheet("""
            font-size: 12px; 
            color: black;
            font-family: 'MS Shell Dlg 2';
        """)
        main_layout.addWidget(self.company_info)

        self.customer_name = QLabel(f"Заказчик: {order['customer_name']}")
        self.customer_name.setStyleSheet("""
            font-size: 12px; 
            color: black;
            font-family: 'MS Shell Dlg 2';
        """)
        main_layout.addWidget(self.customer_name)

        # Нижняя строка
        bottom_layout = QHBoxLayout()
        self.products_count = QLabel(f"Количество: {order['total_products']}")
        self.products_count.setStyleSheet("""
            font-size: 12px; 
            color: black;
            font-family: 'MS Shell Dlg 2';
        """)

        self.status_label = QLabel(f"Статус: {order['status_name']}")
        self.status_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 12px; 
            color: black;
            font-family: 'MS Shell Dlg 2';
        """)
        self.status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight |
                                       QtCore.Qt.AlignmentFlag.AlignBottom)

        bottom_layout.addWidget(self.products_count)
        bottom_layout.addWidget(self.status_label)
        main_layout.addLayout(bottom_layout)


class Ui_Form:
    def __init__(self, user_data=None, on_assignment_callback=None):
        self.user_data = user_data
        self.on_assignment_callback = on_assignment_callback

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setStyleSheet("""
            background-color: rgb(181, 213, 202);
            font-family: 'MS Shell Dlg 2';
        """)

        main_layout = QVBoxLayout(Form)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        self.header = QLabel("НЕ НАЗНАЧЕННЫЕ ЗАКАЗЫ")
        self.header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: black;
                padding: 8px;
                background-color: rgb(181, 213, 202);
                border-radius: 5px;
                font-family: 'MS Shell Dlg 2';
            }
        """)
        main_layout.addWidget(self.header)

        # Поисковая строка
        search_layout = QHBoxLayout()
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Поиск заказов...")
        self.search_field.setStyleSheet("""
            background-color: white; 
            border-radius: 3px;
            font-family: 'MS Shell Dlg 2';
        """)

        self.search_btn = QPushButton("Найти")
        self.search_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(224, 169, 175);
                color: white;
                padding: 5px 15px;
                border-radius: 3px;
                font-size: 13px;
                font-family: 'MS Shell Dlg 2';
            }
        """)

        search_layout.addWidget(self.search_field)
        search_layout.addWidget(self.search_btn)
        main_layout.addLayout(search_layout)
        self.search_btn.clicked.connect(self.on_search_clicked)

        # Список заказов
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: white;
                border-radius: 5px;
                border: 1px solid #ddd;
                font-family: 'MS Shell Dlg 2';
            }
            QListWidget::item {
                border: none;
                margin-bottom: 5px;
                font-family: 'MS Shell Dlg 2';
            }
        """)
        main_layout.addWidget(self.list_widget)

        # Обработчик изменения размеров
        self.list_widget.resizeEvent = self.handle_resize
        self.load_orders()

        self.list_widget.itemDoubleClicked.connect(self.assign_manager)

    def assign_manager(self, item):
        """Назначение менеджера на заказ"""
        widget = self.list_widget.itemWidget(item)
        if widget and hasattr(widget, 'order_data'):
            order_id = widget.order_data['order_id']
            manager_id = self.user_data['id'] if self.user_data else None

            if not manager_id:
                QMessageBox.warning(self.list_widget, "Ошибка", "Не удалось определить менеджера")
                return

            try:
                success = assign_manager_to_order(order_id, manager_id)
                if success:
                    QMessageBox.information(self.list_widget, "Успех", "Заказ успешно назначен!")
                    self.load_orders()  # Обновляем список
                    if self.on_assignment_callback:
                        self.on_assignment_callback()
                else:
                    QMessageBox.warning(self.list_widget, "Ошибка", "Не удалось назначить заказ")
            except Exception as e:
                QMessageBox.critical(self.list_widget, "Ошибка", f"Ошибка базы данных: {str(e)}")


    def handle_resize(self, event):
        """Обновление размеров элементов при изменении окна"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item_widget = self.list_widget.itemWidget(item)
            if item_widget:
                new_width = self.list_widget.width() - 20
                item.setSizeHint(QtCore.QSize(new_width, 100))
        super(QListWidget, self.list_widget).resizeEvent(event)

    def on_search_clicked(self):
        """Обработчик нажатия на кнопку поиска"""
        search_text = self.search_field.text().strip()  # Получить текст из поискового поля
        self.load_orders(customer_filter=search_text)  # Загрузить заказы

    def load_orders(self, customer_filter=None):
        """Получение данных о заказах"""
        orders = get_orders_without_manager(customer_filter)
        self.list_widget.clear()

        colors = ["rgb(255, 252, 214)", "rgb(209, 238, 252)"]   # Для чередования цветов

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


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())