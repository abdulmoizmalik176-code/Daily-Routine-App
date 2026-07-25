import json
import os
from datetime import date, timedelta

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Line

DATA_FILE = "routine_data.json"

# =====================================================
# COLOR THEME (light + dark variants)
# =====================================================
LIGHT = {
    "bg": (0.98, 0.95, 0.91, 1),
    "card": (1, 1, 1, 1),
    "text": (0.24, 0.16, 0.10, 1),
    "muted": (0.61, 0.56, 0.51, 1),
}
DARK_THEME = {
    "bg": (0.125, 0.094, 0.070, 1),
    "card": (0.18, 0.14, 0.11, 1),
    "text": (0.94, 0.90, 0.86, 1),
    "muted": (0.70, 0.64, 0.57, 1),
}
ORANGE = (0.91, 0.35, 0.05, 1)
GOLD = (0.97, 0.66, 0.23, 1)
TEAL = (0.18, 0.55, 0.47, 1)
PURPLE = (0.47, 0.31, 0.66, 1)
PINK = (0.78, 0.27, 0.36, 1)
BLUE = (0.18, 0.43, 0.63, 1)
WHITE = (1, 1, 1, 1)
GRAY = (0.85, 0.82, 0.78, 1)

def theme():
    return DARK_THEME if data.get("dark_mode") else LIGHT

