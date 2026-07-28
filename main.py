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
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle
from kivy.metrics import dp
import traceback

# ================= DATA FILE =================
# The real safe per-app storage path is set inside build() below,
# using self.user_data_dir (only works on a RUNNING app instance).
DATA_FILE = "routine_data.json"

# ================= COLORS =================
LIGHT = {"bg": (0.98, 0.95, 0.91, 1), "card": (1, 1, 1, 1), "text": (0.24, 0.16, 0.10, 1), "muted": (0.61, 0.56, 0.51, 1)}
DARK = {"bg": (0.125, 0.094, 0.070, 1), "card": (0.18, 0.14, 0.11, 1), "text": (0.94, 0.90, 0.86, 1), "muted": (0.70, 0.64, 0.57, 1)}
ORANGE = (0.91, 0.35, 0.05, 1); GOLD = (0.97, 0.66, 0.23, 1); TEAL = (0.18, 0.55, 0.47, 1)
PURPLE = (0.47, 0.31, 0.66, 1); PINK = (0.78, 0.27, 0.36, 1); BLUE = (0.18, 0.43, 0.63, 1); WHITE = (1,1,1,1); GRAY = (0.85,0.82,0.78,1)

def theme(): return DARK if data.get("dark_mode") else LIGHT

DATA_DEFAULT = {
    "tasks": [], "habits": [], "namaz_log": {}, "quran_log": [], "entertainment_log": [],
    "points": 0, "level": 1, "badges": [], "exams": [], "projects": [], "notes": {}, "dark_mode": False
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                d = json.load(f)
                for k, v in DATA_DEFAULT.items():
                    if k not in d: d[k] = v
                return d
        except (json.JSONDecodeError, OSError):
            return dict(DATA_DEFAULT)
    return dict(DATA_DEFAULT)

def save_data():
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except OSError:
        pass

data = load_data()

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

def get_today_namaz_times(): return NAMAZ_TIMES[date.today().month]

def show_popup(title, message, on_close=None):
    t = theme()
    popup = Popup(title=title, content=Label(text=message, color=t["text"], font_size=dp(16), halign="center"),
                  size_hint=(0.8, 0.4), title_color=t["text"], separator_color=ORANGE, title_size=dp(18))
    if on_close:
        popup.bind(on_dismiss=lambda *a: on_close())
    popup.open()

def add_points(amount):
    data["points"] += amount
    new_level = (data["points"] // 100) + 1
    if new_level > data["level"]:
        data["level"] = new_level
        data["badges"].append(f"Level {data['level']} Reached")
        show_popup("Level Up!", f"You are now Level {data['level']}!")
    save_data()

def check_perfect_day():
    today = str(date.today())
    if not data["tasks"]: return
    if all(today in t["done_dates"] for t in data["tasks"]):
        badge = f"Perfect Day - {today}"
        if badge not in data["badges"]:
            data["badges"].append(badge)
            add_points(20)
            show_popup("Perfect Day!", "+20 bonus points!")

class Card(BoxLayout):
    def __init__(self, bg=None, radius=dp(20), **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None  # FIX: without this, explicit height was ignored,
                                  # causing rows to overlap instead of stacking
        self.padding, self.spacing = dp(15), dp(10)
        self._bg_color = bg if bg else theme()["card"]
        with self.canvas.before:
            Color(*self._bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
        self.bind(pos=self._update, size=self._update)
    def _update(self, *args): self._rect.pos, self._rect.size = self.pos, self.size

class FAB(Button):
    def __init__(self, target, **kwargs):
        super().__init__(**kwargs)
        self.size_hint, self.size = (None, None), (dp(60), dp(60))
        self.background_normal, self.background_color = '', (0,0,0,0)
        self.text, self.font_size, self.color = '+', dp(32), WHITE
        self.bind(on_release=partial(go_screen, target))
        with self.canvas.before:
            Color(*ORANGE)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(30)])
        self.bind(pos=self._update, size=self._update)
    def _update(self, *args): self.rect.pos, self.rect.size = self.pos, self.size


def add_fab(root, target):
    """Adds a floating + button positioned safely above the bottom nav,
    so it never overlaps other buttons or text."""
    fab = FAB(target)
    def reposition(*a):
        fab.pos = (root.width - fab.width - dp(20), dp(90))
    root.bind(size=reposition, pos=reposition)
    root.add_widget(fab)
    reposition()
    return fab

class Ring(Widget):
    def __init__(self, pct=0.5, color=ORANGE, **kwargs):
        super().__init__(**kwargs)
        self.pct, self.ring_color = pct, color
        self.bind(pos=self._draw, size=self._draw); self._draw()
    def _draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            cx, cy, r = self.center_x, self.center_y, min(self.width, self.height)/2 - dp(10)
            Color(0.85, 0.82, 0.78, 1) if not data.get("dark_mode") else Color(0.3, 0.25, 0.2, 1)
            Line(circle=(cx, cy, r), width=dp(9))
            Color(*self.ring_color)
            Line(circle=(cx, cy, r, 90, 90 - 360*self.pct if self.pct <= 1 else -270), width=dp(9), cap="round")

def make_button(text, h=dp(52), bg=ORANGE, fg=WHITE, fs=dp(16)):
    return Button(text=text, size_hint_y=None, height=h, background_normal="", background_color=bg, color=fg, font_size=fs, bold=True)

def make_label(text, h=dp(30), fs=dp(15), color=None, bold=False):
    t = theme()
    return Label(text=text, size_hint_y=None, height=h, font_size=fs, color=color if color else t["text"], bold=bold)

def section_label(text, color=ORANGE):
    return make_label(text.upper(), h=dp(32), fs=dp(14), color=color, bold=True)

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
    items = [("Home", "home"), ("Habits", "habits"), ("Tasks", "tasks"), ("Reports", "reports"), ("More", "more")]
    for label, name in items:
        c = ORANGE if name == active else t["muted"]
        btn = Button(text=label, background_normal="", background_color=(0,0,0,0), color=c, font_size=dp(13), bold=(name==active))
        btn.bind(on_release=partial(go_screen, name))
        nav.add_widget(btn)
    return nav


class SafeScreen(Screen):
    """
    Every screen inherits from this instead of Screen directly.
    If anything goes wrong while building a screen, instead of the
    whole app crashing silently, this catches the error and shows
    it on screen so it can be read and fixed.
    """
    def on_pre_enter(self):
        try:
            self._build()
        except Exception:
            self.clear_widgets()
            box = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(10))
            box.add_widget(Label(text="Something went wrong on this screen:",
                                  color=(1, 1, 1, 1), font_size=dp(18), bold=True,
                                  size_hint_y=None, height=dp(50)))
            err_scroll = ScrollView()
            err_label = Label(text=traceback.format_exc(), color=(1, 0.6, 0.6, 1),
                               font_size=dp(12), size_hint_y=None, halign="left", valign="top")
            err_label.bind(texture_size=lambda inst, val: setattr(err_label, "height", val[1]))
            err_label.bind(width=lambda inst, val: err_label.setter("text_size")(err_label, (val, None)))
            err_scroll.add_widget(err_label)
            box.add_widget(err_scroll)
            back_btn = make_button("Go to Home", bg=ORANGE)
            back_btn.bind(on_release=partial(go_screen, "home"))
            box.add_widget(back_btn)
            self.add_widget(box)

sm = None
def go_screen(name, *args): sm.current = name

def get_today_progress():
    today, wd = str(date.today()), date.today().weekday()
    total, done = 0, 0
    for t in data["tasks"]:
        total += 1
        if today in t["done_dates"]: done += 1
    for h in data["habits"]:
        if h["days"][wd]:
            total += 1
            if today in h["log"]: done += 1
    for p in get_today_namaz_times():
        total += 1
        if p in data["namaz_log"].get(today, []): done += 1
    total += 1
    if today in data["quran_log"]: done += 1
    return 0 if total == 0 else done / total

class HomeScreen(SafeScreen):
    timer_running = False
    time_left = 1500

    def _build(self):
        save_data()
        self.clear_widgets()
        root = RelativeLayout(); t = theme()
        with root.canvas.before:
            Color(*t["bg"]); root._rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(root._rect, "pos", root.pos), size=lambda *a: setattr(root._rect, "size", root.size))

        box = BoxLayout(orientation="vertical")
        box.add_widget(header("Assalam-o-Alaikum", c1=ORANGE, c2=GOLD))
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(12))
        content.bind(minimum_height=content.setter("height"))

        pct = get_today_progress()
        card = Card(orientation="horizontal", height=dp(170))
        ring = Ring(pct=pct, size_hint=(None, None), size=(dp(130), dp(130)))
        wrap = BoxLayout(size_hint_x=None, width=dp(140)); wrap.add_widget(ring); card.add_widget(wrap)
        stats = BoxLayout(orientation="vertical")
        stats.add_widget(make_label(f"Streak: {data.get('points',0)//20} days", fs=dp(16), color=ORANGE))
        stats.add_widget(make_label(f"Points: {data['points']}", fs=dp(16), color=PURPLE))
        stats.add_widget(make_label(f"Level: {data['level']}", fs=dp(16), color=GOLD))
        card.add_widget(stats); content.add_widget(card)

        content.add_widget(section_label("Focus Timer"))
        pcard = Card(orientation="horizontal", height=dp(80))
        self.timer_lbl = Label(text="25:00", font_size=dp(32), color=PINK, bold=True, size_hint_x=None, width=dp(120))
        pcard.add_widget(self.timer_lbl)
        self.pom_btn = make_button("Start Focus", h=dp(50), bg=PINK)
        self.pom_btn.bind(on_release=self.toggle_timer)
        pcard.add_widget(self.pom_btn); content.add_widget(pcard)

        content.add_widget(section_label("Today's Focus"))
        today = str(date.today())
        for i, tk in enumerate(data["tasks"]):
            if i >= 5: break
            done = today in tk["done_dates"]
            row = Card(orientation="horizontal", height=dp(70), padding=dp(12))
            check = Button(text="OK" if done else "", size_hint_x=None, width=dp(40), height=dp(40),
                           background_normal="", background_color=(0.15, 0.6, 0.3, 1) if done else GRAY,
                           color=WHITE, font_size=dp(14), bold=True, pos_hint={"center_y": 0.5})
            check.bind(on_release=partial(self.toggle_task, i))
            row.add_widget(check)
            col = BoxLayout(orientation="vertical")
            col.add_widget(make_label(tk["name"], fs=dp(16), bold=True, h=dp(25)))
            col.add_widget(make_label(tk["time"], fs=dp(13), color=t["muted"], h=dp(20)))
            row.add_widget(col); content.add_widget(row)

        scroll.add_widget(content)
        box.add_widget(scroll)
        box.add_widget(bottom_nav("home"))
        root.add_widget(box)
        add_fab(root, "add_task")
        self.add_widget(root)

    def toggle_timer(self, inst):
        if self.timer_running:
            self.timer_running = False
            self.pom_btn.text = "Start Focus"; self.pom_btn.background_color = PINK
            Clock.unschedule(self.update_timer)
            self.time_left = 1500; self.timer_lbl.text = "25:00"
        else:
            self.timer_running = True
            self.pom_btn.text = "Stop"; self.pom_btn.background_color = (0.8, 0.1, 0.1, 1)
            Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.time_left -= 1
        mins, secs = divmod(self.time_left, 60)
        self.timer_lbl.text = f"{mins:02d}:{secs:02d}"
        if self.time_left <= 0:
            Clock.unschedule(self.update_timer)
            self.timer_running = False
            self.pom_btn.text = "Start Focus"; self.pom_btn.background_color = PINK
            show_popup("Time's Up!", "Great focus! Take a 5 min break.")
            self.time_left = 1500; self.timer_lbl.text = "25:00"

    def toggle_task(self, index, *args):
        today = str(date.today())
        tk = data["tasks"][index]
        if today not in tk["done_dates"]:
            tk["done_dates"].append(today); add_points(10); check_perfect_day()
        else: tk["done_dates"].remove(today)
        save_data(); self.on_pre_enter()

