import json
import os
from datetime import date, timedelta
from functools import partial

from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle
from kivy.metrics import dp

# ================= GLOBAL VARIABLES (SAFETY FIX) =================
DATA_FILE = None
data = {}  # Empty dictionary initially, will be loaded inside App.build()

DATA_DEFAULT = {
    "tasks": [], "habits": [], "namaz_log": {}, "quran_log": [], 
    "entertainment_log": [], "points": 0, "level": 1, "badges": [], 
    "exams": [], "projects": [], "notes": {}, "dark_mode": False
}

# ================= COLORS =================
LIGHT = {"bg": (0.98, 0.95, 0.91, 1), "card": (1, 1, 1, 1), "text": (0.24, 0.16, 0.10, 1), "muted": (0.61, 0.56, 0.51, 1)}
DARK = {"bg": (0.125, 0.094, 0.070, 1), "card": (0.18, 0.14, 0.11, 1), "text": (0.94, 0.90, 0.86, 1), "muted": (0.70, 0.64, 0.57, 1)}
ORANGE = (0.91, 0.35, 0.05, 1); GOLD = (0.97, 0.66, 0.23, 1); TEAL = (0.18, 0.55, 0.47, 1)
PURPLE = (0.47, 0.31, 0.66, 1); PINK = (0.78, 0.27, 0.36, 1); BLUE = (0.18, 0.43, 0.63, 1); WHITE = (1,1,1,1); GRAY = (0.85,0.82,0.78,1)

def theme():
    return DARK if data.get("dark_mode") else LIGHT

NAMAZ_TIMES = {
    1: {"Fajr": "5:44", "Zuhr": "12:17", "Asr": "3:44", "Maghrib": "5:25", "Isha": "6:50"},
    2: {"Fajr": "5:28", "Zuhr": "12:22", "Asr": "4:13", "Maghrib": "5:54", "Isha": "7:15"},
    3: {"Fajr": "4:55", "Zuhr": "12:17", "Asr": "4:33", "Maghrib": "6:18", "Isha": "7:38"},
    4: {"Fajr": "4:09", "Zuhr": "12:08", "Asr": "4:47", "Maghrib": "6:41", "Isha": "8:06"},
    5: {"Fajr": "3:30", "Zuhr": "12:04", "Asr": "4:58", "Maghrib": "7:04", "Isha": "8:37"},
    6: {"Fajr": "3:12", "Zuhr": "12:08", "Asr": "5:08", "Maghrib": "7:22", "Isha": "9:03"},
    7: {"Fajr": "3:27", "Zuhr": "12:14", "Asr": "5:11", "Maghrib": "7:22", "Isha": "8:59"},
    8: {"Fajr": "3:58", "Zuhr": "12:12", "Asr": "4:58", "Maghrib": "6:58", "Isha": "8:26"},
    9: {"Fajr": "4:26", "Zuhr": "12:03", "Asr": "4:29", "Maghrib": "6:18", "Isha": "7:39"},
    10: {"Fajr": "4:49", "Zuhr": "11:54", "Asr": "3:54", "Maghrib": "5:38", "Isha": "6:57"},
    11: {"Fajr": "5:12", "Zuhr": "11:52", "Asr": "3:27", "Maghrib": "5:08", "Isha": "6:31"},
    12: {"Fajr": "5:35", "Zuhr": "12:03", "Asr": "3:23", "Maghrib": "5:03", "Isha": "6:30"},
}
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
HABIT_COLORS = [ORANGE, TEAL, PURPLE, PINK, GOLD, BLUE]

# ================= SAFE UI WIDGETS =================
class Card(BoxLayout):
    def __init__(self, bg=None, radius=dp(20), **kwargs):
        super().__init__(**kwargs)
        self.padding, self.spacing = dp(15), dp(10)
        self._bg_color = bg if bg else theme()["card"]
        with self.canvas.before:
            Color(*self._bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
        self.bind(pos=self._update, size=self._update)
    def _update(self, *args): self._rect.pos, self._rect.size = self.pos, self.size

class FAB(Button): # FLOATING ACTION BUTTON
    def __init__(self, target, **kwargs):
        super().__init__(**kwargs)
        self.size_hint, self.size = (None, None), (dp(56), dp(56))
        self.pos_hint = {'right': 0.9, 'bottom': 0.05}
        self.background_normal, self.background_color = '', (0,0,0,0)
        self.text, self.font_size, self.color = '+', dp(30), WHITE
        self.bind(on_release=partial(go_screen, target))
        with self.canvas.before:
            Color(*ORANGE)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(28)])
        self.bind(pos=self._update, size=self._update)
    def _update(self, *args): self.rect.pos, self.rect.size = self.pos, self.size