DATA_FILE_DEFAULT = {
    "tasks": [], "habits": [], "namaz_log": {}, "quran_log": [],
    "entertainment_log": [], "points": 0, "level": 1,
    "badges": [], "exams": [], "projects": [], "notes": {},
    "dark_mode": False
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            d = json.load(f)
            for k, v in DATA_FILE_DEFAULT.items():
                if k not in d:
                    d[k] = v
            return d
    return dict(DATA_FILE_DEFAULT)

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

NAMAZ_TIMES = {
    1:  {"Fajr": "5:44", "Zuhr": "12:17", "Asr": "3:44", "Maghrib": "5:25", "Isha": "6:50"},
    2:  {"Fajr": "5:28", "Zuhr": "12:22", "Asr": "4:13", "Maghrib": "5:54", "Isha": "7:15"},
    3:  {"Fajr": "4:55", "Zuhr": "12:17", "Asr": "4:33", "Maghrib": "6:18", "Isha": "7:38"},
    4:  {"Fajr": "4:09", "Zuhr": "12:08", "Asr": "4:47", "Maghrib": "6:41", "Isha": "8:06"},
    5:  {"Fajr": "3:30", "Zuhr": "12:04", "Asr": "4:58", "Maghrib": "7:04", "Isha": "8:37"},
    6:  {"Fajr": "3:12", "Zuhr": "12:08", "Asr": "5:08", "Maghrib": "7:22", "Isha": "9:03"},
    7:  {"Fajr": "3:27", "Zuhr": "12:14", "Asr": "5:11", "Maghrib": "7:22", "Isha": "8:59"},
    8:  {"Fajr": "3:58", "Zuhr": "12:12", "Asr": "4:58", "Maghrib": "6:58", "Isha": "8:26"},
    9:  {"Fajr": "4:26", "Zuhr": "12:03", "Asr": "4:29", "Maghrib": "6:18", "Isha": "7:39"},
    10: {"Fajr": "4:49", "Zuhr": "11:54", "Asr": "3:54", "Maghrib": "5:38", "Isha": "6:57"},
    11: {"Fajr": "5:12", "Zuhr": "11:52", "Asr": "3:27", "Maghrib": "5:08", "Isha": "6:31"},
    12: {"Fajr": "5:35", "Zuhr": "12:03", "Asr": "3:23", "Maghrib": "5:03", "Isha": "6:30"},
}
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
HABIT_COLORS = [ORANGE, TEAL, PURPLE, PINK, GOLD, BLUE]

def get_today_namaz_times():
    return NAMAZ_TIMES[date.today().month]

def show_popup(title, message):
    t = theme()
    popup = Popup(title=title, content=Label(text=message, color=t["text"]),
                   size_hint=(0.8, 0.4), title_color=t["text"], separator_color=ORANGE)
    popup.open()

def add_points(amount):
    data["points"] += amount
    new_level = (data["points"] // 100) + 1
    if new_level > data["level"]:
        data["level"] = new_level
        badge = f"Level {data['level']} Reached"
        if badge not in data["badges"]:
            data["badges"].append(badge)
        show_popup("Level Up!", f"You are now Level {data['level']}!")

def check_perfect_day():
    today = str(date.today())
    if len(data["tasks"]) == 0:
        return
    all_done = all(today in t["done_dates"] for t in data["tasks"])
    if all_done:
        badge = f"Perfect Day - {today}"
        if badge not in data["badges"]:
            data["badges"].append(badge)
            add_points(20)
            show_popup("Perfect Day!", "+20 bonus points - all tasks done today!")

# ---------------------------------------------------
# STYLE HELPERS
# ---------------------------------------------------

class Card(BoxLayout):
    def __init__(self, bg=None, radius=20, **kwargs):
        super().__init__(**kwargs)
        self._bg_color = bg if bg else theme()["card"]
        with self.canvas.before:
            Color(*self._bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size

class Ring(Widget):
    def __init__(self, pct=0.5, color=ORANGE, **kwargs):
        super().__init__(**kwargs)
        self.pct = pct
        self.ring_color = color
        self.bind(pos=self._draw, size=self._draw)
        self._draw()

    def _draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            cx = self.center_x
            cy = self.center_y
            r = min(self.width, self.height) / 2 - 10
            Color(0.85, 0.82, 0.78, 1) if not data.get("dark_mode") else Color(0.3, 0.25, 0.2, 1)
            Line(circle=(cx, cy, r), width=9)
            Color(*self.ring_color)
            Line(circle=(cx, cy, r, 90, 90 - 360 * self.pct if self.pct <= 1 else -270), width=9, cap="round")

def make_button(text, height=52, bg=ORANGE, fg=WHITE, font_size=15):
    return Button(text=text, size_hint_y=None, height=height, background_normal="",
                  background_color=bg, color=fg, font_size=font_size, bold=True)

def make_label(text, height=28, font_size=14, color=None, bold=False, halign="left"):
    t = theme()
    lbl = Label(text=text, size_hint_y=None, height=height, font_size=font_size,
                color=color if color else t["text"], bold=bold)
    return lbl

def section_label(text, color=ORANGE):
    return make_label(text.upper(), height=32, font_size=13, color=color, bold=True)

def header(title, screen_name, back_to=None, c1=ORANGE, c2=GOLD, dark_toggle=False):
    box = BoxLayout(orientation="vertical", size_hint_y=None, height=110, padding=[20, 15, 20, 10])
    with box.canvas.before:
        Color(*c1)
        box._rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[0])
    def upd(*a):
        box._rect.pos = box.pos
        box._rect.size = box.size
    box.bind(pos=upd, size=upd)

    row = BoxLayout(size_hint_y=None, height=30)
    if back_to:
        back_btn = Button(text="< Back", size_hint_x=None, width=100, background_normal="",
                           background_color=(0, 0, 0, 0), color=WHITE, font_size=13)
        back_btn.bind(on_release=lambda i: go_screen(back_to))
        row.add_widget(back_btn)
    box.add_widget(row)
    title_lbl = Label(text=title, font_size=24, bold=True, color=WHITE)
    box.add_widget(title_lbl)
    return box

def bottom_nav(active):
    nav = BoxLayout(size_hint_y=None, height=70)
    t = theme()
    items = [("Home", "home"), ("Habits", "habits"), ("Tasks", "tasks"),
             ("Reports", "reports"), ("More", "more")]
    for label, name in items:
        c = ORANGE if name == active else t["muted"]
        btn = Button(text=label, background_normal="", background_color=t["card"],
                     color=c, font_size=12, bold=(name == active))
        btn.bind(on_release=lambda inst, s=name: go_screen(s))
        nav.add_widget(btn)
    return nav

sm = None

def go_screen(name):
    sm.current = name

# ---------------------------------------------------
# HOME SCREEN
# ---------------------------------------------------

def get_today_progress():
    today = str(date.today())
    weekday = date.today().weekday()
    total, done = 0, 0
    for t in data["tasks"]:
        total += 1
        if today in t["done_dates"]:
            done += 1
    for h in data["habits"]:
        if h["days"][weekday]:
            total += 1
            if today in h["log"]:
                done += 1
    for p in get_today_namaz_times():
        total += 1
        if p in data["namaz_log"].get(today, []):
            done += 1
    total += 1
    if today in data["quran_log"]:
        done += 1
    if total == 0:
        return 0
    return done / total

class HomeScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        t = theme()
        root = BoxLayout(orientation="vertical")
        with root.canvas.before:
            Color(*t["bg"])
            root._rect = RoundedRectangle(pos=root.pos, size=root.size, radius=[0])
        def upd(*a):
            root._rect.pos = root.pos
            root._rect.size = root.size
        root.bind(pos=upd, size=upd)

        hdr = header("Assalam-o-Alaikum", "home")
        root.add_widget(hdr)

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=15, spacing=10)
        content.bind(minimum_height=content.setter("height"))

        # Progress card
        pct = get_today_progress()
        card = Card(orientation="horizontal", size_hint_y=None, height=170, padding=20, spacing=10)
        ring = Ring(pct=pct, color=ORANGE, size_hint=(None, None), size=(130, 130))
        pct_label = Label(text=f"{int(pct*100)}%", font_size=26, bold=True, color=t["text"],
                           pos_hint={"center_x": 0.5, "center_y": 0.55})
        ring_wrap = BoxLayout(size_hint_x=None, width=140)
        ring_wrap.add_widget(ring)
        card.add_widget(ring_wrap)

        stats_col = BoxLayout(orientation="vertical")
        stats_col.add_widget(make_label(f"Streak: {data.get('points',0)//20} days", font_size=15, color=ORANGE, bold=True))
        stats_col.add_widget(make_label(f"Points: {data['points']}", font_size=15, color=PURPLE, bold=True))
        stats_col.add_widget(make_label(f"Level: {data['level']}", font_size=15, color=GOLD, bold=True))
        card.add_widget(stats_col)
        content.add_widget(card)

        content.add_widget(section_label("Today's Focus"))

        today = str(date.today())
        shown = 0
        for i, tk in enumerate(data["tasks"]):
            if shown >= 5:
                break
            done = today in tk["done_dates"]
            row = self.make_task_row(tk["name"], tk["time"], done,
                                      lambda idx=i: self.toggle_task(idx))
            content.add_widget(row)
            shown += 1

        scroll.add_widget(content)
        root.add_widget(scroll)
        root.add_widget(bottom_nav("home"))
        self.add_widget(root)

    def make_task_row(self, name, sub, done, on_tap):
        t = theme()
        row = Card(orientation="horizontal", size_hint_y=None, height=70, padding=15, spacing=15)
        check = make_button("OK" if done else "", height=40, bg=(0.15, 0.6, 0.3, 1) if done else GRAY,
                             fg=WHITE, font_size=12)
        check.size_hint_x = None
        check.width = 40
        check.bind(on_release=lambda i: on_tap())
        row.add_widget(check)
        col = BoxLayout(orientation="vertical")
        col.add_widget(make_label(name, font_size=15, bold=True, height=25))
        col.add_widget(make_label(sub, font_size=12, color=t["muted"], height=20))
        row.add_widget(col)
        return row

    def toggle_task(self, index):
        today = str(date.today())
        tk = data["tasks"][index]
        if today not in tk["done_dates"]:
            tk["done_dates"].append(today)
            add_points(10)
            check_perfect_day()
        else:
            tk["done_dates"].remove(today)
        self.on_pre_enter()

# ---------------------------------------------------
# HABITS SCREEN + ADD HABIT
# ---------------------------------------------------

class HabitsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        t = theme()
        root = BoxLayout(orientation="vertical")
        with root.canvas.before:
            Color(*t["bg"])
            root._rect = RoundedRectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(root._rect, "pos", root.pos),
                  size=lambda *a: setattr(root._rect, "size", root.size))

        root.add_widget(header("My Habits", "habits", c1=PINK, c2=(0.87, 0.43, 0.27, 1)))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=15, spacing=10)
        content.bind(minimum_height=content.setter("height"))

        add_btn = make_button("+ ADD NEW HABIT", height=55, bg=PINK)
        add_btn.bind(on_release=lambda i: go_screen("add_habit"))
        content.add_widget(add_btn)

        today = str(date.today())
        week_dates = [str(date.today() - timedelta(days=i)) for i in range(6, -1, -1)]

        for idx, h in enumerate(data["habits"]):
            color = tuple(h["color"])
            card = Card(orientation="vertical", size_hint_y=None, height=140, padding=15, spacing=8)
            top_row = BoxLayout(size_hint_y=None, height=30)
            top_row.add_widget(make_label(h["name"], font_size=16, bold=True, height=30))
            streak = sum(1 for d in week_dates if d in h["log"])
            top_row.add_widget(make_label(f"{streak}/7", font_size=15, color=color, bold=True, height=30))
            card.add_widget(top_row)

            heat_row = BoxLayout(size_hint_y=None, height=50, spacing=6)
            for wd, d in enumerate(week_dates):
                done = d in h["log"]
                sq_color = color if done else (0.88, 0.85, 0.80, 1)
                b = make_button("", height=44, bg=sq_color, font_size=1)
                b.bind(on_release=lambda i, hh=idx, dd=d: self.toggle_habit(hh, dd))
                heat_row.add_widget(b)
            card.add_widget(heat_row)
            content.add_widget(card)

        if not data["habits"]:
            content.add_widget(make_label("No habits yet - add one above!", color=t["muted"]))

        scroll.add_widget(content)
        root.add_widget(scroll)
        root.add_widget(bottom_nav("habits"))
        self.add_widget(root)

    def toggle_habit(self, habit_idx, day_str):
        h = data["habits"][habit_idx]
        if day_str in h["log"]:
            h["log"].remove(day_str)
        else:
            h["log"].append(day_str)
            if day_str == str(date.today()):
                add_points(5)
        self.on_pre_enter()


class AddHabitScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        t = theme()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("Add New Habit", "add_habit", back_to="habits", c1=PINK, c2=(0.87, 0.43, 0.27, 1)))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=15, spacing=10)
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(make_label("Habit Name:", height=25, color=PINK, bold=True))
        self.name_input = TextInput(size_hint_y=None, height=45, multiline=False)
        content.add_widget(self.name_input)

        content.add_widget(section_label("Repeat On", color=PINK))
        self.day_buttons = []
        days_row = BoxLayout(size_hint_y=None, height=50, spacing=6)
        self.selected_days = [True, True, True, True, True, False, False]
        for i, dn in enumerate(DAY_NAMES):
            btn = make_button(dn[:2], height=50, bg=PINK if self.selected_days[i] else GRAY,
                               fg=WHITE if self.selected_days[i] else theme()["text"], font_size=12)
            btn.bind(on_release=lambda inst, idx=i: self.toggle_day(idx))
            days_row.add_widget(btn)
            self.day_buttons.append(btn)
        content.add_widget(days_row)

        content.add_widget(section_label("Choose Color", color=PINK))
        self.selected_color_idx = 3
        colors_row = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.color_buttons = []
        for i, c in enumerate(HABIT_COLORS):
            btn = make_button("", height=50, bg=c)
            btn.bind(on_release=lambda inst, idx=i: self.select_color(idx))
            colors_row.add_widget(btn)
            self.color_buttons.append(btn)
        content.add_widget(colors_row)

        save_btn = make_button("+ CREATE HABIT", height=55, bg=PINK)
        save_btn.bind(on_release=self.save_habit)
        content.add_widget(save_btn)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def toggle_day(self, idx):
        self.selected_days[idx] = not self.selected_days[idx]
        self.day_buttons[idx].background_color = PINK if self.selected_days[idx] else GRAY

    def select_color(self, idx):
        self.selected_color_idx = idx

    def save_habit(self, instance):
        name = self.name_input.text
        if not name:
            show_popup("Missing Info", "Please enter a habit name.")
            return
        data["habits"].append({
            "name": name,
            "color": list(HABIT_COLORS[self.selected_color_idx]),
            "days": list(self.selected_days),
            "log": []
        })
        show_popup("Saved", f"Habit '{name}' created!")
        go_screen("habits")

