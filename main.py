from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.anchorlayout import AnchorLayout
import peewee
from models import Subject

Window.clearcolor = (0.95, 0.95, 0.95, 1)  # light grey background


# Database Service
def add_subject_to_db(subject_name):
    subject = Subject(name=subject_name)
    subject.save()


# Popup functions
def show_error(message):
    popup = Popup(
        title="Error",
        content=Label(text=message, color=(1, 0, 0, 1)),
        size_hint=(0.6, 0.4)
    )
    popup.open()


def show_success(message):
    popup = Popup(
        title="Success",
        content=Label(text=message, color=(0, 0.6, 0, 1)),
        size_hint=(0.6, 0.4)
    )
    popup.open()


# Create Subject Screen
class CreateSubjectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # AnchorLayout centers the form vertically and horizontally
        anchor = AnchorLayout(anchor_x='center', anchor_y='center')

        # Main form layout
        main_layout = BoxLayout(
            orientation='vertical',
            padding=30,
            spacing=20,
            size_hint=(0.6, None),
            height=250
        )

        # Title
        title = Label(
            text="Create Subject",
            font_size=26,
            color=(0.1, 0.3, 0.6, 1),
            size_hint_y=None,
            height=50
        )
        main_layout.add_widget(title)

        # Form row
        form_row = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=60)
        lbl = Label(text="Subject Name:", size_hint_x=0.3, halign='right', valign='middle')
        lbl.bind(size=lambda *x: setattr(lbl, 'text_size', lbl.size))

        self.subject_input = TextInput(
            multiline=False,
            size_hint_x=0.7,
            font_size=18,
            padding=[10, 10],
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.3, 0.6, 1)
        )

        form_row.add_widget(lbl)
        form_row.add_widget(self.subject_input)
        main_layout.add_widget(form_row)

        # Submit button
        submit_btn = Button(
            text="Add Subject",
            size_hint_y=None,
            height=50,
            background_color=(0.4, 0.7, 1, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        submit_btn.bind(on_press=self.submit)
        main_layout.add_widget(submit_btn)

        anchor.add_widget(main_layout)
        self.add_widget(anchor)

    def submit(self, instance):
        subject_name = self.subject_input.text.strip().title()
        if subject_name:
            try:
                add_subject_to_db(subject_name)
            except peewee.IntegrityError:
                show_error(f"Subject '{subject_name}' already exists")
            else:
                show_success(f"Subject '{subject_name}' added successfully!")
                self.subject_input.text = ""  # Clear input
        else:
            show_error("Subject name cannot be empty")


# App
class SMISApp(App):
    def build(self):
        return CreateSubjectScreen(name="create_subject")


if __name__ == "__main__":
    SMISApp().run()
