from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(700, 700)
        Form.setStyleSheet("""
            #Form {
                background-color: rgb(181, 213, 202);
            }
            QPushButton {
                background-color: rgb(224, 169, 175);
                border: none;
                border-radius: 6px;
                font-size: 12pt;
                color: rgb(0, 0, 0);
                font-family: "MS Shell Dlg 2";
            }
            QLabel {
                font-size: 14pt;
                color: rgb(0, 0, 0);
                font-family: "MS Shell Dlg 2";
            }
            QLineEdit {
                background-color: rgb(255, 255, 255);
                border-radius: 6px;
                font-size: 12pt;
                color: rgb(0, 0, 0);
                font-family: "MS Shell Dlg 2";
                padding: 5px;
                
            QMessage
            }
        """)

        # Логотип в правом верхнем углу
        self.label_logo = QtWidgets.QLabel(parent=Form)
        self.label_logo.setGeometry(QtCore.QRect(500, 20, 150, 120))
        self.label_logo.setText("")
        self.label_logo.setPixmap(QtGui.QPixmap("logo-01.jpg"))
        self.label_logo.setScaledContents(True)
        self.label_logo.setObjectName("label_logo")


        self.label_title = QtWidgets.QLabel(parent=Form)
        self.label_title.setGeometry(QtCore.QRect(50, 50, 600, 50))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setFamily("MS Shell Dlg 2")
        self.label_title.setFont(font)
        self.label_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_title.setObjectName("label_title")

        # Поле для ввода логина
        self.label_username = QtWidgets.QLabel(parent=Form)
        self.label_username.setGeometry(QtCore.QRect(50, 200, 200, 30))
        self.label_username.setObjectName("label_username")

        self.lineEdit_username = QtWidgets.QLineEdit(parent=Form)
        self.lineEdit_username.setGeometry(QtCore.QRect(50, 240, 600, 40))
        self.lineEdit_username.setObjectName("lineEdit_username")

        # Поле для ввода пароля
        self.label_password = QtWidgets.QLabel(parent=Form)
        self.label_password.setGeometry(QtCore.QRect(50, 300, 200, 30))
        self.label_password.setObjectName("label_password")

        self.lineEdit_password = QtWidgets.QLineEdit(parent=Form)
        self.lineEdit_password.setGeometry(QtCore.QRect(50, 340, 600, 40))
        self.lineEdit_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.lineEdit_password.setObjectName("lineEdit_password")

        # Кнопка "Войти"
        self.pushButton_login = QtWidgets.QPushButton(parent=Form)
        self.pushButton_login.setGeometry(QtCore.QRect(250, 450, 200, 50))
        self.pushButton_login.setObjectName("pushButton_login")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Авторизация"))
        self.label_title.setText(_translate("Form", "Авторизация"))
        self.label_username.setText(_translate("Form", "Логин:"))
        self.label_password.setText(_translate("Form", "Пароль:"))
        self.pushButton_login.setText(_translate("Form", "Войти"))