class HabitsScreen(SafeScreen):
    def _build(self):
        save_data()
        self.clear_widgets(); t = theme()
        root = RelativeLayout()
        with root.canvas.before:
            Color(*t["bg"]); root._rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(root._rect, "pos", root.pos), size=lambda *a: setattr(root._rect, "size", root.size))
        box = BoxLayout(orientation="vertical")
        box.add_widget(header("My Habits", c1=PINK, c2=(0.87, 0.43, 0.27, 1)))
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))
        today, week = str(date.today()), [str(date.today() - timedelta(days=i)) for i in range(6, -1, -1)]
        for idx, h in enumerate(data["habits"]):
            color = tuple(h["color"])
            card = Card(orientation="vertical", height=dp(140))
            top = BoxLayout(size_hint_y=None, height=dp(30))
            top.add_widget(make_label(h["name"], fs=dp(16), bold=True, h=dp(30)))
            streak = sum(1 for d in week if d in h["log"])
            top.add_widget(make_label(f"{streak}/7", fs=dp(15), color=color, bold=True, h=dp(30)))
            card.add_widget(top)
            heat = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(6))
            for wd, d in enumerate(week):
                done = d in h["log"]
                b = Button(text="", size_hint_y=None, height=dp(44), background_normal="", background_color=color if done else GRAY, font_size=1)
                b.bind(on_release=partial(self.toggle_habit, idx, d))
                heat.add_widget(b)
            card.add_widget(heat); content.add_widget(card)
        scroll.add_widget(content)
        box.add_widget(scroll)
        box.add_widget(bottom_nav("habits"))
        root.add_widget(box)
        add_fab(root, "add_habit")
        self.add_widget(root)

    def toggle_habit(self, idx, day, *args):
        h = data["habits"][idx]
        if day in h["log"]: h["log"].remove(day)
        else:
            h["log"].append(day)
            if day == str(date.today()): add_points(5)
        save_data(); self.on_pre_enter()