# ---------------------------------------------------
# TASKS SCREEN + ADD TASK
# ---------------------------------------------------

class TasksScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        t = theme()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("My Tasks", "tasks", c1=TEAL, c2=(0.30, 0.69, 0.59, 1)))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=15, spacing=10)
        content.bind(minimum_height=content.setter("height"))

        add_btn = make_button("+ ADD NEW TASK", height=55, bg=TEAL)
        add_btn.bind(on_release=lambda i: go_screen("add_task"))
        content.add_widget(add_btn)

        today = str(date.today())
        priority_colors = {"High": PINK, "Medium": GOLD, "Low": (0.6, 0.6, 0.6, 1)}
        for i, tk in enumerate(data["tasks"]):
            done = today in tk["done_dates"]
            card = Card(orientation="horizontal", size_hint_y=None, height=80, padding=12, spacing=12)
            check = make_button("OK" if done else "", height=40,
                                 bg=(0.15, 0.6, 0.3, 1) if done else GRAY, font_size=11)
            check.size_hint_x = None
            check.width = 40
            check.bind(on_release=lambda inst, idx=i: self.toggle(idx))
            card.add_widget(check)
            col = BoxLayout(orientation="vertical")
            note = f" ({tk['note']})" if tk.get("note") else ""
            col.add_widget(make_label(tk["name"], font_size=15, bold=True, height=25))
            col.add_widget(make_label(f"{tk['time']}{note}", font_size=12, color=t["muted"], height=20))
            card.add_widget(col)
            pr = tk.get("priority", "Medium")
            pr_lbl = make_label(pr, font_size=11, color=WHITE, bold=True, height=30)
            pr_lbl.size_hint_x = None
            pr_lbl.width = 70
            with pr_lbl.canvas.before:
                Color(*priority_colors.get(pr, GOLD))
                r = RoundedRectangle(pos=pr_lbl.pos, size=pr_lbl.size, radius=[14])
            pr_lbl.bind(pos=lambda inst, val, rr=r: setattr(rr, "pos", inst.pos),
                        size=lambda inst, val, rr=r: setattr(rr, "size", inst.size))
            card.add_widget(pr_lbl)
            content.add_widget(card)

        if not data["tasks"]:
            content.add_widget(make_label("No tasks yet - add one above!", color=t["muted"]))

        scroll.add_widget(content)
        root.add_widget(scroll)
        root.add_widget(bottom_nav("tasks"))
        self.add_widget(root)

    def toggle(self, index):
        today = str(date.today())
        tk = data["tasks"][index]
        if today not in tk["done_dates"]:
            tk["done_dates"].append(today)
            add_points(10)
            check_perfect_day()
        else:
            tk["done_dates"].remove(today)
        self.on_pre_enter()


class AddTaskScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("Add New Task", "add_task", back_to="tasks", c1=TEAL, c2=(0.30, 0.69, 0.59, 1)))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=15, spacing=10)
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(make_label("Task Name:", height=25, color=TEAL, bold=True))
        self.name_input = TextInput(size_hint_y=None, height=45, multiline=False)
        content.add_widget(self.name_input)

        content.add_widget(make_label("Time:", height=25, color=PINK, bold=True))
        self.time_input = TextInput(size_hint_y=None, height=45, multiline=False)
        content.add_widget(self.time_input)

        content.add_widget(section_label("Priority", color=TEAL))
        self.priority = "High"
        pr_row = BoxLayout(size_hint_y=None, height=50, spacing=8)
        self.pr_buttons = {}
        for pr, c in [("High", PINK), ("Medium", GOLD), ("Low", (0.6, 0.6, 0.6, 1))]:
            btn = make_button(pr, height=50, bg=c if pr == "High" else theme()["card"], fg=WHITE if pr == "High" else theme()["text"])
            btn.bind(on_release=lambda inst, p=pr: self.select_priority(p))
            pr_row.add_widget(btn)
            self.pr_buttons[pr] = btn
        content.add_widget(pr_row)

        content.add_widget(make_label("Note (optional):", height=25, color=PURPLE, bold=True))
        self.note_input = TextInput(size_hint_y=None, height=45, multiline=False)
        content.add_widget(self.note_input)

        save_btn = make_button("+ ADD TASK", height=55, bg=ORANGE)
        save_btn.bind(on_release=self.save_task)
        content.add_widget(save_btn)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def select_priority(self, pr):
        self.priority = pr
        colors = {"High": PINK, "Medium": GOLD, "Low": (0.6, 0.6, 0.6, 1)}
        for p, btn in self.pr_buttons.items():
            btn.background_color = colors[p] if p == pr else theme()["card"]
            btn.color = WHITE if p == pr else theme()["text"]

    def save_task(self, instance):
        name = self.name_input.text
        time_val = self.time_input.text
        if not name or not time_val:
            show_popup("Missing Info", "Please enter task name and time.")
            return
        data["tasks"].append({
            "name": name, "time": time_val, "priority": self.priority,
            "recurring": False, "note": self.note_input.text, "done_dates": []
        })
        show_popup("Saved", f"Task '{name}' added!")
        go_screen("tasks")

# ---------------------------------------------------
# REPORTS SCREEN
# ---------------------------------------------------