def make_button(text, h=dp(52), bg=ORANGE, fg=WHITE, fs=dp(15)):
    btn = Button(text=text, size_hint_y=None, height=h, background_normal="", background_color=bg, color=fg, font_size=fs, bold=True)
    return btn

def make_label(text, h=dp(30), fs=dp(14), color=None, bold=False):
    t = theme()
    return Label(text=text, size_hint_y=None, height=h, font_size=fs, color=color if color else t["text"], bold=bold)

def header(title, back_to=None, c1=ORANGE, c2=GOLD):
    box = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(110), padding=[dp(20), dp(15), dp(20), dp(10)])
    with box.canvas.before:
        Color(*c1); box._rect = Rectangle(pos=box.pos, size=box.size)
    box.bind(pos=lambda *a: setattr(box._rect, "pos", box.pos), size=lambda *a: setattr(box._rect, "size", box.size))
    if back_to:
        b = Button(text="< Back", size_hint_x=None, width=dp(100), background_normal="", background_color=(0,0,0,0), color=WHITE, font_size=dp(15), bold=True)
        b.bind(on_release=partial(go_screen, back_to))
        box.add_widget(b)
    box.add_widget(Label(text=title, font_size=dp(24), bold=True, color=WHITE))
    return box

def bottom_nav(active):
    nav = BoxLayout(size_hint_y=None, height=dp(70), padding=dp(5), spacing=dp(5))
    t = theme()
    with nav.canvas.before:
        Color(*t["bg"]); nav._rect = Rectangle(pos=nav.pos, size=nav.size)
    nav.bind(pos=lambda *a: setattr(nav._rect, "pos", nav.pos), size=lambda *a: setattr(nav._rect, "size", nav.size))
    items = [("🏠 Home", "home"), ("🔥 Habits", "habits"), ("✅ Tasks", "tasks"), ("📊 Reports", "reports"), ("⋯ More", "more")]
    for label, name in items:
        c = ORANGE if name == active else t["muted"]
        btn = Button(text=label, background_normal="", background_color=(0,0,0,0), color=c, font_size=dp(12), bold=(name==active))
        btn.bind(on_release=partial(go_screen, name))
        nav.add_widget(btn)
    return nav

sm = None
def go_screen(name): sm.current = name