class AddHabitScreen(SafeScreen):
    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("Add Habit", back_to="habits", c1=PINK))
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
        colors_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        self.sel_color = 3
        self.color_buttons = []
        for i, c in enumerate(HABIT_COLORS):
            b = make_button("SELECTED" if i == self.sel_color else "", h=dp(50), bg=c, fs=dp(10))
            b.bind(on_release=partial(self.select_color, i))
            colors_row.add_widget(b)
            self.color_buttons.append(b)
        content.add_widget(colors_row)
        save_btn = make_button("+ CREATE HABIT", bg=PINK, h=dp(55))
        save_btn.bind(on_release=self.save_habit)
        content.add_widget(save_btn)
        scroll.add_widget(content); root.add_widget(scroll); self.add_widget(root)

    def toggle_day(self, idx, *args):
        self.sel_days[idx] = not self.sel_days[idx]
        self.day_btns[idx].background_color = PINK if self.sel_days[idx] else GRAY

    def select_color(self, idx, *args):
        self.sel_color = idx
        for i, btn in enumerate(self.color_buttons):
            btn.text = "SELECTED" if i == idx else ""

    def save_habit(self, inst):
        n = self.name_input.text
        if not n: show_popup("Error", "Enter a habit name."); return
        data["habits"].append({"name": n, "color": list(HABIT_COLORS[self.sel_color]), "days": list(self.sel_days), "log": []})
        save_data()
        show_popup("Saved", f"Habit '{n}' created!", on_close=lambda: go_screen("habits"))