class ReportsScreen(Screen):
    mode = "weekly"

    def on_pre_enter(self):
        self.clear_widgets()
        t = theme()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("Reports", "reports", c1=BLUE, c2=(0.27, 0.51, 0.70, 1)))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=15, spacing=10)
        content.bind(minimum_height=content.setter("height"))

        toggle_row = BoxLayout(size_hint_y=None, height=45, spacing=8)
        w_btn = make_button("Weekly", height=45, bg=BLUE if self.mode == "weekly" else t["card"],
                             fg=WHITE if self.mode == "weekly" else t["text"])
        m_btn = make_button("Monthly", height=45, bg=BLUE if self.mode == "monthly" else t["card"],
                             fg=WHITE if self.mode == "monthly" else t["text"])
        w_btn.bind(on_release=lambda i: self.set_mode("weekly"))
        m_btn.bind(on_release=lambda i: self.set_mode("monthly"))
        toggle_row.add_widget(w_btn)
        toggle_row.add_widget(m_btn)
        content.add_widget(toggle_row)

        if self.mode == "weekly":
            today = date.today()
            dates = [str(today - timedelta(days=i)) for i in range(7)]
            label_suffix = "this week"
            namaz_max = 35
            days_count = 7
        else:
            today = date.today()
            month_prefix = today.strftime("%Y-%m")
            dates = None
            label_suffix = "this month"
            days_count = today.day
            namaz_max = days_count * 5

        def in_range(d):
            if dates is not None:
                return d in dates
            return d.startswith(today.strftime("%Y-%m"))

        total_tasks_done = sum(1 for tk in data["tasks"] for d in tk["done_dates"] if in_range(d))
        namaz_count = sum(len(v) for d, v in data["namaz_log"].items() if in_range(d))
        quran_count = sum(1 for d in data["quran_log"] if in_range(d))
        ent_count = sum(1 for d in data["entertainment_log"] if in_range(d))

        grid = BoxLayout(size_hint_y=None, height=200)
        col1 = BoxLayout(orientation="vertical", spacing=8)
        col2 = BoxLayout(orientation="vertical", spacing=8)

        def stat_tile(value, label, color):
            tile = Card(orientation="vertical", bg=color, size_hint_y=None, height=95, padding=10)
            tile.add_widget(Label(text=value, font_size=24, bold=True, color=WHITE))
            tile.add_widget(Label(text=label, font_size=11, color=WHITE))
            return tile

        col1.add_widget(stat_tile(str(total_tasks_done), f"Tasks Done {label_suffix}", TEAL))
        col1.add_widget(stat_tile(f"{namaz_count}/{namaz_max}", "Namaz Prayed", ORANGE))
        col2.add_widget(stat_tile(f"{quran_count}/{days_count}", "Quran Days", PURPLE))
        col2.add_widget(stat_tile(f"{ent_count}/{days_count}", "Entertainment", GOLD))
        grid.add_widget(col1)
        grid.add_widget(col2)
        content.add_widget(grid)

        content.add_widget(section_label("Moods", color=BLUE))
        shown = 0
        for d, entry in sorted(data["notes"].items(), reverse=True):
            if in_range(d) and shown < 10:
                row = Card(orientation="horizontal", size_hint_y=None, height=45, padding=12)
                row.add_widget(make_label(d, font_size=13, height=30))
                row.add_widget(make_label(entry["mood"], font_size=13, color=BLUE, bold=True, height=30))
                content.add_widget(row)
                shown += 1

        scroll.add_widget(content)
        root.add_widget(scroll)
        root.add_widget(bottom_nav("reports"))
        self.add_widget(root)

    def set_mode(self, m):
        ReportsScreen.mode = m
        self.on_pre_enter()

# ---------------------------------------------------
# MORE SCREEN (grid) + sub-screens
# ---------------------------------------------------

class MoreScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("More", "more", c1=PURPLE, c2=(0.59, 0.42, 0.77, 1)))

        scroll = ScrollView()
        grid = BoxLayout(orientation="vertical", size_hint_y=None, padding=15, spacing=12)
        grid.bind(minimum_height=grid.setter("height"))

        items = [
            ("Exam Days", "exams", PINK),
            ("Projects & Goals", "projects", BLUE),
            ("Daily Note & Mood", "checkin", GOLD),
            ("Points & Badges", "points", (0.77, 0.58, 0.08, 1)),
            ("Namaz & Quran", "namaz", ORANGE),
        ]
        for label, screen_name, color in items:
            btn = make_button(label, height=70, bg=color, font_size=17)
            btn.bind(on_release=lambda inst, s=screen_name: go_screen(s))
            grid.add_widget(btn)

        dark_label = "Switch to Light Mode" if data.get("dark_mode") else "Switch to Dark Mode"
        dark_btn = make_button(dark_label, height=70, bg=(0.42, 0.39, 0.37, 1), font_size=17)
        dark_btn.bind(on_release=self.toggle_dark)
        grid.add_widget(dark_btn)

        scroll.add_widget(grid)
        root.add_widget(scroll)
        root.add_widget(bottom_nav("more"))
        self.add_widget(root)

    def toggle_dark(self, instance):
        data["dark_mode"] = not data.get("dark_mode", False)
        Window.clearcolor = theme()["bg"]
        self.on_pre_enter()


class ExamsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        t = theme()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("Exam Days", "exams", back_to="more", c1=PURPLE, c2=(0.59, 0.42, 0.77, 1)))
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=15, spacing=10)
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(make_label("Subject:", height=25, color=PURPLE, bold=True))
        self.subject_input = TextInput(size_hint_y=None, height=45, multiline=False)
        content.add_widget(self.subject_input)
        content.add_widget(make_label("Date (YYYY-MM-DD):", height=25, color=PURPLE, bold=True))
        self.date_input = TextInput(size_hint_y=None, height=45, multiline=False)
        content.add_widget(self.date_input)
        add_btn = make_button("+ ADD EXAM", height=50, bg=PURPLE)
        add_btn.bind(on_release=self.add_exam)
        content.add_widget(add_btn)

        today = date.today()
        for exam in data["exams"]:
            try:
                ed = date.fromisoformat(exam["date"])
                dl = (ed - today).days
                info = f"in {dl} day(s)" if dl > 0 else ("TODAY!" if dl == 0 else "passed")
            except ValueError:
                info = "invalid date"
            card = Card(orientation="vertical", size_hint_y=None, height=70, padding=12)
            card.add_widget(make_label(exam["subject"], font_size=15, bold=True, height=25))
            card.add_widget(make_label(info, font_size=12, color=PINK, height=20))
            content.add_widget(card)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def add_exam(self, instance):
        if not self.subject_input.text or not self.date_input.text:
            show_popup("Missing Info", "Enter subject and date.")
            return
        data["exams"].append({"subject": self.subject_input.text, "date": self.date_input.text})
        self.on_pre_enter()


class ProjectsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("Projects & Goals", "projects", back_to="more", c1=BLUE, c2=(0.27, 0.51, 0.70, 1)))
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=15, spacing=10)
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(make_label("Title:", height=25, color=BLUE, bold=True))
        self.title_input = TextInput(size_hint_y=None, height=45, multiline=False)
        content.add_widget(self.title_input)
        content.add_widget(make_label("End Date (YYYY-MM-DD):", height=25, color=BLUE, bold=True))
        self.end_input = TextInput(size_hint_y=None, height=45, multiline=False)
        content.add_widget(self.end_input)
        add_btn = make_button("+ ADD PROJECT", height=50, bg=BLUE)
        add_btn.bind(on_release=self.add_project)
        content.add_widget(add_btn)

        for i, p in enumerate(data["projects"]):
            card = Card(orientation="vertical", size_hint_y=None, height=90, padding=12, spacing=6)
            card.add_widget(make_label(p["title"], font_size=15, bold=True, height=25))
            status = "Completed" if p["completed"] else "In Progress"
            row = BoxLayout(size_hint_y=None, height=35)
            row.add_widget(make_label(status, font_size=12, color=TEAL if p["completed"] else PINK, height=35))
            if not p["completed"]:
                cbtn = make_button("Complete", height=35, bg=ORANGE, font_size=11)
                cbtn.bind(on_release=lambda inst, idx=i: self.complete(idx))
                row.add_widget(cbtn)
            card.add_widget(row)
            content.add_widget(card)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def add_project(self, instance):
        if not self.title_input.text or not self.end_input.text:
            show_popup("Missing Info", "Enter title and end date.")
            return
        data["projects"].append({"title": self.title_input.text, "start": str(date.today()),
                                  "end": self.end_input.text, "completed": False})
        self.on_pre_enter()

    def complete(self, index):
        data["projects"][index]["completed"] = True
        self.on_pre_enter()


class CheckinScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("Daily Note & Mood", "checkin", back_to="more", c1=GOLD, c2=(0.94, 0.66, 0.31, 1)))
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=15, spacing=10)
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(make_label("How do you feel today?", font_size=16, bold=True, height=35, halign="center"))
        self.selected_mood = "Happy"
        self.mood_buttons = {}
        moods = ["Happy", "Normal", "Tired/Low", "Frustrated", "Sleepy"]
        for m in moods:
            btn = make_button(m, height=48, bg=GOLD if m == "Happy" else theme()["card"],
                               fg=WHITE if m == "Happy" else theme()["text"])
            btn.bind(on_release=lambda inst, mm=m: self.pick_mood(mm))
            content.add_widget(btn)
            self.mood_buttons[m] = btn

        content.add_widget(make_label("Write anything about your day:", height=25, color=GOLD, bold=True))
        self.note_input = TextInput(size_hint_y=None, height=120, multiline=True)
        content.add_widget(self.note_input)

        save_btn = make_button("SAVE CHECK-IN", height=55, bg=GOLD)
        save_btn.bind(on_release=self.save)
        content.add_widget(save_btn)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def pick_mood(self, m):
        self.selected_mood = m
        for mm, btn in self.mood_buttons.items():
            btn.background_color = GOLD if mm == m else theme()["card"]
            btn.color = WHITE if mm == m else theme()["text"]

    def save(self, instance):
        today = str(date.today())
        data["notes"][today] = {"mood": self.selected_mood, "note": self.note_input.text.strip()}
        show_popup("Saved", "Check-in saved!")


class PointsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("Points & Badges", "points", back_to="more", c1=(0.77, 0.58, 0.08, 1), c2=(0.88, 0.72, 0.25, 1)))
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=15, spacing=10)
        content.bind(minimum_height=content.setter("height"))

        row = BoxLayout(size_hint_y=None, height=95, spacing=10)
        row.add_widget(self._stat_card(str(data["points"]), "Points", ORANGE))
        row.add_widget(self._stat_card(str(data["level"]), "Level", PURPLE))
        content.add_widget(row)

        content.add_widget(section_label("Badges Earned", color=(0.77, 0.58, 0.08, 1)))
        if not data["badges"]:
            content.add_widget(make_label("No badges yet - keep going!"))
        for b in data["badges"]:
            card = Card(orientation="horizontal", size_hint_y=None, height=55, padding=15, bg=ORANGE)
            card.add_widget(Label(text=b, color=WHITE, bold=True, font_size=14))
            content.add_widget(card)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def _stat_card(self, value, label, color):
        c = Card(orientation="vertical", bg=color, padding=10)
        c.add_widget(Label(text=value, font_size=26, bold=True, color=WHITE))
        c.add_widget(Label(text=label, font_size=12, color=WHITE))
        return c


class NamazScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("Namaz & Quran", "namaz", back_to="more", c1=ORANGE, c2=GOLD))
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=15, spacing=10)
        content.bind(minimum_height=content.setter("height"))

        today = str(date.today())
        times = get_today_namaz_times()
        if today not in data["namaz_log"]:
            data["namaz_log"][today] = []
        for p in times:
            done = p in data["namaz_log"][today]
            card = Card(orientation="horizontal", size_hint_y=None, height=70, padding=12, spacing=12)
            check = make_button("OK" if done else "", height=40, bg=(0.15, 0.6, 0.3, 1) if done else GRAY, font_size=11)
            check.size_hint_x = None
            check.width = 40
            check.bind(on_release=lambda inst, pp=p: self.toggle_namaz(pp))
            card.add_widget(check)
            col = BoxLayout(orientation="vertical")
            col.add_widget(make_label(p, font_size=15, bold=True, height=25))
            col.add_widget(make_label(times[p], font_size=12, color=theme()["muted"], height=20))
            card.add_widget(col)
            content.add_widget(card)

        q_done = today in data["quran_log"]
        qcard = Card(orientation="horizontal", size_hint_y=None, height=70, padding=12, spacing=12)
        qcheck = make_button("OK" if q_done else "", height=40, bg=(0.15, 0.6, 0.3, 1) if q_done else GRAY, font_size=11)
        qcheck.size_hint_x = None
        qcheck.width = 40
        qcheck.bind(on_release=self.toggle_quran)
        qcard.add_widget(qcheck)
        qcard.add_widget(make_label("Quran Recitation", font_size=15, bold=True))
        content.add_widget(qcard)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def toggle_namaz(self, prayer):
        today = str(date.today())
        if prayer not in data["namaz_log"][today]:
            data["namaz_log"][today].append(prayer)
            add_points(15)
        else:
            data["namaz_log"][today].remove(prayer)
        self.on_pre_enter()

    def toggle_quran(self, instance):
        today = str(date.today())
        if today not in data["quran_log"]:
            data["quran_log"].append(today)
            add_points(15)
        else:
            data["quran_log"].remove(today)
        self.on_pre_enter()

# ---------------------------------------------------
# MAIN APP
# ---------------------------------------------------

class RoutineApp(App):
    def build(self):
        global sm
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
        sm.add_widget(PointsScreen(name="points"))
        sm.add_widget(NamazScreen(name="namaz"))
        return sm

    def on_stop(self):
        save_data()


if __name__ == "__main__":
    RoutineApp().run()
