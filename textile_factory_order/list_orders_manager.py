import pymysql
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
                             QLabel, QHBoxLayout, QLineEdit, QPushButton, QDialog,QMessageBox)
from factory_bd import get_orders_status, update_order_status, get_product_materials, get_order_products


def set_global_font(app):
    font = QtGui.QFont("MS Shell Dlg 2", 9)
    app.setFont(font)


class OrderDetailsDialog(QDialog):
    """Окно для подробной информации о заказе"""
    def __init__(self, order_data, parent=None):
        super().__init__(parent)
        self.order_data = order_data
        self.setWindowTitle(f"Информация о заказе №{order_data['order_id']}")
        self.setFixedSize(500, 600)

        dialog_font = QtGui.QFont("MS Shell Dlg 2", 9)
        self.setFont(dialog_font)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.setStyleSheet("""
            * {
                font-family: "MS Shell Dlg 2";
                font-size: 9pt;
            }
            QDialog { 
                background-color: rgb(181, 213, 202);
            }
            .header-label {
                font-weight: bold;
                color: #2c3e50;
            }
            .product-title {
                font-weight: bold; 
                color: #2c3e50;
                margin-top: 10px;
            }
            .material-info {
                margin-left: 20px;
                color: #555;
            }
            QComboBox {
                padding: 5px;
                border-radius: 3px;
                background-color: white;
            }
            QPushButton {
                padding: 5px 15px;
                border-radius: 3px;
                background-color: rgb(224, 169, 175);
                color: white;
            }
            QPushButton:hover {
                background-color: rgb(200, 149, 155);
            }
        """)

        info_layout = QVBoxLayout()
        self.add_bold_label(info_layout, "Дата создания:", order_data['order_date'])
        self.add_bold_label(info_layout, "Статус:", order_data['status_name'])
        self.add_bold_label(info_layout, "Компания:", order_data['company'])
        self.add_bold_label(info_layout, "Заказчик:", order_data['customer_name'])
        self.add_bold_label(info_layout, "Телефон:", order_data['customer_phone'])
        self.add_bold_label(info_layout, "Email:", order_data['customer_email'])
        main_layout.addLayout(info_layout)

        # Секция с изделиями
        products = get_order_products(order_data['order_id'])
        if products:
            products_layout = QVBoxLayout()
            title_label = QLabel("Изделия в заказе:")
            title_label.setProperty("class", "product-title")
            products_layout.addWidget(title_label)

            for idx, product in enumerate(products, 1):
                product_layout = QVBoxLayout()
                self.add_product_info(product_layout, f"Изделие {idx}:", product['product_type'])
                self.add_product_info(product_layout, "Размеры:", f"{product['length']}см x {product['width']}см")
                self.add_product_info(product_layout, "Количество:", f"{product['quantity']} шт")

                # Материалы
                materials = get_product_materials(product['id'])
                if materials:
                    materials_label = QLabel("Материалы:")
                    materials_label.setProperty("class", "material-info")
                    product_layout.addWidget(materials_label)
                    for material in materials:
                        text = f"• {material['material_name']} ({material['category_name']})"
                        mat_label = QLabel(text)
                        mat_label.setProperty("class", "material-info")
                        product_layout.addWidget(mat_label)

                products_layout.addLayout(product_layout)

            main_layout.addLayout(products_layout)

        # Итоговая сумма
        total_label = QLabel(f"Итоговая стоимость: {self.order_data.get('price_with_profit', 0)} руб")
        total_label.setProperty("class", "header-label")
        total_label.setStyleSheet("margin-top: 10px;")
        main_layout.addWidget(total_label)

        if order_data['status_id'] == 1:  # Показывать только если статус = 1 (новый)
            status_layout = QHBoxLayout()
            status_label = QLabel("Статус:")
            status_label.setProperty("class", "header-label")
            status_layout.addWidget(status_label)

            self.status_combo = QtWidgets.QComboBox()
            self.status_combo.setFont(dialog_font)
            self.load_statuses()
            status_layout.addWidget(self.status_combo)
            main_layout.addLayout(status_layout)

            self.save_btn = QPushButton("Сохранить статус")
            self.save_btn.setFont(dialog_font)
            self.save_btn.clicked.connect(self.save_status)
            main_layout.addWidget(self.save_btn)

    def add_bold_label(self, layout, title, value):
        """Метка с жирным заголовком"""
        label = QLabel(f"<b>{title}</b> {value}")
        label.setTextFormat(QtCore.Qt.TextFormat.RichText)
        layout.addWidget(label)

    def add_product_info(self, layout, title, value):
        """Информация о продукте"""
        label = QLabel(f"<b>{title}</b> {value}")
        label.setTextFormat(QtCore.Qt.TextFormat.RichText)
        label.setStyleSheet("margin-left: 10px;")
        layout.addWidget(label)

    def load_statuses(self):
        """Загружает статусы 'Подтвержден менеджером' и 'Не подтвержден менеджером'"""
        try:
            # Подключаемся к бд и получаем статусы
            connection = pymysql.connect(
                host="fatima6p.beget.tech",
                user="fatima6p_orange",
                password="password",
                database="fatima6p_orange",
                charset='utf8mb4',
                connect_timeout=10,
                cursorclass=pymysql.cursors.DictCursor
            )
            with connection.cursor() as cursor:
                # Выбираем только статусы с id 3 и 4
                cursor.execute("SELECT id, name FROM order_status WHERE id IN (3, 4)")
                statuses = cursor.fetchall()
                for status in statuses:
                    self.status_combo.addItem(status['name'], status['id'])
        except Exception as e:
            print(f"Ошибка при загрузке статусов: {e}")
            QMessageBox.critical(self, "Ошибка", "Не удалось загрузить статусы")
        finally:
            if connection:
                connection.close()

    def save_status(self):
        """Сохраняет выбранный статус заказа"""
        new_status_id = self.status_combo.currentData()  # Получаем ID выбранного статуса
        order_id = self.order_data['order_id']

        try:
            # Вызываем функцию для обновления статуса в базе данных
            success = update_order_status(order_id, new_status_id)
            if success:
                QMessageBox.information(self, "Успех", "Статус заказа успешно обновлен!")
                self.accept()  # Закрытие диалогового окна
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось обновить статус заказа")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка базы данных: {str(e)}")


