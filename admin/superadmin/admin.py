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
from db import models

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
from sqlalchemy.exc import IntegrityError
from kivy.lang.builder import Builder

KV_FILE = os.path.join(os.path.dirname(__file__), 'superadmin.kv')

Builder.load_file(KV_FILE)
ADMIN_FILE = os.path.join(os.path.dirname(__file__), 'admin.json')
# ======== AUTHENTICATION ========
def authenticate_admin(username, password):
    with open(ADMIN_FILE, 'r') as f:
        admin_data = json.load(f)
    admin_name = admin_data.get('admin_name')
    admin_password = admin_data.get('admin_password')
    if username is None or password is None:
        raise Exception('the user name or password can\'t be empty')
    if username == admin_name and pbkdf2_sha256.verify(password, admin_password):
        return admin_data
    return None

class SuperAdmin:
    def __init__(self, models):
        self.models = models
        

    def create_teacher(self, **kwargs):
        # Teacher: peewee Model class
        # teacher_data: dict with teacher info

        return self.models.Teacher.create_teacher(models.session, **kwargs)

    def read_teachers(self):
        return self.models.session.query(self.models.Teacher).all()

    @classmethod
    def update_teacher(cls, teacher_id, updated_data):
        query = cls.models.session.query(cls.models.Teacher).filter(cls.models.Teacher.id == teacher_id)
        query.update(**updated_data)
        cls.models.session.commit()
        return query.one_or_none()

    @classmethod
    def delete_teacher(cls, teacher_id):
        query = cls.models.session.query(cls.models.Teacher).filter(cls.models.Teacher.id == teacher_id)
        query.delete()
        cls.models.session.commit()
        return query.one_or_none()

from kivy.uix.screenmanager import Screen
from .ui_helpers import ConfirmPopup, ErrorPopup, AdminFormPopup
# from your_models import SuperAdmin, models

class SuperAdminScreen(Screen):
    """Handles Super Admin panel operations."""

    def on_kv_post(self, base_widget):
        """Load admins once KV widgets are ready."""
        self.refresh()

    def refresh(self):
        """Reloads admin list into the scrollable layout."""
        layout = self.ids.admins_layout
        layout.clear_widgets()

        admins = SuperAdmin(models).read_teachers()
        for admin in admins:
            self.add_admin_row(admin)

    def add_admin_row(self, admin):
        """Adds a row with username, edit, and delete buttons."""
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        from kivy.uix.label import Label

        box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        box.add_widget(Label(text=admin.username, color=(0, 0, 0, 1)))

        edit_btn = Button(text="Edit", size_hint_x=None, width=80)
        edit_btn.bind(on_press=lambda _, a=admin: self.edit_admin(a))
        box.add_widget(edit_btn)

        del_btn = Button(text="Delete", size_hint_x=None, width=80, background_color=(1, 0.3, 0.3, 1))
        del_btn.bind(on_press=lambda _, a=admin: self.delete_admin(a))
        box.add_widget(del_btn)

        self.ids.admins_layout.add_widget(box)

    # ---------- POPUP HANDLERS ----------

    def add_admin(self):
        """Show popup to create a new admin."""
        popup = AdminFormPopup(
            title="Add Super Admin",
            on_save=self._add_admin_action
        )
        popup.open()

    def edit_admin(self, admin):
        """Show popup to edit an existing admin."""
        popup = AdminFormPopup(
            title="Edit Super Admin",
            admin=admin,
            on_save=lambda data: self._edit_admin_action(admin, data)
        )
        popup.open()

    def delete_admin(self, admin):
        """Ask confirmation before deleting admin."""
        popup = ConfirmPopup(
            message=f"Delete {admin.username}?",
            on_confirm=lambda _: self._delete_admin_action(admin)
        )
        popup.open()

    # ---------- ACTION LOGIC ----------

    def _add_admin_action(self, data):
        try:
            SuperAdmin(models).create_teacher(
                first_name=data['first_name'],
                father_name=data['father_name'],
                grandfather_name=data['grandfather_name'],
                sex=data['sex'],
                password=data['password'],
                role='admin'
            )
            self.refresh()
        except IntegrityError:
            ErrorPopup("An admin with the same name already exists.").open()

    def _edit_admin_action(self, admin, data):
        admin.first_name = data['first_name']
        admin.father_name = data['father_name']
        admin.grandfather_name = data['grandfather_name']
        admin.sex = data['sex']
        admin.set_password(data['password'])
        admin.save()
        self.refresh()

    def _delete_admin_action(self, admin):
        admin.delete_instance()
        self.refresh()