# ================= HOME SCREEN =================
class HomeScreen(Screen):
    timer_running = False
    time_left = 1500

    def on_pre_enter(self):
        self.clear_widgets()
        root = RelativeLayout()
        t = theme()
        with root.canvas.before:
            Color(*t["bg"]); root._rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(root._rect, "pos", root.pos), size=lambda *a: setattr(root._rect, "size", root.size))

        box = BoxLayout(orientation="vertical")
        box.add_widget(header("☀️ Assalam-o-Alaikum", c1=ORANGE, c2=GOLD))
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))

        # Progress Stats Card
        card = Card(orientation="vertical", height=dp(100))
        card.add_widget(make_label(f"🔥 Streak: {data.get('points',0)//20} days", fs=dp(16), color=ORANGE))
        card.add_widget(make_label(f"⭐ Points: {data['points']}", fs=dp(16), color=PURPLE))
        card.add_widget(make_label(f"🏆 Level: {data['level']}", fs=dp(16), color=GOLD))
        content.add_widget(card)

        # Pomodoro Timer Card
        content.add_widget(section_label("⏱️ Focus Timer"))
        pcard = Card(orientation="horizontal", height=dp(80))
        self.timer_lbl = Label(text="25:00", font_size=dp(32), color=PINK, bold=True, size_hint_x=None, width=dp(120))
        pcard.add_widget(self.timer_lbl)
        self.pom_btn = make_button("Start Focus", h=dp(50), bg=PINK)
        self.pom_btn.bind(on_release=self.toggle_timer)
        pcard.add_widget(self.pom_btn)
        content.add_widget(pcard)

        # Today's Tasks
        content.add_widget(section_label("Today's Focus"))
        today = str(date.today())
        for i, tk in enumerate(data["tasks"]):
            if i >= 5: break
            done = today in tk["done_dates"]
            row = Card(orientation="horizontal", height=dp(70), padding=dp(12))
            check = Button(text="✓" if done else "", size_hint_x=None, width=dp(40), height=dp(40), 
                           background_normal="", background_color=(0.15, 0.6, 0.3, 1) if done else GRAY, 
                           color=WHITE, font_size=dp(20), bold=True)
            check.bind(on_release=partial(self.toggle_task, i))
            row.add_widget(check)
            col = BoxLayout(orientation="vertical")
            col.add_widget(make_label(tk["name"], fs=dp(16), bold=True, h=dp(25)))
            col.add_widget(make_label(tk["time"], fs=dp(12), color=t["muted"], h=dp(20)))
            row.add_widget(col)
            content.add_widget(row)

        scroll.add_widget(content)
        box.add_widget(scroll)
        box.add_widget(bottom_nav("home"))
        root.add_widget(box)
        root.add_widget(FAB("add_task"))
        self.add_widget(root)

    def toggle_timer(self, inst):
        if self.timer_running:
            self.timer_running = False
            self.pom_btn.text = "Start Focus"
            self.pom_btn.background_color = PINK
            Clock.unschedule(self.update_timer)
            self.time_left = 1500
            self.timer_lbl.text = "25:00"
        else:
            self.timer_running = True
            self.pom_btn.text = "Stop"
            self.pom_btn.background_color = (0.8, 0.1, 0.1, 1)
            Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.time_left -= 1
        mins, secs = divmod(self.time_left, 60)
        self.timer_lbl.text = f"{mins:02d}:{secs:02d}"
        if self.time_left <= 0:
            Clock.unschedule(self.update_timer)
            self.timer_running = False
            self.pom_btn.text = "Start Focus"
            self.pom_btn.background_color = PINK
            show_popup("⏱️ Time's Up!", "Great focus! Take a 5 min break.")
            self.time_left = 1500
            self.timer_lbl.text = "25:00"

    def toggle_task(self, index):
        today = str(date.today())
        tk = data["tasks"][index]
        if today not in tk["done_dates"]:
            tk["done_dates"].append(today)
            add_points(10)
        else:
            tk["done_dates"].remove(today)
        save_data()
        self.on_pre_enter()

# ================= Helper Functions & Popups =================
def get_today_namaz_times(): return NAMAZ_TIMES[date.today().month]

def show_popup(title, message):
    t = theme()
    popup = Popup(title=title, content=Label(text=message, color=t["text"], font_size=dp(16), halign="center"),
                  size_hint=(0.8, 0.4), title_color=t["text"], separator_color=ORANGE, title_size=dp(18))
    popup.open()

