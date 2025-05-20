from datetime import datetime

import pymysql
from factory_bd import connect_to_db
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QLineEdit, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QScrollArea, QFrame)
from PyQt6.QtWidgets import QStyledItemDelegate
from PyQt6.QtGui import QColor


class Ui_Form(QWidget):
    def __init__(self,user_data=None):
        super().__init__()
        self.worker_id = None
        self.user_data = user_data
        self.db = connect_to_db()
        self.setupUi(self)

    def set_worker_id(self, worker_id):
        """Устанавливает ID сотрудника"""
        self.worker_id = worker_id
        print(f"[DEBUG] Установлен логин сотрудника: {self.worker_id}")

    def create_order(self):
        """Создает заказ в базе данных"""
        print("[DEBUG] Начало создания заказа.")

        if not self.user_data:
            error_message = "Данные пользователя не установлены."
            print(f"[ОШИБКА] {error_message}")
            QtWidgets.QMessageBox.warning(self, "Ошибка", error_message)
            return

        print(f"[DEBUG] Данные пользователя: {self.user_data}")

        try:
            # Получаем ID заказчика из user_data
            customer_id = self.user_data['id']  # Используем ID пользователя как ID заказчика
            print(f"[DEBUG] Используем ID заказчика из user_data: {customer_id}")

            # ID менеджера NULL
            manager_id = None

            # Собираем данные о продуктах из таблицы
            products = []
            for row in range(self.products_table.rowCount()):
                print(f"[DEBUG] Обработка строки {row + 1} из таблицы.")

                # Проверка заполненности
                row_data = []
                for col in range(self.products_table.columnCount()):
                    item = self.products_table.item(row, col)
                    if item is None or item.text().strip() == "":
                        error_message = f"Не заполнена ячейка в строке {row + 1}, столбец {col + 1}."
                        print(f"[ОШИБКА] {error_message}")
                        QtWidgets.QMessageBox.warning(self, "Ошибка", error_message)
                        return
                    row_data.append(item.text().strip())

                # Извлекаем данные из строки
                product_type = row_data[0]  # Тип продукции
                length = int(row_data[1])  # Длина
                width = int(row_data[2])  # Ширина
                fabric = row_data[3]  # Ткань
                threads = row_data[4]  # Нитки

                # Обработка фурнитуры
                hardware_display = row_data[5]  # Фурнитура (название - количество)
                if hardware_display != "-":
                    hardware, hardware_quantity = hardware_display.split(" - ")
                    hardware_quantity = int(hardware_quantity)
                else:
                    hardware = "-"
                    hardware_quantity = 0

                # Обработка декора
                decor_display = row_data[6]  # Декор (название - количество)
                if decor_display != "-":
                    decor, decor_quantity = decor_display.split(" - ")
                    decor_quantity = int(decor_quantity)
                else:
                    decor = "-"
                    decor_quantity = 0

                lining = row_data[7]  # Подкладка
                quantity = int(row_data[8])  # Количество изделий

                print(f"[DEBUG] Данные из таблицы:")
                print(f"  Тип продукции: {product_type}")
                print(f"  Длина: {length} см")
                print(f"  Ширина: {width} см")
                print(f"  Ткань: {fabric}")
                print(f"  Нитки: {threads}")
                print(f"  Фурнитура: {hardware} (Количество: {hardware_quantity})")
                print(f"  Декор: {decor} (Количество: {decor_quantity})")
                print(f"  Подкладка: {lining}")
                print(f"  Количество изделий: {quantity}")

                # Преобразуем тип продукции в ID
                product_type_id = self.get_product_type_id(product_type)
                if not product_type_id:
                    error_message = f"Тип продукции '{product_type}' не найден в бд"
                    print(f"[ОШИБКА] {error_message}")
                    QtWidgets.QMessageBox.warning(self, "Ошибка", error_message)
                    return

                print(f"[DEBUG] Найден ID типа продукции: {product_type_id}")

                # Получаем ID материалов (ткань, нитки, фурнитура, декор, подкладка)
                fabric_id = self.get_material_id(fabric)
                threads_id = self.get_material_id(threads)
                hardware_id = self.get_material_id(hardware) if hardware != "-" else None
                decor_id = self.get_material_id(decor) if decor != "-" else None
                lining_id = self.get_material_id(lining) if lining != "-" else None

                if not fabric_id or not threads_id:
                    error_message = "Материал (ткань или нитки) не найден в базе данных."
                    print(f"[ОШИБКА] {error_message}")
                    QtWidgets.QMessageBox.warning(self, "Ошибка", error_message)
                    return

                print(f"[DEBUG] Найден ID ткани: {fabric_id}")
                print(f"[DEBUG] Найден ID ниток: {threads_id}")
                print(f"[DEBUG] Найден ID фурнитуры: {hardware_id}")
                print(f"[DEBUG] Найден ID декора: {decor_id}")
                print(f"[DEBUG] Найден ID подкладки: {lining_id}")

                # Материалы
                materials = [
                    {"id": fabric_id, "quantity": 1},  # Ткань
                    {"id": threads_id, "quantity": 1},  # Нитки
                ]
                if hardware_id:
                    materials.append({"id": hardware_id, "quantity": hardware_quantity})  # Фурнитура
                if decor_id:
                    materials.append({"id": decor_id, "quantity": decor_quantity})  # Декор
                if lining_id:
                    materials.append({"id": lining_id, "quantity": 1})  # Подкладка

                products.append({
                    "product_type_id": product_type_id,
                    "length": length,
                    "width": width,
                    "quantity": quantity,
                    "materials": materials
                })

            # Вызов функции добавления заказа
            print("[DEBUG] Вызов функции добавления заказа в базу данных.")
            self.add_order_to_db(manager_id, customer_id, products)

            success_message = "Заказ успешно создан!"
            print(f"[УСПЕХ] {success_message}")
            QtWidgets.QMessageBox.information(self, "Успех", success_message)
            self.products_table.setRowCount(0)

        except Exception as e:
            # Обработка ошибок
            error_message = f"Ошибка при создании заказа: {str(e)}"
            print(f"[ОШИБКА] {error_message}")
            QtWidgets.QMessageBox.critical(self, "Ошибка", error_message)

    def add_order_to_db(self, manager_id, customer_id, products):
        """Добавляет заказ в бд"""
        try:
            with self.db.cursor() as cursor:
                # Добавляем запись в таблицу orders
                create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                number_of_products = sum(product["quantity"] for product in products)  # Общее количество изделий

                print(f"[DEBUG] Данные для таблицы orders:")
                print(f"  create_date: {create_date}")
                print(f"  number_of_products: {number_of_products}")
                print(f"  customer_id: {customer_id}")
                print(f"  manager_id: {manager_id}")


                order_query = """
                INSERT INTO orders (create_date, number_of_products, status_id, id_customer, id_manager, real_price, price_with_profit)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(order_query, (
                    create_date,  # Дата и время создания заказа
                    number_of_products,  # Общее количество изделий
                    1,  # status_id = 1 (новый заказ)
                    customer_id,  # ID заказчика
                    manager_id,  # ID менеджера (NULL или 0)
                    0.00,  # real_price (по умолчанию)
                    0  # price_with_profit (по умолчанию)
                ))
                order_id = cursor.lastrowid  # Получаем ID заказа
                print(f"[DEBUG] Заказ добавлен в таблицу orders. ID заказа: {order_id}")

                # Добавляем записи в таблицу product для каждого изделия
                for product in products:
                    print(f"[DEBUG] Данные для таблицы product:")
                    print(f"  id_order: {order_id}")
                    print(f"  product_type_id: {product['product_type_id']}")
                    print(f"  length: {product['length']}")
                    print(f"  width: {product['width']}")
                    print(f"  quantity: {product['quantity']}")

                    product_query = """
                    INSERT INTO product (id_order, product_type_id, length, width, quantity, real_price_of_one, making_stage_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(product_query, (
                        order_id,  # ID заказа
                        product["product_type_id"],  # ID типа продукции
                        product["length"],  # Длина изделия
                        product["width"],  # Ширина изделия
                        product["quantity"],  # Количество изделий
                        0.00,  # real_price_of_one (по умолчанию 0)
                        1  # making_stage_id = 1 (нач. этап)
                    ))
                    product_id = cursor.lastrowid  # Получаем ID изделия
                    print(f"[DEBUG] Изделие добавлено в таблицу product. ID изделия: {product_id}")

                    # Добавляем записи в таблицу product_material для каждого материала
                    for material in product["materials"]:
                        print(f"[DEBUG] Данные для таблицы product_material:")
                        print(f"  id_product: {product_id}")
                        print(f"  id_material: {material['id']}")
                        print(f"  quantity: {material['quantity']}")

                        material_query = """
                        INSERT INTO product_material (id_product, id_material, quantity, wigth, lenght)
                        VALUES (%s, %s, %s, %s, %s)
                        """
                        cursor.execute(material_query, (
                            product_id,  # ID изделия
                            material["id"],  # ID материала
                            material["quantity"],  # Количество материала
                            None,  # Ширина (по умолчанию)
                            None  # Длина (по умолчанию)
                        ))
                        print(f"[DEBUG] Материал добавлен в таблицу product_material. ID материала: {material['id']}")

                # Фиксируем изменения в базе данных
                self.db.commit()
                print("[УСПЕХ] Заказ успешно добавлен в базу данных.")

        except pymysql.Error as e:
            # Откат
            self.db.rollback()
            error_message = f"Ошибка при добавлении заказа: {str(e)}"
            print(f"[ОШИБКА] {error_message}")
            raise Exception(error_message)  # Пробрасываем исключение для обработки в create_order

    def get_manager_id_by_login(self, login):
        """Возвращает ID менеджера по его логину."""
        if not login:
            print("[ОШИБКА] Логин не передан.")
            return None

        print(f"[DEBUG] Поиск ID менеджера по логину: '{login}'")

        query = "SELECT id FROM worker WHERE login = %s"
        try:
            with self.db.cursor() as cursor:
                print(f"[DEBUG] Выполняем запрос: {query} с логином '{login}'")
                cursor.execute(query, (login,))
                print("[DEBUG] Запрос выполнен.")

                result = cursor.fetchone()
                print(f"[DEBUG] Результат запроса: {result}")

                if result:
                    # Извлечение значения из словаря
                    manager_id = result['id']
                    print(f"[DEBUG] Извлеченный ID менеджера: {manager_id}")
                    return manager_id
                else:
                    print(f"[ОШИБКА] Менеджер с логином '{login}' не найден в базе данных.")
                    return None
        except pymysql.Error as e:
            print(f"[ОШИБКА] Ошибка при выполнении SQL-запроса: {e}")
            return None
        except Exception as e:
            print(f"[ОШИБКА] Необработанная ошибка: {str(e)}")
            return None

    def get_product_type_id(self, product_type_name_with_desc):
        """
        Возвращает ID типа продукции по его названию. Строки вида "название – описание".
        """
        # Извлекаем название (до '–')
        product_type_name = product_type_name_with_desc.split("–")[0].strip()
        print(f"[DEBUG] Извлеченное название типа продукции: '{product_type_name}'")

        query = "SELECT id FROM product_type WHERE name = %s"
        try:
            with self.db.cursor() as cursor:
                print(f"[DEBUG] Выполняем запрос: {query} с названием типа продукции '{product_type_name}'")
                cursor.execute(query, (product_type_name,))
                result = cursor.fetchone()
                print(f"[DEBUG] Результат запроса: {result}")

                if result:
                    # Извлечение значения из словаря
                    product_type_id = result['id']
                    print(f"[DEBUG] Извлеченный ID типа продукции: {product_type_id}")
                    return product_type_id
                else:
                    print(f"[ОШИБКА] Тип продукции '{product_type_name}' не найден в базе данных.")
                    return None
        except pymysql.Error as e:
            print(f"[ОШИБКА] Ошибка при выполнении SQL-запроса: {e}")
            return None
        except Exception as e:
            print(f"[ОШИБКА] Необработанная ошибка: {str(e)}")
            return None

    def get_material_id(self, material_name):
        """Возвращает ID материала по его названию"""
        query = "SELECT id FROM material WHERE name = %s"
        try:
            with self.db.cursor() as cursor:
                cursor.execute(query, (material_name,))
                result = cursor.fetchone()
                if result:
                    # ID материала из словаря
                    material_id = result['id']
                    print(f"[DEBUG] Найден ID материала: {material_id}")
                    return material_id
                else:
                    print(f"[ОШИБКА] Материал '{material_name}' не найден в базе данных.")
                    return None
        except pymysql.Error as e:
            print(f"[ОШИБКА] Ошибка при выполнении SQL-запроса: {e}")
            return None
        except Exception as e:
            print(f"[ОШИБКА] Необработанная ошибка: {str(e)}")
            return None

    def load_materials(self, category_id):
        """Загружает материалы по категории"""
        if not self.db:
            return []

        try:
            with self.db.cursor() as cursor:
                query = "SELECT name FROM material WHERE id_category = %s"
                cursor.execute(query, (category_id,))
                return [row["name"] for row in cursor.fetchall()]
        except pymysql.Error as e:
            print(f"Ошибка загрузки материалов: {e}")
            return []

    def load_product_types(self):
        """Загружает типы продукции с их описанием"""
        if not self.db:
            return []

        try:
            with self.db.cursor() as cursor:
                query = "SELECT name, description FROM product_type"
                cursor.execute(query)
                return [f"{row['name']} – {row['description']}" for row in cursor.fetchall()]
        except pymysql.Error as e:
            print(f"Ошибка загрузки типов продукции: {e}")
            return []

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setStyleSheet("background-color: rgb(181, 213, 202);")

        main_layout = QVBoxLayout(Form)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header = QLabel("НОВЫЙ ЗАКАЗ")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: black; padding: 8px;")
        header.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(header)

        input_scroll = QScrollArea()
        input_scroll.setWidgetResizable(True)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        self.create_input_fields(content_layout)

        input_scroll.setWidget(content_widget)
        main_layout.addWidget(input_scroll)

        self.add_btn = QPushButton("Добавить в заказ")
        self.add_btn.setStyleSheet("background-color: rgb(224, 169, 175); color: white; padding: 10px;")
        self.add_btn.clicked.connect(self.add_to_order)
        main_layout.addWidget(self.add_btn)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: #ccc;")
        main_layout.addWidget(separator)

        # QScrollArea для таблицы
        table_scroll = QScrollArea()
        table_scroll.setWidgetResizable(True)
        table_scroll.setStyleSheet("background-color: white; border-radius: 5px;")

        # Создаем таблицу
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(9)
        self.products_table.setHorizontalHeaderLabels([
            "Тип", "Высота", "Ширина", "Ткань", "Нитки", "Фурнитура", "Декор", "Подкладка", "Количество"
        ])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.products_table.verticalHeader().setVisible(False)
        self.products_table.setStyleSheet("""
                QTableWidget {
                    background-color: white;
                    border-radius: 5px;
                }
                QHeaderView::section {
                    background-color: rgb(209, 238, 252);
                    color: black;
                }
            """)
        self.products_table.setItemDelegate(AlternateRowColorDelegate(self.products_table))
        # Добавляем таблицу в QScrollArea
        table_scroll.setWidget(self.products_table)
        main_layout.addWidget(table_scroll)

        # Кнопки управления заказом
        order_buttons_layout = QHBoxLayout()
        self.create_btn = QPushButton("Заказать")
        self.create_btn.setStyleSheet("background-color: rgb(224, 169, 175); color: white; padding: 10px;")
        self.create_btn.clicked.connect(self.create_order)

        self.delete_btn = QPushButton("Удалить выбранную запись")
        self.delete_btn.setStyleSheet("background-color: rgb(200, 149, 155); color: white; padding: 10px;")
        self.delete_btn.clicked.connect(self.delete_selected_row)

        order_buttons_layout.addWidget(self.delete_btn)
        order_buttons_layout.addStretch()
        order_buttons_layout.addWidget(self.create_btn)

        main_layout.addLayout(order_buttons_layout)

    def create_input_fields(self, layout):
        """Создает поля ввода и загружает данные из бд"""
        self.fields = {
            "Тип продукции": QComboBox(),
            "Высота (см)": QLineEdit(),
            "Ширина (см)": QLineEdit(),
            "Ткань": QComboBox(),
            "Нитки": QComboBox(),
            "Фурнитура": QComboBox(),
            "Количество фурнитуры": QLineEdit(),
            "Декор": QComboBox(),
            "Количество декора": QLineEdit(),
            "Подкладка": QComboBox(),
            "Количество": QLineEdit()
        }

        # Загрузка данных в комбобоксы
        self.fields["Тип продукции"].addItems(self.load_product_types())
        self.fields["Ткань"].addItems(self.load_materials(1))
        self.fields["Нитки"].addItems(self.load_materials(2))

        self.fields["Фурнитура"].addItem("-")
        self.fields["Фурнитура"].addItems(self.load_materials(3))

        self.fields["Декор"].addItem("-")
        self.fields["Декор"].addItems(self.load_materials(5))

        self.fields["Подкладка"].addItem("-")
        self.fields["Подкладка"].addItems(self.load_materials(4))

        label_style = "font-weight: bold; color: black; min-width: 120px;"
        field_style = "background-color: white; border: 1px solid #ddd; padding: 5px; min-width: 200px; color: black;"

        for key, widget in self.fields.items():
            row = QHBoxLayout()
            label = QLabel(key)
            label.setStyleSheet(label_style)
            widget.setStyleSheet(field_style)

            row.addWidget(label)
            row.addWidget(widget)
            row.addStretch()
            layout.addLayout(row)

        # Скрываем поля для количества фурнитуры и декора по умолчанию
        self.fields["Количество фурнитуры"].setVisible(False)
        self.fields["Количество декора"].setVisible(False)

        # Подключаем обработчики событий для комбобоксов
        self.fields["Фурнитура"].currentTextChanged.connect(self.toggle_hardware_quantity_field)
        self.fields["Декор"].currentTextChanged.connect(self.toggle_decor_quantity_field)

    def toggle_hardware_quantity_field(self, text):
        """Управляет видимостью поля для ввода количества фурнитуры"""
        if text != "-":
            self.fields["Количество фурнитуры"].setVisible(True)
        else:
            self.fields["Количество фурнитуры"].setVisible(False)
            self.fields["Количество фурнитуры"].clear()  # Очищаем, если фурнитура не выбрана

    def toggle_decor_quantity_field(self, text):
        """Управляет видимостью поля для ввода количества декора"""
        if text != "-":
            self.fields["Количество декора"].setVisible(True)
        else:
            self.fields["Количество декора"].setVisible(False)
            self.fields["Количество декора"].clear()  # Очищаем, если декор не выбран

    def load_customers(self):
        """Загружает заказчиков с типом отображаемой информации"""
        if not self.db:
            return []

        try:
            with self.db.cursor() as cursor:
                query = "SELECT id, company_name, surname, name, patronymic, id_type_customer FROM customer"
                cursor.execute(query)
                customers = cursor.fetchall()

                # Список заказчиков в зависимости от типа
                customer_list = []
                for customer in customers:
                    if customer['id_type_customer'] == 1:
                        customer_list.append(customer['company_name'])  # Компания
                    elif customer['id_type_customer'] == 2:
                        customer_list.append(
                            f"{customer['surname']} {customer['name']} {customer['patronymic']}")  # ФИО

                return customer_list, {customer['company_name']: customer['id'] for customer in customers if
                                       customer['id_type_customer'] == 1}, \
                    {f"{customer['surname']} {customer['name']} {customer['patronymic']}": customer['id'] for customer
                     in customers if customer['id_type_customer'] == 2}
        except pymysql.Error as e:
            print(f"Ошибка загрузки заказчиков: {e}")
            return [], {}, {}

    def add_to_order(self):
        """Добавляет введенные данные в таблицу"""
        row_position = self.products_table.rowCount()

        # Обязательные поля
        required_fields = ["Тип продукции", "Высота (см)", "Ширина (см)", "Ткань", "Нитки", "Количество"]

        # Проверка
        for key in required_fields:
            widget = self.fields[key]
            value = widget.currentText() if isinstance(widget, QComboBox) else widget.text().strip()

            if not value:
                QtWidgets.QMessageBox.warning(None, "Ошибка", f"Заполните поле: {key}")
                return  # Прерываем выполнение функции, если поле не заполнено

        # Данные для таблицы
        data = [
            self.fields["Тип продукции"].currentText(),  # Тип продукции
            self.fields["Высота (см)"].text(),  # Высота
            self.fields["Ширина (см)"].text(),  # Ширина
            self.fields["Ткань"].currentText(),  # Ткань
            self.fields["Нитки"].currentText(),  # Нитки
            self.fields["Фурнитура"].currentText(),  # Фурнитура
            self.fields["Количество фурнитуры"].text() if self.fields["Фурнитура"].currentText() != "-" else "-",
            # Количество фурнитуры
            self.fields["Декор"].currentText(),  # Декор
            self.fields["Количество декора"].text() if self.fields["Декор"].currentText() != "-" else "-",
            # Количество декора
            self.fields["Подкладка"].currentText(),  # Подкладка
            self.fields["Количество"].text(),  # Количество изделий
        ]

        # Форматируем фурнитуру и декор в формат "название - количество"
        if data[5] != "-" and data[6] != "-":  # Если фурнитура выбрана
            data[5] = f"{data[5]} - {data[6]}"  # Объединяем название и количество
        if data[7] != "-" and data[8] != "-":  # Если декор выбран
            data[7] = f"{data[7]} - {data[8]}"

        data.pop(6)  # Удаляем количество фурнитуры
        data.pop(7)  # Удаляем количество декора

        # Добавляем строку в таблицу
        self.products_table.insertRow(row_position)
        for col, value in enumerate(data):
            self.products_table.setItem(row_position, col, QTableWidgetItem(value))

        # Очищаем поля после добавления
        for widget in self.fields.values():
            if isinstance(widget, QComboBox):
                widget.setCurrentIndex(-1)
            else:
                widget.clear()

        # Скрываем поля для количества фурнитуры и декора после добавления
        self.fields["Количество фурнитуры"].setVisible(False)
        self.fields["Количество декора"].setVisible(False)

    def delete_selected_row(self):
        """Удаляет выделенную строку"""
        selected_row = self.products_table.currentRow()
        if selected_row >= 0:
            self.products_table.removeRow(selected_row)
        else:
            QtWidgets.QMessageBox.warning(None, "Ошибка", "Выберите строку для удаления.")


class AlternateRowColorDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.colors = [QColor(255, 252, 214), QColor(209, 238, 252)]  # Желтый и синий

    def paint(self, painter, option, index):
        if index.row() % 2 == 0:
            painter.fillRect(option.rect, self.colors[0])  # Чередуем цвета
        else:
            painter.fillRect(option.rect, self.colors[1])
        super().paint(painter, option, index)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Ui_Form()
    window.show()
    sys.exit(app.exec())
