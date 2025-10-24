# Copyright 2025 dagim Genene
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

import os
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.lang.builder import Builder

KV_FILE = os.path.join(os.path.dirname(__file__), 'superadmin.kv')

Builder.load_file(KV_FILE)
class ErrorPopup(Popup):
    """Displays a simple error message."""
    def __init__(self, message, **kwargs):
        super().__init__(title="Error", size_hint=(0.5, 0.3), **kwargs)
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=message))
        ok_btn = Button(text="OK", size_hint_y=None, height=40)
        ok_btn.bind(on_press=lambda _: self.dismiss())
        content.add_widget(ok_btn)
        self.content = content


class ConfirmPopup(Popup):
    """Displays a Yes/No confirmation popup."""
    def __init__(self, message, on_confirm, **kwargs):
        super().__init__(title="Confirm", size_hint=(0.5, 0.3), **kwargs)
        self.on_confirm = on_confirm
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=message))
        btn_layout = BoxLayout(spacing=10, size_hint_y=None, height=40)
        yes_btn = Button(text="Yes", background_color=(1, 0.3, 0.3, 1))
        no_btn = Button(text="No")
        yes_btn.bind(on_press=self.confirm)
        no_btn.bind(on_press=lambda _: self.dismiss())
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)
        self.content = content

    def confirm(self, _):
        if self.on_confirm:
            self.on_confirm(_)
        self.dismiss()


class AdminFormPopup(Popup):
    """Popup form for adding or editing admins."""
    def __init__(self, title, on_save, admin=None, **kwargs):
        super().__init__(title=title, size_hint=(0.6, 0.5), **kwargs)
        self.on_save = on_save

        self.first_name = TextInput(hint_text="First Name", multiline=False)
        self.father_name = TextInput(hint_text="Father Name", multiline=False)
        self.grandfather_name = TextInput(hint_text="Grandfather Name", multiline=False)
        self.sex = Spinner(text="Select Sex", values=("Male", "Female"))
        self.password_input = TextInput(hint_text="Password", multiline=False, password=True)

        if admin:
            self.first_name.text = admin.first_name
            self.father_name.text = admin.father_name
            self.grandfather_name.text = admin.grandfather_name
            self.sex.text = admin.sex

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        for w in [self.first_name, self.father_name, self.grandfather_name, self.sex, self.password_input]:
            layout.add_widget(w)

        btn_layout = BoxLayout(spacing=10, size_hint_y=None, height=40)
        save_btn = Button(text="Save")
        cancel_btn = Button(text="Cancel")
        save_btn.bind(on_press=self._save)
        cancel_btn.bind(on_press=lambda _: self.dismiss())
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        layout.add_widget(btn_layout)
        self.content = layout

    def _save(self, _):
        data = {
            'first_name': self.first_name.text.strip(),
            'father_name': self.father_name.text.strip(),
            'grandfather_name': self.grandfather_name.text.strip(),
            'sex': self.sex.text.strip(),
            'password': self.password_input.text.strip(),
        }
        if all(data.values()):
            self.on_save(data)
            self.dismiss()
