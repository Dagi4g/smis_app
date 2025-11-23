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

from ethiopian_date import EthiopianDateConverter
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from datetime import datetime, date
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.utils import get_color_from_hex

from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle
from kivy.lang.builder import Builder

# Builder.load_file('calender.kv')

class BorderedButton(Button):
    """take a given button and color its boarder so  
        usage :
            btn = BorderedButton(boarder_color=(int,int,int,int),**kwargs)
        
        this class has similar usage as Button class in addition to a keyword argument called boarder_color which is a list of tuple.
    
    """
    def __init__(self, border_color=(1,0,0,1), **kwargs):
        super().__init__(**kwargs)
        self.border_color = border_color
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.border_color)
            Line(rectangle=(self.x, self.y, self.width, self.height), width=2)


class EthiopianCalendarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.layout.add_widget(Label(text='calender'))
        self.add_widget(self.layout)

        # Initialize with the current Ethiopian date
        today = datetime.now()
        eth_today = EthiopianDateConverter.to_ethiopian(today.year, today.month, today.day)
        self.current_year = eth_today.year
        self.current_month = eth_today.month
        self.current_day = eth_today.day
        self.today = eth_today

        self.display_calendar()

    def display_calendar(self):
        self.layout.clear_widgets()
        
        self.layout.add_widget(Label(text='calender'))
        # --- Navigation bar ---
        nav_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        prev_btn = Button(text="< Previous", background_color=(0.8, 0.8, 0.8, 1))
        next_btn = Button(text="Next >", background_color=(0.8, 0.8, 0.8, 1))

        prev_btn.bind(on_press=lambda _: self.change_month(-1))
        next_btn.bind(on_press=lambda _: self.change_month(1))

        title_label = Label(
            text=f"{self.get_month_name(self.current_month)} {self.current_year}",
            font_size=22,
            color=(0.1, 0.3, 0.6, 1),
            font_name="AmharicFont"
        )

        nav_layout.add_widget(prev_btn)
        nav_layout.add_widget(title_label)
        nav_layout.add_widget(next_btn)
        self.layout.add_widget(nav_layout)

        # --- Days of the week ---
        days_of_week = ["እሑድ", "ሰኞ", "ማክሰኞ", "ረቡዕ", "ሐሙስ", "ዓርብ", "ቅዳሜ"]
        week_grid = GridLayout(cols=7, spacing=5, size_hint_y=None, height=40)
        for day_name in days_of_week:
            week_grid.add_widget(Label(
                text=day_name,
                color=(0.2, 0.2, 0.2, 1),
                bold=True,
                font_size=16,
                font_name="AmharicFont"
            ))
        self.layout.add_widget(week_grid)

        # --- Calendar grid ---
        grid = GridLayout(cols=7, spacing=5, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        # Determine weekday of the first day in this Ethiopian month
        greg_start = EthiopianDateConverter.to_gregorian(self.current_year, self.current_month, 1)
        weekday_start = date(greg_start.year, greg_start.month, greg_start.day).weekday()  # Monday=0
        weekday_start = (weekday_start + 1) % 7  # make Sunday=0

        # Add empty slots before first day
        for _ in range(weekday_start):
            grid.add_widget(Label(text=""))

        # Fill the calendar (Pagumen has 5 or 6 days)
        num_days = 6 if (self.current_month == 13 and self.is_leap_year(self.current_year)) else \
                    5 if self.current_month == 13 else 30

        for day in range(1, num_days + 1):
            et_day = EthiopianDateConverter.to_ethiopian(datetime.now().year, datetime.now().month, datetime.now().day)
            # Only blur future days if it's the current month/year
            if (self.current_year,self.current_month,day) > (et_day.year, et_day.month, et_day.day) :
                # Dim future days
                btn = Button(
                    text=str(day),
                    size_hint_y=None,
                    height=50,
                    background_color=get_color_from_hex("#CCCCCC"),
                    color=(0.5, 0.5, 0.5, 1),
                    disabled=True
                )
            else:
                # Normal day
                if self.is_today(day):
        
                    # Highlight current day
                    btn = BorderedButton(
                        text=str(day),
                        size_hint_y=None,
                        height=50,
                        border_color=(1,0,0,1),  # red border
                        background_color=get_color_from_hex("#CCCCCC"),
                        color=(1,1,1,1)
                    )

                else:
                    btn = Button(
                        text=str(day),
                        size_hint_y=None,
                        height=50,
                        background_color=get_color_from_hex("#E0F7FA"),
                    color=(0, 0, 0, 1)
                )
                btn.bind(on_press=lambda inst, d=day: self.select_day(self.current_year, self.current_month, d))
            grid.add_widget(btn)
        self.layout.add_widget(grid)

        # --- Back button ---
        back_btn = Button(
            text="Back",
            size_hint_y=None,
            height=50,
            background_color=(0.7, 0.7, 0.7, 1)
        )
        back_btn.bind(on_press=lambda _: setattr(self.manager, 'current', 'dashboard'))
        self.layout.add_widget(back_btn)


    def  is_today(self,day):
        return day == self.current_day and self.current_month == EthiopianDateConverter.to_ethiopian(datetime.now().year, datetime.now().month, datetime.now().day).month and self.current_year == EthiopianDateConverter.to_ethiopian(datetime.now().year, datetime.now().month, datetime.now().day).year
    def select_day(self, year, month, day):
        print(f"Selected Ethiopian date: {year}/{month}/{day}")

    def get_month_name(self, month):
        names = [
            "መስከረም", "ጥቅምት", "ኅዳር", "ታህሳስ", "ጥር",
            "የካቲት", "መጋቢት", "ሚያዝያ", "ግንቦት", "ሰኔ",
            "ሐምሌ", "ነሐሴ", "ጳጉሜን"
        ]
        return names[month - 1]

    def is_leap_year(self, eth_year):
        # Ethiopian leap year rule: leap every 4 years (no century exception)
        return eth_year % 4 == 3

    def change_month(self, direction):
        # direction = +1 (next), -1 (previous)
        self.current_month += direction
        if self.current_month > 13:
            self.current_month = 1
            self.current_year += 1
        elif self.current_month < 1:
            self.current_month = 13
            self.current_year -= 1
        self.display_calendar()