class TasksScreen(SafeScreen):
    def _build(self):
        save_data()
        self.clear_widgets(); t = theme()
        root = RelativeLayout()
        with root.canvas.before:
            Color(*t["bg"]); root._rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(root._rect, "pos", root.pos), size=lambda *a: setattr(root._rect, "size", root.size))
        box = BoxLayout(orientation="vertical")
        box.add_widget(header("My Tasks", c1=TEAL, c2=(0.30, 0.69, 0.59, 1)))
        scroll = ScrollView(); content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10)); content.bind(minimum_height=content.setter("height"))
        today, colors = str(date.today()), {"High": PINK, "Medium": GOLD, "Low": (0.6,0.6,0.6,1)}
        for i, tk in enumerate(data["tasks"]):
            done = today in tk["done_dates"]
            row = Card(orientation="horizontal", height=dp(80), padding=dp(12))
            check = Button(text="OK" if done else "", size_hint_x=None, width=dp(40), height=dp(40), background_normal="", background_color=(0.15,0.6,0.3,1) if done else GRAY, color=WHITE, font_size=dp(12), bold=True, pos_hint={"center_y":0.5})
            check.bind(on_release=partial(self.toggle_task, i))
            row.add_widget(check)
            col = BoxLayout(orientation="vertical")
            col.add_widget(make_label(tk["name"], fs=dp(16), bold=True, h=dp(25)))
            col.add_widget(make_label(tk["time"], fs=dp(13), color=t["muted"], h=dp(20)))
            row.add_widget(col)
            pr = tk.get("priority", "Medium")
            pr_lbl = Label(text=pr, font_size=dp(11), color=WHITE, bold=True, size_hint_x=None, width=dp(70), halign="center", valign="middle")
            with pr_lbl.canvas.before:
                Color(*colors.get(pr, GOLD))
                r = RoundedRectangle(pos=pr_lbl.pos, size=pr_lbl.size, radius=[dp(14)])
            pr_lbl.bind(pos=lambda inst, val, rr=r: setattr(rr, "pos", inst.pos), size=lambda inst, val, rr=r: setattr(rr, "size", inst.size))
            row.add_widget(pr_lbl)
            content.add_widget(row)
        scroll.add_widget(content); box.add_widget(scroll); box.add_widget(bottom_nav("tasks")); root.add_widget(box); add_fab(root, "add_task"); self.add_widget(root)

    def toggle_task(self, idx, *args):
        today = str(date.today())
        tk = data["tasks"][idx]
        if today not in tk["done_dates"]:
            tk["done_dates"].append(today); add_points(10); check_perfect_day()
        else: tk["done_dates"].remove(today)
        save_data(); self.on_pre_enter()

