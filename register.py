import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
import pymysql.cursors
from config import connect_db

class RegisterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Load the UI
        uic.loadUi('views/dangky.ui', self)

        # Connect button to function
        self.register_button.clicked.connect(self.register)
    
    def register(self):
        name = self.hovaten_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        role = self.role_input.currentText()
        
        connection = connect_db()
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO NhanVien (HoTen,TaiKhoan, MatKhau, PhanQuyen) VALUES (%s,%s, %s, %s)"
                cursor.execute(sql, (name,username, password, role))
                connection.commit()
                QMessageBox.information(self, 'Thành công', 'Đăng ký thành công!')
        except pymysql.MySQLError as e:
            QMessageBox.warning(self, 'Lỗi', f'Không thể đăng ký: {e}')
        finally:
            connection.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RegisterWindow()
    window.show()
    sys.exit(app.exec())