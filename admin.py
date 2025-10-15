# Copyright 2025 Daim Genene
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os 
from passlib.hash import pbkdf2_sha256
import peewee
import models

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window


ADMIN_FILE = os.path.join(os.path.dirname(__file__), 'admin.json')
# ======== AUTHENTICATION ========
def authenticate_admin(username, password):
    with open(ADMIN_FILE, 'r') as f:
        admin_data = json.load(f)
    admin_name = admin_data.get('admin_name')
    admin_password = admin_data.get('admin_password')
    if username == admin_name and pbkdf2_sha256.verify(password, admin_password):
        return admin_data
    return None

class SuperAdmin:
    def __init__(self, models):
        self.models = models
        
    @classmethod
    def create_teacher(cls, models, **kwargs):
        # Teacher: peewee Model class
        # teacher_data: dict with teacher info
        
        try :
            return models.Teacher.create_teacher(**kwargs)
        except Exception as e:
            print(f"Error creating teacher: {e}")
            return None

    def read_teachers(self):
        return list(self.models.Teacher.select())

    @classmethod
    def update_teacher(cls, teacher_id, updated_data):
        query = cls.models.Teacher.update(**updated_data).where(cls.models.Teacher.id == teacher_id)
        return query.execute()

    @classmethod
    def delete_teacher(cls, teacher_id):
        query = cls.models.Teacher.delete().where(cls.models.Teacher.id == teacher_id)
        return query.execute()

class SuperAdminScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        self.layout.add_widget(Label(text="Super Admin Panel", font_size=30, color=(0.1, 0.3, 0.6, 1)))
        self.refresh_btn = Button(text="Refresh", size_hint_y=None, height=40)
        self.refresh_btn.bind(on_press=lambda _: self.refresh())
        self.layout.add_widget(self.refresh_btn)
        self.add_btn = Button(text="add school admin", size_hint_y=None, height=40)
        self.add_btn.bind(on_press=self.show_add_popup)
        self.layout.add_widget(self.add_btn)
        self.admins_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.admins_layout.bind(minimum_height=self.admins_layout.setter('height'))
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.admins_layout)
        self.layout.add_widget(scroll)
        self.add_widget(self.layout)
        self.refresh()

    def refresh(self):
        self.admins_layout.clear_widgets()
        admins = SuperAdmin(models).read_teachers()
        for admin in admins:
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            box.add_widget(Label(text=f"{admin.username}", color=(0,0,0,1)))
            edit_btn = Button(text="Edit", size_hint_x=None, width=80)
            edit_btn.bind(on_press=lambda _, a=admin: self.show_edit_popup(a))
            del_btn = Button(text="Delete", size_hint_x=None, width=80, background_color=(1,0.3,0.3,1))
            del_btn.bind(on_press=lambda _, a=admin: self.delete_admin(a))
            box.add_widget(edit_btn)
            box.add_widget(del_btn)
            self.admins_layout.add_widget(box)

    def show_add_popup(self, instance):
        self._show_admin_popup("Add Super Admin")

    def show_edit_popup(self, admin):
        self._show_admin_popup("Edit Super Admin", admin)

    def _show_admin_popup(self, title, admin=None):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        first_name = TextInput(hint_text="First Name", multiline=False)
        father_name = TextInput(hint_text="Father Name", multiline=False)
        grandfather_name = TextInput(hint_text="Grandfather Name", multiline=False)
        sex = Spinner(text="Select Sex", values=("Male", "Female", "Other"))
        password_input = TextInput(hint_text="Password", multiline=False, password=True)
        
        if admin:
            first_name.text = admin.first_name
            father_name.text = admin.father_name
            grandfather_name.text = admin.grandfather_name
            sex.text = admin.sex
        content.add_widget(first_name)
        content.add_widget(father_name)
        content.add_widget(grandfather_name)
        content.add_widget(sex)
        content.add_widget(password_input)
        btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        save_btn = Button(text="Save")
        cancel_btn = Button(text="Cancel")
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        popup = Popup(title=title, content=content, size_hint=(0.6, 0.5))
        def save_action(_):
            first_name_val = first_name.text.strip()
            father_name_val = father_name.text.strip()
            grandfather_name_val = grandfather_name.text.strip()
            sex_val = sex.text.strip()
            password = password_input.text.strip()
            if not first_name_val or not father_name_val or not grandfather_name_val or not sex_val or not password:
                return
            if admin:
                admin.first_name = first_name_val
                admin.father_name = father_name_val
                admin.grandfather_name = grandfather_name_val
                admin.sex = sex_val
                admin.set_password(password)
                admin.save()
            else:
                SuperAdmin.create_teacher(models, first_name=first_name_val, father_name=father_name_val, grandfather_name=grandfather_name_val, sex=sex_val, password=password, role='admin')
            popup.dismiss()
            self.refresh()
        save_btn.bind(on_press=save_action)
        cancel_btn.bind(on_press=lambda _: popup.dismiss())
        popup.open()

    def delete_admin(self, admin):
        def confirm_delete(_):
            admin.delete_instance()
            popup.dismiss()
            self.refresh()
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=f"Delete {admin.username}?"))
        btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        yes_btn = Button(text="Yes", background_color=(1,0.3,0.3,1))
        no_btn = Button(text="No")
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)
        popup = Popup(title="Confirm Delete", content=content, size_hint=(0.5, 0.3))
        yes_btn.bind(on_press=confirm_delete)
        no_btn.bind(on_press=lambda _: popup.dismiss())
        popup.open()
    
    def dashboard(self, instance):
        
        self.manager.current = "dashboard"


