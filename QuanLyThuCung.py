import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import pymysql
import os

def connect_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='cua_hang_thu_cung',
        cursorclass=pymysql.cursors.DictCursor
    )

def get_pets():
    connection = connect_db()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM thucung")
        pets = cursor.fetchall()
    connection.close()
    return pets

def delete_pet(pet_id):
    connection = connect_db()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM thucung WHERE MaThuCung=%s", (pet_id,))
        connection.commit()
    connection.close()
    messagebox.showinfo("Thành công", "Xóa thú cưng thành công!")
    display_pets()

def add_pet():
    add_window = tk.Toplevel(root)
    add_window.title("Thêm Thú Cưng")
    add_window.geometry("400x600")
    add_window.configure(bg="#4E342E")

    fields = ["Ten", "Loai", "Giong", "GioiTinh", "Tuoi", "GiaBan", "TinhTrangSucKhoe"]
    entries = {}

    for field in fields:
        tk.Label(add_window, text=f"{field}:", bg="#4E342E", fg="white", font=("Arial", 12)).pack(pady=5)
        entry = tk.Entry(add_window, font=("Arial", 12))
        entry.pack(pady=5)
        entries[field] = entry

    def select_image():
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            entries['image_link'].delete(0, tk.END)
            entries['image_link'].insert(0, file_path)

    tk.Label(add_window, text="image_link:", bg="#4E342E", fg="white", font=("Arial", 12)).pack(pady=5)
    entries['image_link'] = tk.Entry(add_window, font=("Arial", 12))
    entries['image_link'].pack(pady=5)
    ttk.Button(add_window, text="Chọn ảnh", command=select_image, style="TButton").pack(pady=5)

    def save_pet():
        pet_data = {field: entry.get() for field, entry in entries.items()}
        connection = connect_db()
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO thucung (Ten, Loai, Giong, GioiTinh, Tuoi, GiaBan, TinhTrangSucKhoe, image_link)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (pet_data['Ten'], pet_data['Loai'], pet_data['Giong'], pet_data['GioiTinh'], pet_data['Tuoi'], pet_data['GiaBan'], pet_data['TinhTrangSucKhoe'], pet_data['image_link']))
            connection.commit()
        connection.close()
        messagebox.showinfo("Thành công", "Thêm thú cưng thành công!")
        add_window.destroy()
        display_pets()

    ttk.Button(add_window, text="Lưu", command=save_pet, style="TButton").pack(pady=20)

