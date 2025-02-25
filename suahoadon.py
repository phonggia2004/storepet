from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QDialog, QMessageBox, QTableWidgetItem, QInputDialog
from PyQt6.QtCore import Qt, QDate
from config import connect_db

class EditInvoiceDialog(QDialog):
    def __init__(self, parent=None, invoice_data=None):
        super().__init__(parent)
        uic.loadUi('views/suahoadon.ui', self)
        
        self.db = connect_db()
        self.cursor = self.db.cursor() if self.db else None
        self.invoice_data = invoice_data
        
        # Setup tables
        self.setup_product_table()
        self.setup_detail_table()
        
        # Connect signals
        self.categoryCombo.currentIndexChanged.connect(self.load_products)
        self.addToInvoiceButton.clicked.connect(self.add_to_invoice)
        self.saveButton.clicked.connect(self.save_changes)
        self.cancelButton.clicked.connect(self.reject)
        self.editDetailButton.clicked.connect(self.edit_detail)
        self.deleteDetailButton.clicked.connect(self.delete_detail)
        
        # Load data
        if invoice_data:
            self.load_invoice_data()
            self.load_detail_data()
            
        # Load initial products
        self.load_products()
        
        # Make invoice ID read-only
        self.invoiceId.setReadOnly(True)

    def setup_product_table(self):
        """Cấu hình bảng sản phẩm/thú cưng"""
    # Headers sẽ thay đổi tùy theo loại được chọn
        self.product_headers = {
            "Thú cưng": ["Mã", "Tên", "Giá", "Tình trạng sức khỏe"],
            "Sản phẩm": ["Mã", "Tên", "Giá", "Số lượng tồn"]
        }
    # Mặc định là thú cưng
        headers = self.product_headers["Thú cưng"]
        self.productTable.setColumnCount(len(headers))
        self.productTable.setHorizontalHeaderLabels(headers)
        self.productTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)

    def setup_detail_table(self):
        """Cấu hình bảng chi tiết hóa đơn"""
        headers = ["Mã Chi Tiết", "Mã Hóa Đơn", "Mã Thú Cưng", "Mã Sản Phẩm", "Số Lượng", "Giá", "Thành Tiền"]
        self.detailTable.setColumnCount(len(headers))
        self.detailTable.setHorizontalHeaderLabels(headers)
        self.detailTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)

    def load_invoice_data(self):
        """Load thông tin hóa đơn"""
        self.invoiceId.setText(self.invoice_data['MaHoaDon'])
        self.customerId.setText(self.invoice_data['MaKhachHang'])
        self.invoiceDate.setDate(QDate.fromString(self.invoice_data['NgayLap'], "yyyy-MM-dd"))

    def load_products(self):
        """Load danh sách sản phẩm hoặc thú cưng"""
        try:
            category = self.categoryCombo.currentText()
         # Cập nhật headers dựa trên loại được chọn
            headers = self.product_headers[category]
            self.productTable.setHorizontalHeaderLabels(headers)

            if category == "Thú cưng":
                self.cursor.execute("""
                    SELECT MaThuCung, Ten, GiaBan, TinhTrangSucKhoe 
                    FROM thucung 
                """)
            else:
                self.cursor.execute("""
                    SELECT MaSanPham, Ten, Gia, SoLuongTonKho 
                    FROM sanpham
                """)
            
            products = self.cursor.fetchall()
            self.productTable.setRowCount(len(products))
        
            for row, product in enumerate(products):
                for col, value in enumerate(product):
                    item = QTableWidgetItem(str(value))
                    if col == 2:  # Format price
                        item.setText(f"{value:,.0f} VNĐ")
                    elif col == 3 and category == "Thú cưng":  # Tình trạng sức khỏe
                        # Có thể thêm xử lý đặc biệt cho tình trạng sức khỏe nếu cần
                        pass
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.productTable.setItem(row, col, item)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải danh sách: {str(e)}")

    def load_detail_data(self):
        """Load chi tiết hóa đơn"""
        try:
            self.cursor.execute("""
                SELECT ct.MaChiTiet, ct.MaHoaDon, 
                       ct.MaThuCung, ct.MaSanPham, 
                       ct.SoLuong, ct.Gia,
                       ct.SoLuong * ct.Gia as ThanhTien
                FROM chitiethoadon ct
                WHERE ct.MaHoaDon = %s
            """, (self.invoice_data['MaHoaDon'],))
            
            details = self.cursor.fetchall()
            self.detailTable.setRowCount(len(details))
            
            for row, detail in enumerate(details):
                for col, value in enumerate(detail):
                    item = QTableWidgetItem(str(value))
                    if col in [5, 6]:  # Format price and total
                        item.setText(f"{value:,.0f} VNĐ")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.detailTable.setItem(row, col, item)
                    self.update_total_amount()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải chi tiết hóa đơn: {str(e)}")

    def add_to_invoice(self):
        """Thêm sản phẩm vào hóa đơn"""
        selected_row = self.productTable.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một sản phẩm!")
            return
        
        try:
            category = self.categoryCombo.currentText()
            ma = self.productTable.item(selected_row, 0).text()
            gia = self.productTable.item(selected_row, 2).text().replace(' VNĐ', '').replace(',', '')
        
            if category == "Sản phẩm":
                soluong_ton = int(self.productTable.item(selected_row, 3).text())
                if soluong_ton < self.quantitySpinBox.value():
                    QMessageBox.warning(self, "Cảnh báo", "Số lượng tồn không đủ!")
                    return
                
            soluong = self.quantitySpinBox.value()
        
            # Thêm vào chi tiết hóa đơn
            if category == "Thú cưng":
                self.cursor.execute("""
                    INSERT INTO chitiethoadon (MaHoaDon, MaThuCung, SoLuong, Gia)
                    VALUES (%s, %s, %s, %s)
                """, (self.invoice_data['MaHoaDon'], ma, soluong, gia))
            else:
                self.cursor.execute("""
                    INSERT INTO chitiethoadon (MaHoaDon, MaSanPham, SoLuong, Gia)
                    VALUES (%s, %s, %s, %s)
                """, (self.invoice_data['MaHoaDon'], ma, soluong, gia))
            
            self.db.commit()
            self.load_detail_data()
            self.load_products()
            self.update_total_amount()# Reload to update stock
            
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Lỗi", f"Không thể thêm vào hóa đơn: {str(e)}")

    def edit_detail(self):
        """Sửa chi tiết hóa đơn"""
        selected_row = self.detailTable.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một chi tiết để sửa!")
            return
            
        try:
            machitiet = self.detailTable.item(selected_row, 0).text()
            soluong_cu = int(self.detailTable.item(selected_row, 4).text())
            
            # Hiển thị dialog nhập số lượng mới
            soluong_moi, ok = QInputDialog.getInt(
                self, "Sửa số lượng", "Số lượng mới:",
                soluong_cu, 1, 100, 1
            )
            
            if ok and soluong_moi != soluong_cu:
                self.cursor.execute("""
                    UPDATE chitiethoadon 
                    SET SoLuong = %s
                    WHERE MaChiTiet = %s
                """, (soluong_moi, machitiet))
                
                self.db.commit()
                self.load_detail_data()
                self.load_products()
                self.update_total_amount()# Reload to update stock
                
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Lỗi", f"Không thể sửa chi tiết: {str(e)}")

    def delete_detail(self):
        """Xóa chi tiết hóa đơn"""
        selected_row = self.detailTable.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một chi tiết để xóa!")
            return
            
        machitiet = self.detailTable.item(selected_row, 0).text()
        
        reply = QMessageBox.question(
            self, "Xác nhận", 
            "Bạn có chắc muốn xóa chi tiết này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.cursor.execute("DELETE FROM chitiethoadon WHERE MaChiTiet = %s", (machitiet,))
                self.db.commit()
                self.load_detail_data()
                self.load_products()
                self.update_total_amount()# Reload to update stock
            except Exception as e:
                self.db.rollback()
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa chi tiết: {str(e)}")

    def validate_data(self):
        """Kiểm tra dữ liệu trước khi lưu"""
        if not self.customerId.text().strip():
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập mã khách hàng!")
            return False
            
        # Kiểm tra mã khách hàng có tồn tại
        self.cursor.execute(
            "SELECT COUNT(*) FROM khachhang WHERE MaKhachHang = %s",
            (self.customerId.text().strip(),)
        )
        if self.cursor.fetchone()[0] == 0:
            QMessageBox.warning(self, "Cảnh báo", "Mã khách hàng không tồn tại!")
            return False
            
        return True

    def save_changes(self):
        """Lưu thay đổi hóa đơn"""
        if not self.validate_data():
            return
            
        try:
            # Cập nhật thông tin hóa đơn
            self.cursor.execute("""
                UPDATE hoadon 
                SET MaKhachHang = %s, NgayLap = %s
                WHERE MaHoaDon = %s
            """, (
                self.customerId.text().strip(),
                self.invoiceDate.date().toString("yyyy-MM-dd"),
                self.invoiceId.text().strip()
            ))
            
            self.db.commit()
            QMessageBox.information(self, "Thành công", "Đã cập nhật hóa đơn thành công!")
            self.accept()
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật hóa đơn: {str(e)}")

    def update_total_amount(self):
        """Cập nhật tổng tiền trên form"""
        try:
            self.cursor.execute("""
                SELECT SUM(SoLuong * Gia) 
                FROM  chitiethoadon 
                WHERE MaHoaDon = %s
            """, (self.invoice_data['MaHoaDon'],))
        
            total = self.cursor.fetchone()[0] or 0
            self.totalAmount.setText(f"{total:,.0f} VNĐ")
        
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tính tổng tiền: {str(e)}")
    
    def closeEvent(self, event):
        """Xử lý sự kiện đóng cửa sổ"""
        if self.db and self.db.open:
            self.db.close()
        event.accept()