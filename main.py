from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.core.text import LabelBase

from datetime import datetime,timedelta
import models  # your database models
import peewee
import admin # admin authentication
from admin import SuperAdminScreen

# Ethiopian calendar conversion

from ethiopia_calander import EthiopianCalendarScreen
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup

Window.clearcolor = (0.95, 0.95, 0.95, 1)

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
        grade_sections = models.GradeSection.select().where(models.GradeSection.grade > 8).order_by(models.GradeSection.grade, models.GradeSection.section)
        for gs in grade_sections:
            students = models.Student.select().where(models.Student.section_id == gs)
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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = self._login_screen()
        self.add_widget(layout)

    def login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        admin_result = admin.authenticate_admin(username, password)
        if admin_result is not None:
            print(f"Admin {admin_result['admin_name']} successful logged in")
            self.manager.current = "super_admin"
            return
            

        teacher = models.Teacher.authenticate(username, password)
        if teacher is not None and teacher.role == 'teacher':
            print(f"Login successful for {teacher.full_name}")
            self.manager.current = "dashboard"
            return
        
        print("Invalid username or password")

    def logout(self,instance):
        self.add_widget(self._login_screen())
    def _login_screen(self):
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20,)
        layout.add_widget(Label(text="Login", font_size=30, color=(0.1, 0.3, 0.6, 1)))

        self.username_input = TextInput(hint_text="Username", multiline=False)
        self.password_input = TextInput(hint_text="Password", multiline=False, password=True)
        layout.add_widget(self.username_input)
        layout.add_widget(self.password_input)

        login_btn = Button(text="Login", size_hint_y=None, height=50, background_color=(0.4, 0.7, 1, 1), color=(1, 1, 1, 1))
        login_btn.bind(on_press=self.login)
        layout.add_widget(login_btn)
        return layout

# -------- DASHBOARD --------
class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        layout.add_widget(Label(text="Dashboard", font_size=30, color=(0.1, 0.3, 0.6, 1)))

        marks_btn = Button(text="Marks", size_hint_y=None, height=50)
        attendance_btn = Button(text="Attendance", size_hint_y=None, height=50)
        attendance_btn.bind(on_press=self.open_calendar)

        layout.add_widget(marks_btn)
        layout.add_widget(attendance_btn)
        self.add_widget(layout)

    def open_calendar(self, instance):
        self.manager.current = "calendar"



# -------- MAIN APP --------
class SMISApp(App):
    def build(self):
        LabelBase.register(name="AmharicFont", fn_regular="AbyssinicaSIL-2.300/AbyssinicaSIL-2.300/AbyssinicaSIL-Regular.ttf")
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(EthiopianCalendarScreen(name="calendar"))
        sm.add_widget(AllStudentsGroupedByGradeSection(name="all_students"))
        sm.add_widget(SuperAdminScreen(name="super_admin"))
        return sm


if __name__ == "__main__":
    SMISApp().run()