class OrderItemWidget(QWidget):
    """Элемент списка"""
    def __init__(self, order_data, bg_color, parent=None):
        super().__init__(parent)
        self.order_data = order_data
        print(f"[DEBUG] Создаем OrderItemWidget с данными: {order_data}")
        self.setup_ui(order_data, bg_color)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed
        )

    def setup_ui(self, order, bg_color):
        print(f"[DEBUG] Настройка интерфейса для заказа: {order}")
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

        try:
            self.order_date = QLabel(order['order_date'])
        except KeyError:
            formatted_date = order['create_date'].strftime("%d.%m.%Y в %H:%M")
            self.order_date = QLabel(formatted_date)

        self.order_date.setStyleSheet("""
            font-size: 12px; 
            color: black;
            font-family: 'MS Shell Dlg 2';
        """)

        top_layout.addWidget(self.order_number)
        top_layout.addStretch()
        top_layout.addWidget(self.order_date)
        main_layout.addLayout(top_layout)

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
    def __init__(self, user_data=None):
        self.user_data = user_data  # Данные пользователя

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setStyleSheet("""
            background-color: rgb(181, 213, 202);
            font-family: 'MS Shell Dlg 2';
        """)

        main_layout = QVBoxLayout(Form)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        self.header = QLabel("СПИСОК ЗАКАЗОВ")
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

        self.list_widget.resizeEvent = self.handle_resize
        self.load_orders()
        self.list_widget.itemDoubleClicked.connect(self.show_order_details)

    def show_order_details(self, item):
        """Показывает детали заказа при двойном клике"""
        widget = self.list_widget.itemWidget(item)
        if widget and hasattr(widget, 'order_data'):
            try:
                dialog = OrderDetailsDialog(widget.order_data)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    # Обновление списка при измененном статусе
                    self.load_orders()
            except KeyError as e:
                print(f"Ошибка отображения данных: отсутствует поле {e}")

    def handle_resize(self, event):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item_widget = self.list_widget.itemWidget(item)
            if item_widget:
                new_width = self.list_widget.width() - 20
                item.setSizeHint(QtCore.QSize(new_width, 100))
        super(QListWidget, self.list_widget).resizeEvent(event)

    def load_orders(self, status_filter=None):
        manager_id = None
        if self.user_data and self.user_data['type'] == 'worker':
            manager_id = self.user_data['id']

        orders = get_orders_status(manager_id=manager_id, status_filter=status_filter)
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

    def on_search_clicked(self):
        """Обработчик нажатия на Поиск"""
        search_text = self.search_field.text().strip()  # Получаем текст из поля
        self.load_orders(status_filter=search_text)  # Загрузить заказы с фильтром по статусу


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    set_global_font(app)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())