def add_points(amount):
    data["points"] += amount
    new_level = (data["points"] // 100) + 1
    if new_level > data["level"]:
        data["level"] = new_level
        data["badges"].append(f"🏆 Level {data['level']} Reached")
        show_popup("Level Up!", f"You are now Level {data['level']}!")
    save_data()

def section_label(text, color=ORANGE):
    return make_label(text.upper(), height=dp(32), font_size=dp(14), color=color, bold=True)

def save_data():
    if DATA_FILE:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

# ================= TASKS SCREEN =================
class TasksScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets(); t = theme()
        root = RelativeLayout()
        with root.canvas.before:
            Color(*t["bg"]); root._rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(root._rect, "pos", root.pos), size=lambda *a: setattr(root._rect, "size", root.size))
        box = BoxLayout(orientation="vertical")
        box.add_widget(header("✅ My Tasks", c1=TEAL, c2=(0.30, 0.69, 0.59, 1)))
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))

        add_btn = make_button("➕ ADD NEW TASK", h=dp(55), bg=TEAL)
        add_btn.bind(on_release=partial(go_screen, "add_task"))
        content.add_widget(add_btn)

        today = str(date.today())
        for i, tk in enumerate(data["tasks"]):
            done = today in tk["done_dates"]
            row = Card(orientation="horizontal", height=dp(70), padding=dp(12))
            check = Button(text="✓" if done else "", size_hint_x=None, width=dp(40), height=dp(40), 
                           background_normal="", background_color=(0.15,0.6,0.3,1) if done else GRAY, 
                           color=WHITE, font_size=dp(18), bold=True)
            check.bind(on_release=partial(self.toggle_task, i))
            row.add_widget(check)
            col = BoxLayout(orientation="vertical")
            col.add_widget(make_label(tk["name"], fs=dp(16), bold=True, h=dp(25)))
            col.add_widget(make_label(tk["time"], fs=dp(12), color=t["muted"], h=dp(20)))
            row.add_widget(col)
            content.add_widget(row)

        scroll.add_widget(content)
        box.add_widget(scroll)
        box.add_widget(bottom_nav("tasks"))
        root.add_widget(box)
        root.add_widget(FAB("add_task"))
        self.add_widget(root)

    def toggle_task(self, idx):
        today = str(date.today())
        tk = data["tasks"][idx]
        if today not in tk["done_dates"]:
            tk["done_dates"].append(today)
            add_points(10)
        else:
            tk["done_dates"].remove(today)
        save_data()
        self.on_pre_enter()

class AddTaskScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("➕ Add Task", back_to="tasks", c1=TEAL))
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(make_label("Task Name:", fs=dp(16), color=TEAL, bold=True))
        self.name_input = TextInput(size_hint_y=None, height=dp(45), font_size=dp(16))
        content.add_widget(self.name_input)

        content.add_widget(make_label("Time:", fs=dp(16), color=PINK, bold=True))
        self.time_input = TextInput(size_hint_y=None, height=dp(45), font_size=dp(16))
        content.add_widget(self.time_input)

        content.add_widget(section_label("Priority", color=TEAL))
        self.priority = "High"
        pr_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        for pr, c in [("High", PINK), ("Medium", GOLD), ("Low", (0.6,0.6,0.6,1))]:
            b = make_button(pr, h=dp(50), bg=c if pr == "High" else GRAY, fs=dp(13))
            b.bind(on_release=partial(self.set_priority, pr))
            pr_row.add_widget(b)
        content.add_widget(pr_row)

        content.add_widget(make_label("Note (optional):", fs=dp(16), color=PURPLE, bold=True))
        self.note_input = TextInput(size_hint_y=None, height=dp(45), font_size=dp(16))
        content.add_widget(self.note_input)

        save_btn = make_button("➕ ADD TASK", bg=ORANGE, h=dp(55))
        save_btn.bind(on_release=self.save_task)
        content.add_widget(save_btn)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def set_priority(self, pr):
        self.priority = pr

    def save_task(self, inst):
        n, t = self.name_input.text, self.time_input.text
        if not n or not t:
            show_popup("Error", "Enter name & time.")
            return
        data["tasks"].append({"name": n, "time": t, "priority": self.priority, "recurring": False, "note": self.note_input.text, "done_dates": []})
        save_data()
        show_popup("Saved", f"Task '{n}' added!")
        go_screen("tasks")

