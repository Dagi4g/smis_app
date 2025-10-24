# Copyright 2025 Dagim Genene
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

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from sqlalchemy.exc import IntegrityError
from kivy.uix.scrollview import ScrollView
from db import models
#!! this class is in the kivy ORM code it needs to  be changed  into Sqlalchemy code.
class SchoolAdminTeacherCRUD:
    def __init__(self, models):
        self.models = models

    def create_teacher(self, **kwargs):
        try:
            return self.models.session.add(self.models.Teacher(**kwargs))
        except Exception as e:
            print(f"Error creating teacher: {e}")
            return None

    def read_teachers(self):
        return list(self.models.session.query(self.models.Teacher).all())

    def update_teacher(self, teacher_id, **kwargs):
        try:
            query = self.models.session.query(self.models.Teacher).filter(self.models.Teacher.id == teacher_id)
            query.update(**kwargs)
            self.models.session.commit()
            return True
        except Exception as e:
            print(f"Error updating teacher: {e}")
            return False

    def delete_teacher(self, teacher_id):
        try:
            query = self.models.Teacher.delete().where(self.models.Teacher.id == teacher_id)
            query.execute()
            return True
        except Exception as e:
            print(f"Error deleting teacher: {e}")
            return False
    
    def get_teacher(self, teacher_id):
        try:
            return self.models.session.query(self.models.Teacher).filter(self.models.Teacher.id == teacher_id).one()
        except self.models.session.NoResultFound:
            return None

class SchoolAdminTeacherCRUDScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.admin = SchoolAdminTeacherCRUD(models)
        
        self.layout = BoxLayout(orientation='vertical', padding=49, spacing=10)
        self.layout.add_widget(Label(text="School Admin - Teacher Management", font_size=24, color=(0.1, 0.3, 0.6, 1)))
        self.add_btn = Button(text="Add Teacher", size_hint_y=None, height=40)
        self.add_btn.bind(on_press=lambda instance: self.show_add_popup(instance))
        self.layout.add_widget(self.add_btn)

        self.refresh_button = Button(text="Refresh", size_hint_y=None, height=40)
        self.refresh_button.bind(on_press=lambda _: self.refresh())
        self.layout.add_widget(self.refresh_button)
        self.teacher_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.teacher_layout.bind(minimum_height=self.teacher_layout.setter('height'))
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.teacher_layout)
        self.layout.add_widget(scroll)
        self.add_widget(self.layout)
    
    def refresh(self):
        # Clear existing widgets except the header and add button
        self.teacher_layout.clear_widgets()
        self.layout.add_widget(Label(text="School Admin - Teacher Management", font_size=24, color=(0.1, 0.3, 0.6, 1)))
        self.layout.add_widget(self.add_btn)
        
        teachers = self.admin.read_teachers()
        for teacher in teachers:
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            box.add_widget(Label(text=f"{teacher.full_name} ({teacher.username})", color=(0,0,0,1)))
            edit_btn = Button(text="Edit", size_hint_x=None, width=80)
            edit_btn.bind(on_press=lambda _, t=teacher: self.show_edit_popup(t))
            box.add_widget(edit_btn)
            del_btn = Button(text="Delete", size_hint_x=None, width=80, background_color=(1,0.3,0.3,1))
            del_btn.bind(on_press=lambda _, t=teacher: self.delete_teacher(t))
            box.add_widget(del_btn)
            self.layout.add_widget(box)
        
    
    def show_add_popup(self, instance):
        self._show_teacher_popup("Add Teacher")
    
    def error_popup(self, message):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=message))
        ok_btn = Button(text="OK", size_hint_y=None, height=40)
        content.add_widget(ok_btn)
        popup = Popup(title="Error", content=content, size_hint=(0.5, 0.3))
        ok_btn.bind(on_press=lambda _: popup.dismiss())
        popup.open()
        
    def _show_teacher_popup(self, title, teacher=None):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        first_name_input = TextInput(hint_text="First Name", multiline=False)
        father_name_input = TextInput(hint_text="Father Name", multiline=False)
        grandfather_name_input = TextInput(hint_text="Grandfather Name", multiline=False)
        sex_input = Spinner(text="Select Sex", values=("Male", "Female",))
        password_input = TextInput(hint_text="Password", multiline=False, password=True)
        
        if teacher:
            first_name_input.text = teacher.first_name
            father_name_input.text = teacher.father_name
            grandfather_input.text  = teacher.grandfather_name
            sex_input.text  = teacher.sex
            role.text = teacher.role
        
        content.add_widget(first_name_input)
        content.add_widget(father_name_input)
        content.add_widget(grandfather_name_input)
        content.add_widget(sex_input)
        content.add_widget(password_input)
        btn_layout = BoxLayout(orientation='horizontal',spacing=10, size_hint_y=None,height=40)
        save_btn = Button(text="Save")
        cancel_btn = Button(text="Cancel")
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        popup = Popup(title=title, content=content, size_hint=(0.6, 0.5))

        def save_teacher(_):
            data = {
                "first_name": first_name_input.text.strip(),
                "father_name": father_name_input.text.strip(),
                "grandfather_name": grandfather_name_input.text.strip(),
                "sex": sex_input.text.strip(),
                "password": password_input.text.strip(),
                "role" : "teacher"
            }
            try :
                self.admin.create_teacher(**data)
            except IntegrityError:
                self.error_popup("A teacher with the same name already exists.")
                models.session.rollback()
                return
            popup.dismiss()
            self.refresh()
        save_btn = Button(text="Save", size_hint_y=None, height=40)
        save_btn.bind(on_press=save_teacher)
        cancel_btn.bind(on_press=lambda _: popup.dismiss())

        popup.open()