def view_pet(pet):
    view_window = tk.Toplevel(root)
    view_window.title("Thông Tin Thú Cưng")
    view_window.geometry("400x600")
    view_window.configure(bg="#4E342E")

    canvas = tk.Canvas(view_window, bg="#4E342E")
    scrollbar = tk.Scrollbar(view_window, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#4E342E")

    scrollable_frame.bind(
        "<Configure>",
        lambda _: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    fields = ["Ten", "Loai", "Giong", "GioiTinh", "Tuoi", "GiaBan", "TinhTrangSucKhoe"]
    entries = {}

    for field in fields:
        frame = tk.Frame(scrollable_frame, bg="#4E342E")
        frame.pack(pady=5, fill="x")
        tk.Label(frame, text=f"{field}:", bg="#4E342E", fg="white", font=("Arial", 12)).pack(side="left")
        entry = tk.Entry(frame, font=("Arial", 12))
        entry.insert(0, pet[field])
        entry.pack(side="left", padx=5, fill="x", expand=True)
        entries[field] = entry

    if pet['image_link'] and os.path.exists(pet['image_link']):
        try:
            img = Image.open(pet['image_link']).resize((250, 250))
            img = ImageTk.PhotoImage(img)
            img_label = tk.Label(scrollable_frame, image=img, bg="#4E342E")
            img_label.image = img
            img_label.pack(pady=10)
        except Exception as e:
            tk.Label(scrollable_frame, text=f"Lỗi hiển thị ảnh: {e}", fg="red", bg="#4E342E", font=("Arial", 12)).pack()
    else:
        tk.Label(scrollable_frame, text="Không có ảnh", fg="yellow", bg="#4E342E", font=("Arial", 12)).pack()

    def update_pet():
        pet_data = {field: entry.get() for field, entry in entries.items()}
        connection = connect_db()
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE thucung
                SET Ten=%s, Loai=%s, Giong=%s, GioiTinh=%s, Tuoi=%s, GiaBan=%s, TinhTrangSucKhoe=%s
                WHERE MaThuCung=%s
            """, (pet_data['Ten'], pet_data['Loai'], pet_data['Giong'], pet_data['GioiTinh'], pet_data['Tuoi'], pet_data['GiaBan'], pet_data['TinhTrangSucKhoe'], pet['MaThuCung']))
            connection.commit()
        connection.close()
        messagebox.showinfo("Thành công", "Cập nhật thông tin thú cưng thành công!")
        view_window.destroy()
        display_pets()

    ttk.Button(scrollable_frame, text="Cập nhật", command=update_pet, style="TButton").pack(pady=20)

def display_pets():
    pets = get_pets()
    for widget in pets_frame.winfo_children():
        widget.destroy()
    
    for index, pet in enumerate(pets):
        row, col = divmod(index, 4)
        pet_frame = tk.Frame(pets_frame, relief=tk.RAISED, borderwidth=2, padx=15, pady=15, bg="#6D4C41")
        pet_frame.grid(row=row, column=col, padx=20, pady=20)
        
        if pet['image_link'] and os.path.exists(pet['image_link']):
            try:
                img = Image.open(pet['image_link']).resize((150, 150))
                img = ImageTk.PhotoImage(img)
                img_label = tk.Label(pet_frame, image=img, cursor="hand2", bg="#6D4C41")
                img_label.image = img
                img_label.pack()
                img_label.bind("<Button-1>", lambda _, p=pet: view_pet(p))
            except Exception as e:
                tk.Label(pet_frame, text=f"Lỗi ảnh: {e}", fg="red", bg="#6D4C41").pack()
        else:
            tk.Label(pet_frame, text="Không có ảnh", fg="yellow", bg="#6D4C41").pack()
        
        
        ttk.Button(pet_frame, text="Xóa", command=lambda p=pet['MaThuCung']: delete_pet(p), style="TButton").pack()

def search_pet():
    query = search_entry.get().lower()
    pets = get_pets()
    for widget in pets_frame.winfo_children():
        widget.destroy()
    
    filtered_pets = [pet for pet in pets if query in pet['Ten'].lower() or query in pet['Giong'].lower()]
    for index, pet in enumerate(filtered_pets):
        row, col = divmod(index, 4)
        pet_frame = tk.Frame(pets_frame, relief=tk.RAISED, borderwidth=2, padx=15, pady=15, bg="#6D4C41")
        pet_frame.grid(row=row, column=col, padx=20, pady=20)
        
        if pet['image_link'] and os.path.exists(pet['image_link']):
            try:
                img = Image.open(pet['image_link']).resize((150, 150))
                img = ImageTk.PhotoImage(img)
                img_label = tk.Label(pet_frame, image=img, cursor="hand2", bg="#6D4C41")
                img_label.image = img
                img_label.pack()
                img_label.bind("<Button-1>", lambda e, p=pet: view_pet(p))
            except:
                tk.Label(pet_frame, text="Lỗi ảnh", fg="red", bg="#6D4C41").pack()
        else:
            tk.Label(pet_frame, text="Không có ảnh", fg="yellow", bg="#6D4C41").pack()
        
        ttk.Button(pet_frame, text="Xem", command=lambda p=pet: view_pet(p), style="TButton").pack()
        ttk.Button(pet_frame, text="Xóa", command=lambda p=pet['MaThuCung']: delete_pet(p), style="TButton").pack()

def go_home():
    root.destroy()
    os.system('python home.py')

root = tk.Tk()
root.title("Quản Lý Thú Cưng")
root.geometry("1300x900")
root.configure(bg="#3E2723")

home_button = ttk.Button(root, text="Trang chủ", command=go_home, style="TButton")
home_button.place(x=10, y=10)

style = ttk.Style()
style.configure("TButton", font=("Arial", 12), padding=8, background="#8D6E63")

search_frame = tk.Frame(root, bg="#3E2723")
search_frame.pack(pady=10)
tk.Label(search_frame, text="Tìm kiếm:", fg="white", bg="#3E2723", font=("Arial", 12)).pack(side=tk.LEFT)
search_entry = tk.Entry(search_frame, font=("Arial", 12))
search_entry.pack(side=tk.LEFT, padx=5)
ttk.Button(search_frame, text="Tìm", command=search_pet, style="TButton").pack(side=tk.LEFT)

ttk.Button(root, text="Thêm Thú Cưng", command=add_pet, style="TButton").pack(pady=10)

ttk.Button(root, text="Làm mới", command=display_pets, style="TButton").pack(pady=10)

# Create a canvas and scrollbar for the pets frame
canvas = tk.Canvas(root, bg="#3E2723")
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
pets_frame = tk.Frame(canvas, bg="#3E2723")

pets_frame.bind(
    "<Configure>",
    lambda _: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=pets_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

display_pets()
root.mainloop()
