from PyQt6.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget,
                             QTableWidget, QLineEdit, QTableWidgetItem, QMessageBox, QApplication, QDialog, QCalendarWidget, QComboBox)
from dialogs import AddDialog, EditDialog, DeleteUserDialog
from database import add_train, update_train, delete_train, get_all_trains, train_exists
import os
import matplotlib.pyplot as plt
import pandas as pd


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Расписание Электричек")
        self.setGeometry(100, 100, 800, 600)

        # Стилизация
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f3f3f3;
            }
            QPushButton {
                background-color: #dcdcdc;
                border-style: outset;
                border-width: 2px;
                border-radius: 10px;
                border-color: beige;
                font: bold 14px;
                min-width: 10em;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #c8c8c8;
                border-style: inset;
            }
            QLineEdit {
                border: 2px solid #c8c8c8;
                border-radius: 10px;
                padding: 6px;
                background-color: #ffffff;
                font: 14px;
            }
            QTableWidget {
                border: 2px solid #c8c8c8;
                border-radius: 10px;
                font: 14px;
            }
        """)

        layout = QVBoxLayout()  # Основной вертикальный макет

        # Макет для элементов поиска
        search_layout = QHBoxLayout()
        self.calendar = QCalendarWidget(self)
        self.calendar.hide()  # Скрыть календарь до вызова
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Введите текст для поиска...")
        self.search_button = QPushButton("Поиск")
        self.search_button.clicked.connect(self.search_trains)
        self.reset_search_button = QPushButton("Показать все")
        self.reset_search_button.clicked.connect(self.reset_search)
        self.btn_open_calendar = QPushButton("Открыть календарь")
        self.btn_open_calendar.clicked.connect(self.open_calendar)
        self.direction_filter_combobox = QComboBox(self)
        self.direction_filter_combobox.addItems(["Все", "Из Москвы", "В Москву", "Не указано"])
        self.calendar.selectionChanged.connect(self.apply_filters)
        self.direction_filter_combobox.currentTextChanged.connect(self.apply_filters)

        self.btn_export_excel = QPushButton("Экспорт в Excel")
        self.btn_export_excel.setStyleSheet("QPushButton { background-color: green; color: white; }"
                                            "QPushButton:hover { background-color: #006400; }")
        self.btn_export_excel.clicked.connect(self.export_to_excel)

        # Добавляем элементы поиска в горизонтальный макет
        search_layout.addWidget(self.direction_filter_combobox)
        search_layout.addWidget(self.btn_open_calendar)
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.reset_search_button)
        search_layout.addWidget(self.btn_export_excel)

        layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(10)  # Увеличиваем количество столбцов на 1
        self.table.setHorizontalHeaderLabels(
            ["ID", "Название", "Отправление", "Прибытие", "Маршрут", "Статус", "Расписание по дням", "Платформа",
             "Путь", "Направление"])
        layout.addWidget(self.table)  # Добавляем таблицу в основной макет

        # Кнопки управления
        btn_add = QPushButton("Добавить поезд")
        btn_edit = QPushButton("Редактировать поезд")
        btn_delete = QPushButton("Удалить поезд")
        btn_show_chart = QPushButton("Диаграмма статусов")
        btn_add.clicked.connect(self.add_train)
        btn_edit.clicked.connect(self.edit_train)
        btn_delete.clicked.connect(self.delete_train)
        btn_show_chart.clicked.connect(self.display_status_chart)
        btn_show_chart.setStyleSheet("QPushButton {"
                                     "background-color: orange;"
                                     "color: white;"
                                     "border-radius: 10px;"
                                     "padding: 6px;"
                                     "font: bold 14px;"
                                     "}"
                                     "QPushButton:hover {"
                                     "background-color: #e69500;"  # немного темнее оранжевого для эффекта при наведении
                                     "}")
        # Кнопка для удаления пользователя
        btn_delete_user = QPushButton("Удалить пользователя")
        btn_delete_user.clicked.connect(self.delete_user)
        btn_delete_user.setStyleSheet("QPushButton { background-color: #ff4d4d; color: white; }"
                                      "QPushButton:hover { background-color: #ff3333; }")


        layout.addWidget(btn_delete_user)  # Добавляем кнопку в макет
        layout.addWidget(btn_add)
        layout.addWidget(btn_edit)
        layout.addWidget(btn_delete)
        layout.addWidget(btn_show_chart)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


        self.load_trains()

    def add_train(self):
        dialog = AddDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.name_edit.text()
            departure_time = dialog.departure_time_edit.time().toString("HH:mm")
            arrival_time = dialog.arrival_time_edit.time().toString("HH:mm")
            route = dialog.route_edit.text()
            status = dialog.status_edit.currentText()
            schedule = dialog.schedule_edit.currentText()
            platform = dialog.platform_edit.text()
            path = dialog.path_edit.text()
            direction = dialog.direction_edit.currentText()


            # Проверка на уникальность перед добавлением
            if not train_exists(name, departure_time, arrival_time, route):
                add_train(name, departure_time, arrival_time, route, status, schedule, platform, path, direction)
                self.load_trains()
            else:
                QMessageBox.warning(self, "Предупреждение", "Такой поезд уже существует в расписании.")

    def edit_train(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            train_id = self.table.item(selected_row, 0).text()
            current_name = self.table.item(selected_row, 1).text()
            current_departure = self.table.item(selected_row, 2).text()
            current_arrival = self.table.item(selected_row, 3).text()
            current_route = self.table.item(selected_row, 4).text()
            current_status = self.table.item(selected_row, 5).text()
            current_schedule = self.table.item(selected_row, 6).text()
            current_platform = self.table.item(selected_row, 7).text()
            current_path = self.table.item(selected_row, 8).text()
            current_direction = self.table.item(selected_row, 9).text()


            dialog = EditDialog(train_id, current_name, current_departure, current_arrival, current_route, current_status, current_schedule, current_platform, current_path, current_direction)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Получите обновленные данные из диалога и обновите запись в базе данных
                updated_name = dialog.name_edit.text()
                updated_departure = dialog.departure_time_edit.time().toString("HH:mm")
                updated_arrival = dialog.arrival_time_edit.time().toString("HH:mm")
                updated_route = dialog.route_edit.text()
                updated_status = dialog.status_edit.currentText()
                updated_schedule = dialog.schedule_edit.currentText()
                updated_platform = dialog.platform_edit.text()
                updated_path = dialog.path_edit.text()
                updated_direction = dialog.direction_edit.currentText()


                update_train(train_id, updated_name, updated_departure, updated_arrival, updated_route, updated_status, updated_schedule, updated_platform, updated_path, updated_direction)
                self.load_trains()  # Обновление таблицы
        else:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, выберите поезд для редактирования")

    def delete_train(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            reply = QMessageBox.question(
                self, 'Удалить запись',
                'Вы уверены, что хотите удалить этот поезд?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                id = self.table.item(selected_row, 0).text()
                delete_train(id)
                self.load_trains()
        else:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, выберите поезд для удаления")

    def load_trains(self):
        self.table.setRowCount(0)  # Очищаем таблицу перед загрузкой новых данных
        for train in get_all_trains():
            self.add_table_row(train)

    def add_table_row(self, train):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QTableWidgetItem(str(train['id'])))
        self.table.setItem(row_position, 1, QTableWidgetItem(train['name']))
        self.table.setItem(row_position, 2, QTableWidgetItem(train['departure_time']))
        self.table.setItem(row_position, 3, QTableWidgetItem(train['arrival_time']))
        self.table.setItem(row_position, 4, QTableWidgetItem(train['route']))
        self.table.setItem(row_position, 5, QTableWidgetItem(train['status']))
        self.table.setItem(row_position, 6, QTableWidgetItem(train['schedule']))
        self.table.setItem(row_position, 7, QTableWidgetItem(train['platform']))
        self.table.setItem(row_position, 8, QTableWidgetItem(train['path']))
        self.table.setItem(row_position, 9, QTableWidgetItem(train['direction']))

    def search_trains(self):
        search_text = self.search_edit.text().lower()
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 1)
            route_item = self.table.item(row, 4)
            schedule_item = self.table.item(row, 6)
            name = name_item.text().lower() if name_item else ""
            route = route_item.text().lower() if route_item else ""
            schedule = schedule_item.text().lower() if schedule_item else ""
            direction = schedule_item.text().lower() if schedule_item else ""

            match = search_text in name or search_text in route or search_text in schedule or search_text in direction
            self.table.setRowHidden(row, not match)

    def reset_search(self):
        """ Сброс фильтра поиска и показ всех записей """
        self.search_edit.clear()
        self.load_trains()
        for row in range(self.table.rowCount()):
            self.table.setRowHidden(row, False)

    def center_on_screen(self):
        # Центрирует окно на экране
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())

    def delete_user(self):
        delete_dialog = DeleteUserDialog()
        delete_dialog.exec()

    def display_status_chart(self):
        status_counts = self.get_status_counts()
        labels = list(status_counts.keys())
        sizes = list(status_counts.values())

        # Определение цветов для каждого статуса
        colors = ['#28a745' if label == "Вовремя" else '#dc3545' if label == "Отменена" else '#ff8c00' for label in labels]

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        ax.axis('equal')
        plt.show()

    def get_status_counts(self):
        # Получение данных о статусах из базы данных
        trains = get_all_trains()
        status_counts = {"Вовремя": 0, "Опаздывает": 0, "Отменена": 0}
        for train in trains:
            status_counts[train['status']] += 1
        return status_counts

    def export_to_excel(self):
        # Здесь будет реализация функции экспорта
        self.export_trains_to_excel()

    def export_trains_to_excel(self):
        try:
            data = get_all_trains()  # Получаем данные
            df = pd.DataFrame(data)
            filename = 'trains_schedule.xlsx'
            df.to_excel(filename, index=False)

            # Открытие файла Excel после его создания
            if os.name == 'nt':  # Для Windows
                os.startfile(filename)
            else:  # Для macOS, Linux и других ОС
                opener = 'open' if os.name == 'mac' else 'xdg-open'
                subprocess.run([opener, filename])

            QMessageBox.information(self, "Экспорт завершен", f"Данные успешно экспортированы в {filename}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка экспорта", str(e))

        # Функция для отображения календаря

    def open_calendar(self):
        self.calendar = QCalendarWidget()
        self.calendar.selectionChanged.connect(self.apply_filters)
        self.calendar.show()

        # Функция фильтрации по выбранной дате

    def apply_filters(self):
        selected_date = self.calendar.selectedDate()  # Выбранная дата
        selected_direction = self.direction_filter_combobox.currentText()  # Выбранное направление

        for row in range(self.table.rowCount()):
            # Фильтрация по дате
            schedule_item = self.table.item(row, 6)  # 'Расписание по дням'
            schedule = schedule_item.text() if schedule_item else ""
            is_weekday = selected_date.dayOfWeek() < 6
            is_correct_schedule = (is_weekday and ("Каждый день" in schedule or "По будним" in schedule) or
                                   not is_weekday and ("Каждый день" in schedule or "По выходным" in schedule))

            # Фильтрация по направлению
            direction_cell = self.table.item(row, 9)  # 'Направление'
            direction = direction_cell.text() if direction_cell else ""
            is_correct_direction = (selected_direction == "Все" or selected_direction == direction)

            # Скрытие или показ строки в зависимости от соответствия обоим фильтрам
            self.table.setRowHidden(row, not (is_correct_direction and is_correct_schedule))
