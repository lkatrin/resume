from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QDialog, QListWidgetItem,
                             QLabel, QHBoxLayout, QLineEdit, QPushButton, QGroupBox, QMessageBox)
from factory_bd import get_orders_customer, get_product_materials, get_order_products
from factory_bd import connect_to_db
import pymysql


class OrderDetailsDialog(QDialog):
    def __init__(self, order_data, parent=None):
        super().__init__(parent)
        self.order_data = order_data
        if 'order_id' not in order_data:
            raise ValueError("Некорректные данные заказа")
        self.setWindowTitle(f"Информация о заказе №{order_data['order_id']}")
        self.setFixedSize(500, 500)

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
        """)

        # Основная информация
        info_layout = QVBoxLayout()
        self.add_bold_label(info_layout, "Дата создания:", order_data['order_date'])
        self.add_bold_label(info_layout, "Статус:", order_data['status_name'])
        self.add_bold_label(info_layout, "Компания:", order_data['company'])
        self.add_bold_label(info_layout, "Заказчик:", order_data['customer_name'])
        manager_name = order_data.get('manager_name', 'Не назначен')
        self.add_bold_label(info_layout, "Менеджер:", manager_name)
        main_layout.addLayout(info_layout)

        # Секция с изделиями
        products = get_order_products(order_data['order_id'])
        if products:
            products_group = QGroupBox("Изделия в заказе")
            products_layout = QVBoxLayout()

            for idx, product in enumerate(products, 1):
                product_group = QGroupBox(f"Изделие {idx}: {product['product_type']}")
                product_layout = QVBoxLayout()

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

                product_group.setLayout(product_layout)
                products_layout.addWidget(product_group)

            products_group.setLayout(products_layout)
            main_layout.addWidget(products_group)

        # Итоговая сумма
        total_label = QLabel(f"Итоговая стоимость: {self.order_data.get('price_with_profit', 0)} руб")
        total_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        main_layout.addWidget(total_label)

    def add_bold_label(self, layout, title, value):
        safe_value = value if value not in [None, ""] else "Не назначен"
        label = QLabel(f"<b>{title}</b> {safe_value}")
        label.setTextFormat(QtCore.Qt.TextFormat.RichText)
        layout.addWidget(label)

    def add_product_info(self, layout, title, value):
        safe_value = value if value is not None else "Н/Д"
        label = QLabel(f"<b>{title}</b> {safe_value}")
        label.setTextFormat(QtCore.Qt.TextFormat.RichText)
        label.setStyleSheet("margin-left: 10px;")
        layout.addWidget(label)


class OrderItemWidget(QWidget):
    def __init__(self, order_data, bg_color, parent=None):
        super().__init__(parent)
        self.order_data = order_data
        self.setup_ui(order_data, bg_color)

    def setup_ui(self, order, bg_color):
        self.setMinimumHeight(180)
        self.setStyleSheet(f"""
            background-color: {bg_color}; 
            border-radius: 8px;
            font-family: 'MS Shell Dlg 2';
            padding: 6px;
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(6)

        # Верхняя строка (номер заказа + дата)
        top_layout = QHBoxLayout()
        self.order_number = QLabel(f"Заказ №{order['order_id']}")
        self.order_number.setStyleSheet("font-weight: bold; font-size: 14px; color: black;")
        self.order_date = QLabel(order['order_date'])
        self.order_date.setStyleSheet("font-size: 12px; color: black;")

        top_layout.addWidget(self.order_number)
        top_layout.addStretch()
        top_layout.addWidget(self.order_date)
        main_layout.addLayout(top_layout)

        # Информация о компании
        self.company_info = QLabel(order['company'])
        self.company_info.setStyleSheet("font-size: 12px; color: black;")
        main_layout.addWidget(self.company_info)

        # Информация о менеджере
        self.manager_name = QLabel(f"Менеджер: {order.get('manager_name', 'Не назначен')}")
        self.manager_name.setStyleSheet("font-size: 12px; color: black;")
        main_layout.addWidget(self.manager_name)

        # Нижняя строка (количество + статус)
        bottom_layout = QHBoxLayout()
        self.products_count = QLabel(f"Количество: {order['total_products']}")
        self.products_count.setStyleSheet("font-size: 12px; color: black;")

        self.status_label = QLabel(f"Статус: {order['status_name']}")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 12px; color: black;")
        self.status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        bottom_layout.addWidget(self.products_count)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.status_label)
        main_layout.addLayout(bottom_layout)

        if order['status_name'] == "Новый":
            self.cancel_btn = QPushButton("Отменить заказ")
            self.cancel_btn.setFixedHeight(30)
            self.cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgb(224, 169, 175);
                    color: white;
                    padding: 8px;
                    border-radius: 5px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: rgb(200, 149, 155);
                }
            """)
            self.cancel_btn.clicked.connect(self.cancel_order)

            # Добавляем вертикальный спейсер перед кнопкой
            main_layout.addStretch()

            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            btn_layout.addWidget(self.cancel_btn)
            main_layout.addLayout(btn_layout)

    def cancel_order(self):
        """Обработчик нажатия на кнопку 'Отменить заказ'"""
        order_id = self.order_data['order_id']
        if self.cancel_order_in_db(order_id):
            self.status_label.setText("Статус: Отменен")
            self.cancel_btn.setEnabled(False)

    def cancel_order_in_db(self, order_id):
        """Обновляет статус заказа на 'Отменен' в бд"""
        conn = connect_to_db()
        if not conn:
            return False

        try:
            with conn.cursor() as cursor:
                query = "UPDATE orders SET status_id = 2 WHERE id = %s AND status_id = 1"
                cursor.execute(query, (order_id,))
                conn.commit()
                return cursor.rowcount > 0

        except pymysql.Error as err:
            print(f"Ошибка отмены заказа: {err}")
            return False
        finally:
            conn.close()


class Ui_Form:
    def __init__(self, user_data=None):
        self.user_data = user_data

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setStyleSheet("""
               background-color: rgb(181, 213, 202);
               font-family: 'MS Shell Dlg 2';
           """)

        main_layout = QVBoxLayout(Form)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        self.header = QLabel("МОИ ЗАКАЗЫ")
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
        self.search_field.setPlaceholderText("Поиск по статусу...")
        self.search_field.setStyleSheet("background-color: white; border-radius: 3px;")

        self.search_btn = QPushButton("Найти")
        self.search_btn.setStyleSheet("""
               QPushButton {
                   background-color: rgb(224, 169, 175);
                   color: white;
                   padding: 5px 15px;
                   border-radius: 3px;
                   font-size: 13px;
               }
               QPushButton:hover {
                   background-color: rgb(200, 149, 155);
               }
           """)

        self.search_btn.clicked.connect(self.on_search_clicked)

        search_layout.addWidget(self.search_field)
        search_layout.addWidget(self.search_btn)
        main_layout.addLayout(search_layout)

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
        self.list_widget.itemDoubleClicked.connect(self.show_order_details)

    def on_search_clicked(self):
        """Обработчик нажатия на кнопку поиска"""
        search_text = self.search_field.text().strip()  # Получить текст из поискового поля
        self.load_orders(status_filter=search_text)  # Загрузить заказы с фильтром

    def handle_resize(self, event):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item_widget = self.list_widget.itemWidget(item)
            if item_widget:
                new_width = self.list_widget.width() - 20
                item.setSizeHint(QtCore.QSize(new_width, 160))
        super(QListWidget, self.list_widget).resizeEvent(event)

    def load_orders(self, status_filter=None):
        """Загружает данные о заказах"""
        customer_id = self.user_data.get('id') if self.user_data and self.user_data['type'] == 'customer' else None
        orders = get_orders_customer(customer_id=customer_id)

        # Применяем фильтр если задан
        if status_filter:
            orders = [order for order in orders if status_filter.lower() in order['status_name'].lower()]

        # Очищаем список и добавляем актуальные данные
        self.list_widget.clear()

        colors = ["rgb(255, 252, 214)", "rgb(209, 238, 252)"]

        for idx, order in enumerate(orders):
            bg_color = colors[idx % 2]
            item_widget = OrderItemWidget(order, bg_color)

            item = QListWidgetItem()
            item.setSizeHint(QtCore.QSize(self.list_widget.width() - 20, 160))

            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, item_widget)

    def show_order_details(self, item):
        """Для открытия подробной информации о заказе"""
        widget = self.list_widget.itemWidget(item)
        if widget and hasattr(widget, 'order_data'):
            try:
                dialog = OrderDetailsDialog(widget.order_data)
                dialog.exec()
            except Exception as e:
                print(f"Ошибка открытия диалога: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
