import sys
import pymysql
from PyQt6.QtWidgets import QApplication, QWidget, QTableWidgetItem, QMessageBox, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QHeaderView
# from PyQt6.QtCore import Qt

# Hàm kết nối Database
def connect_db():
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="cua_hang_thu_cung",
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except pymysql.MySQLError as e:
        QMessageBox.critical(None, "Lỗi kết nối Database", f"Không thể kết nối: {str(e)}")
        sys.exit(1)

# Class chính
class EmployeeManager(QWidget):
    def __init__(self):
        super().__init__()
        self.conn = connect_db()
        self.cursor = self.conn.cursor()

        self.setWindowTitle("Quản lý nhân viên")
        self.setGeometry(200, 100, 800, 500)

        # Layout chính
        layout = QVBoxLayout()

        # Layout nhập dữ liệu
        input_layout = QHBoxLayout()
        self.nameInput = QLineEdit()
        self.accountInput = QLineEdit()
        self.passwordInput = QLineEdit()
        self.roleInput = QLineEdit()

        self.nameInput.setPlaceholderText("Họ và tên")
        self.accountInput.setPlaceholderText("Tài khoản")
        self.passwordInput.setPlaceholderText("Mật khẩu")
        self.roleInput.setPlaceholderText("Phân quyền")

        input_layout.addWidget(self.nameInput)
        input_layout.addWidget(self.accountInput)
        input_layout.addWidget(self.passwordInput)
        input_layout.addWidget(self.roleInput)
        layout.addLayout(input_layout)

        # Layout các nút chức năng
        button_layout = QHBoxLayout()
        self.addButton = QPushButton("Thêm")
        self.updateButton = QPushButton("Sửa")
        self.deleteButton = QPushButton("Xóa")
        self.homeButton = QPushButton("Quay lại trang chủ")

        button_layout.addWidget(self.addButton)
        button_layout.addWidget(self.updateButton)
        button_layout.addWidget(self.deleteButton)
        button_layout.addWidget(self.homeButton)
        layout.addLayout(button_layout)

        # Bảng hiển thị dữ liệu
        self.employeeTable = QTableWidget()
        self.employeeTable.setColumnCount(5)
        self.employeeTable.setHorizontalHeaderLabels(["Mã", "Họ tên", "Tài khoản", "Mật khẩu", "Phân quyền"])
        self.employeeTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.employeeTable)
        self.setLayout(layout)

        # Kết nối sự kiện
        self.addButton.clicked.connect(self.add_employee)
        self.updateButton.clicked.connect(self.update_employee)
        self.deleteButton.clicked.connect(self.delete_employee)
        self.homeButton.clicked.connect(self.go_home)

        self.load_employees()

    def load_employees(self):
        """Nạp dữ liệu từ database vào bảng"""
        self.employeeTable.setRowCount(0)
        query = "SELECT * FROM nhanvien"
        self.cursor.execute(query)
        employees = self.cursor.fetchall()
        for row_number, row_data in enumerate(employees):
            self.employeeTable.insertRow(row_number)
            for column_number, key in enumerate(row_data):
                self.employeeTable.setItem(row_number, column_number, QTableWidgetItem(str(row_data[key])))

    def add_employee(self):
        """Thêm nhân viên mới"""
        name = self.nameInput.text().strip()
        account = self.accountInput.text().strip()
        password = self.passwordInput.text().strip()
        role = self.roleInput.text().strip()

        if not name or not account or not password or not role:
            QMessageBox.warning(self, "Lỗi", "Vui lòng điền đủ thông tin")
            return

        query = "INSERT INTO nhanvien (HoTen, TaiKhoan, MatKhau, PhanQuyen) VALUES (%s, %s, %s, %s)"
        values = (name, account, password, role)
        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            self.load_employees()
            QMessageBox.information(self, "Thành công", "Nhân viên đã được thêm")
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể thêm nhân viên: {str(e)}")

    def update_employee(self):
        """Cập nhật nhân viên"""
        selected_row = self.employeeTable.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Lỗi", "Chọn nhân viên để sửa")
            return

        employee_id = self.employeeTable.item(selected_row, 0).text()
        name = self.nameInput.text().strip()
        account = self.accountInput.text().strip()
        password = self.passwordInput.text().strip()
        role = self.roleInput.text().strip()

        if not name or not account or not password or not role:
            QMessageBox.warning(self, "Lỗi", "Vui lòng điền đủ thông tin")
            return

        query = "UPDATE nhanvien SET HoTen=%s, TaiKhoan=%s, MatKhau=%s, PhanQuyen=%s WHERE MaNhanVien=%s"
        values = (name, account, password, role, employee_id)
        self.cursor.execute(query, values)
        self.conn.commit()
        self.load_employees()
        QMessageBox.information(self, "Thành công", "Nhân viên đã được cập nhật")

    def delete_employee(self):
        """Xóa nhân viên"""
        selected_row = self.employeeTable.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Lỗi", "Chọn nhân viên để xóa")
            return

        employee_id = self.employeeTable.item(selected_row, 0).text()
        query = "DELETE FROM nhanvien WHERE MaNhanVien=%s"
        self.cursor.execute(query, (employee_id,))
        self.conn.commit()
        self.load_employees()
        QMessageBox.information(self, "Thành công", "Nhân viên đã bị xóa")

    def go_home(self):
        """Quay lại trang chủ"""
        self.close()
        # Assuming home.py has a class HomeWindow to show the home page
        from home import HomeWindow
        self.home_window = HomeWindow()
        self.home_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EmployeeManager()
    window.show()
    sys.exit(app.exec())
