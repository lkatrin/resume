import sys
from PyQt6.QtWidgets import QApplication, QDialog
from mainwindow import MainWindow
from login_dialog import LoginDialog
from database import create_tables

def main():
    app = QApplication(sys.argv)
    create_tables()  # Создание таблиц в базе данных, если они еще не существуют

    while True:
        login_dialog = LoginDialog()
        response = login_dialog.exec()

        if response == QDialog.DialogCode.Accepted:
            mainWindow = MainWindow()
            mainWindow.show()
            break
        elif response == QDialog.DialogCode.Rejected:
            break  # Выход из цикла и завершение программы, если окно входа закрыто

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

