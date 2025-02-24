import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QTableWidgetItem, QMessageBox
from PyQt6 import uic
from PyQt6.QtCore import Qt, QDate
import pymysql
from datetime import datetime
from config import connect_db

class AddOrderForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        # Load UI file từ thư mục hiện tại
        uic.loadUi("views/themdonhang.ui", self)

        # Đặt ngày lập mặc định
        self.date_edit.setDate(QDate.currentDate())  # Sử dụng QDateEdit từ file .ui

        # Load dữ liệu khách hàng vào combo_khach
        self.load_khach_hang()

        # Cấu hình danh mục (Thú Cưng và Sản Phẩm)
        self.combo_danhmuc.addItem("Chọn loại sản phẩm")
        self.combo_danhmuc.addItem("Thú Cưng")
        self.combo_danhmuc.addItem("Sản Phẩm")

        # Kết nối tín hiệu cho combo_danhmuc để cập nhật sản phẩm/thú cưng
        self.combo_danhmuc.currentIndexChanged.connect(self.update_product_list)
        self.btn_add.clicked.connect(self.add_product)
        self.btn_save.clicked.connect(self.save_order)

    def load_khach_hang(self):
        """Tải danh sách khách hàng từ cơ sở dữ liệu vào combo_khach"""
        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT MaKhachHang, HoTen FROM KhachHang")
                for makhach, tenkhach in cursor.fetchall():
                    self.combo_khach.addItem(f"{makhach} - {tenkhach}", makhach)
            except pymysql.Error as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể tải danh sách khách hàng: {str(e)}")
            finally:
                cursor.close()
                conn.close()

    def update_product_list(self):
        """Cập nhật danh sách sản phẩm/thú cưng khi chọn danh mục"""
        self.combo_sanpham.clear()

        loai = self.combo_danhmuc.currentText()
        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()

                if loai == "Thú Cưng":
                    cursor.execute("SELECT MaThuCung, Ten, GiaBan FROM ThuCung")
                    for mathucung, tenthucung, gia in cursor.fetchall():
                        self.combo_sanpham.addItem(f"{mathucung} - {tenthucung} ({gia}đ)", (mathucung, gia))

                elif loai == "Sản Phẩm":
                    cursor.execute("SELECT MaSanPham, Ten, Gia FROM SanPham")
                    for masp, tensp, gia in cursor.fetchall():
                        self.combo_sanpham.addItem(f"{masp} - {tensp} ({gia}đ)", (masp, gia))
            except pymysql.Error as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể tải danh sách sản phẩm: {str(e)}")
            finally:
                cursor.close()
                conn.close()

    def add_product(self):
        """Thêm thú cưng hoặc sản phẩm vào bảng"""
        loai = self.combo_danhmuc.currentText()
        product_data = self.combo_sanpham.currentData()
        soluong = self.spin_sl.value()

        if not product_data or loai == "Chọn loại sản phẩm":
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn loại sản phẩm và sản phẩm/thú cưng!")
            return

        ma, gia = product_data
        self.add_to_table(ma, soluong, gia, loai)

    def add_to_table(self, ma, soluong, gia, loai):
        """Thêm vào bảng QTableWidget (table)"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(loai))  # Loại (Thú Cưng/Sản Phẩm)
        self.table.setItem(row, 1, QTableWidgetItem(str(ma)))  # Mã (MaThuCung/MaSanPham)
        self.table.setItem(row, 2, QTableWidgetItem(str(soluong)))  # Số lượng
        self.table.setItem(row, 3, QTableWidgetItem(f"{gia * soluong:,.0f} VNĐ"))  # Giá (thành tiền)
        self.update_total_price()

    def update_total_price(self):
        """Cập nhật tổng tiền"""
        total_price = 0
        for row in range(self.table.rowCount()):
            gia = float(self.table.item(row, 3).text().replace(" VNĐ", "").replace(",", ""))
            total_price += gia
        self.label_tong_tien_value.setText(f"{total_price:,.0f} VNĐ")

    def save_order(self):
        """Lưu hóa đơn và chi tiết vào database"""
        conn = connect_db()
        if not conn:
            QMessageBox.critical(self, "Lỗi", "Không thể kết nối đến cơ sở dữ liệu!")
            return

        cursor = conn.cursor()
        makhach = self.combo_khach.currentData()
        ngaylap = self.date_edit.date().toString("yyyy-MM-dd")  # Lấy ngày từ QDateEdit

        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Lỗi", "Vui lòng thêm ít nhất một thú cưng hoặc sản phẩm!")
            cursor.close()
            conn.close()
            return

        try:
            # 1. Tạo hóa đơn trước và lấy MaHoaDon
            cursor.execute(
                "INSERT INTO HoaDon (MaKhachHang, NgayLap, TongTien) VALUES (%s, %s, %s)",
                (makhach, ngaylap, 0)
            )
            conn.commit()
            cursor.execute("SELECT LAST_INSERT_ID()")
            mahoadon = cursor.fetchone()[0]

            tong_tien = 0
            for row in range(self.table.rowCount()):
                loai = self.table.item(row, 0).text()
                ma = self.table.item(row, 1).text()
                soluong = int(self.table.item(row, 2).text())
                gia = float(self.table.item(row, 3).text().replace(" VNĐ", "").replace(",", ""))  # Loại bỏ " VNĐ" và dấu phẩy để lấy giá

                ma_thucung = ma if loai == "Thú Cưng" else None
                ma_sanpham = ma if loai == "Sản Phẩm" else None

                cursor.execute(
                    "INSERT INTO ChiTietHoaDon (MaHoaDon, MaThuCung, MaSanPham, SoLuong, Gia) VALUES (%s, %s, %s, %s, %s)",
                    (mahoadon, ma_thucung, ma_sanpham, soluong, gia)
                )

                tong_tien += soluong * gia

            # 3. Cập nhật tổng tiền của hóa đơn
            cursor.execute("UPDATE HoaDon SET TongTien = %s WHERE MaHoaDon = %s", (tong_tien, mahoadon))
            conn.commit()

            QMessageBox.information(self, "Thành công", "Đơn hàng đã được lưu thành công!")
            self.close()
            if self.parent_window:
                self.parent_window.load_orders()  # Cập nhật giao diện chính (nếu có)

        except pymysql.Error as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi lưu đơn hàng: {str(e)}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AddOrderForm()
    window.show()
    sys.exit(app.exec())