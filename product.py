
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox, QTableWidgetItem
from config import connect_db

class ProductApp(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("views/product.ui", self)
        
        # self.btn_add.clicked.connect(self.add_product)
        # self.btn_update.clicked.connect(self.update_product)
        # self.btn_delete.clicked.connect(self.delete_product)
        # self.btn_search.clicked.connect(self.search_products)
        # self.btn_refresh.clicked.connect(self.refresh_data)
        # self.lineEdit_mahang.textChanged.connect(self.fill_product_info)

        self.load_products()

    def load_products(self):
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT MaSanPham, Ten, DanhMuc, Gia, SoLuongTonKho, MoTa 
            FROM sanpham
            ORDER BY MaSanPham
        """)
        rows = cursor.fetchall()

        self.tableWidget.setRowCount(0)
    
        # Set up table
        self.tableWidget.setRowCount(len(rows))
    
        # Fill table with data
        for row, product in enumerate(rows):
            for col, value in enumerate(product):
                item = QTableWidgetItem(str(value))
                self.tableWidget.setItem(row, col, item)
        
        # Ẩn cột "Mã Sản Phẩm" (cột đầu tiên)
        self.tableWidget.setColumnHidden(0, True)

        cursor.close()
        conn.close()


    # def fill_product_info(self):
    #     mahang = self.lineEdit_mahang.text().strip()
    #     if not mahang:
    #         self.clear_inputs()
    #         return

    #     conn = connect_db()
    #     if conn:
    #         try:
    #             cursor = conn.cursor()
    #             cursor.execute("SELECT tenhang, mota, dongia, nguongoc FROM tbmathang WHERE mahang = %s", (mahang,))
    #             row = cursor.fetchone()
    #             if row:
    #                 self.lineEdit_tenhang.setText(row[0])
    #                 self.lineEdit_mota.setText(row[1])
    #                 self.lineEdit_dongia.setText(str(row[2]))
    #                 self.lineEdit_nguongoc.setText(row[3])
    #             else:
    #                 self.clear_inputs()
    #         except Exception as e:
    #             QMessageBox.critical(self, "Lỗi", str(e))
    #         finally:
    #             cursor.close()
    #             conn.close()
    
    # def add_product(self):
    #     values = {
    #         "mahang": self.lineEdit_mahang.text().strip(),
    #         "tenhang": self.lineEdit_tenhang.text().strip(),
    #         "mota": self.lineEdit_mota.text().strip(),
    #         "dongia": self.lineEdit_dongia.text().strip(),
    #         "nguongoc": self.lineEdit_nguongoc.text().strip(),
    #     }
    #     if not values["mahang"] or not values["tenhang"] or not values["dongia"]:
    #         QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập đầy đủ thông tin bắt buộc!")
    #         return

    #     conn = connect_db()
    #     if conn:
    #         try:
    #             cursor = conn.cursor()
    #             sql = """INSERT INTO tbmathang (mahang, tenhang, mota, dongia, nguongoc) 
    #                      VALUES (%s, %s, %s, %s, %s)"""
    #             cursor.execute(sql, tuple(values.values()))
    #             conn.commit()
    #             QMessageBox.information(self, "Thành công", "Thêm mặt hàng thành công!")
    #             self.load_products()
    #             self.clear_inputs()
    #         except Exception as e:
    #             QMessageBox.critical(self, "Lỗi", str(e))
    #         finally:
    #             cursor.close()
    #             conn.close()
    
    # def update_product(self):
    #     mahang = self.lineEdit_mahang.text().strip()
    #     if not mahang:
    #         QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập mã hàng!")
    #         return

    #     values = {
    #         "tenhang": self.lineEdit_tenhang.text().strip(),
    #         "mota": self.lineEdit_mota.text().strip(),
    #         "dongia": self.lineEdit_dongia.text().strip(),
    #         "nguongoc": self.lineEdit_nguongoc.text().strip(),
    #     }

    #     conn = connect_db()
    #     if conn:
    #         try:
    #             cursor = conn.cursor()
    #             sql = """UPDATE tbmathang 
    #                      SET tenhang=%s, mota=%s, dongia=%s, nguongoc=%s 
    #                      WHERE mahang=%s"""
    #             cursor.execute(sql, (values["tenhang"], values["mota"], values["dongia"], values["nguongoc"], mahang))
    #             conn.commit()
    #             QMessageBox.information(self, "Thành công", "Cập nhật thành công!")
    #             self.load_products()
    #             self.clear_inputs()
    #         except Exception as e:
    #             QMessageBox.critical(self, "Lỗi", str(e))
    #         finally:
    #             cursor.close()
    #             conn.close()
    
    # def delete_product(self):
    #     mahang = self.lineEdit_mahang.text().strip()
    #     if not mahang:
    #         QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập mã hàng!")
    #         return

    #     reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa mặt hàng này?",
    #                                  QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

    #     if reply == QMessageBox.StandardButton.Yes:
    #         conn = connect_db()
    #         if conn:
    #             try:
    #                 cursor = conn.cursor()
    #                 cursor.execute("DELETE FROM tbmathang WHERE mahang=%s", (mahang,))
    #                 conn.commit()
    #                 QMessageBox.information(self, "Thành công", "Xóa thành công!")
    #                 self.load_products()
    #                 self.clear_inputs()
    #             except Exception as e:
    #                 QMessageBox.critical(self, "Lỗi", str(e))
    #             finally:
    #                 cursor.close()
    #                 conn.close()

    # def search_products(self):
    #     mahang = self.lineEdit_mahang.text().strip()
    #     tenhang = self.lineEdit_tenhang.text().strip()
    #     nguongoc = self.lineEdit_nguongoc.text().strip()
        
    #     if not mahang and not tenhang and not nguongoc:
    #         QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập ít nhất một trường để tìm kiếm!")
    #         return

    #     conn = connect_db()
    #     if conn:
    #         try:
    #             cursor = conn.cursor()
    #             sql = "SELECT * FROM tbmathang WHERE (mahang LIKE %s OR %s = '') AND (tenhang LIKE %s OR %s = '') AND (nguongoc LIKE %s OR %s = '')"
    #             params = (f"%{mahang}%", mahang, f"%{tenhang}%", tenhang, f"%{nguongoc}%", nguongoc)
    #             cursor.execute(sql, params)
    #             rows = cursor.fetchall()

    #             self.table_products.setRowCount(len(rows))
    #             for i, row in enumerate(rows):
    #                 for j, value in enumerate(row):
    #                     self.table_products.setItem(i, j, QTableWidgetItem(str(value)))
    #         except Exception as e:
    #             QMessageBox.critical(self, "Lỗi", str(e))
    #         finally:
    #             cursor.close()
    #             conn.close()

    def refresh_data(self):
        self.clear_inputs()
        self.load_products()

    def clear_inputs(self):
        self.lineEdit_tenhang.clear()
        self.lineEdit_mota.clear()
        self.lineEdit_dongia.clear()
        self.lineEdit_nguongoc.clear()

if __name__ == "__main__":
    app = QApplication([])
    window = ProductApp()
    window.show()
    app.exec()
