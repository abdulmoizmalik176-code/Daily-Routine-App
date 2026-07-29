import json
import os
import copy
from datetime import date, datetime, timedelta
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
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle
from kivy.metrics import dp
import traceback

# ================= DATA FILE =================
DATA_FILE = "routine_data.json"

# ================= COLORS & THEME =================
LIGHT = {
    "bg": (0.96, 0.95, 0.98, 1),
    "card": (1, 1, 1, 1),
    "text": (0.15, 0.12, 0.22, 1),
    "muted": (0.52, 0.48, 0.62, 1)
}
DARK = {
    "bg": (0.11, 0.10, 0.15, 1),
    "card": (0.17, 0.15, 0.23, 1),
    "text": (0.94, 0.92, 0.98, 1),
    "muted": (0.65, 0.61, 0.76, 1)
}

# Accent Palette (Matching Mockup Image)
INDIGO = (0.28, 0.18, 0.53, 1)
PURPLE_PRIMARY = (0.40, 0.31, 0.64, 1)
PURPLE_LIGHT = (0.82, 0.74, 0.98, 1)
ACCENT_BG = (0.23, 0.14, 0.45, 1)

ORANGE = (0.91, 0.35, 0.05, 1)
GOLD = (0.97, 0.66, 0.23, 1)
TEAL = (0.18, 0.55, 0.47, 1)
PURPLE = (0.47, 0.31, 0.66, 1)
PINK = (0.78, 0.27, 0.36, 1)
BLUE = (0.18, 0.43, 0.63, 1)
WHITE = (1, 1, 1, 1)
GRAY = (0.88, 0.86, 0.92, 1)
GREEN_CHECK = (0.15, 0.65, 0.35, 1)

def theme(): return DARK if data.get("dark_mode") else LIGHT

DATA_DEFAULT = {
    "tasks": [
        {"name": "Study Python", "time": "10:00 AM", "priority": "High", "recurring": False, "note": "Learn Kivy UI", "done_dates": [], "progress": 0, "date_added": str(date.today())},
        {"name": "Read English", "time": "11:00 AM", "priority": "Medium", "recurring": False, "note": "Chapter 4", "done_dates": [], "progress": 0, "date_added": str(date.today())},
        {"name": "Exercise", "time": "05:00 PM", "priority": "Low", "recurring": True, "note": "30 mins cardio", "done_dates": [], "progress": 0, "date_added": str(date.today())},
        {"name": "Learn Quran", "time": "08:00 PM", "priority": "High", "recurring": True, "note": "Surah Yaseen", "done_dates": [], "progress": 0, "date_added": str(date.today())}
    ],
    "habits": [
        {"name": "🕌 Namaz", "color": [0.91, 0.35, 0.05, 1], "days": [True]*7, "log": []},
        {"name": "📖 Quran", "color": [0.47, 0.31, 0.66, 1], "days": [True]*7, "log": []},
        {"name": "💧 Water", "color": [0.18, 0.43, 0.63, 1], "days": [True]*7, "log": []},
        {"name": "🏃 Exercise", "color": [0.18, 0.55, 0.47, 1], "days": [True]*7, "log": []}
    ],
    "namaz_log": {},
    "quran_log": [],
    "entertainment_log": [],
    "points": 320,
    "level": 3,
    "badges": ["Level 3 Reached"],
    "exams": [
        {"subject": "Math", "date": "2026-05-23"},
        {"subject": "English", "date": "2026-05-26"},
        {"subject": "Physics", "date": str(date.today())}
    ],
    "projects": [
        {"title": "Science Fair", "start": str(date.today()), "end": "2026-05-30", "completed": False},
        {"title": "Mobile App", "start": str(date.today()), "end": "2026-06-15", "completed": False}
    ],
    "notes": {},
    "points_awarded_log": {},
    "dark_mode": False
}

def load_data():
    if DATA_FILE and os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                d = json.load(f)
                for k, v in DATA_DEFAULT.items():
                    if k not in d: d[k] = v
                return d
        except (json.JSONDecodeError, OSError):
            return copy.deepcopy(DATA_DEFAULT)
    return copy.deepcopy(DATA_DEFAULT)

def save_data():
    if not DATA_FILE: return
    try:
        dir_path = os.path.dirname(DATA_FILE)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
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

