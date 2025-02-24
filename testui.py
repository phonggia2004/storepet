from PyQt6 import uic
try:
    uic.loadUi("views/trangchu.ui")
    print("File .ui hợp lệ")
except Exception as e:
    print(f"Lỗi: {e}")