# ================= HABITS SCREEN =================
class HabitsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets(); t = theme()
        root = RelativeLayout()
        with root.canvas.before:
            Color(*t["bg"]); root._rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(root._rect, "pos", root.pos), size=lambda *a: setattr(root._rect, "size", root.size))
        box = BoxLayout(orientation="vertical")
        box.add_widget(header("🔥 My Habits", c1=PINK, c2=(0.87, 0.43, 0.27, 1)))
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))

        add_btn = make_button("➕ ADD NEW HABIT", h=dp(55), bg=PINK)
        add_btn.bind(on_release=partial(go_screen, "add_habit"))
        content.add_widget(add_btn)

        today = str(date.today())
        week = [str(date.today() - timedelta(days=i)) for i in range(6, -1, -1)]
        for idx, h in enumerate(data["habits"]):
            color = tuple(h["color"])
            card = Card(orientation="vertical", height=dp(140))
            top = BoxLayout(size_hint_y=None, height=dp(30))
            top.add_widget(make_label(h["name"], fs=dp(16), bold=True, h=dp(30)))
            streak = sum(1 for d in week if d in h["log"])
            top.add_widget(make_label(f"{streak}/7", fs=dp(15), color=color, bold=True, h=dp(30), halign="right"))
            card.add_widget(top)
            heat = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(6))
            for d in week:
                done = d in h["log"]
                b = Button(text="", size_hint_y=None, height=dp(44), background_normal="", background_color=color if done else GRAY, font_size=1)
                b.bind(on_release=partial(self.toggle_habit, idx, d))
                heat.add_widget(b)
            card.add_widget(heat)
            content.add_widget(card)

        scroll.add_widget(content)
        box.add_widget(scroll)
        box.add_widget(bottom_nav("habits"))
        root.add_widget(box)
        root.add_widget(FAB("add_habit"))
        self.add_widget(root)

    def toggle_habit(self, idx, day):
        h = data["habits"][idx]
        if day in h["log"]: h["log"].remove(day)
        else:
            h["log"].append(day)
            if day == str(date.today()): add_points(5)
        save_data()
        self.on_pre_enter()

class AddHabitScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("➕ Add Habit", back_to="habits", c1=PINK))
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(make_label("Habit Name:", fs=dp(16), color=PINK, bold=True))
        self.name_input = TextInput(size_hint_y=None, height=dp(45), font_size=dp(16))
        content.add_widget(self.name_input)

        content.add_widget(section_label("Repeat On", color=PINK))
        self.sel_days = [True]*5 + [False]*2
        days_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(6))
        self.day_btns = []
        for i, dn in enumerate(DAY_NAMES):
            b = make_button(dn[:2], h=dp(50), bg=PINK if self.sel_days[i] else GRAY, fs=dp(13))
            b.bind(on_release=partial(self.toggle_day, i))
            days_row.add_widget(b); self.day_btns.append(b)
        content.add_widget(days_row)

        content.add_widget(section_label("Color", color=PINK))
        self.sel_color = 3
        colors_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        for i, c in enumerate(HABIT_COLORS):
            b = make_button("", h=dp(50), bg=c)
            b.bind(on_release=partial(self.select_color, i))
            colors_row.add_widget(b)
        content.add_widget(colors_row)

        create_btn = make_button("➕ CREATE HABIT", bg=PINK, h=dp(55))
        create_btn.bind(on_release=self.save_habit)
        content.add_widget(create_btn)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def toggle_day(self, idx):
        self.sel_days[idx] = not self.sel_days[idx]
        self.day_btns[idx].background_color = PINK if self.sel_days[idx] else GRAY

    def select_color(self, idx):
        self.sel_color = idx

    def save_habit(self, inst):
        n = self.name_input.text
        if not n: show_popup("Error", "Enter a habit name."); return
        data["habits"].append({"name": n, "color": list(HABIT_COLORS[self.sel_color]), "days": list(self.sel_days), "log": []})
        save_data()
        show_popup("Saved", f"Habit '{n}' created!")
        go_screen("habits")

