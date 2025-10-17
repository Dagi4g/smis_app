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
from db import models

class SchoolAdminStudentCRUD:
    def __init__(self, models):
        self.models = models

    def create_student(self, **kwargs):
        try:
            return self.models.Student.create_student(**kwargs)
        except Exception as e:
            print(f"Error creating student: {e}")
            return None

    def read_students(self):
        return list(self.models.Student.select())

    def update_student(self, student_id, **kwargs):
        try:
            query = self.models.Student.update(**kwargs).where(self.models.Student.id == student_id)
            query.execute()
            return True
        except Exception as e:
            print(f"Error updating student: {e}")
            return False

    def delete_student(self, student_id):
        try:
            query = self.models.Student.delete().where(self.models.Student.id == student_id)
            query.execute()
            return True
        except Exception as e:
            print(f"Error deleting student: {e}")
            return False
    
    def get_student(self, student_id):
        try:
            return self.models.Student.get(self.models.Student.id == student_id)
        except self.models.Student.DoesNotExist:
            return None

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
        self.add_widget(self.layout)
    
    def show_add_popup(self, instance):
        self._show_teacher_popup("Add Teacher")
        
    def _show_teacher_popup(self, title, teacher=None):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        first_name_input = TextInput(hint_text="First Name", multiline=False)
        father_name_input = TextInput(hint_text="Father Name", multiline=False)
        grandfather_name_input = TextInput(hint_text="Grandfather Name", multiline=False)
        sex_input = Spinner(text="Select Sex", values=("Male", "Female",))
        password_input = TextInput(hint_text="Password", multiline=False, password=True)

        popup_layout.add_widget(first_name_input)
        popup_layout.add_widget(father_name_input)
        popup_layout.add_widget(grandfather_name_input)
        popup_layout.add_widget(sex_input)
        popup_layout.add_widget(password_input)
        def save_teacher(popup_layout, teacher=None):
            data = {
                "first_name": first_name_input.text.strip(),
                "father_name": father_name_input.text.strip(),
                "grandfather_name": grandfather_name_input.text.strip(),
                "sex": sex_input.text.strip(),
                "password": password_input.text.strip()
            }
            models.Teacher.create_teacher(**data)
        save_btn = Button(text="Save", size_hint_y=None, height=40)
        save_btn.bind(on_press=lambda _: save_teacher(popup_layout, teacher))
        popup_layout.add_widget(save_btn)

        popup = Popup(title=title, content=popup_layout, size_hint=(0.8, 0.8))
        popup.open()