def parse_flexible_date(dt_str):
    if not dt_str: return None
    dt_str = str(dt_str).strip()
    for fmt in ("%Y-%m-%d", "%m-%d", "%d-%m", "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            parsed = datetime.strptime(dt_str, fmt).date()
            if fmt in ("%m-%d", "%d-%m"):
                parsed = parsed.replace(year=date.today().year)
            return parsed
        except ValueError:
            pass
    return None

def get_today_namaz_times(): return NAMAZ_TIMES[date.today().month]

def show_popup(title, message, on_close=None):
    popup_layout = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
    with popup_layout.canvas.before:
        Color(0.18, 0.14, 0.25, 1)
        rect = RoundedRectangle(radius=[dp(14)])
    popup_layout.bind(pos=lambda inst, val: setattr(rect, "pos", inst.pos),
                      size=lambda inst, val: setattr(rect, "size", inst.size))

    msg_label = Label(text=message, color=(1, 1, 1, 1), font_size=dp(15), halign="center", valign="middle")
    msg_label.bind(size=lambda inst, val: setattr(msg_label, "text_size", val))
    popup_layout.add_widget(msg_label)

    close_btn = Button(text="OK", size_hint_y=None, height=dp(42), background_normal="", background_color=PURPLE_PRIMARY, color=WHITE, bold=True)
    popup_layout.add_widget(close_btn)

    popup = Popup(title=title, content=popup_layout, size_hint=(0.85, 0.35),
                  title_color=GOLD, title_size=dp(18), auto_dismiss=False)
    close_btn.bind(on_release=lambda *a: (popup.dismiss(), on_close() if on_close else None))
    popup.open()

def award_points_once(item_id, amount):
    today = str(date.today())
    if today not in data.get("points_awarded_log", {}):
        data.setdefault("points_awarded_log", {})[today] = []

    if item_id not in data["points_awarded_log"][today]:
        data["points_awarded_log"][today].append(item_id)
        data["points"] = data.get("points", 0) + amount
        check_level_up()
        save_data()

def revoke_points_once(item_id, amount):
    today = str(date.today())
    if today in data.get("points_awarded_log", {}) and item_id in data["points_awarded_log"][today]:
        data["points_awarded_log"][today].remove(item_id)
        data["points"] = max(0, data.get("points", 0) - amount)
        save_data()

def check_level_up():
    new_level = (data.get("points", 0) // 100) + 1
    if new_level > data.get("level", 1):
        data["level"] = new_level
        data.setdefault("badges", []).append(f"Level {data['level']} Reached")
        show_popup("Level Up! 🏆", f"Congratulations! You reached Level {data['level']}!")

def calculate_real_streak():
    today = date.today()
    streak = 0
    curr_date = today

    active_days = set()
    for tk in data.get("tasks", []):
        active_days.update(tk.get("done_dates", []))
    for h in data.get("habits", []):
        active_days.update(h.get("log", []))
    for d, namazs in data.get("namaz_log", {}).items():
        if namazs: active_days.add(d)
    active_days.update(data.get("quran_log", []))

    while True:
        d_str = str(curr_date)
        if d_str in active_days:
            streak += 1
            curr_date -= timedelta(days=1)
        else:
            if curr_date == today:
                curr_date -= timedelta(days=1)
                continue
            break
    return streak

def check_perfect_day():
    today = str(date.today())
    if not data.get("tasks"): return
    if all(today in t.get("done_dates", []) for t in data["tasks"]):
        badge = f"Perfect Day - {today}"
        if badge not in data.setdefault("badges", []):
            data["badges"].append(badge)
            award_points_once(f"perfect_day_{today}", 20)
            show_popup("Perfect Day! ✨", "+20 bonus points earned!")

class Card(BoxLayout):
    def __init__(self, bg=None, radius=dp(18), **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.padding, self.spacing = dp(12), dp(8)
        self._bg_color = bg if bg else theme()["card"]
        with self.canvas.before:
            Color(*self._bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
        self.bind(pos=self._update, size=self._update)
    def _update(self, *args): self._rect.pos, self._rect.size = self.pos, self.size

class FAB(Button):
    def __init__(self, target, **kwargs):
        super().__init__(**kwargs)
        self.size_hint, self.size = (None, None), (dp(56), dp(56))
        self.background_normal, self.background_color = '', (0,0,0,0)
        self.text, self.font_size, self.color = '+', dp(30), WHITE
        self.bind(on_release=partial(go_screen, target))
        with self.canvas.before:
            Color(*PURPLE_PRIMARY)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(28)])
        self.bind(pos=self._update, size=self._update)
    def _update(self, *args): self.rect.pos, self.rect.size = self.pos, self.size

def add_fab(root, target):
    fab = FAB(target)
    def reposition(*a): fab.pos = (root.width - fab.width - dp(20), dp(85))
    root.bind(size=reposition, pos=reposition)
    root.add_widget(fab)
    reposition()
    return fab

class Ring(Widget):
    def __init__(self, pct=0.78, color=TEAL, **kwargs):
        super().__init__(**kwargs)
        self.pct, self.ring_color = pct, color
        self.bind(pos=self._draw, size=self._draw); self._draw()
    def _draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            cx, cy = self.center_x, self.center_y
            r = max(1, min(self.width, self.height)/2 - dp(10))
            Color(0.85, 0.82, 0.92, 1) if not data.get("dark_mode") else Color(0.25, 0.22, 0.32, 1)
            Line(circle=(cx, cy, r), width=dp(9))
            Color(*self.ring_color)
            Line(circle=(cx, cy, r, 90, 90 - 360*self.pct if self.pct <= 1 else -270), width=dp(9), cap="round")

class BarChartWidget(Widget):
    """Draws weekly Monday to Sunday progress bar chart matching Reports mockup."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(130)
        self.bind(pos=self._draw, size=self._draw); self._draw()

    def _draw(self, *args):
        self.canvas.clear()
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        week_dates = [monday + timedelta(days=i) for i in range(7)]

        values = []
        for d in week_dates:
            d_str = str(d)
            count = sum(1 for tk in data.get("tasks", []) if d_str in tk.get("done_dates", []))
            count += len(data.get("namaz_log", {}).get(d_str, []))
            if d_str in data.get("quran_log", []): count += 1
            values.append(count)

        max_v = max(max(values) if values else 1, 6)

        with self.canvas:
            Color(0.7, 0.65, 0.8, 0.4)
            Line(points=[self.x + dp(20), self.y + dp(20), self.x + self.width - dp(20), self.y + dp(20)], width=dp(1.5))

            bar_width = dp(16)
            spacing = (self.width - dp(40) - (7 * bar_width)) / 6.0

            for i, (dn, val) in enumerate(zip(DAY_NAMES, values)):
                bx = self.x + dp(20) + i * (bar_width + spacing)
                bh = max(dp(8), (val / max_v) * (self.height - dp(45)))
                by = self.y + dp(20)

                Color(*PURPLE_PRIMARY if i == today.weekday() else PURPLE_LIGHT)
                RoundedRectangle(pos=(bx, by), size=(bar_width, bh), radius=[dp(4), dp(4), 0, 0])

def make_button(text, h=dp(50), bg=PURPLE_PRIMARY, fg=WHITE, fs=dp(15)):
    return Button(text=text, size_hint_y=None, height=h, background_normal="", background_color=bg, color=fg, font_size=fs, bold=True)

def make_label(text, h=dp(30), fs=dp(14), color=None, bold=False, halign="left", valign="middle", **kwargs):
    t = theme()
    actual_h = kwargs.get('height', h)
    actual_fs = kwargs.get('font_size', fs)
    lbl = Label(text=text, size_hint_y=None, height=actual_h, font_size=actual_fs, color=color if color else t["text"], bold=bold, halign=halign, valign=valign)
    lbl.bind(size=lambda inst, val: setattr(lbl, "text_size", val))
    return lbl

def section_label(text, color=PURPLE_PRIMARY):
    return make_label(text.upper(), h=dp(32), fs=dp(13), color=color, bold=True)

def header(title, back_to=None, c1=PURPLE_PRIMARY, c2=INDIGO):
    box = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(120), padding=[dp(20), dp(10), dp(20), dp(10)])
    with box.canvas.before:
        Color(*c1); box._rect = Rectangle(pos=box.pos, size=box.size)
    box.bind(pos=lambda *a: setattr(box._rect, "pos", box.pos), size=lambda *a: setattr(box._rect, "size", box.size))

    top_row = BoxLayout(size_hint_y=None, height=dp(25))
    today_str = date.today().strftime("%A, %b %d, %Y")
    date_lbl = Label(text=today_str, font_size=dp(12), color=(1,1,1,0.85), halign="left", valign="center")
    date_lbl.bind(size=lambda inst, val: setattr(date_lbl, "text_size", val))
    top_row.add_widget(date_lbl)

    if back_to:
        b = Button(text="< Back", size_hint_x=None, width=dp(70), background_normal="", background_color=(0,0,0,0), color=WHITE, font_size=dp(13), bold=True)
        b.bind(on_release=partial(go_screen, back_to))
        top_row.add_widget(b)

    box.add_widget(top_row)
    box.add_widget(Label(text=title, font_size=dp(22), bold=True, color=WHITE, halign="left", valign="center"))
    return box

def bottom_nav(active):
    nav = BoxLayout(size_hint_y=None, height=dp(68), padding=dp(4), spacing=dp(4))
    t = theme()
    with nav.canvas.before:
        Color(*t["bg"]); nav._rect = Rectangle(pos=nav.pos, size=nav.size)
    nav.bind(pos=lambda *a: setattr(nav._rect, "pos", nav.pos), size=lambda *a: setattr(nav._rect, "size", nav.size))
    items = [("🏠 Home", "home"), ("🔥 Habits", "habits"), ("✅ Tasks", "tasks"), ("📊 Reports", "reports"), ("⋯ More", "more")]
    for label, name in items:
        c = PURPLE_PRIMARY if name == active else t["muted"]
        btn = Button(text=label, background_normal="", background_color=(0,0,0,0), color=c, font_size=dp(12), bold=(name==active))
        btn.bind(on_release=partial(go_screen, name))
        nav.add_widget(btn)
    return nav

class SafeScreen(Screen):
    def on_pre_enter(self):
        try:
            self._build()
        except Exception:
            self.clear_widgets()
            box = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(10))
            box.add_widget(Label(text="Something went wrong on this screen:", color=(1, 1, 1, 1), font_size=dp(18), bold=True, size_hint_y=None, height=dp(50)))
            err_scroll = ScrollView()
            err_label = Label(text=traceback.format_exc(), color=(1, 0.6, 0.6, 1), font_size=dp(12), size_hint_y=None, halign="left", valign="top")
            err_label.bind(texture_size=lambda inst, val: setattr(err_label, "height", val[1]))
            err_label.bind(width=lambda inst, val: err_label.setter("text_size")(err_label, (val, None)))
            err_scroll.add_widget(err_label)
            box.add_widget(err_scroll)
            back_btn = make_button("Go to Home", bg=PURPLE_PRIMARY)
            back_btn.bind(on_release=partial(go_screen, "home"))
            box.add_widget(back_btn)
            self.add_widget(box)

sm = None
def go_screen(name, *args):
    if sm: sm.current = name

def get_today_progress():
    today, wd = str(date.today()), date.today().weekday()
    total, done = 0, 0
    for t in data.get("tasks", []):
        total += 1
        if today in t.get("done_dates", []): done += 1
    for h in data.get("habits", []):
        if h.get("days", [True]*7)[wd]:
            total += 1
            if today in h.get("log", []): done += 1
    for p in get_today_namaz_times():
        total += 1
        if p in data.get("namaz_log", {}).get(today, []): done += 1
    total += 1
    if today in data.get("quran_log", []): done += 1
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
        box.add_widget(header("👋 Assalam-o-Alaikum!", c1=PURPLE_PRIMARY, c2=INDIGO))
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(12))
        content.bind(minimum_height=content.setter("height"))

        # 1. Main Dashboard Card (Progress Ring + Stats)
        pct = get_today_progress()
        card = Card(orientation="horizontal", height=dp(160), bg=ACCENT_BG)
        ring = Ring(pct=pct, color=TEAL, size_hint=(None, None), size=(dp(120), dp(120)))
        ring_wrap = RelativeLayout(size_hint_x=None, width=dp(130))
        ring_wrap.add_widget(ring)
        pct_lbl = Label(text=f"{int(pct*100)}%", font_size=dp(20), bold=True, color=WHITE)
        ring_wrap.add_widget(pct_lbl)
        card.add_widget(ring_wrap)

        stats = BoxLayout(orientation="vertical", spacing=dp(4))
        real_streak = calculate_real_streak()
        stats.add_widget(make_label(f"🔥 Streak: {real_streak} Days", fs=dp(15), color=GOLD, bold=True))
        stats.add_widget(make_label(f"⭐ Points: {data.get('points', 0)}", fs=dp(15), color=PURPLE_LIGHT, bold=True))
        stats.add_widget(make_label(f"🏆 Level: {data.get('level', 1)}", fs=dp(15), color=GOLD, bold=True))
        card.add_widget(stats)
        content.add_widget(card)

        # 2. Today's Focus Quick Overview Grid (3 Mini Cards matching Mockup Image)
        content.add_widget(section_label("Today's Focus Summary"))
        grid_row = BoxLayout(size_hint_y=None, height=dp(85), spacing=dp(8))
        
        today_str = str(date.today())
        tasks_done_cnt = sum(1 for tk in data.get("tasks", []) if today_str in tk.get("done_dates", []))
        tasks_tot_cnt = max(1, len(data.get("tasks", [])))
        
        namaz_done_cnt = len(data.get("namaz_log", {}).get(today_str, []))
        quran_done_cnt = 1 if today_str in data.get("quran_log", []) else 0

        def mini_card(icon, title, val, color):
            c = Card(orientation="vertical", bg=color, height=dp(85), padding=dp(8))
            c.add_widget(Label(text=f"{icon} {title}", font_size=dp(12), bold=True, color=WHITE))
            c.add_widget(Label(text=val, font_size=dp(14), bold=True, color=WHITE))
            return c

        grid_row.add_widget(mini_card("✅", "Tasks", f"{tasks_done_cnt}/{tasks_tot_cnt} Done", TEAL))
        grid_row.add_widget(mini_card("🕌", "Namaz", f"{namaz_done_cnt}/5 Done", PINK))
        grid_row.add_widget(mini_card("📖", "Quran", f"{quran_done_cnt}/1 Done", PURPLE_PRIMARY))
        content.add_widget(grid_row)

        # 3. Focus Timer Card
        content.add_widget(section_label("⏱️ Pomodoro Focus Timer"))
        pcard = Card(orientation="horizontal", height=dp(75))
        mins, secs = divmod(self.time_left, 60)
        timer_text = f"{mins:02d}:{secs:02d}"
        btn_text = "Stop" if self.timer_running else "Start Focus"
        btn_color = (0.8, 0.1, 0.1, 1) if self.timer_running else PURPLE_PRIMARY

        self.timer_lbl = Label(text=timer_text, font_size=dp(30), color=PURPLE_PRIMARY, bold=True, size_hint_x=None, width=dp(110))
        pcard.add_widget(self.timer_lbl)
        self.pom_btn = make_button(btn_text, h=dp(48), bg=btn_color)
        self.pom_btn.bind(on_release=self.toggle_timer)
        pcard.add_widget(self.pom_btn)
        content.add_widget(pcard)

        # 4. Quick Actions Row
        content.add_widget(section_label("⚡ Quick Actions"))
        qa_row = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(8))
        for qa_label, qa_scr, qa_c in [("Tasks", "tasks", TEAL), ("Habits", "habits", PINK), ("Reports", "reports", PURPLE_PRIMARY), ("More", "more", GOLD)]:
            btn = make_button(qa_label, h=dp(50), bg=qa_c, fs=dp(13))
            btn.bind(on_release=partial(go_screen, qa_scr))
            qa_row.add_widget(btn)
        content.add_widget(qa_row)

        # 5. Today's Task List
        content.add_widget(section_label("📋 Today's Focus List"))
        for i, tk in enumerate(data.get("tasks", [])):
            if i >= 5: break
            done = today_str in tk.get("done_dates", [])
            row = Card(orientation="horizontal", height=dp(70), padding=dp(10))
            check = Button(text="✓" if done else "", size_hint_x=None, width=dp(38), height=dp(38),
                           background_normal="", background_color=GREEN_CHECK if done else GRAY,
                           color=WHITE, font_size=dp(16), bold=True, pos_hint={"center_y": 0.5})
            check.bind(on_release=partial(self.toggle_task, i))
            row.add_widget(check)

            col = BoxLayout(orientation="vertical")
            col.add_widget(make_label(tk.get("name", "Task"), fs=dp(15), bold=True, h=dp(24)))
            col.add_widget(make_label(f"{tk.get('time', '')} • Progress: {tk.get('progress', 0)}%", fs=dp(12), color=t["muted"], h=dp(18)))

            detail_btn = Button(text="Details", size_hint_x=None, width=dp(60), height=dp(34),
                                background_normal="", background_color=PURPLE_PRIMARY, color=WHITE, font_size=dp(11), bold=True, pos_hint={"center_y": 0.5})
            detail_btn.bind(on_release=partial(show_task_details, i, self.on_pre_enter))

            row.add_widget(col)
            row.add_widget(detail_btn)
            content.add_widget(row)

        scroll.add_widget(content)
        box.add_widget(scroll)
        box.add_widget(bottom_nav("home"))
        root.add_widget(box)
        add_fab(root, "add_task")
        self.add_widget(root)

    def toggle_timer(self, inst):
        if self.timer_running:
            self.timer_running = False
            self.pom_btn.text = "Start Focus"; self.pom_btn.background_color = PURPLE_PRIMARY
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
            self.pom_btn.text = "Start Focus"; self.pom_btn.background_color = PURPLE_PRIMARY
            show_popup("⏱️ Time's Up!", "Great focus! Take a 5 min break.")
            self.time_left = 1500; self.timer_lbl.text = "25:00"

    def toggle_task(self, index, *args):
        today = str(date.today())
        tk = data["tasks"][index]
        if "done_dates" not in tk: tk["done_dates"] = []

        item_key = f"task_{tk.get('name', index)}_{today}"
        if today not in tk["done_dates"]:
            tk["done_dates"].append(today)
            tk["progress"] = 100
            award_points_once(item_key, 10)
            check_perfect_day()
        else:
            tk["done_dates"].remove(today)
            tk["progress"] = 0
            revoke_points_once(item_key, 10)

        save_data(); self.on_pre_enter()

def show_task_details(index, refresh_callback=None, *args):
    tk = data["tasks"][index]
    today = str(date.today())

    popup_content = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))
    with popup_content.canvas.before:
        Color(0.18, 0.14, 0.25, 1)
        rect = RoundedRectangle(radius=[dp(15)])
    popup_content.bind(pos=lambda inst, val: setattr(rect, "pos", inst.pos),
                       size=lambda inst, val: setattr(rect, "size", inst.size))

    popup_content.add_widget(Label(text=f"Task: {tk.get('name', '')}", font_size=dp(18), bold=True, color=GOLD, size_hint_y=None, height=dp(30)))
    popup_content.add_widget(Label(text=f"Time: {tk.get('time', '')} | Priority: {tk.get('priority', 'Medium')}", font_size=dp(13), color=WHITE, size_hint_y=None, height=dp(25)))
    popup_content.add_widget(Label(text=f"Recurring: {'Yes' if tk.get('recurring') else 'No'} | Added: {tk.get('date_added', today)}", font_size=dp(12), color=GRAY, size_hint_y=None, height=dp(20)))

    note_text = tk.get("note", "").strip() or "No note provided for this task."
    popup_content.add_widget(Label(text="Note:", font_size=dp(13), bold=True, color=TEAL, size_hint_y=None, height=dp(20)))
    
    note_box = Label(text=note_text, font_size=dp(12), color=WHITE, size_hint_y=None, height=dp(45), halign="left", valign="top")
    note_box.bind(size=lambda inst, val: setattr(note_box, "text_size", (val[0], None)))
    popup_content.add_widget(note_box)

    curr_prog = tk.get("progress", 100 if today in tk.get("done_dates", []) else 0)
    prog_label = Label(text=f"Progress: {curr_prog}%", font_size=dp(14), bold=True, color=PINK, size_hint_y=None, height=dp(25))
    popup_content.add_widget(prog_label)

    slider = Slider(min=0, max=100, value=curr_prog, step=5, size_hint_y=None, height=dp(35))
    def on_slider_change(inst, val):
        prog_label.text = f"Progress: {int(val)}%"
    slider.bind(value=on_slider_change)
    popup_content.add_widget(slider)

    btn_row = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
    cancel_btn = Button(text="Cancel", background_normal="", background_color=GRAY, color=WHITE, bold=True)
    save_btn = Button(text="Save Changes", background_normal="", background_color=PURPLE_PRIMARY, color=WHITE, bold=True)
    btn_row.add_widget(cancel_btn)
    btn_row.add_widget(save_btn)
    popup_content.add_widget(btn_row)

    popup = Popup(title="Task Details", content=popup_content, size_hint=(0.9, 0.65), auto_dismiss=True)
    cancel_btn.bind(on_release=lambda *a: popup.dismiss())

    def save_details(*a):
        new_prog = int(slider.value)
        tk["progress"] = new_prog
        if "done_dates" not in tk: tk["done_dates"] = []

        item_key = f"task_{tk.get('name', index)}_{today}"
        if new_prog == 100:
            if today not in tk["done_dates"]:
                tk["done_dates"].append(today)
                award_points_once(item_key, 10)
        else:
            if today in tk["done_dates"]:
                tk["done_dates"].remove(today)
                revoke_points_once(item_key, 10)

        save_data()
        popup.dismiss()
        if refresh_callback: refresh_callback()

    save_btn.bind(on_release=save_details)
    popup.open()

class TasksScreen(SafeScreen):
    filter_mode = "All"

    def _build(self):
        save_data()
        self.clear_widgets(); t = theme()
        root = RelativeLayout()
        with root.canvas.before:
            Color(*t["bg"]); root._rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(root._rect, "pos", root.pos), size=lambda *a: setattr(root._rect, "size", root.size))
        box = BoxLayout(orientation="vertical")
        box.add_widget(header("📋 My Tasks", c1=PURPLE_PRIMARY, c2=INDIGO))
        scroll = ScrollView(); content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10)); content.bind(minimum_height=content.setter("height"))

        # Task Filter Tabs (Matching Mockup Image)
        filter_row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        for mode in ["All", "Today", "Completed"]:
            is_sel = (self.filter_mode == mode)
            btn = make_button(mode, h=dp(40), bg=PURPLE_PRIMARY if is_sel else GRAY, fs=dp(13))
            btn.bind(on_release=partial(self.set_filter, mode))
            filter_row.add_widget(btn)
        content.add_widget(filter_row)

        add_btn = make_button("+ Add Task", h=dp(48), bg=PURPLE_PRIMARY)
        add_btn.bind(on_release=partial(go_screen, "add_task"))
        content.add_widget(add_btn)

        today = str(date.today())
        priority_colors = {"High": PINK, "Medium": GOLD, "Low": TEAL}

        for i, tk in enumerate(data.get("tasks", [])):
            done = today in tk.get("done_dates", [])
            
            # Apply Filter
            if self.filter_mode == "Today" and tk.get("date_added") != today: continue
            if self.filter_mode == "Completed" and not done: continue

            row = Card(orientation="horizontal", height=dp(75), padding=dp(10))
            check = Button(text="✓" if done else "", size_hint_x=None, width=dp(38), height=dp(38), background_normal="", background_color=GREEN_CHECK if done else GRAY, color=WHITE, font_size=dp(16), bold=True, pos_hint={"center_y":0.5})
            check.bind(on_release=partial(self.toggle_task, i))
            row.add_widget(check)

            col = BoxLayout(orientation="vertical")
            col.add_widget(make_label(tk.get("name", "Task"), fs=dp(15), bold=True, h=dp(24)))
            col.add_widget(make_label(f"{tk.get('time', '')} • {tk.get('note', '')[:12]}...", fs=dp(12), color=t["muted"], h=dp(18)))
            row.add_widget(col)

            pr = tk.get("priority", "Medium")
            pr_lbl = Label(text=pr, font_size=dp(11), color=WHITE, bold=True, size_hint_x=None, width=dp(60), halign="center", valign="middle")
            with pr_lbl.canvas.before:
                Color(*priority_colors.get(pr, GOLD))
                r = RoundedRectangle(pos=pr_lbl.pos, size=pr_lbl.size, radius=[dp(12)])
            pr_lbl.bind(pos=lambda inst, val, rr=r: setattr(rr, "pos", inst.pos), size=lambda inst, val, rr=r: setattr(rr, "size", inst.size))
            row.add_widget(pr_lbl)

            detail_btn = Button(text="View", size_hint_x=None, width=dp(50), height=dp(34),
                                background_normal="", background_color=PURPLE_PRIMARY, color=WHITE, font_size=dp(11), bold=True, pos_hint={"center_y":0.5})
            detail_btn.bind(on_release=partial(show_task_details, i, self.on_pre_enter))
            row.add_widget(detail_btn)

            content.add_widget(row)
        scroll.add_widget(content); box.add_widget(scroll); box.add_widget(bottom_nav("tasks")); root.add_widget(box); add_fab(root, "add_task"); self.add_widget(root)

    def set_filter(self, mode, *args):
        self.filter_mode = mode
        self.on_pre_enter()

    def toggle_task(self, idx, *args):
        today = str(date.today())
        tk = data["tasks"][idx]
        if "done_dates" not in tk: tk["done_dates"] = []

        item_key = f"task_{tk.get('name', idx)}_{today}"
        if today not in tk["done_dates"]:
            tk["done_dates"].append(today)
            tk["progress"] = 100
            award_points_once(item_key, 10)
            check_perfect_day()
        else:
            tk["done_dates"].remove(today)
            tk["progress"] = 0
            revoke_points_once(item_key, 10)

        save_data(); self.on_pre_enter()

class AddTaskScreen(SafeScreen):
    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("➕ Add Task", back_to="tasks", c1=PURPLE_PRIMARY))
        scroll = ScrollView(); content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10)); content.bind(minimum_height=content.setter("height"))
        content.add_widget(make_label("Task Name:", fs=dp(15), color=PURPLE_PRIMARY, bold=True))
        self.name_input = TextInput(size_hint_y=None, height=dp(45), font_size=dp(15)); content.add_widget(self.name_input)
        content.add_widget(make_label("Time:", fs=dp(15), color=PINK, bold=True))
        self.time_input = TextInput(size_hint_y=None, height=dp(45), font_size=dp(15)); content.add_widget(self.time_input)
        content.add_widget(section_label("Priority", color=PURPLE_PRIMARY))
        self.priority = "High"
        pr_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        self.priority_colors = {"High": PINK, "Medium": GOLD, "Low": TEAL}
        self.pr_buttons = {}
        for pr, c in self.priority_colors.items():
            b = make_button(pr, h=dp(45), bg=c if pr=="High" else GRAY, fs=dp(13))
            b.bind(on_release=partial(self.select_priority, pr))
            pr_row.add_widget(b)
            self.pr_buttons[pr] = b
        content.add_widget(pr_row)
        content.add_widget(make_label("Note (optional):", fs=dp(15), color=PURPLE_PRIMARY, bold=True))
        self.note_input = TextInput(size_hint_y=None, height=dp(45), font_size=dp(15)); content.add_widget(self.note_input)
        save_btn = make_button("+ ADD TASK", bg=PURPLE_PRIMARY, h=dp(52))
        save_btn.bind(on_release=self.save_task)
        content.add_widget(save_btn)
        scroll.add_widget(content); root.add_widget(scroll); self.add_widget(root)

    def select_priority(self, pr, *args):
        self.priority = pr
        for name, btn in self.pr_buttons.items():
            btn.background_color = self.priority_colors[name] if name == pr else GRAY

    def save_task(self, inst):
        n, t = self.name_input.text.strip(), self.time_input.text.strip()
        if not n or not t: show_popup("Error", "Enter name & time."); return
        data.setdefault("tasks", []).append({
            "name": n, "time": t, "priority": self.priority,
            "recurring": False, "note": self.note_input.text,
            "done_dates": [], "progress": 0, "date_added": str(date.today())
        })
        save_data()
        show_popup("Task Added", f"Task '{n}' saved!", on_close=lambda: go_screen("tasks"))

class HabitsScreen(SafeScreen):
    def _build(self):
        save_data()
        self.clear_widgets(); t = theme()
        root = RelativeLayout()
        with root.canvas.before:
            Color(*t["bg"]); root._rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(root._rect, "pos", root.pos), size=lambda *a: setattr(root._rect, "size", root.size))
        box = BoxLayout(orientation="vertical")
        box.add_widget(header("🔥 My Habits", c1=PURPLE_PRIMARY, c2=INDIGO))
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))

        add_btn = make_button("+ Add Habit", h=dp(48), bg=PURPLE_PRIMARY)
        add_btn.bind(on_release=partial(go_screen, "add_habit"))
        content.add_widget(add_btn)

        week = [str(date.today() - timedelta(days=i)) for i in range(6, -1, -1)]
        for idx, h in enumerate(data.get("habits", [])):
            color = tuple(h.get("color", PURPLE_PRIMARY))
            card = Card(orientation="vertical", height=dp(135))
            top = BoxLayout(size_hint_y=None, height=dp(30))
            top.add_widget(make_label(h.get("name", "Habit"), fs=dp(15), bold=True, h=dp(30)))
            streak = sum(1 for d in week if d in h.get("log", []))
            top.add_widget(make_label(f"{streak}/7", fs=dp(14), color=PURPLE_PRIMARY, bold=True, h=dp(30)))
            card.add_widget(top)

            # 7-Day Heatmap Dots (Matching Mockup Image)
            heat = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(8))
            for d in week:
                done = d in h.get("log", [])
                b = Button(text="", size_hint_y=None, height=dp(38), background_normal="",
                           background_color=color if done else GRAY)
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
        if "log" not in h: h["log"] = []
        item_key = f"habit_{h.get('name', idx)}_{day}"
        if day in h["log"]:
            h["log"].remove(day)
            if day == str(date.today()): revoke_points_once(item_key, 5)
        else:
            h["log"].append(day)
            if day == str(date.today()): award_points_once(item_key, 5)
        save_data(); self.on_pre_enter()

class AddHabitScreen(SafeScreen):
    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("➕ Add Habit", back_to="habits", c1=PURPLE_PRIMARY))
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))
        content.add_widget(make_label("Habit Name:", fs=dp(15), color=PURPLE_PRIMARY, bold=True))
        self.name_input = TextInput(size_hint_y=None, height=dp(45), font_size=dp(15))
        content.add_widget(self.name_input)
        content.add_widget(section_label("Repeat On", color=PURPLE_PRIMARY))
        self.sel_days = [True]*5 + [False]*2
        days_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        self.day_btns = []
        for i, dn in enumerate(DAY_NAMES):
            b = make_button(dn[:2], h=dp(45), bg=PURPLE_PRIMARY if self.sel_days[i] else GRAY, fs=dp(12))
            b.bind(on_release=partial(self.toggle_day, i))
            days_row.add_widget(b); self.day_btns.append(b)
        content.add_widget(days_row)
        content.add_widget(section_label("Color", color=PURPLE_PRIMARY))
        colors_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        self.sel_color = 0
        self.color_buttons = []
        for i, c in enumerate(HABIT_COLORS):
            b = make_button("SELECTED" if i == self.sel_color else "", h=dp(45), bg=c, fs=dp(9))
            b.bind(on_release=partial(self.select_color, i))
            colors_row.add_widget(b)
            self.color_buttons.append(b)
        content.add_widget(colors_row)
        save_btn = make_button("+ CREATE HABIT", bg=PURPLE_PRIMARY, h=dp(52))
        save_btn.bind(on_release=self.save_habit)
        content.add_widget(save_btn)
        scroll.add_widget(content); root.add_widget(scroll); self.add_widget(root)

    def toggle_day(self, idx, *args):
        self.sel_days[idx] = not self.sel_days[idx]
        self.day_btns[idx].background_color = PURPLE_PRIMARY if self.sel_days[idx] else GRAY

    def select_color(self, idx, *args):
        self.sel_color = idx
        for i, btn in enumerate(self.color_buttons):
            btn.text = "SELECTED" if i == idx else ""

    def save_habit(self, inst):
        n = self.name_input.text.strip()
        if not n: show_popup("Error", "Enter a habit name."); return
        data.setdefault("habits", []).append({"name": n, "color": list(HABIT_COLORS[self.sel_color]), "days": list(self.sel_days), "log": []})
        save_data()
        show_popup("Saved", f"Habit '{n}' created!", on_close=lambda: go_screen("habits"))

class ReportsScreen(SafeScreen):
    mode = "weekly"
    def _build(self):
        self.clear_widgets(); root = BoxLayout(orientation="vertical"); t = theme()
        root.add_widget(header("📊 Reports & History", c1=PURPLE_PRIMARY, c2=INDIGO))
        scroll = ScrollView(); content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10)); content.bind(minimum_height=content.setter("height"))
        today = date.today()
        dates = [str(today - timedelta(days=i)) for i in range(7)] if self.mode == "weekly" else None
        def in_range(d): return d in dates if dates else d.startswith(today.strftime("%Y-%m"))
        total_tasks = sum(1 for tk in data.get("tasks", []) for d in tk.get("done_dates", []) if in_range(d))
        namaz_count = sum(len(v) for d, v in data.get("namaz_log", {}).items() if in_range(d))
        quran_count = sum(1 for d in data.get("quran_log", []) if in_range(d))
        days_count = 7 if self.mode == "weekly" else today.day

        # Weekly / Monthly Toggle (Matching Mockup Image)
        toggle_row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        wb = make_button("Weekly", h=dp(40), bg=PURPLE_PRIMARY if self.mode=="weekly" else GRAY, fs=dp(13))
        mb = make_button("Monthly", h=dp(40), bg=PURPLE_PRIMARY if self.mode=="monthly" else GRAY, fs=dp(13))
        wb.bind(on_release=partial(self.set_mode, "weekly"))
        mb.bind(on_release=partial(self.set_mode, "monthly"))
        toggle_row.add_widget(wb); toggle_row.add_widget(mb)
        content.add_widget(toggle_row)

        # 4 Stats Tiles (Matching Mockup Image)
        grid = BoxLayout(size_hint_y=None, height=dp(190))
        col1, col2 = BoxLayout(orientation="vertical", spacing=dp(8)), BoxLayout(orientation="vertical", spacing=dp(8))
        def stat_tile(v, lbl, c):
            tile = Card(orientation="vertical", bg=c, height=dp(90), padding=dp(8))
            tile.add_widget(Label(text=v, font_size=dp(22), bold=True, color=WHITE))
            tile.add_widget(Label(text=lbl, font_size=dp(11), color=WHITE))
            return tile
        col1.add_widget(stat_tile(str(total_tasks), "Tasks Done", TEAL))
        col1.add_widget(stat_tile(f"{quran_count}/{days_count}", "Quran Days", PINK))
        col2.add_widget(stat_tile(f"{namaz_count}/{days_count*5}", "Namaz", PURPLE_PRIMARY))
        col2.add_widget(stat_tile(str(data.get("points", 0)), "Points", GOLD))
        grid.add_widget(col1); grid.add_widget(col2); content.add_widget(grid)

        # Weekly Progress Bar Chart
        content.add_widget(section_label("📈 Weekly Progress Chart", color=PURPLE_PRIMARY))
        chart_card = Card(orientation="vertical", height=dp(140), padding=dp(10))
        chart_card.add_widget(BarChartWidget())
        content.add_widget(chart_card)

        # Saved Daily Mood Notes History
        content.add_widget(section_label("Saved Daily Mood Notes History", color=PURPLE_PRIMARY))
        if not data.get("notes"):
            content.add_widget(make_label("No daily check-ins recorded yet.", fs=dp(13), color=GRAY))
        else:
            card_text_col = t["text"]
            for d, entry in sorted(data.get("notes", {}).items(), reverse=True):
                card = Card(orientation="vertical", height=dp(105), padding=dp(10), spacing=dp(4))
                top_line = BoxLayout(size_hint_y=None, height=dp(24))
                top_line.add_widget(make_label(f"Date: {d}", fs=dp(13), bold=True, color=card_text_col, h=dp(24)))
                top_line.add_widget(make_label(f"Mood: {entry.get('mood', 'Normal')}", fs=dp(13), color=GOLD, bold=True, h=dp(24)))
                card.add_widget(top_line)

                note_txt = entry.get('note', '').strip() or "(No written note)"
                note_lbl = Label(text=f"Note: {note_txt}", font_size=dp(12), color=card_text_col,
                                 size_hint_y=None, height=dp(45), halign="left", valign="top")
                note_lbl.bind(size=lambda inst, val: setattr(note_lbl, "text_size", (val[0], None)))
                card.add_widget(note_lbl)
                content.add_widget(card)

        scroll.add_widget(content); root.add_widget(scroll); root.add_widget(bottom_nav("reports")); self.add_widget(root)

    def set_mode(self, m, *args):
        ReportsScreen.mode = m
        self.on_pre_enter()

class NamazScreen(SafeScreen):
    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("🕌 Namaz Tracker", back_to="more", c1=ORANGE, c2=GOLD))
        scroll = ScrollView(); content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10)); content.bind(minimum_height=content.setter("height"))
        
        # Subtitle Row (Matching Mockup Image)
        content.add_widget(make_label("Islamabad - Today", fs=dp(14), bold=True, color=ORANGE, halign="center"))
        
        today = str(date.today())
        times = get_today_namaz_times()
        if today not in data.get("namaz_log", {}):
            data.setdefault("namaz_log", {})[today] = []
        for p in times:
            done = p in data["namaz_log"][today]
            row = Card(orientation="horizontal", height=dp(68), padding=dp(10), spacing=dp(10))
            col = BoxLayout(orientation="vertical")
            col.add_widget(make_label(p, fs=dp(15), bold=True, h=dp(24)))
            col.add_widget(make_label(times[p], fs=dp(12), color=theme()["muted"], h=dp(18)))
            row.add_widget(col)

            check = Button(text="✓" if done else "", size_hint_x=None, width=dp(38), height=dp(38),
                           background_normal="", background_color=GREEN_CHECK if done else GRAY,
                           color=WHITE, font_size=dp(16), bold=True, pos_hint={"center_y":0.5})
            check.bind(on_release=partial(self.toggle_namaz, p))
            row.add_widget(check)
            content.add_widget(row)

        q_done = today in data.get("quran_log", [])
        qrow = Card(orientation="horizontal", height=dp(68), padding=dp(10), spacing=dp(10))
        qrow.add_widget(make_label("📖 Quran Recitation", fs=dp(15), bold=True))
        qcheck = Button(text="✓" if q_done else "", size_hint_x=None, width=dp(38), height=dp(38),
                        background_normal="", background_color=GREEN_CHECK if q_done else GRAY,
                        color=WHITE, font_size=dp(16), bold=True, pos_hint={"center_y":0.5})
        qcheck.bind(on_release=self.toggle_quran)
        qrow.add_widget(qcheck)
        content.add_widget(qrow)

        scroll.add_widget(content); root.add_widget(scroll); self.add_widget(root)

    def toggle_namaz(self, p, *args):
        today = str(date.today())
        if p not in data["namaz_log"][today]:
            data["namaz_log"][today].append(p)
            award_points_once(f"namaz_{p}_{today}", 15)
        else:
            data["namaz_log"][today].remove(p)
            revoke_points_once(f"namaz_{p}_{today}", 15)
        save_data(); self.on_pre_enter()

    def toggle_quran(self, inst):
        today = str(date.today())
        if "quran_log" not in data: data["quran_log"] = []
        if today not in data["quran_log"]:
            data["quran_log"].append(today)
            award_points_once(f"quran_{today}", 15)
        else:
            data["quran_log"].remove(today)
            revoke_points_once(f"quran_{today}", 15)
        save_data(); self.on_pre_enter()

class MoreScreen(SafeScreen):
    def _build(self):
        self.clear_widgets(); root = BoxLayout(orientation="vertical")
        root.add_widget(header("⋯ More Options", c1=PURPLE_PRIMARY, c2=INDIGO))
        scroll = ScrollView(); content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10)); content.bind(minimum_height=content.setter("height"))
        
        # Navigation Options with Chevron > (Matching Mockup Image)
        options = [
            ("🎓 Exam Days", "exams", PINK),
            ("📁 Projects", "projects", BLUE),
            ("📝 Daily Note", "checkin", GOLD),
            ("🕌 Namaz & Quran", "namaz", ORANGE),
            ("🔍 Work History Viewer", "history", TEAL)
        ]
        for label, s, c in options:
            row = Card(orientation="horizontal", height=dp(58), padding=dp(10))
            row.add_widget(make_label(label, fs=dp(15), bold=True))
            btn = Button(text=">", size_hint_x=None, width=dp(40), background_normal="", background_color=(0,0,0,0), color=PURPLE_PRIMARY, font_size=dp(18), bold=True)
            btn.bind(on_release=partial(go_screen, s))
            row.add_widget(btn)
            content.add_widget(row)

        dm = "Light Mode" if data.get("dark_mode") else "Dark Mode"
        dark_card = Card(orientation="horizontal", height=dp(58), padding=dp(10))
        dark_card.add_widget(make_label(f"🌓 {dm}", fs=dp(15), bold=True))
        dark_btn = make_button("TOGGLE", h=dp(38), bg=PURPLE_PRIMARY, fs=dp(11))
        dark_btn.size_hint_x = None; dark_btn.width = dp(80)
        dark_btn.bind(on_release=self.toggle_dark)
        dark_card.add_widget(dark_btn)
        content.add_widget(dark_card)

        # Motivational Banner Card (Matching Mockup Image)
        content.add_widget(section_label("Keep Going! 🌟", color=GOLD))
        mcard = Card(orientation="vertical", height=dp(80), bg=ACCENT_BG, padding=dp(12))
        mcard.add_widget(Label(text="Small steps make big changes. 💪", font_size=dp(14), bold=True, color=WHITE))
        mcard.add_widget(Label(text="Stay consistent and achieve your goals!", font_size=dp(12), color=GOLD))
        content.add_widget(mcard)

        scroll.add_widget(content); root.add_widget(scroll); root.add_widget(bottom_nav("more")); self.add_widget(root)

    def toggle_dark(self, inst):
        data["dark_mode"] = not data.get("dark_mode", False)
        save_data(); Window.clearcolor = theme()["bg"]; self.on_pre_enter()

class ExamsScreen(SafeScreen):
    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("🎓 Exam Days", back_to="more", c1=PURPLE_PRIMARY))
        scroll = ScrollView(); content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10)); content.bind(minimum_height=content.setter("height"))
        
        add_btn = make_button("+ Add Exam", h=dp(48), bg=PURPLE_PRIMARY)
        add_btn.bind(on_release=self.show_add_dialog)
        content.add_widget(add_btn)

        today = date.today()
        for exam in data.get("exams", []):
            parsed_dt = parse_flexible_date(exam.get("date"))
            if parsed_dt:
                dl = (parsed_dt - today).days
                info = f"{parsed_dt.strftime('%d %b')}"
                status_text = "Upcoming" if dl > 0 else ("Today" if dl == 0 else "Passed")
                status_color = PINK if dl > 0 else (TEAL if dl == 0 else GRAY)
            else:
                info = exam.get("date", "")
                status_text = "Invalid"
                status_color = GRAY

            card = Card(orientation="horizontal", height=dp(70), padding=dp(10))
            col = BoxLayout(orientation="vertical")
            col.add_widget(make_label(exam.get("subject", "Exam"), fs=dp(15), bold=True, h=dp(24)))
            col.add_widget(make_label(f"📅 {info}", fs=dp(12), color=theme()["muted"], h=dp(18)))
            card.add_widget(col)

            badge = Label(text=status_text, font_size=dp(11), color=WHITE, bold=True, size_hint_x=None, width=dp(75), halign="center", valign="middle")
            with badge.canvas.before:
                Color(*status_color)
                r = RoundedRectangle(pos=badge.pos, size=badge.size, radius=[dp(12)])
            badge.bind(pos=lambda inst, val, rr=r: setattr(rr, "pos", inst.pos), size=lambda inst, val, rr=r: setattr(rr, "size", inst.size))
            card.add_widget(badge)
            content.add_widget(card)

        scroll.add_widget(content); root.add_widget(scroll); self.add_widget(root)

    def show_add_dialog(self, *args):
        pbox = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(8))
        pbox.add_widget(make_label("Subject:", fs=dp(14), color=WHITE))
        sub_in = TextInput(size_hint_y=None, height=dp(40))
        pbox.add_widget(sub_in)
        pbox.add_widget(make_label("Date (YYYY-MM-DD or MM-DD):", fs=dp(14), color=WHITE))
        dt_in = TextInput(size_hint_y=None, height=dp(40))
        pbox.add_widget(dt_in)

        btn = make_button("Save Exam", h=dp(42), bg=PURPLE_PRIMARY)
        pbox.add_widget(btn)

        pop = Popup(title="Add Exam", content=pbox, size_hint=(0.85, 0.5))
        def save_ex(*a):
            if sub_in.text and dt_in.text:
                data.setdefault("exams", []).append({"subject": sub_in.text.strip(), "date": dt_in.text.strip()})
                save_data()
                pop.dismiss()
                self.on_pre_enter()
        btn.bind(on_release=save_ex)
        pop.open()

class ProjectsScreen(SafeScreen):
    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("📁 Projects", back_to="more", c1=PURPLE_PRIMARY))
        scroll = ScrollView(); content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10)); content.bind(minimum_height=content.setter("height"))
        
        add_btn = make_button("+ Add Project", h=dp(48), bg=PURPLE_PRIMARY)
        add_btn.bind(on_release=self.show_add_dialog)
        content.add_widget(add_btn)

        for i, p in enumerate(data.get("projects", [])):
            card = Card(orientation="horizontal", height=dp(75), padding=dp(10))
            col = BoxLayout(orientation="vertical")
            col.add_widget(make_label(p.get("title", "Project"), fs=dp(15), bold=True, h=dp(24)))
            col.add_widget(make_label(f"📅 Due: {p.get('end', '')}", fs=dp(12), color=theme()["muted"], h=dp(18)))
            card.add_widget(col)

            st = "Completed" if p.get("completed") else "In Progress"
            st_color = GREEN_CHECK if p.get("completed") else GOLD
            badge = Label(text=st, font_size=dp(10), color=WHITE, bold=True, size_hint_x=None, width=dp(85), halign="center", valign="middle")
            with badge.canvas.before:
                Color(*st_color)
                r = RoundedRectangle(pos=badge.pos, size=badge.size, radius=[dp(12)])
            badge.bind(pos=lambda inst, val, rr=r: setattr(rr, "pos", inst.pos), size=lambda inst, val, rr=r: setattr(rr, "size", inst.size))
            card.add_widget(badge)
            content.add_widget(card)

        scroll.add_widget(content); root.add_widget(scroll); self.add_widget(root)

    def show_add_dialog(self, *args):
        pbox = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(8))
        pbox.add_widget(make_label("Title:", fs=dp(14), color=WHITE))
        tit_in = TextInput(size_hint_y=None, height=dp(40))
        pbox.add_widget(tit_in)
        pbox.add_widget(make_label("End Date (YYYY-MM-DD):", fs=dp(14), color=WHITE))
        edt_in = TextInput(size_hint_y=None, height=dp(40))
        pbox.add_widget(edt_in)

        btn = make_button("Save Project", h=dp(42), bg=PURPLE_PRIMARY)
        pbox.add_widget(btn)

        pop = Popup(title="Add Project", content=pbox, size_hint=(0.85, 0.5))
        def save_proj(*a):
            if tit_in.text and edt_in.text:
                data.setdefault("projects", []).append({"title": tit_in.text.strip(), "start": str(date.today()), "end": edt_in.text.strip(), "completed": False})
                save_data()
                pop.dismiss()
                self.on_pre_enter()
        btn.bind(on_release=save_proj)
        pop.open()

class CheckinScreen(SafeScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sel_mood = "Happy"

    def _build(self):
        self.clear_widgets(); t = theme()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("📝 Daily Note & Mood", back_to="more", c1=GOLD))
        scroll = ScrollView(); content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10)); content.bind(minimum_height=content.setter("height"))

        today = str(date.today())
        existing = data.get("notes", {}).get(today, {})
        if existing and "mood" in existing:
            self.sel_mood = existing["mood"]

        content.add_widget(make_label("How do you feel today?", fs=dp(15), bold=True, h=dp(30)))

        mood_options = ["Happy", "Normal", "Tired/Low", "Frustrated", "Sleepy"]
        self.mood_buttons = {}

        for m in mood_options:
            is_selected = (m == self.sel_mood)
            btn = make_button(f"{'[SELECTED] ' if is_selected else ''}{m}", h=dp(42), bg=GOLD if is_selected else GRAY, fs=dp(13))
            btn.bind(on_release=partial(self.select_mood, m))
            self.mood_buttons[m] = btn
            content.add_widget(btn)

        content.add_widget(make_label("Write notes about your day:", h=dp(25), color=GOLD, bold=True))
        existing_note = existing.get("note", "")
        self.note = TextInput(text=existing_note, size_hint_y=None, height=dp(110), multiline=True)
        content.add_widget(self.note)

        save_btn = make_button("SAVE CHECK-IN", h=dp(50), bg=GOLD)
        save_btn.bind(on_release=self.save)
        content.add_widget(save_btn)

        if existing:
            content.add_widget(section_label("Today's Saved Entry Preview", color=GOLD))
            preview_card = Card(orientation="vertical", height=dp(95), padding=dp(10))
            preview_card.add_widget(make_label(f"Saved Today ({today}): Mood - {existing.get('mood')}", fs=dp(13), bold=True, color=GOLD, h=dp(24)))
            
            p_lbl = Label(text=f"Note: {existing.get('note', '')}", font_size=dp(12), color=t["text"], size_hint_y=None, height=dp(42), halign="left", valign="top")
            p_lbl.bind(size=lambda inst, val: setattr(p_lbl, "text_size", (val[0], None)))
            preview_card.add_widget(p_lbl)
            content.add_widget(preview_card)

        scroll.add_widget(content); root.add_widget(scroll); self.add_widget(root)

    def select_mood(self, mm, *args):
        self.sel_mood = mm
        for name, btn in self.mood_buttons.items():
            if name == mm:
                btn.text = f"[SELECTED] {name}"
                btn.background_color = GOLD
            else:
                btn.text = name
                btn.background_color = GRAY

    def save(self, inst):
        today = str(date.today())
        data.setdefault("notes", {})[today] = {"mood": self.sel_mood, "note": self.note.text.strip()}
        save_data()
        show_popup("Saved Successfully", "Your daily mood and notes have been permanently stored!", on_close=self.on_pre_enter)

class HistoryScreen(SafeScreen):
    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("🔍 Work History Viewer", back_to="more", c1=TEAL))
        scroll = ScrollView(); content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(10)); content.bind(minimum_height=content.setter("height"))

        content.add_widget(make_label("Select or Enter Date (YYYY-MM-DD):", fs=dp(15), bold=True, color=TEAL))
        self.date_input = TextInput(text=str(date.today()), size_hint_y=None, height=dp(42), font_size=dp(15))
        content.add_widget(self.date_input)

        search_btn = make_button("LOAD DATE ACTIVITIES", bg=TEAL, h=dp(45))
        search_btn.bind(on_release=self.load_history)
        content.add_widget(search_btn)

        self.history_container = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10))
        self.history_container.bind(minimum_height=self.history_container.setter("height"))
        content.add_widget(self.history_container)

        scroll.add_widget(content); root.add_widget(scroll); self.add_widget(root)
        self.load_history()

    def load_history(self, *args):
        self.history_container.clear_widgets()
        target_date = self.date_input.text.strip()
        t = theme()
        card_text_col = t["text"]

        done_tasks = [tk for tk in data.get("tasks", []) if target_date in tk.get("done_dates", [])]
        task_count = max(1, len(done_tasks))
        needed_h = dp(30 + (task_count * 25) + (task_count * 10) + 30)

        card1 = Card(orientation="vertical", height=needed_h, padding=dp(12), spacing=dp(6))
        card1.add_widget(make_label(f"Tasks Completed on {target_date}: ({len(done_tasks)})", bold=True, color=TEAL, h=dp(24)))
        for tk in done_tasks:
            card1.add_widget(make_label(f"• {tk.get('name', '')} ({tk.get('time', '')})", fs=dp(13), color=card_text_col, h=dp(20)))
        if not done_tasks: card1.add_widget(make_label("No completed tasks logged.", fs=dp(12), color=GRAY, h=dp(20)))
        self.history_container.add_widget(card1)

        namaz_done = data.get("namaz_log", {}).get(target_date, [])
        namaz_count = max(1, len(namaz_done))
        namaz_h = dp(30 + (namaz_count * 25) + (namaz_count * 10) + 30)

        card2 = Card(orientation="vertical", height=namaz_h, padding=dp(12), spacing=dp(6))
        card2.add_widget(make_label(f"Namaz Prayed: ({len(namaz_done)}/5)", bold=True, color=ORANGE, h=dp(24)))
        for p in namaz_done:
            card2.add_widget(make_label(f"• {p}", fs=dp(13), color=card_text_col, h=dp(20)))
        if not namaz_done: card2.add_widget(make_label("No prayers logged for this day.", fs=dp(12), color=GRAY, h=dp(20)))
        self.history_container.add_widget(card2)

        mood_entry = data.get("notes", {}).get(target_date)
        card3 = Card(orientation="vertical", height=dp(105), padding=dp(12))
        card3.add_widget(make_label("Daily Mood & Note:", bold=True, color=GOLD, h=dp(24)))
        if mood_entry:
            note_lbl = Label(text=f"Mood: {mood_entry.get('mood')} | Note: {mood_entry.get('note')}",
                             font_size=dp(12), color=card_text_col, size_hint_y=None, height=dp(45),
                             halign="left", valign="top")
            note_lbl.bind(size=lambda inst, val: setattr(note_lbl, "text_size", (val[0], None)))
            card3.add_widget(note_lbl)
        else:
            card3.add_widget(make_label("No check-in recorded for this day.", fs=dp(12), color=GRAY, h=dp(24)))
        self.history_container.add_widget(card3)

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
        sm.add_widget(HistoryScreen(name="history"))
        sm.add_widget(ExamsScreen(name="exams"))
        sm.add_widget(ProjectsScreen(name="projects"))
        sm.add_widget(CheckinScreen(name="checkin"))
        sm.add_widget(NamazScreen(name="namaz"))
        return sm

    def on_stop(self): save_data()

if __name__ == "__main__":
    RoutineApp().run()