# ================= NAMAZ SCREEN =================
class NamazScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("🕌 Namaz & Quran", back_to="more", c1=ORANGE, c2=GOLD))
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))

        today = str(date.today())
        times = get_today_namaz_times()
        if today not in data["namaz_log"]: data["namaz_log"][today] = []
        for p in times:
            done = p in data["namaz_log"][today]
            row = Card(orientation="horizontal", height=dp(70), padding=dp(12), spacing=dp(12))
            check = Button(text="✓" if done else "", size_hint_x=None, width=dp(40), height=dp(40), background_normal="", background_color=(0.15,0.6,0.3,1) if done else GRAY, color=WHITE, font_size=dp(18), bold=True)
            check.bind(on_release=partial(self.toggle_namaz, p))
            row.add_widget(check)
            col = BoxLayout(orientation="vertical")
            col.add_widget(make_label(p, fs=dp(15), bold=True, h=dp(25)))
            col.add_widget(make_label(times[p], fs=dp(12), color=theme()["muted"], h=dp(20)))
            row.add_widget(col)
            content.add_widget(row)

        q_done = today in data["quran_log"]
        qrow = Card(orientation="horizontal", height=dp(70), padding=dp(12), spacing=dp(12))
        qcheck = Button(text="✓" if q_done else "", size_hint_x=None, width=dp(40), height=dp(40), background_normal="", background_color=(0.15,0.6,0.3,1) if q_done else GRAY, color=WHITE, font_size=dp(18), bold=True)
        qcheck.bind(on_release=self.toggle_quran)
        qrow.add_widget(qcheck)
        qrow.add_widget(make_label("📖 Quran Recitation", fs=dp(15), bold=True))
        content.add_widget(qrow)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def toggle_namaz(self, p):
        today = str(date.today())
        if p not in data["namaz_log"][today]:
            data["namaz_log"][today].append(p)
            add_points(15)
        else:
            data["namaz_log"][today].remove(p)
        save_data()
        self.on_pre_enter()

    def toggle_quran(self, inst):
        today = str(date.today())
        if today not in data["quran_log"]:
            data["quran_log"].append(today)
            add_points(15)
        else:
            data["quran_log"].remove(today)
        save_data()
        self.on_pre_enter()

# ================= MORE & SUB SCREENS =================
class ReportsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets(); t = theme()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("📊 Reports", c1=BLUE, c2=(0.27,0.51,0.70,1)))
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))
        today = date.today()
        dates = [str(today - timedelta(days=i)) for i in range(7)]
        def in_range(d): return d in dates
        total_tasks = sum(1 for tk in data["tasks"] for d in tk["done_dates"] if in_range(d))
        namaz_count = sum(len(v) for d, v in data["namaz_log"].items() if in_range(d))
        quran_count = sum(1 for d in data["quran_log"] if in_range(d))
        
        content.add_widget(Label(text=f"📅 This Week", font_size=dp(18), bold=True, color=t["text"]))
        content.add_widget(Label(text=f"✅ Tasks: {total_tasks}", font_size=dp(16), color=TEAL))
        content.add_widget(Label(text=f"🕌 Namaz: {namaz_count}/35", font_size=dp(16), color=ORANGE))
        content.add_widget(Label(text=f"📖 Quran: {quran_count}/7", font_size=dp(16), color=PURPLE))
        
        scroll.add_widget(content)
        root.add_widget(scroll)
        root.add_widget(bottom_nav("reports"))
        self.add_widget(root)

class MoreScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets(); root = BoxLayout(orientation="vertical")
        root.add_widget(header("⋯ More Options", c1=PURPLE, c2=(0.59,0.42,0.77,1)))
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(12))
        content.bind(minimum_height=content.setter("height"))
        for label, s, c in [("📅 Exam Days", "exams", PINK), ("🎯 Projects", "projects", BLUE), ("📝 Daily Note", "checkin", GOLD)]:
            btn = make_button(label, h=dp(65), bg=c, fs=dp(17))
            btn.bind(on_release=partial(go_screen, s))
            content.add_widget(btn)
        dm = "Light Mode" if data.get("dark_mode") else "Dark Mode"
        btn = make_button(f"🌓 {dm}", h=dp(65), bg=(0.4,0.4,0.4,1), fs=dp(17))
        btn.bind(on_release=self.toggle_dark)
        content.add_widget(btn)
        scroll.add_widget(content)
        root.add_widget(scroll)
        root.add_widget(bottom_nav("more"))
        self.add_widget(root)
    def toggle_dark(self, inst):
        data["dark_mode"] = not data.get("dark_mode", False)
        save_data()
        Window.clearcolor = theme()["bg"]
        self.on_pre_enter()

class ExamsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("📅 Exam Days", back_to="more", c1=PINK))
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))
        content.add_widget(make_label("Subject:", h=dp(25), color=PINK, bold=True))
        self.sub = TextInput(size_hint_y=None, height=dp(45))
        content.add_widget(self.sub)
        content.add_widget(make_label("Date (YYYY-MM-DD):", h=dp(25), color=PINK, bold=True))
        self.dt = TextInput(size_hint_y=None, height=dp(45))
        content.add_widget(self.dt)
        add_btn = make_button("➕ ADD EXAM", h=dp(50), bg=PINK)
        add_btn.bind(on_release=self.add_exam)
        content.add_widget(add_btn)
        scroll.add_widget(content); root.add_widget(scroll); self.add_widget(root)
    def add_exam(self, inst):
        if not self.sub.text or not self.dt.text: show_popup("Error", "Enter subject and date."); return
        data["exams"].append({"subject": self.sub.text, "date": self.dt.text})
        save_data()
        self.on_pre_enter()

class ProjectsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("🎯 Projects", back_to="more", c1=BLUE))
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))
        content.add_widget(make_label("Title:", h=dp(25), color=BLUE, bold=True))
        self.tit = TextInput(size_hint_y=None, height=dp(45))
        content.add_widget(self.tit)
        content.add_widget(make_label("End Date (YYYY-MM-DD):", h=dp(25), color=BLUE, bold=True))
        self.edt = TextInput(size_hint_y=None, height=dp(45))
        content.add_widget(self.edt)
        add_btn = make_button("➕ ADD PROJECT", h=dp(50), bg=BLUE)
        add_btn.bind(on_release=self.add_project)
        content.add_widget(add_btn)
        scroll.add_widget(content); root.add_widget(scroll); self.add_widget(root)
    def add_project(self, inst):
        if not self.tit.text or not self.edt.text: show_popup("Error", "Enter title and end date."); return
        data["projects"].append({"title": self.tit.text, "start": str(date.today()), "end": self.edt.text, "completed": False})
        save_data()
        self.on_pre_enter()

class CheckinScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("📝 Daily Note", back_to="more", c1=GOLD))
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))
        content.add_widget(make_label("How do you feel today?", fs=dp(16), bold=True, h=dp(35), halign="center"))
        self.sel_mood = "Happy"
        for m in ["Happy", "Normal", "Tired/Low", "Frustrated", "Sleepy"]:
            btn = make_button(m, h=dp(48), bg=GOLD if m=="Happy" else GRAY)
            btn.bind(on_release=partial(self.select_mood, m))
            content.add_widget(btn)
        content.add_widget(make_label("Write anything:", h=dp(25), color=GOLD, bold=True))
        self.note = TextInput(size_hint_y=None, height=dp(120), multiline=True)
        content.add_widget(self.note)
        save_btn = make_button("SAVE CHECK-IN", h=dp(55), bg=GOLD)
        save_btn.bind(on_release=self.save_checkin)
        content.add_widget(save_btn)
        scroll.add_widget(content); root.add_widget(scroll); self.add_widget(root)
    def select_mood(self, mm):
        self.sel_mood = mm
        self.on_pre_enter()
    def save_checkin(self, inst):
        today = str(date.today())
        data["notes"][today] = {"mood": self.sel_mood, "note": self.note.text.strip()}
        save_data()
        show_popup("Saved", "Check-in saved!")

# ================= MAIN APP =================
class RoutineApp(App):
    def build(self):
        global data, DATA_FILE, sm
        # 100% SAFE: Path is initialized inside a running App instance
        DATA_FILE = os.path.join(self.user_data_dir, "routine_data.json")
        
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                loaded = json.load(f)
                for k, v in DATA_DEFAULT.items():
                    if k not in loaded: loaded[k] = v
                data.update(loaded)
        else:
            data.update(DATA_DEFAULT)

        Window.clearcolor = theme()["bg"]
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(HabitsScreen(name="habits"))
        sm.add_widget(AddHabitScreen(name="add_habit"))
        sm.add_widget(TasksScreen(name="tasks"))
        sm.add_widget(AddTaskScreen(name="add_task"))
        sm.add_widget(ReportsScreen(name="reports"))
        sm.add_widget(MoreScreen(name="more"))
        sm.add_widget(ExamsScreen(name="exams"))
        sm.add_widget(ProjectsScreen(name="projects"))
        sm.add_widget(CheckinScreen(name="checkin"))
        sm.add_widget(NamazScreen(name="namaz"))
        return sm

    def on_stop(self):
        save_data()

if __name__ == "__main__":
    RoutineApp().run()
