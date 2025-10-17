import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import pickle
import os
from datetime import datetime # تم إبقاء استيراد datetime لأنه ضروري لحفظ وتحديد المواعيد

# بيانات المستخدمين (المشرفين)
USERS = {'admin': '1234'}

# ملف الأطباء
DOCTORS_FILE = "doctors.pkl"

# تحميل / حفظ الأطباء
DOCTORS = {}  # تعريفها كمتغير عام هنا قبل الدوال
def load_doctors_data():
    global DOCTORS
    if os.path.exists(DOCTORS_FILE):
        with open(DOCTORS_FILE, 'rb') as f:
            DOCTORS = pickle.load(f)
    else:
        DOCTORS = {
            'د. أحمد': {'speciality': 'باطنية', 'age': 45, 'info': 'خبير في الأمراض المزمنة'},
            'د. ليلى': {'speciality': 'جلدية', 'age': 38, 'info': 'خبيرة في أمراض الجلد'},
            'د. سامي': {'speciality': 'أسنان', 'age': 40, 'info': 'خبير في طب الأسنان'}
        }

def save_doctors_data():
    with open(DOCTORS_FILE, 'wb') as f:
        pickle.dump(DOCTORS, f)

# ملفات أخرى
BOOKING_FILE = "bookings.pkl"
SETTINGS_FILE = "settings.pkl"

def load_bookings_data():
    if os.path.exists(BOOKING_FILE):
        with open(BOOKING_FILE, 'rb') as f:
            return pickle.load(f)
    return []

def save_bookings_data(bookings):
    with open(BOOKING_FILE, 'wb') as f:
        pickle.dump(bookings, f)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'rb') as f:
            return pickle.load(f)
    return {'bg_color': 'white', 'app_name': 'برنامج حجز مستشفى عن بعد', 'logo_path': None}

def save_settings(settings):
    with open(SETTINGS_FILE, 'wb') as f:
        pickle.dump(settings, f)