class AddTaskScreen(SafeScreen):
    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("Add Task", back_to="tasks", c1=TEAL))
        scroll = ScrollView(); content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10)); content.bind(minimum_height=content.setter("height"))
        content.add_widget(make_label("Task Name:", fs=dp(16), color=TEAL, bold=True))
        self.name_input = TextInput(size_hint_y=None, height=dp(45), font_size=dp(16)); content.add_widget(self.name_input)
        content.add_widget(make_label("Time:", fs=dp(16), color=PINK, bold=True))
        self.time_input = TextInput(size_hint_y=None, height=dp(45), font_size=dp(16)); content.add_widget(self.time_input)
        content.add_widget(section_label("Priority", color=TEAL))
        self.priority = "High"
        pr_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        self.priority_colors = {"High": PINK, "Medium": GOLD, "Low": (0.6,0.6,0.6,1)}
        self.pr_buttons = {}
        for pr, c in self.priority_colors.items():
            b = make_button(pr, h=dp(50), bg=c if pr=="High" else GRAY, fs=dp(13))
            b.bind(on_release=partial(self.select_priority, pr))
            pr_row.add_widget(b)
            self.pr_buttons[pr] = b
        content.add_widget(pr_row)
        content.add_widget(section_label("Settings", color=TEAL))
        toggle_row = Card(orientation="horizontal", height=dp(60))
        toggle_row.add_widget(make_label("Repeats Daily", fs=dp(16), bold=True))
        self.recur = False
        toggle_btn = make_button("OFF", h=dp(30), bg=GRAY, fs=dp(12))
        toggle_btn.size_hint_x = None; toggle_btn.width = dp(60)
        toggle_btn.bind(on_release=self.toggle_recurring)
        toggle_row.add_widget(toggle_btn)
        content.add_widget(toggle_row)
        content.add_widget(make_label("Note (optional):", fs=dp(16), color=PURPLE, bold=True))
        self.note_input = TextInput(size_hint_y=None, height=dp(45), font_size=dp(16)); content.add_widget(self.note_input)
        save_btn = make_button("+ ADD TASK", bg=ORANGE, h=dp(55))
        save_btn.bind(on_release=self.save_task)
        content.add_widget(save_btn)
        scroll.add_widget(content); root.add_widget(scroll); self.add_widget(root)

    def select_priority(self, pr, *args):
        self.priority = pr
        for name, btn in self.pr_buttons.items():
            btn.background_color = self.priority_colors[name] if name == pr else GRAY

    def toggle_recurring(self, inst):
        self.recur = not self.recur
        inst.text = "ON" if self.recur else "OFF"
        inst.background_color = TEAL if self.recur else GRAY

    def save_task(self, inst):
        n, t = self.name_input.text, self.time_input.text
        if not n or not t: show_popup("Error", "Enter name & time."); return
        data["tasks"].append({"name": n, "time": t, "priority": self.priority, "recurring": self.recur, "note": self.note_input.text, "done_dates": []})
        save_data()
        show_popup("Saved", f"Task '{n}' added!", on_close=lambda: go_screen("tasks"))

