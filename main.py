from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.text import LabelBase
from kivy.uix.popup import Popup

from eth_custom_calendar.ethiopia_custom_calender import EthiopianCalendarScreen
Window.clearcolor = (0.95, 0.95, 0.95, 1)
from admin.superadmin.admin import SuperAdminScreen ,  authenticate_admin 
from db import models
from admin.school_admin import SchoolAdminTeacherCRUDScreen 
class ErrorPopup(Popup):
	
    def on_ok(self):
        self.dismiss()
        
        
    def show_message(self,message):
        self.error_label.text = message
        self.open()

            

# -------- LOGIN SCREEN --------
class LoginScreen(Screen):
    def login(self):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        admin_result = authenticate_admin(username, password)
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
        sm.add_widget(EthiopianCalendarScreen(name="calendar"))
        sm.add_widget(SuperAdminScreen(name="super_admin"))
        sm.add_widget(SchoolAdminTeacherCRUDScreen(name="school_admin_teacher_crud"))
        return sm


if __name__ == "__main__":
    SmisApp().run()
