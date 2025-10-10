from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.core.text import LabelBase

from datetime import datetime,timedelta
import models  # your database models
import models  # your database models

# Ethiopian date conversion
from ethiopian_date import EthiopianDateConverter

Window.clearcolor = (0.95, 0.95, 0.95, 1)


# -------- LOGIN SCREEN --------
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        layout.add_widget(Label(text="Login", font_size=30, color=(0.1, 0.3, 0.6, 1)))

        self.username_input = TextInput(hint_text="Username", multiline=False)
        self.password_input = TextInput(hint_text="Password", multiline=False, password=True)
        layout.add_widget(self.username_input)
        layout.add_widget(self.password_input)

        login_btn = Button(text="Login", size_hint_y=None, height=50, background_color=(0.4, 0.7, 1, 1), color=(1, 1, 1, 1))
        login_btn.bind(on_press=self.login)
        layout.add_widget(login_btn)

        self.add_widget(layout)

    def login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()

        teacher = models.Teacher.authenticate(username, password)
        if teacher:
            print(f"Login successful for {teacher.full_name}")
            self.manager.current = "dashboard"
        else:
            print("Invalid username or password")


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


# -------- ETHIOPIAN CALENDAR SCREEN --------
class EthiopianCalendarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.add_widget(self.layout)
        self.display_calendar()

    def display_calendar(self):
        self.layout.clear_widgets()

        # Get current Ethiopian date
        today = datetime.now() - timedelta(hours=72)
        eth_date = EthiopianDateConverter.to_ethiopian(today.year, today.month, today.day)
        year, month, day = eth_date.year, eth_date.month, eth_date.day
        

        self.layout.add_widget(Label(text=f"Ethiopian Calendar - {year}/{self.get_month_name(month)}", font_size=24, color=(0.1, 0.3, 0.6, 1),font_name="AmharicFont"))

        # Grid of days
        grid = GridLayout(cols=7, spacing=5, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        for d in range(1, 31):  # 30 days typical Ethiopian month
            btn = Button(text=str(d), size_hint_y=None, height=50)
            btn.bind(on_press=lambda inst, d=d: self.select_day(year, month, d))
            grid.add_widget(btn)

        self.layout.add_widget(grid)

        back_btn = Button(text="Back", size_hint_y=None, height=50, background_color=(0.7, 0.7, 0.7, 1))
        back_btn.bind(on_press=lambda _: setattr(self.manager, 'current', 'dashboard'))
        self.layout.add_widget(back_btn)

    def select_day(self, year, month, day):
        print(f"Selected Ethiopian date: {year}/{month}/{day}")
        # You can later open an attendance marking screen here.
    
    def get_month_name(self, month):
        names = [
            "መስከረም", "ጥቅምት", "ኅዳር", "ታህሳስ", "ጥር",
            "የካቲት", "መጋቢት", "ሚያዝያ", "ግንቦት", "ሰኔ",
            "ሐምሌ", "ነሐሴ", "ጳጉሜን"
        ]
        return names[month - 1]


# -------- MAIN APP --------
class SMISApp(App):
    def build(self):
        LabelBase.register(name="AmharicFont", fn_regular="AbyssinicaSIL-2.300/AbyssinicaSIL-2.300/AbyssinicaSIL-Regular.ttf")
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(EthiopianCalendarScreen(name="calendar"))
        return sm


if __name__ == "__main__":
    SMISApp().run()