class ReportsScreen(SafeScreen):
    mode = "weekly"
    def _build(self):
        self.clear_widgets(); t = theme(); root = BoxLayout(orientation="vertical")
        root.add_widget(header("Reports", c1=BLUE, c2=(0.27,0.51,0.70,1)))
        scroll = ScrollView(); content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10)); content.bind(minimum_height=content.setter("height"))
        today = date.today()
        dates = [str(today - timedelta(days=i)) for i in range(7)] if self.mode == "weekly" else None
        def in_range(d): return d in dates if dates else d.startswith(today.strftime("%Y-%m"))
        total_tasks = sum(1 for tk in data["tasks"] for d in tk["done_dates"] if in_range(d))
        namaz_count = sum(len(v) for d, v in data["namaz_log"].items() if in_range(d))
        quran_count = sum(1 for d in data["quran_log"] if in_range(d))
        ent_count = sum(1 for d in data["entertainment_log"] if in_range(d))
        days_count = 7 if self.mode == "weekly" else today.day
        namaz_max = 35 if self.mode == "weekly" else days_count*5
        toggle_row = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(8))
        wb = make_button("Weekly", h=dp(45), bg=BLUE if self.mode=="weekly" else GRAY, fs=dp(14))
        mb = make_button("Monthly", h=dp(45), bg=BLUE if self.mode=="monthly" else GRAY, fs=dp(14))
        wb.bind(on_release=partial(self.set_mode, "weekly"))
        mb.bind(on_release=partial(self.set_mode, "monthly"))
        toggle_row.add_widget(wb); toggle_row.add_widget(mb)
        content.add_widget(toggle_row)
        grid = BoxLayout(size_hint_y=None, height=dp(200))
        col1, col2 = BoxLayout(orientation="vertical", spacing=dp(8)), BoxLayout(orientation="vertical", spacing=dp(8))
        def stat_tile(v, lbl, c):
            tile = Card(orientation="vertical", bg=c, height=dp(95), padding=dp(10))
            tile.add_widget(Label(text=v, font_size=dp(24), bold=True, color=WHITE))
            tile.add_widget(Label(text=lbl, font_size=dp(11), color=WHITE))
            return tile
        col1.add_widget(stat_tile(str(total_tasks), f"Tasks Done ({self.mode})", TEAL))
        col1.add_widget(stat_tile(f"{namaz_count}/{namaz_max}", "Namaz Prayed", ORANGE))
        col2.add_widget(stat_tile(f"{quran_count}/{days_count}", "Quran Days", PURPLE))
        col2.add_widget(stat_tile(f"{ent_count}/{days_count}", "Entertainment", GOLD))
        grid.add_widget(col1); grid.add_widget(col2); content.add_widget(grid)
        content.add_widget(section_label("Moods", color=BLUE))
        for d, entry in sorted(data["notes"].items(), reverse=True):
            if in_range(d):
                row = Card(orientation="horizontal", height=dp(45), padding=dp(12))
                row.add_widget(make_label(d, fs=dp(13), h=dp(30)))
                row.add_widget(make_label(entry["mood"], fs=dp(13), color=BLUE, bold=True, h=dp(30)))
                content.add_widget(row)
        scroll.add_widget(content); root.add_widget(scroll); root.add_widget(bottom_nav("reports")); self.add_widget(root)

    def set_mode(self, m, *args):
        ReportsScreen.mode = m
        self.on_pre_enter()

