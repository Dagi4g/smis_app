from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.core.text import LabelBase

from datetime import datetime,timedelta
from db import models  # the database models
import peewee
from admin.superadmin import admin # admin authentication
from admin.superadmin.admin import SuperAdminScreen

# Ethiopian calendar conversion
from admin.school_admin import SchoolAdminTeacherCRUDScreen
from eth_custom_calendar import ethiopia_custom_calender
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup

Window.clearcolor = (0.95, 0.95, 0.95, 1)

class ErrorPopup(Popup):
        
    def on_ok(self):
        self.dismiss()
        
        
    def show_message(self,message):
        self.error_label.text = message
        self.open()

            

class AllStudentsGroupedByGradeSection(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical')
        scroll_view = ScrollView()
        self.grid_layout = GridLayout(cols=1, padding=10, spacing=10, size_hint_y=None)
        self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))
        scroll_view.add_widget(self.grid_layout)
        main_layout.add_widget(scroll_view)
        self.refresh()
        self.add_widget(main_layout)

    def refresh(self):
        self.grid_layout.clear_widgets()

        # List all students whose grade is above 8, grouped by grade/section
        grade_sections = models.session.query(models.GradeSection).filter(models.GradeSection.grade > 8).order_by(models.GradeSection.grade, models.GradeSection.section).all()
        for gs in grade_sections:
            students = session.query(models.Student).filter(models.Student.section_id == gs.id).all()
            student_names = [s.full_name for s in students]
            
            # Simulate <ol>...</ol> by numbering students
            if student_names:
                student_list = "\n".join([f"{i+1}. {name} " for i, name in enumerate(student_names)])
            else:
                student_list = "No students"
            label = Label(
                text=f"[b]{gs.grade} {gs.section}[/b]\n{student_list}",
                size_hint_y=None,
                height=40 + 20 * len(student_names),
                color=(0, 0, 0, 1),
                markup=True,
                halign="left",
                valign="top"
            )
            label.bind(size=label.setter('text_size'))
            btn = Button(text="back", size_hint_y=None, height=40, background_color=(0.4, 0.7, 1, 1), color=(1, 1, 1, 1))
            self.grid_layout.add_widget(label)
            btn.bind(on_press= lambda _:setattr(self.manager, 'current', 'dashboard'))
            self.grid_layout.add_widget(btn)
# -------- LOGIN SCREEN --------
class LoginScreen(Screen):
    def login(self):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        admin_result = admin.authenticate_admin(username, password)
        if not username and not password:
            ErrorPopup().show_message(message='empty user name and password ')
            return
        if admin_result is not None:
            print(f"Admin {admin_result['admin_name']} successful logged in")
            self.clear_userdata()

            self.manager.current = "super_admin"
            return
        
            

        teacher = models.Teacher.authenticate(models.session, username, password)
        if teacher is not None and teacher.role == 'teacher':
            print(f"Login successful for {teacher.full_name}")
            self.clear_userdata()
            self.manager.current = "dashboard"
            return
        elif teacher is not None and teacher.role == 'admin':
            print(f"Login successful for admin {teacher.full_name}")
            self.clear_userdata()
            self.manager.current = "school_admin_teacher_crud"
            return
        
        self.clear_userdata(password_only=True)

        ErrorPopup().show_message(message="Invalid username or password")
    def clear_userdata(self,password_only=False):
        if password_only:
            self.password_input.text = ''
        else:
            self.username_input.text = ""
            self.password_input.text = ""


# -------- DASHBOARD --------
class DashboardScreen(Screen):
    #In this dashboard page both the attendance and mark buttons will be placed for the teacher to press and go to the 
    # screen that corresponds to the button in the kivy file class .

    def open_calendar(self):
        self.manager.current = "calendar"



# -------- MAIN APP --------
class SmisApp(App):
    def build(self):
        LabelBase.register(name="AmharicFont", fn_regular="AbyssinicaSIL-2.300/AbyssinicaSIL-2.300/AbyssinicaSIL-Regular.ttf")
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(ethiopia_custom_calender.EthiopianCalendarScreen(name="calendar"))
        sm.add_widget(AllStudentsGroupedByGradeSection(name="all_students"))
        sm.add_widget(SuperAdminScreen(name="super_admin"))
        sm.add_widget(SchoolAdminTeacherCRUDScreen(name="school_admin_teacher_crud"))
        return sm


if __name__ == "__main__":
    SmisApp().run()