class App:
    def __init__(self, master):
        self.master = master
        self.settings = load_settings()
        self.master.title(self.settings.get('app_name', "برنامج حجز مستشفى عن بعد"))
        self.master.geometry("600x600")
        self.master.configure(bg=self.settings.get('bg_color', 'white'))
        
        load_doctors_data()
        self.bookings = load_bookings_data()
        self.current_user = None
        
        # ليبل للإشعارات في وسط الشاشة
        self.notice_label = tk.Label(self.master, text="", bg='yellow', font=('Arial', 12))
        
        self.logo_label = None
        self.apply_settings()

        footer_text = "مستشفى الشفاء - شارع الصحة - هاتف: 0123456789"
        self.footer = tk.Label(self.master, text=footer_text, font=('Arial',12), fg='black', bg=self.settings.get('bg_color', 'white'))
        self.footer.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.create_login_screen()

    def clear_screen(self):
        for widget in self.master.winfo_children():
            # إزالة الليبل الخاص بالشعار إذا كان موجوداً
            if widget is self.logo_label:
                self.logo_label.destroy()
                self.logo_label = None # إعادة تعيينه
            
            # إزالة الليبل الخاص بالإشعارات إذا كان موجوداً
            if widget is self.notice_label:
                self.notice_label.pack_forget() # إخفاء الليبل بدلاً من تدميره
            
            # تدمير باقي الودجات باستثناء Footer
            if widget not in (self.footer, self.notice_label):
                 widget.destroy()

    def show_notice(self, message, color="yellow"):
        # عرض الإشعار في منتصف الشاشة
        self.notice_label.config(text=message, bg=color, bd=1, relief='solid', padx=10, pady=5)
        self.notice_label.place(relx=0.5, rely=0.5, anchor='center', y=100) # مكان نسبي

        if message == "":
            self.notice_label.place_forget() # إخفاء الإشعار

    def create_login_screen(self):
        self.clear_screen()
        self.apply_logo_to_center()
        
        tk.Label(self.master, text="تسجيل الدخول (المستخدم الرئيسي)", font=('Arial', 16,'bold'), bg=self.settings.get('bg_color', 'white')).pack(pady=20)
        
        tk.Label(self.master, text="اسم المستخدم:", font=('Arial', 12), bg=self.settings.get('bg_color', 'white')).pack()
        self.user_entry = tk.Entry(self.master, font=('Arial', 12))
        self.user_entry.pack(pady=5)
        
        tk.Label(self.master, text="كلمة السر:", font=('Arial', 12), bg=self.settings.get('bg_color', 'white')).pack()
        self.pass_entry = tk.Entry(self.master, font=('Arial', 12), show="*") # تم تعديل Show لتظهر النجوم
        self.pass_entry.pack(pady=5)
        
        tk.Button(self.master, text="تسجيل الدخول", font=('Arial', 12), bg='#4CAF50', fg='white', command=self.login).pack(pady=15)
        
        tk.Label(self.master, text="أو", font=('Arial', 12), bg=self.settings.get('bg_color', 'white')).pack(pady=10)
        
        # تم استبدال زر الدخول المباشر بزر دخول المريض (لتعبئة بياناته)
        tk.Button(self.master, text="دخول الحجز (للمريض)", font=('Arial', 12), bg='#2196F3', fg='white', command=self.patient_login_screen).pack()

    def login(self):
        user = self.user_entry.get()
        password = self.pass_entry.get()
        
        # إخفاء الإشعار السابق
        self.show_notice("") 
        
        if user in USERS and USERS[user] == password:
            self.current_user = user
            self.main_admin_screen()
        else:
            # عرض الإشعار في المنتصف
            self.show_notice("اسم المستخدم أو كلمة السر غير صحيحة", color='red') 

    # شاشة دخول المريض (لإدخال الاسم ورقم الهاتف)
    def patient_login_screen(self):
        self.clear_screen()
        tk.Label(self.master, text="تسجيل دخول المريض", font=('Arial',16,'bold'), bg=self.settings.get('bg_color', 'white')).pack(pady=15)

        form_frame = tk.Frame(self.master, bg=self.settings.get('bg_color', 'white'))
        form_frame.pack(pady=10)
        
        tk.Label(form_frame, text="اسم المريض:", font=('Arial',12), bg=self.settings.get('bg_color', 'white')).grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.patient_name_entry = tk.Entry(form_frame, font=('Arial',12))
        self.patient_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(form_frame, text="رقم الهاتف:", font=('Arial',12), bg=self.settings.get('bg_color', 'white')).grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.phone_entry = tk.Entry(form_frame, font=('Arial',12))
        self.phone_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(self.master, text="بدء الحجز", font=('Arial', 14), bg='#2196F3', fg='white', command=self.start_booking).pack(pady=15)
        tk.Button(self.master, text="العودة", font=('Arial', 12), command=self.create_login_screen).pack()

    def start_booking(self):
        name = self.patient_name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        
        if not name or not phone:
            self.show_notice("الرجاء إدخال اسم المريض ورقم الهاتف", color='red')
            return

        # حفظ البيانات مؤقتاً والانتقال لشاشة الحجز
        self._temp_patient_name = name
        self._temp_patient_phone = phone
        self.booking_screen()

    def booking_screen(self):
        self.clear_screen()
        tk.Label(self.master, text="تعبئة بيانات الحجز", font=('Arial',16,'bold'), bg=self.settings.get('bg_color', 'white')).pack(pady=15)

        form_frame = tk.Frame(self.master, bg=self.settings.get('bg_color', 'white'))
        form_frame.pack(pady=10)
        
        # تم استخدام الاسم ورقم الهاتف من الشاشة السابقة
        tk.Label(form_frame, text="الاسم الكامل:", font=('Arial',12), bg=self.settings.get('bg_color', 'white')).grid(row=0, column=0, sticky='e')
        self.name_label = tk.Label(form_frame, text=self._temp_patient_name, font=('Arial',12, 'bold'), bg=self.settings.get('bg_color', 'white'))
        self.name_label.grid(row=0, column=1, pady=5, sticky='w')
        
        tk.Label(form_frame, text="رقم الهاتف:", font=('Arial',12), bg=self.settings.get('bg_color', 'white')).grid(row=1, column=0, sticky='e')
        self.phone_label = tk.Label(form_frame, text=self._temp_patient_phone, font=('Arial',12, 'bold'), bg=self.settings.get('bg_color', 'white'))
        self.phone_label.grid(row=1, column=1, pady=5, sticky='w')
        
        tk.Label(form_frame, text="العنوان:", font=('Arial',12), bg=self.settings.get('bg_color', 'white')).grid(row=2, column=0, sticky='e')
        self.address_entry = tk.Entry(form_frame, font=('Arial',12))
        self.address_entry.grid(row=2, column=1, pady=5)
        
        tk.Label(form_frame, text="هل تعاني من مرض سابق؟", font=('Arial',12), bg=self.settings.get('bg_color', 'white')).grid(row=3, column=0, sticky='e')
        self.sick_var = tk.StringVar(value="لا")
        sick_frame = tk.Frame(form_frame, bg=self.settings.get('bg_color', 'white'))
        sick_frame.grid(row=3, column=1, pady=5)
        tk.Radiobutton(sick_frame, text="نعم", variable=self.sick_var, value="نعم", bg=self.settings.get('bg_color', 'white')).pack(side='left')
        tk.Radiobutton(sick_frame, text="لا", variable=self.sick_var, value="لا", bg=self.settings.get('bg_color', 'white')).pack(side='left')
        
        tk.Label(form_frame, text="اختر الطبيب:", font=('Arial',12), bg=self.settings.get('bg_color', 'white')).grid(row=4, column=0, sticky='e')
        
        # قائمة الأطباء مع التخصص
        doctor_options = [f"{name} ({data['speciality']})" for name, data in DOCTORS.items()]
        self.doctor_cb = ttk.Combobox(form_frame, values=doctor_options, font=('Arial',12), state="readonly")
        self.doctor_cb.grid(row=4, column=1, pady=5)
        if DOCTORS:
            self.doctor_cb.current(0)
            
        tk.Label(form_frame, text="العمر:", font=('Arial',12), bg=self.settings.get('bg_color', 'white')).grid(row=5, column=0, sticky='e')
        self.age_entry = tk.Entry(form_frame, font=('Arial',12))
        self.age_entry.grid(row=5, column=1, pady=5)

        tk.Button(self.master, text="حجز الموعد", font=('Arial', 14), bg='#4CAF50', fg='white', command=self.book_appointment).pack(pady=15)
        tk.Button(self.master, text="العودة", font=('Arial', 12), command=self.patient_login_screen).pack()

    def book_appointment(self):
        # استخدام الاسم ورقم الهاتف من البيانات المؤقتة
        name = self._temp_patient_name
        phone = self._temp_patient_phone
        
        address = self.address_entry.get().strip()
        sick = self.sick_var.get()
        
        # استخراج اسم الطبيب فقط من القائمة المنسدلة (مثال: "د. أحمد (باطنية)" -> "د. أحمد")
        selected_doctor_full = self.doctor_cb.get()
        doctor_name = selected_doctor_full.split(' ')[0] # نفترض أن اسم الطبيب هو الكلمة الأولى قبل الفراغ
        
        age = self.age_entry.get().strip()

        if not name or not phone or not address or not age.isdigit():
            self.show_notice("الرجاء تعبئة جميع الحقول بشكل صحيح", color='red')
            return

        booking = {
            'name': name,
            'phone': phone, # تم إضافة رقم الهاتف
            'address': address,
            'sick': sick,
            'doctor': doctor_name, # حفظ اسم الطبيب فقط
            'age': int(age),
            'status': 'في الانتظار',
            'appointment_time': None,
            'requested_at': datetime.now()
        }

        self.bookings.append(booking)
        save_bookings_data(self.bookings)
        self.show_notice("تم الحجز بنجاح", color='green')
        self.create_login_screen()

    def main_admin_screen(self):
        self.clear_screen()
        tk.Label(self.master, text=f"مرحباً {self.current_user} - إدارة الحجوزات", font=('Arial',16,'bold'), bg=self.settings.get('bg_color', 'white')).pack(pady=10)
        
        columns = ("name", "phone", "address", "sick", "doctor", "age", "status", "appt_time") # إضافة رقم الهاتف
        self.tree = ttk.Treeview(self.master, columns=columns, show='headings')
        self.tree.pack(fill='both', expand=True, pady=10)
        
        headers = {
            "name": "الاسم", 
            "phone": "الهاتف", # إضافة الهاتف
            "address": "العنوان", 
            "sick": "مرض سابق", 
            "doctor": "الطبيب", 
            "age": "العمر", 
            "status": "الحالة", 
            "appt_time": "ميعاد الموعد"
        }
        
        for col in columns:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=100, anchor='center')
        
        self.load_bookings()

        btn_frame = tk.Frame(self.master, bg=self.settings.get('bg_color', 'white'))
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="قبول الحجز وتحديد موعد", bg='#2196F3', fg='white', command=self.accept_booking).pack(side='left', padx=5)
        tk.Button(btn_frame, text="تحديث", command=self.load_bookings).pack(side='left', padx=5)
        tk.Button(btn_frame, text="تعديل", command=self.edit_booking).pack(side='left', padx=5)
        tk.Button(btn_frame, text="حذف", command=self.delete_booking).pack(side='left', padx=5)
        tk.Button(btn_frame, text="تسجيل خروج", bg='#f44336', fg='white', command=self.logout).pack(side='left', padx=5)
        
        if self.current_user == 'admin':
            tk.Button(btn_frame, text="الإعدادات", bg='#9C27B0', fg='white', command=self.open_settings).pack(side='left', padx=5)
            tk.Button(btn_frame, text="إدارة الأطباء", bg='#009688', fg='white', command=self.manage_doctors).pack(side='left', padx=5)

    def load_bookings(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for b in self.bookings:
            appt_str = b['appointment_time'].strftime("%Y-%m-%d %H:%M") if b['appointment_time'] else "-"
            # التحقق من وجود 'phone' لضمان التوافق مع البيانات القديمة
            phone_val = b.get('phone', '-') 
            self.tree.insert('', 'end', values=(b['name'], phone_val, b['address'], b['sick'], b['doctor'], b['age'], b['status'], appt_str))
            
    # إدارة الأطباء ----------------------------------------------------
    def manage_doctors(self):
        self.clear_screen()
        tk.Label(self.master, text="إدارة الأطباء", font=('Arial', 16, 'bold'), bg=self.settings.get('bg_color', 'white')).pack(pady=15)
        
        columns = ("name", "speciality", "age", "info")
        self.doctor_tree = ttk.Treeview(self.master, columns=columns, show='headings')
        self.doctor_tree.pack(fill='both', expand=True, pady=10)
        
        headers = {"name": "اسم الطبيب", "speciality": "التخصص", "age": "العمر", "info": "معلومات إضافية"}
        for col in columns:
            self.doctor_tree.heading(col, text=headers[col])
            self.doctor_tree.column(col, width=130, anchor='center')
        
        self.load_doctors_to_tree()
        
        btn_frame = tk.Frame(self.master, bg=self.settings.get('bg_color', 'white'))
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="إضافة طبيب", bg='#4CAF50', fg='white', command=self.add_doctor_screen).pack(side='left', padx=5)
        tk.Button(btn_frame, text="تعديل طبيب", bg='#2196F3', fg='white', command=self.edit_doctor_screen).pack(side='left', padx=5)
        tk.Button(btn_frame, text="حذف طبيب", bg='#f44336', fg='white', command=self.delete_doctor).pack(side='left', padx=5)
        tk.Button(btn_frame, text="عودة", command=self.main_admin_screen).pack(side='left', padx=5)

    def load_doctors_to_tree(self):
        for row in self.doctor_tree.get_children():
            self.doctor_tree.delete(row)
        for name, data in DOCTORS.items():
            self.doctor_tree.insert('', 'end', values=(name, data['speciality'], data['age'], data['info']))

    def add_doctor_screen(self):
        win = tk.Toplevel(self.master)
        win.title("إضافة طبيب")
        self.doctor_form(win, mode='add')

    def edit_doctor_screen(self):
        selected = self.doctor_tree.focus()
        if not selected:
            self.show_notice("يرجى اختيار الطبيب لتعديله", color='red')
            return
        
        values = self.doctor_tree.item(selected, 'values')
        name = values[0]
        data = DOCTORS[name]
        
        win = tk.Toplevel(self.master)
        win.title("تعديل طبيب")
        self.doctor_form(win, mode='edit', name=name, data=data)

    def doctor_form(self, win, mode='add', name='', data=None):
        tk.Label(win, text="اسم الطبيب:", font=('Arial', 12)).grid(row=0, column=0, pady=5, sticky='e')
        name_entry = tk.Entry(win, font=('Arial', 12))
        name_entry.grid(row=0, column=1, pady=5)
        if mode == 'edit':
            name_entry.insert(0, name)

        tk.Label(win, text="التخصص:", font=('Arial', 12)).grid(row=1, column=0, pady=5, sticky='e')
        spec_entry = tk.Entry(win, font=('Arial', 12))
        spec_entry.grid(row=1, column=1, pady=5)
        if data:
            spec_entry.insert(0, data['speciality'])

        tk.Label(win, text="العمر:", font=('Arial', 12)).grid(row=2, column=0, pady=5, sticky='e')
        age_entry = tk.Entry(win, font=('Arial', 12))
        age_entry.grid(row=2, column=1, pady=5)
        if data:
            age_entry.insert(0, str(data['age']))

        tk.Label(win, text="معلومات إضافية:", font=('Arial', 12)).grid(row=3, column=0, pady=5, sticky='e')
        info_entry = tk.Entry(win, font=('Arial', 12))
        info_entry.grid(row=3, column=1, pady=5)
        if data:
            info_entry.insert(0, data['info'])

        def save():
            new_name = name_entry.get().strip()
            speciality = spec_entry.get().strip()
            age = age_entry.get().strip()
            info = info_entry.get().strip()

            if not new_name or not speciality or not age.isdigit():
                messagebox.showerror("خطأ", "يرجى إدخال البيانات بشكل صحيح")
                return

            if mode == 'add':
                if new_name in DOCTORS:
                    messagebox.showerror("خطأ", "اسم الطبيب موجود بالفعل")
                    return
            elif mode == 'edit' and new_name != name and new_name in DOCTORS:
                messagebox.showerror("خطأ", "اسم الطبيب الجديد مستخدم بالفعل")
                return
            
            # عملية الحفظ
            if mode == 'edit' and name in DOCTORS:
                del DOCTORS[name]
                
            DOCTORS[new_name] = {'speciality': speciality, 'age': int(age), 'info': info}
            
            save_doctors_data()
            self.load_doctors_to_tree()
            self.show_notice("تم حفظ بيانات الطبيب", color='green')
            win.destroy()

        tk.Button(win, text="حفظ", bg='#4CAF50', fg='white', command=save).grid(row=4, column=0, columnspan=2, pady=10)

    def delete_doctor(self):
        selected = self.doctor_tree.focus()
        if not selected:
            self.show_notice("يرجى اختيار الطبيب للحذف", color='red')
            return

        values = self.doctor_tree.item(selected, 'values')
        name = values[0]

        confirm = messagebox.askyesno("تأكيد الحذف", f"هل أنت متأكد من حذف الطبيب {name}؟")
        if confirm:
            if name in DOCTORS:
                del DOCTORS[name]
                save_doctors_data()
                self.load_doctors_to_tree()
                self.show_notice("تم حذف الطبيب بنجاح", color='green')

    # -------------------------------------------------------------------
    def logout(self):
        self.current_user = None
        self.show_notice("")
        self.create_login_screen()

    def open_settings(self):
        self.clear_screen()
        tk.Label(self.master, text="الإعدادات", font=('Arial', 16, 'bold'), bg=self.settings.get('bg_color', 'white')).pack(pady=20)
        
        form_frame = tk.Frame(self.master, bg=self.settings.get('bg_color', 'white'))
        form_frame.pack(pady=10)
        
        tk.Label(form_frame, text="لون الخلفية:", font=('Arial', 12), bg=self.settings.get('bg_color', 'white')).grid(row=0, column=0, sticky='e')
        bg_entry = tk.Entry(form_frame, font=('Arial', 12))
        bg_entry.grid(row=0, column=1, pady=5)
        bg_entry.insert(0, self.settings.get('bg_color', 'white'))

        tk.Label(form_frame, text="اسم التطبيق:", font=('Arial', 12), bg=self.settings.get('bg_color', 'white')).grid(row=1, column=0, sticky='e')
        name_entry = tk.Entry(form_frame, font=('Arial', 12))
        name_entry.grid(row=1, column=1, pady=5)
        name_entry.insert(0, self.settings.get('app_name', 'برنامج حجز مستشفى عن بعد'))

        def choose_logo():
            path = filedialog.askopenfilename(title="اختر الشعار", filetypes=[("صور", ".png;.jpg;.jpeg")])
            if path:
                self.settings['logo_path'] = path
                messagebox.showinfo("تم", "تم اختيار الشعار بنجاح")

        tk.Button(form_frame, text="اختيار الشعار", command=choose_logo).grid(row=2, column=0, columnspan=2, pady=5)

        def save_set():
            self.settings['bg_color'] = bg_entry.get()
            self.settings['app_name'] = name_entry.get()
            save_settings(self.settings)
            self.apply_settings()
            messagebox.showinfo("تم", "تم حفظ الإعدادات بنجاح")
            self.main_admin_screen()

        tk.Button(self.master, text="حفظ الإعدادات", bg='#4CAF50', fg='white', command=save_set).pack(pady=15)
        tk.Button(self.master, text="عودة", command=self.main_admin_screen).pack()

    def apply_settings(self):
        self.master.configure(bg=self.settings.get('bg_color', 'white'))
        self.master.title(self.settings.get('app_name', 'برنامج حجز مستشفى عن بعد'))
        # تطبيق الشعار في شاشات معينة فقط (سيتم استدعاؤها في create_login_screen)
        # سيتم التعامل مع إظهاره في الوسط من خلال دالة منفصلة

    def apply_logo_to_center(self):
        # تدمير الليبل القديم إن وجد
        if self.logo_label:
            self.logo_label.destroy()
            self.logo_label = None

        if self.settings.get('logo_path') and os.path.exists(self.settings['logo_path']):
            try:
                from PIL import Image, ImageTk
                logo_img = Image.open(self.settings['logo_path']).resize((100,100))
                logo_photo = ImageTk.PhotoImage(logo_img)
                
                self.logo_label = tk.Label(self.master, image=logo_photo, bg=self.settings.get('bg_color', 'white'))
                self.logo_label.image = logo_photo
                
                # وضع الشعار في أعلى وسط الشاشة باستخدام place
                self.logo_label.place(relx=0.5, rely=0.05, anchor='n') 

            except ImportError:
                # هذه الرسالة تظهر إذا لم يتم تثبيت مكتبة Pillow
                print("يرجى تثبيت مكتبة Pillow: pip install Pillow")
            except Exception as e:
                print(f"خطأ في تحميل الشعار: {e}")

    def accept_booking(self):
        selected = self.tree.focus()
        if not selected:
            self.show_notice("يرجى اختيار حجز", color='red')
            return

        idx = self.tree.index(selected)
        booking = self.bookings[idx]

        top = tk.Toplevel(self.master)
        top.title("تحديد موعد")
        
        tk.Label(top, text="تاريخ ووقت الموعد (YYYY-MM-DD HH:MM):", font=('Arial',12)).pack(pady=5)
        entry = tk.Entry(top, font=('Arial',12))
        entry.pack(pady=5)

        def save_appt():
            try:
                dt = datetime.strptime(entry.get().strip(), "%Y-%m-%d %H:%M")
                booking['status'] = 'تم القبول'
                booking['appointment_time'] = dt
                save_bookings_data(self.bookings)
                self.load_bookings()
                self.show_notice("تم تحديد الموعد", color='green')
                top.destroy()
            except ValueError:
                messagebox.showerror("خطأ", "صيغة التاريخ غير صحيحة. يجب أن تكون YYYY-MM-DD HH:MM")

        tk.Button(top, text="حفظ", bg='#4CAF50', fg='white', command=save_appt).pack(pady=5)


    def edit_booking(self):
        selected = self.tree.focus()
        if not selected:
            self.show_notice("يرجى اختيار حجز", color='red')
            return

        idx = self.tree.index(selected)
        booking = self.bookings[idx]

        top = tk.Toplevel(self.master)
        top.title("تعديل الحجز")

        labels = ["الاسم", "رقم الهاتف", "العنوان", "مرض سابق", "الطبيب", "العمر"]
        keys = ["name", "phone", "address", "sick", "doctor", "age"]
        entries = {}

        for i, (lab, key) in enumerate(zip(labels, keys)):
            tk.Label(top, text=lab, font=('Arial',12)).grid(row=i, column=0, sticky='e', padx=5, pady=5)
            e = tk.Entry(top, font=('Arial',12))
            e.grid(row=i, column=1, padx=5, pady=5)
            e.insert(0, str(booking.get(key, '-'))) # استخدام .get لضمان التوافق
            entries[key] = e

        def save_changes():
            try:
                booking['name'] = entries['name'].get().strip()
                booking['phone'] = entries['phone'].get().strip() # حفظ الهاتف
                booking['address'] = entries['address'].get().strip()
                booking['sick'] = entries['sick'].get().strip()
                booking['doctor'] = entries['doctor'].get().strip()
                booking['age'] = int(entries['age'].get())

                save_bookings_data(self.bookings)
                self.load_bookings()
                self.show_notice("تم تعديل الحجز", color='green')
                top.destroy()
            except ValueError:
                messagebox.showerror("خطأ", "الرجاء إدخال عمر صحيح")
                
        tk.Button(top, text="حفظ", bg='#4CAF50', fg='white', command=save_changes).grid(row=len(labels), column=0, columnspan=2, pady=10)

    def delete_booking(self):
        selected = self.tree.focus()
        if not selected:
            self.show_notice("يرجى اختيار حجز للحذف", color='red')
            return

        idx = self.tree.index(selected)
        confirm = messagebox.askyesno("تأكيد", "هل أنت متأكد من حذف الحجز؟")
        if confirm:
            del self.bookings[idx]
            save_bookings_data(self.bookings)
            self.load_bookings()
            self.show_notice("تم حذف الحجز", color='green')

if __name__ == "__main__":
    # تأكد من تثبيت مكتبة Pillow لعرض الشعار (إذا كان هناك شعار)
    # pip install Pillow
    try:
        from PIL import Image, ImageTk
    except ImportError:
        print("تحذير: مكتبة Pillow غير مثبتة. لن يتم عرض الشعار.")

    root = tk.Tk()
    app = App(root)
    root.mainloop()