class MoreScreen(SafeScreen):
    def _build(self):
        self.clear_widgets(); root = BoxLayout(orientation="vertical")
        root.add_widget(header("More Options", c1=PURPLE, c2=(0.59,0.42,0.77,1)))
        scroll = ScrollView(); content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(12)); content.bind(minimum_height=content.setter("height"))
        for label, s, c in [("Exam Days", "exams", PINK), ("Projects", "projects", BLUE), ("Daily Note", "checkin", GOLD), ("Namaz & Quran", "namaz", ORANGE)]:
            btn = make_button(label, h=dp(65), bg=c, fs=dp(17))
            btn.bind(on_release=partial(go_screen, s))
            content.add_widget(btn)
        dm = "Light Mode" if data.get("dark_mode") else "Dark Mode"
        dark_btn = make_button(dm, h=dp(65), bg=(0.4,0.4,0.4,1), fs=dp(17))
        dark_btn.bind(on_release=self.toggle_dark)
        content.add_widget(dark_btn)
        scroll.add_widget(content); root.add_widget(scroll); root.add_widget(bottom_nav("more")); self.add_widget(root)
    def toggle_dark(self, inst):
        data["dark_mode"] = not data.get("dark_mode", False)
        save_data(); Window.clearcolor = theme()["bg"]; self.on_pre_enter()

class ExamsScreen(SafeScreen):
    def _build(self):
        self.clear_widgets(); t = theme()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("Exam Days", back_to="more", c1=PINK))
        scroll = ScrollView(); content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10)); content.bind(minimum_height=content.setter("height"))
        content.add_widget(make_label("Subject:", h=dp(25), color=PINK, bold=True))
        self.sub = TextInput(size_hint_y=None, height=dp(45)); content.add_widget(self.sub)
        content.add_widget(make_label("Date (YYYY-MM-DD):", h=dp(25), color=PINK, bold=True))
        self.dt = TextInput(size_hint_y=None, height=dp(45)); content.add_widget(self.dt)
        add_btn = make_button("+ ADD EXAM", h=dp(50), bg=PINK)
        add_btn.bind(on_release=self.add_exam)
        content.add_widget(add_btn)
        today = date.today()
        for exam in data["exams"]:
            try:
                dl = (date.fromisoformat(exam["date"]) - today).days
                info = f"in {dl} days" if dl > 0 else ("TODAY!" if dl == 0 else "passed")
            except ValueError: info = "invalid date"
            card = Card(orientation="vertical", height=dp(70), padding=dp(12))
            card.add_widget(make_label(exam["subject"], fs=dp(15), bold=True, h=dp(25)))
            card.add_widget(make_label(info, fs=dp(12), color=PINK, h=dp(20)))
            content.add_widget(card)
        scroll.add_widget(content); root.add_widget(scroll); self.add_widget(root)
    def add_exam(self, inst):
        if not self.sub.text or not self.dt.text: show_popup("Error", "Enter subject and date."); return
        data["exams"].append({"subject": self.sub.text, "date": self.dt.text}); save_data(); self.on_pre_enter()

class ProjectsScreen(SafeScreen):
    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("Projects", back_to="more", c1=BLUE))
        scroll = ScrollView(); content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10)); content.bind(minimum_height=content.setter("height"))
        content.add_widget(make_label("Title:", h=dp(25), color=BLUE, bold=True))
        self.tit = TextInput(size_hint_y=None, height=dp(45)); content.add_widget(self.tit)
        content.add_widget(make_label("End Date (YYYY-MM-DD):", h=dp(25), color=BLUE, bold=True))
        self.edt = TextInput(size_hint_y=None, height=dp(45)); content.add_widget(self.edt)
        add_btn = make_button("+ ADD PROJECT", h=dp(50), bg=BLUE)
        add_btn.bind(on_release=self.add_project)
        content.add_widget(add_btn)
        for i, p in enumerate(data["projects"]):
            card = Card(orientation="vertical", height=dp(90), padding=dp(12), spacing=dp(6))
            card.add_widget(make_label(p["title"], fs=dp(15), bold=True, h=dp(25)))
            row = BoxLayout(size_hint_y=None, height=dp(35))
            status_text = "Completed" if p["completed"] else "In Progress"
            row.add_widget(make_label(status_text, fs=dp(12), color=TEAL if p["completed"] else PINK, h=dp(35)))
            if not p["completed"]:
                b = make_button("Complete", h=dp(35), bg=ORANGE, fs=dp(11))
                b.bind(on_release=partial(self.complete_project, i))
                row.add_widget(b)
            card.add_widget(row); content.add_widget(card)
        scroll.add_widget(content); root.add_widget(scroll); self.add_widget(root)
    def add_project(self, inst):
        if not self.tit.text or not self.edt.text: show_popup("Error", "Enter title and end date."); return
        data["projects"].append({"title": self.tit.text, "start": str(date.today()), "end": self.edt.text, "completed": False}); save_data(); self.on_pre_enter()
    def complete_project(self, idx, *args):
        data["projects"][idx]["completed"] = True; save_data(); self.on_pre_enter()

