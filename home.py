import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from product import ProductApp
from hoadon import OrderManagement # ✅ Import giao diện Quản lý Sản phẩm

class MainWindow(QWidget):
    def __init__(self, username, chuc_vu):
        super().__init__()
        uic.loadUi("views/trangchu1.ui", self)

        # Hiển thị thông tin người dùng
        self.username = username
        self.chuc_vu = chuc_vu
        self.userName.setText(f"Người dùng: {self.username}")
        self.Role.setText(f"Chức vụ: {self.chuc_vu}")

        # Quản lý trang hiển thị
        self.trangHienTai = None
        self.danhSachTrang = {}

        # Kết nối sự kiện các nút
        self.thietLapKetNoi()

        # Hiển thị trang chủ mặc định
        self.hienThiTrangChu()

    def thietLapKetNoi(self):
        """Kết nối các nút với chức năng tương ứng"""
        self.btnProductManagement.clicked.connect(lambda: self.hienThiTrang("sanPham"))
        self.btnInvoiceManagement.clicked.connect(lambda: self.hienThiTrang("hoaDon"))
        self.logoutButton.clicked.connect(self.dangXuat)

    def hienThiTrangChu(self):
        """Hiển thị giao diện trang chủ"""
        self.mainContent.setCurrentIndex(0)
        self.trangHienTai = "trangChu"

    def hienThiTrang(self, tenTrang):
        """Chuyển đổi hiển thị giữa các trang"""
        if tenTrang not in self.danhSachTrang:
            if tenTrang == "sanPham":
                self.danhSachTrang[tenTrang] = ProductApp()
            elif tenTrang == "hoaDon":
                self.danhSachTrang[tenTrang] = OrderManagement()

        # Thêm trang vào `mainContent`
            self.mainContent.addWidget(self.danhSachTrang[tenTrang])

    # Chuyển đến trang đã chọn
        self.mainContent.setCurrentWidget(self.danhSachTrang[tenTrang])
        self.trangHienTai = tenTrang


    def dangXuat(self):
        """Xử lý đăng xuất và quay về giao diện đăng nhập"""
        from dangnhap import LoginWindow
        self.cuaSoDangNhap = LoginWindow()
        self.cuaSoDangNhap.show()
        self.close()

def main():
    """Chạy ứng dụng"""
    try:
        app = QtWidgets.QApplication(sys.argv)
        cuaSo = MainWindow("admin", "Quản lý")  # 🛠️ Truyền thông tin đăng nhập mặc định
        cuaSo.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Lỗi: {str(e)}")

if __name__ == "__main__":
    main()