class CheckinScreen(SafeScreen):
    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("Daily Note", back_to="more", c1=GOLD))
        scroll = ScrollView(); content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10)); content.bind(minimum_height=content.setter("height"))
        content.add_widget(make_label("How do you feel today?", fs=dp(16), bold=True, h=dp(35)))
        self.sel_mood = "Happy"
        for m in ["Happy", "Normal", "Tired/Low", "Frustrated", "Sleepy"]:
            btn = make_button(m, h=dp(48), bg=GOLD if m=="Happy" else GRAY)
            btn.bind(on_release=partial(self.select_mood, m))
            content.add_widget(btn)
        content.add_widget(make_label("Write anything about your day:", h=dp(25), color=GOLD, bold=True))
        self.note = TextInput(size_hint_y=None, height=dp(120), multiline=True); content.add_widget(self.note)
        save_btn = make_button("SAVE CHECK-IN", h=dp(55), bg=GOLD)
        save_btn.bind(on_release=self.save)
        content.add_widget(save_btn)
        scroll.add_widget(content); root.add_widget(scroll); self.add_widget(root)
    def select_mood(self, mm, *args):
        self.sel_mood = mm; self.on_pre_enter()
    def save(self, inst):
        today = str(date.today())
        data["notes"][today] = {"mood": self.sel_mood, "note": self.note.text.strip()}; save_data(); show_popup("Saved", "Check-in saved!")

class NamazScreen(SafeScreen):
    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("Namaz & Quran", back_to="more", c1=ORANGE, c2=GOLD))
        scroll = ScrollView(); content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10)); content.bind(minimum_height=content.setter("height"))
        today = str(date.today())
        times = get_today_namaz_times()
        if today not in data["namaz_log"]: data["namaz_log"][today] = []
        for p in times:
            done = p in data["namaz_log"][today]
            row = Card(orientation="horizontal", height=dp(70), padding=dp(12), spacing=dp(12))
            check = Button(text="OK" if done else "", size_hint_x=None, width=dp(40), height=dp(40), background_normal="", background_color=(0.15,0.6,0.3,1) if done else GRAY, color=WHITE, font_size=dp(12), bold=True)
            check.bind(on_release=partial(self.toggle_namaz, p))
            row.add_widget(check)
            col = BoxLayout(orientation="vertical")
            col.add_widget(make_label(p, fs=dp(15), bold=True, h=dp(25)))
            col.add_widget(make_label(times[p], fs=dp(12), color=theme()["muted"], h=dp(20)))
            row.add_widget(col); content.add_widget(row)
        q_done = today in data["quran_log"]
        qrow = Card(orientation="horizontal", height=dp(70), padding=dp(12), spacing=dp(12))
        qcheck = Button(text="OK" if q_done else "", size_hint_x=None, width=dp(40), height=dp(40), background_normal="", background_color=(0.15,0.6,0.3,1) if q_done else GRAY, color=WHITE, font_size=dp(12), bold=True)
        qcheck.bind(on_release=self.toggle_quran)
        qrow.add_widget(qcheck)
        qrow.add_widget(make_label("Quran Recitation", fs=dp(15), bold=True))
        content.add_widget(qrow)
        scroll.add_widget(content); root.add_widget(scroll); self.add_widget(root)
    def toggle_namaz(self, p, *args):
        today = str(date.today())
        if p not in data["namaz_log"][today]: data["namaz_log"][today].append(p); add_points(15)
        else: data["namaz_log"][today].remove(p)
        save_data(); self.on_pre_enter()
    def toggle_quran(self, inst):
        today = str(date.today())
        if today not in data["quran_log"]: data["quran_log"].append(today); add_points(15)
        else: data["quran_log"].remove(today)
        save_data(); self.on_pre_enter()

class RoutineApp(App):
    def build(self):
        global sm, DATA_FILE, data
        DATA_FILE = os.path.join(self.user_data_dir, "routine_data.json")
        data = load_data()
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
    def on_stop(self): save_data()

if __name__ == "__main__": RoutineApp().run()
