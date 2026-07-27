
import copy
import json
import os
from datetime import date, datetime, timedelta
from functools import partial

from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button, ToggleButton
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget


DEFAULT_DATA = {
    "tasks": [],
    "habits": [],
    "namaz_log": {},
    "quran_log": [],
    "exams": [],
    "projects": [],
    "notes": {},
    "points": 0,
    "level": 1,
    "badges": [],
    "dark_mode": False,
}

data = copy.deepcopy(DEFAULT_DATA)
DATA_FILE = None


LIGHT = {
    "bg": (0.98, 0.95, 0.91, 1),
    "card": (1, 1, 1, 1),
    "text": (0.24, 0.16, 0.10, 1),
    "muted": (0.61, 0.56, 0.51, 1),
    "border": (0.90, 0.85, 0.80, 1),
}
DARK = {
    "bg": (0.12, 0.09, 0.07, 1),
    "card": (0.18, 0.14, 0.11, 1),
    "text": (0.95, 0.90, 0.86, 1),
    "muted": (0.70, 0.64, 0.57, 1),
    "border": (0.28, 0.22, 0.17, 1),
}

ORANGE = (0.91, 0.35, 0.05, 1)
GOLD = (0.97, 0.66, 0.23, 1)
TEAL = (0.18, 0.55, 0.47, 1)
PURPLE = (0.47, 0.31, 0.66, 1)
PINK = (0.78, 0.27, 0.36, 1)
BLUE = (0.18, 0.43, 0.63, 1)
RED = (0.80, 0.24, 0.24, 1)
GREEN = (0.17, 0.61, 0.31, 1)
WHITE = (1, 1, 1, 1)
GRAY = (0.85, 0.82, 0.78, 1)
MID = (0.55, 0.50, 0.46, 1)

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
HABIT_COLORS = [ORANGE, TEAL, PURPLE, PINK, GOLD, BLUE]


# Islamabad, Pakistan – monthly prayer times (based on the file you uploaded).
# Stored in 24-hour format to make comparisons simple and reliable.
NAMAZ_TIMES = {
    1:  {"Fajr": "05:44", "Zuhr": "12:17", "Asr": "15:44", "Maghrib": "17:25", "Isha": "18:50"},
    2:  {"Fajr": "05:28", "Zuhr": "12:22", "Asr": "16:13", "Maghrib": "17:54", "Isha": "19:15"},
    3:  {"Fajr": "04:55", "Zuhr": "12:17", "Asr": "16:33", "Maghrib": "18:18", "Isha": "19:38"},
    4:  {"Fajr": "04:09", "Zuhr": "12:08", "Asr": "16:47", "Maghrib": "18:41", "Isha": "20:06"},
    5:  {"Fajr": "03:30", "Zuhr": "12:04", "Asr": "16:58", "Maghrib": "19:04", "Isha": "20:37"},
    6:  {"Fajr": "03:12", "Zuhr": "12:08", "Asr": "17:08", "Maghrib": "19:22", "Isha": "21:03"},
    7:  {"Fajr": "03:27", "Zuhr": "12:14", "Asr": "17:11", "Maghrib": "19:22", "Isha": "20:59"},
    8:  {"Fajr": "03:58", "Zuhr": "12:12", "Asr": "16:58", "Maghrib": "18:58", "Isha": "20:26"},
    9:  {"Fajr": "04:26", "Zuhr": "12:03", "Asr": "16:29", "Maghrib": "18:18", "Isha": "19:39"},
    10: {"Fajr": "04:49", "Zuhr": "11:54", "Asr": "15:54", "Maghrib": "17:38", "Isha": "18:57"},
    11: {"Fajr": "05:12", "Zuhr": "11:52", "Asr": "15:27", "Maghrib": "17:08", "Isha": "18:31"},
    12: {"Fajr": "05:35", "Zuhr": "12:03", "Asr": "15:23", "Maghrib": "17:03", "Isha": "18:30"},
}


def current_theme():
    return DARK if data.get("dark_mode") else LIGHT


def set_window_theme():
    Window.clearcolor = current_theme()["bg"]


def get_data_path():
    app = App.get_running_app()
    if app and getattr(app, "data_file", None):
        return app.data_file
    return os.path.join(os.getcwd(), "routine_data.json")


def ensure_defaults(raw):
    merged = copy.deepcopy(DEFAULT_DATA)
    if isinstance(raw, dict):
        for key, value in raw.items():
            merged[key] = value
    return merged


def load_data(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return ensure_defaults(json.load(f))
        except Exception:
            return copy.deepcopy(DEFAULT_DATA)
    return copy.deepcopy(DEFAULT_DATA)


def save_data():
    path = get_data_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    except Exception:
        pass
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def show_popup(title, message):
    t = current_theme()
    content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
    content.add_widget(Label(text=message, color=t["text"], halign="center"))
    btn = Button(text="OK", size_hint_y=None, height=dp(44), background_normal="", background_color=ORANGE, color=WHITE)
    popup = Popup(title=title, content=content, size_hint=(0.8, 0.35), separator_color=ORANGE, title_color=t["text"])
    btn.bind(on_release=popup.dismiss)
    content.add_widget(btn)
    popup.open()


def today_str():
    return str(date.today())


def month_num():
    return date.today().month


def month_name(num=None):
    if num is None:
        num = month_num()
    return date(2025, num, 1).strftime("%B")


def get_today_namaz_times():
    return NAMAZ_TIMES[month_num()]


def parse_time(value):
    for fmt in ("%H:%M", "%I:%M %p", "%I:%M%p"):
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            pass
    raise ValueError("Invalid time format")


def get_next_prayer():
    times = get_today_namaz_times()
    now = datetime.now().replace(second=0, microsecond=0)
    candidates = []
    for prayer, tm in times.items():
        try:
            dt = datetime.strptime(f"{date.today()} {tm}", "%Y-%m-%d %H:%M")
            candidates.append((prayer, dt))
        except ValueError:
            continue
    candidates.sort(key=lambda x: x[1])
    for prayer, dt in candidates:
        if now <= dt:
            return prayer, dt.strftime("%H:%M")
    if candidates:
        return candidates[0][0], candidates[0][1].strftime("%H:%M")
    return "—", "—"


def add_points(amount):
    data["points"] = max(0, int(data.get("points", 0)) + int(amount))
    new_level = max(1, data["points"] // 100 + 1)
    if new_level > data["level"]:
        data["level"] = new_level
        badge = f"🏆 Level {data['level']} Reached"
        if badge not in data["badges"]:
            data["badges"].append(badge)
        show_popup("Level Up!", f"You are now Level {data['level']}!")
    save_data()


def check_perfect_day():
    if not data["tasks"]:
        return
    today = today_str()
    if all(today in task["done_dates"] for task in data["tasks"]):
        badge = f"⭐ Perfect Day - {today}"
        if badge not in data["badges"]:
            data["badges"].append(badge)
            add_points(20)
            save_data()
            show_popup("Perfect Day!", "+20 bonus points for completing all tasks today!")


def get_today_progress():
    today = today_str()
    weekday = date.today().weekday()
    total = 0
    done = 0

    for task in data["tasks"]:
        total += 1
        if today in task["done_dates"]:
            done += 1

    for habit in data["habits"]:
        if habit["days"][weekday]:
            total += 1
            if today in habit["log"]:
                done += 1

    total += 5
    namaz_done = data["namaz_log"].get(today, [])
    for prayer in get_today_namaz_times().keys():
        if prayer in namaz_done:
            done += 1
    done += 1 if today in data["quran_log"] else 0

    return 0 if total == 0 else done / total


# ---------------------- UI HELPERS ----------------------

class Card(BoxLayout):
    def __init__(self, bg=None, radius=dp(18), **kwargs):
        super().__init__(**kwargs)
        self.padding = kwargs.pop("padding", (dp(14), dp(14)))
        self.spacing = kwargs.pop("spacing", dp(8))
        self._bg = bg if bg else current_theme()["card"]
        with self.canvas.before:
            Color(*self._bg)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size


class SectionTitle(Label):
    def __init__(self, text, color=ORANGE, **kwargs):
        super().__init__(text=text, size_hint_y=None, height=dp(28), color=color, bold=True, **kwargs)
        self.font_size = kwargs.get("font_size", dp(13))


def make_button(text, height=dp(50), bg=ORANGE, fg=WHITE, font_size=dp(15), bold=True):
    return Button(
        text=text,
        size_hint_y=None,
        height=height,
        background_normal="",
        background_color=bg,
        color=fg,
        font_size=font_size,
        bold=bold,
    )


def text_field(hint="", multiline=False, height=dp(46)):
    return TextInput(
        hint_text=hint,
        size_hint_y=None,
        height=height,
        multiline=multiline,
        font_size=dp(15),
    )


def header(title, back_to=None, color=ORANGE, subtitle=None):
    top = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(110), padding=[dp(18), dp(16), dp(18), dp(10)], spacing=dp(4))
    with top.canvas.before:
        Color(*color)
        top._rect = RoundedRectangle(pos=top.pos, size=top.size, radius=[0])
    top.bind(pos=lambda *_: setattr(top._rect, "pos", top.pos), size=lambda *_: setattr(top._rect, "size", top.size))

    row = BoxLayout(size_hint_y=None, height=dp(28))
    if back_to:
        back = Button(text="← Back", size_hint_x=None, width=dp(92), background_normal="", background_color=(0, 0, 0, 0), color=WHITE, font_size=dp(13), bold=True)
        back.bind(on_release=lambda *_: go_screen(back_to))
        row.add_widget(back)
    top.add_widget(row)
    top.add_widget(Label(text=title, font_size=dp(24), bold=True, color=WHITE))
    if subtitle:
        top.add_widget(Label(text=subtitle, font_size=dp(12), color=WHITE))
    else:
        top.add_widget(Widget(size_hint_y=None, height=dp(12)))
    return top


def bottom_nav(active):
    t = current_theme()
    nav = BoxLayout(size_hint_y=None, height=dp(70), padding=dp(4), spacing=dp(4))
    with nav.canvas.before:
        Color(*t["card"])
        nav._rect = RoundedRectangle(pos=nav.pos, size=nav.size, radius=[0])
    nav.bind(pos=lambda *_: setattr(nav._rect, "pos", nav.pos), size=lambda *_: setattr(nav._rect, "size", nav.size))

    items = [("🏠 Home", "home"), ("🔥 Habits", "habits"), ("✅ Tasks", "tasks"), ("📊 Reports", "reports"), ("⋯ More", "more")]
    for text, name in items:
        color = ORANGE if active == name else t["muted"]
        btn = Button(text=text, background_normal="", background_color=(0, 0, 0, 0), color=color, font_size=dp(12), bold=(name == active))
        btn.bind(on_release=lambda _, s=name: go_screen(s))
        nav.add_widget(btn)
    return nav


sm = None


def go_screen(name):
    if sm:
        sm.current = name


def clear_box(box):
    box.clear_widgets()


def priority_color(priority):
    return {"High": PINK, "Medium": GOLD, "Low": MID}.get(priority, GOLD)


def mark_task_done(task_idx):
    today = today_str()
    task = data["tasks"][task_idx]
    if today in task["done_dates"]:
        show_popup("Already Done", "This task is already marked done today.")
        return
    task["done_dates"].append(today)
    add_points(10)
    check_perfect_day()
    save_data()
    if sm:
        sm.current = "tasks"


def delete_task(task_idx):
    if 0 <= task_idx < len(data["tasks"]):
        data["tasks"].pop(task_idx)
        save_data()
    if sm:
        sm.current = "tasks"


def toggle_today_habit(habit_idx):
    today = today_str()
    habit = data["habits"][habit_idx]
    if today in habit["log"]:
        show_popup("Already Done", "This habit is already marked for today.")
        return
    habit["log"].append(today)
    add_points(5)
    save_data()
    if sm:
        sm.current = "habits"


def toggle_habit_day(habit_idx, day_str):
    habit = data["habits"][habit_idx]
    if day_str in habit["log"]:
        habit["log"].remove(day_str)
    else:
        habit["log"].append(day_str)
    save_data()
    if sm:
        sm.current = "habits"


def delete_habit(habit_idx):
    if 0 <= habit_idx < len(data["habits"]):
        data["habits"].pop(habit_idx)
        save_data()
    if sm:
        sm.current = "habits"


def toggle_namaz(prayer_name):
    today = today_str()
    if today not in data["namaz_log"]:
        data["namaz_log"][today] = []
    done = data["namaz_log"][today]
    if prayer_name in done:
        show_popup("Already Done", f"{prayer_name} is already marked for today.")
        return
    done.append(prayer_name)
    add_points(15)
    save_data()
    if sm:
        sm.current = "namaz"


def toggle_quran():
    today = today_str()
    if today in data["quran_log"]:
        show_popup("Already Done", "Quran recitation is already marked for today.")
        return
    data["quran_log"].append(today)
    add_points(15)
    save_data()
    if sm:
        sm.current = "namaz"


def delete_exam(idx):
    if 0 <= idx < len(data["exams"]):
        data["exams"].pop(idx)
        save_data()
    if sm:
        sm.current = "exams"


def delete_project(idx):
    if 0 <= idx < len(data["projects"]):
        data["projects"].pop(idx)
        save_data()
    if sm:
        sm.current = "projects"


# ---------------------- SCREENS ----------------------

class HomeScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        t = current_theme()

        root = BoxLayout(orientation="vertical")
        root.add_widget(header("Assalam-o-Alaikum ☀️", color=ORANGE, subtitle=f"Today is {date.today().strftime('%A, %d %B %Y')}"))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(14), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))

        # Summary card
        progress = int(get_today_progress() * 100)
        summary = Card(orientation="vertical", size_hint_y=None, height=dp(160), spacing=dp(8))
        summary.add_widget(Label(text=f"📈 Today Progress: {progress}%", font_size=dp(18), bold=True, color=t["text"]))
        summary.add_widget(Label(text=f"🔥 Streak/Points: {data.get('points', 0) // 20} days", font_size=dp(14), color=ORANGE))
        summary.add_widget(Label(text=f"⭐ Points: {data['points']}", font_size=dp(14), color=PURPLE))
        summary.add_widget(Label(text=f"🏆 Level: {data['level']}", font_size=dp(14), color=GOLD))
        content.add_widget(summary)

        prayer, prayer_time = get_next_prayer()
        next_card = Card(orientation="vertical", size_hint_y=None, height=dp(95))
        next_card.add_widget(Label(text=f"🕌 Next Prayer", font_size=dp(16), bold=True, color=t["text"]))
        next_card.add_widget(Label(text=f"{prayer} at {prayer_time}", font_size=dp(17), bold=True, color=ORANGE))
        content.add_widget(next_card)

        # Quick actions
        content.add_widget(SectionTitle("Quick Actions", color=ORANGE))
        q1 = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        for text, target, color in [
            ("✅ Tasks", "tasks", TEAL),
            ("🔥 Habits", "habits", PINK),
            ("🕌 Namaz", "namaz", ORANGE),
            ("⋯ More", "more", PURPLE),
        ]:
            b = make_button(text, bg=color)
            b.bind(on_release=lambda _, s=target: go_screen(s))
            q1.add_widget(b)
        content.add_widget(q1)

        # Today's tasks preview
        content.add_widget(SectionTitle("Today's Tasks", color=TEAL))
        today = today_str()
        if not data["tasks"]:
            content.add_widget(Card(orientation="vertical", size_hint_y=None, height=dp(60)))
            content.children[0].add_widget(Label(text="No tasks added yet.", color=t["muted"]))
        else:
            for idx, task in enumerate(data["tasks"][:4]):
                done = today in task["done_dates"]
                row = Card(orientation="horizontal", size_hint_y=None, height=dp(76), spacing=dp(10))
                check = make_button("✓" if done else "○", height=dp(42), bg=GREEN if done else GRAY, font_size=dp(17))
                check.size_hint_x = None
                check.width = dp(42)
                check.bind(on_release=lambda _, i=idx: mark_task_done(i))
                row.add_widget(check)
                text_col = BoxLayout(orientation="vertical")
                text_col.add_widget(Label(text=f"📝 {task['name']}", color=t["text"], bold=True))
                extra = f"{task['time']}  •  {task.get('priority', 'Medium')}"
                if task.get("note"):
                    extra += f"\n{task['note']}"
                text_col.add_widget(Label(text=extra, color=t["muted"], halign="left", valign="middle"))
                row.add_widget(text_col)
                content.add_widget(row)

        scroll.add_widget(content)
        root.add_widget(scroll)
        root.add_widget(bottom_nav("home"))
        self.add_widget(root)


class TasksScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        t = current_theme()

        root = BoxLayout(orientation="vertical")
        root.add_widget(header("✅ My Tasks", back_to=None, color=TEAL, subtitle="Add, complete and manage your daily routine"))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(14), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))

        add_btn = make_button("➕ Add New Task", bg=TEAL)
        add_btn.bind(on_release=lambda *_: go_screen("add_task"))
        content.add_widget(add_btn)

        today = today_str()
        if not data["tasks"]:
            empty = Card(orientation="vertical", size_hint_y=None, height=dp(60))
            empty.add_widget(Label(text="No tasks yet. Tap + to add one.", color=t["muted"]))
            content.add_widget(empty)

        for idx, task in enumerate(data["tasks"]):
            done = today in task["done_dates"]
            row = Card(orientation="horizontal", size_hint_y=None, height=dp(82), spacing=dp(8))
            check = make_button("✓" if done else "○", height=dp(42), bg=GREEN if done else GRAY, font_size=dp(17))
            check.size_hint_x = None
            check.width = dp(42)
            check.bind(on_release=lambda _, i=idx: mark_task_done(i))
            row.add_widget(check)

            text_col = BoxLayout(orientation="vertical")
            note = f"\n{task['note']}" if task.get("note") else ""
            text_col.add_widget(Label(text=f"{task['name']}  •  {task['time']}", color=t["text"], bold=True, halign="left"))
            text_col.add_widget(Label(text=f"Priority: {task.get('priority', 'Medium')}{note}", color=t["muted"], halign="left"))
            row.add_widget(text_col)

            del_btn = make_button("🗑", height=dp(42), bg=RED, font_size=dp(17))
            del_btn.size_hint_x = None
            del_btn.width = dp(42)
            del_btn.bind(on_release=lambda _, i=idx: delete_task(i))
            row.add_widget(del_btn)

            content.add_widget(row)

        scroll.add_widget(content)
        root.add_widget(scroll)
        root.add_widget(bottom_nav("tasks"))
        self.add_widget(root)


class AddTaskScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("➕ Add Task", back_to="tasks", color=TEAL))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(14), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(SectionTitle("Task Name", color=TEAL))
        self.name_input = text_field("e.g. Physics Homework")
        content.add_widget(self.name_input)

        content.add_widget(SectionTitle("Time", color=PINK))
        self.time_input = text_field("e.g. 05:00 PM or 17:00")
        content.add_widget(self.time_input)

        content.add_widget(SectionTitle("Priority", color=ORANGE))
        self.priority = "High"
        self.priority_buttons = {}
        pr_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        for pr, color in [("High", PINK), ("Medium", GOLD), ("Low", MID)]:
            btn = make_button(pr, height=dp(48), bg=color if pr == self.priority else current_theme()["card"], fg=current_theme()["text"], font_size=dp(13))
            btn.bind(on_release=lambda _, p=pr: self.set_priority(p))
            pr_row.add_widget(btn)
            self.priority_buttons[pr] = btn
        content.add_widget(pr_row)

        content.add_widget(SectionTitle("Notes", color=PURPLE))
        self.note_input = text_field("Optional note", multiline=False)
        content.add_widget(self.note_input)

        self.recurring = False
        self.repeat_btn = make_button("Repeats daily: OFF", bg=current_theme()["card"], fg=current_theme()["text"])
        self.repeat_btn.bind(on_release=self.toggle_repeat)
        content.add_widget(self.repeat_btn)

        save_btn = make_button("💾 Save Task", bg=ORANGE)
        save_btn.bind(on_release=self.save_task)
        content.add_widget(save_btn)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def set_priority(self, priority):
        self.priority = priority
        colors = {"High": PINK, "Medium": GOLD, "Low": MID}
        for p, btn in self.priority_buttons.items():
            if p == priority:
                btn.background_color = colors[p]
                btn.color = WHITE
            else:
                btn.background_color = current_theme()["card"]
                btn.color = current_theme()["text"]

    def toggle_repeat(self, *_):
        self.recurring = not self.recurring
        self.repeat_btn.text = "Repeats daily: ON" if self.recurring else "Repeats daily: OFF"

    def save_task(self, *_):
        name = self.name_input.text.strip()
        time_value = self.time_input.text.strip()
        if not name or not time_value:
            show_popup("Missing Info", "Please enter task name and time.")
            return
        data["tasks"].append({
            "name": name,
            "time": time_value,
            "priority": self.priority,
            "recurring": self.recurring,
            "note": self.note_input.text.strip(),
            "done_dates": [],
        })
        save_data()
        show_popup("Saved", f"Task '{name}' added!")
        go_screen("tasks")


class HabitsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        t = current_theme()

        root = BoxLayout(orientation="vertical")
        root.add_widget(header("🔥 Habits", color=PINK, subtitle="Track repeat actions across the week"))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(14), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))

        add_btn = make_button("➕ Add New Habit", bg=PINK)
        add_btn.bind(on_release=lambda *_: go_screen("add_habit"))
        content.add_widget(add_btn)

        if not data["habits"]:
            empty = Card(orientation="vertical", size_hint_y=None, height=dp(60))
            empty.add_widget(Label(text="No habits yet. Add one above.", color=t["muted"]))
            content.add_widget(empty)

        week_dates = [str(date.today() - timedelta(days=i)) for i in range(6, -1, -1)]
        for idx, habit in enumerate(data["habits"]):
            color = tuple(habit["color"])
            card = Card(orientation="vertical", size_hint_y=None, height=dp(165), spacing=dp(8))
            top = BoxLayout(size_hint_y=None, height=dp(30))
            top.add_widget(Label(text=f"🌟 {habit['name']}", color=t["text"], bold=True))
            del_btn = make_button("🗑", height=dp(32), bg=RED, font_size=dp(15))
            del_btn.size_hint_x = None
            del_btn.width = dp(38)
            del_btn.bind(on_release=lambda _, i=idx: delete_habit(i))
            top.add_widget(del_btn)
            card.add_widget(top)

            streak = sum(1 for d in week_dates if d in habit["log"])
            card.add_widget(Label(text=f"Weekly streak: {streak}/7", color=color, bold=True, size_hint_y=None, height=dp(22)))

            days = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
            for day in week_dates:
                done = day in habit["log"]
                b = make_button(day[-2:], bg=color if done else current_theme()["card"], fg=WHITE if done else current_theme()["text"], font_size=dp(12), height=dp(44))
                b.bind(on_release=lambda _, i=idx, d=day: toggle_habit_day(i, d))
                days.add_widget(b)
            card.add_widget(days)

            today_btn = make_button("Mark Today", bg=GREEN if today_str() in habit["log"] else ORANGE)
            today_btn.bind(on_release=lambda _, i=idx: toggle_today_habit(i))
            card.add_widget(today_btn)

            content.add_widget(card)

        scroll.add_widget(content)
        root.add_widget(scroll)
        root.add_widget(bottom_nav("habits"))
        self.add_widget(root)


class AddHabitScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("➕ Add Habit", back_to="habits", color=PINK))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(14), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(SectionTitle("Habit Name", color=PINK))
        self.name_input = text_field("e.g. Drink water")
        content.add_widget(self.name_input)

        content.add_widget(SectionTitle("Repeat On", color=PURPLE))
        self.selected_days = [True, True, True, True, True, False, False]
        self.day_buttons = []
        row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        for i, d in enumerate(DAY_NAMES):
            b = make_button(d[:2], bg=PINK if self.selected_days[i] else current_theme()["card"], fg=WHITE if self.selected_days[i] else current_theme()["text"], font_size=dp(12))
            b.bind(on_release=lambda _, idx=i: self.toggle_day(idx))
            row.add_widget(b)
            self.day_buttons.append(b)
        content.add_widget(row)

        content.add_widget(SectionTitle("Color", color=ORANGE))
        self.selected_color = 0
        self.color_buttons = []
        row2 = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        for i, color in enumerate(HABIT_COLORS):
            b = make_button("", bg=color, height=dp(48))
            b.bind(on_release=lambda _, idx=i: self.select_color(idx))
            row2.add_widget(b)
            self.color_buttons.append(b)
        content.add_widget(row2)

        save_btn = make_button("💾 Create Habit", bg=PINK)
        save_btn.bind(on_release=self.save_habit)
        content.add_widget(save_btn)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def toggle_day(self, idx):
        self.selected_days[idx] = not self.selected_days[idx]
        self.day_buttons[idx].background_color = PINK if self.selected_days[idx] else current_theme()["card"]
        self.day_buttons[idx].color = WHITE if self.selected_days[idx] else current_theme()["text"]

    def select_color(self, idx):
        self.selected_color = idx

    def save_habit(self, *_):
        name = self.name_input.text.strip()
        if not name:
            show_popup("Missing Info", "Please enter a habit name.")
            return
        data["habits"].append({
            "name": name,
            "color": list(HABIT_COLORS[self.selected_color]),
            "days": list(self.selected_days),
            "log": [],
        })
        save_data()
        show_popup("Saved", f"Habit '{name}' created!")
        go_screen("habits")


class NamazScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        t = current_theme()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("🕌 Namaz & Quran", color=ORANGE, subtitle=f"{month_name()} timings for Islamabad"))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(14), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))

        today = today_str()
        if today not in data["namaz_log"]:
            data["namaz_log"][today] = []
            save_data()

        card = Card(orientation="vertical", size_hint_y=None, height=dp(105))
        prayer, prayer_time = get_next_prayer()
        card.add_widget(Label(text=f"Next Prayer: {prayer}", color=t["text"], bold=True, font_size=dp(16)))
        card.add_widget(Label(text=f"At {prayer_time}", color=ORANGE, bold=True, font_size=dp(18)))
        content.add_widget(card)

        for prayer_name, prayer_time in get_today_namaz_times().items():
            done = prayer_name in data["namaz_log"][today]
            row = Card(orientation="horizontal", size_hint_y=None, height=dp(74), spacing=dp(8))
            btn = make_button("✓" if done else "○", height=dp(42), bg=GREEN if done else GRAY, font_size=dp(18))
            btn.size_hint_x = None
            btn.width = dp(42)
            btn.bind(on_release=lambda _, p=prayer_name: toggle_namaz(p))
            row.add_widget(btn)
            txt = BoxLayout(orientation="vertical")
            txt.add_widget(Label(text=f"{prayer_name}", color=t["text"], bold=True))
            txt.add_widget(Label(text=prayer_time, color=t["muted"]))
            row.add_widget(txt)
            content.add_widget(row)

        q_done = today in data["quran_log"]
        qrow = Card(orientation="horizontal", size_hint_y=None, height=dp(74), spacing=dp(8))
        qbtn = make_button("✓" if q_done else "○", height=dp(42), bg=GREEN if q_done else GRAY, font_size=dp(18))
        qbtn.size_hint_x = None
        qbtn.width = dp(42)
        qbtn.bind(on_release=lambda *_: toggle_quran())
        qrow.add_widget(qbtn)
        qtxt = BoxLayout(orientation="vertical")
        qtxt.add_widget(Label(text="📖 Quran Recitation", color=t["text"], bold=True))
        qtxt.add_widget(Label(text="Mark once per day", color=t["muted"]))
        qrow.add_widget(qtxt)
        content.add_widget(qrow)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)


class ReportsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        t = current_theme()

        root = BoxLayout(orientation="vertical")
        root.add_widget(header("📊 Reports", color=BLUE, subtitle="Weekly and monthly progress overview"))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(14), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))

        if not hasattr(self, "mode"):
            self.mode = "weekly"

        switch = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        w = make_button("Weekly", bg=BLUE if self.mode == "weekly" else current_theme()["card"], fg=WHITE if self.mode == "weekly" else t["text"], height=dp(44), font_size=dp(13))
        m = make_button("Monthly", bg=BLUE if self.mode == "monthly" else current_theme()["card"], fg=WHITE if self.mode == "monthly" else t["text"], height=dp(44), font_size=dp(13))
        w.bind(on_release=lambda *_: self.set_mode("weekly"))
        m.bind(on_release=lambda *_: self.set_mode("monthly"))
        switch.add_widget(w)
        switch.add_widget(m)
        content.add_widget(switch)

        if self.mode == "weekly":
            label_suffix = "this week"
            dates = [str(date.today() - timedelta(days=i)) for i in range(6, -1, -1)]
            namaz_max = 35
            check_dates = dates
        else:
            label_suffix = "this month"
            prefix = date.today().strftime("%Y-%m")
            check_dates = None
            namaz_max = date.today().day * 5

        def in_scope(d):
            if check_dates is not None:
                return d in check_dates
            return d.startswith(prefix)

        tasks_done = sum(1 for task in data["tasks"] for d in task["done_dates"] if in_scope(d))
        namaz_done = sum(len(v) for d, v in data["namaz_log"].items() if in_scope(d))
        quran_done = sum(1 for d in data["quran_log"] if in_scope(d))
        notes_done = sum(1 for d in data["notes"] if in_scope(d))

        stats = BoxLayout(size_hint_y=None, height=dp(210), spacing=dp(8))
        left = BoxLayout(orientation="vertical", spacing=dp(8))
        right = BoxLayout(orientation="vertical", spacing=dp(8))

        def tile(value, label, bg):
            c = Card(bg=bg, orientation="vertical", size_hint_y=None, height=dp(95))
            c.add_widget(Label(text=value, color=WHITE, bold=True, font_size=dp(24)))
            c.add_widget(Label(text=label, color=WHITE, font_size=dp(11)))
            return c

        left.add_widget(tile(str(tasks_done), f"Tasks done {label_suffix}", TEAL))
        left.add_widget(tile(f"{namaz_done}/{namaz_max}", "Namaz prayed", ORANGE))
        right.add_widget(tile(f"{quran_done}/{7 if self.mode=='weekly' else date.today().day}", "Quran days", PURPLE))
        right.add_widget(tile(str(notes_done), "Daily notes", GOLD))
        stats.add_widget(left)
        stats.add_widget(right)
        content.add_widget(stats)

        content.add_widget(SectionTitle("Moods", color=BLUE))
        mood_items = sorted(data["notes"].items(), reverse=True)
        shown = 0
        for d, entry in mood_items:
            if in_scope(d) and shown < 10:
                row = Card(orientation="horizontal", size_hint_y=None, height=dp(48))
                row.add_widget(Label(text=d, color=t["text"]))
                row.add_widget(Label(text=entry.get("mood", "—"), color=BLUE, bold=True))
                content.add_widget(row)
                shown += 1

        scroll.add_widget(content)
        root.add_widget(scroll)
        root.add_widget(bottom_nav("reports"))
        self.add_widget(root)

    def set_mode(self, mode):
        self.mode = mode
        self.on_pre_enter()


class MoreScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("⋯ More", color=PURPLE, subtitle="Extra tools and settings"))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(14), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))

        items = [
            ("📅 Exam Days", "exams", PINK),
            ("🎯 Projects & Goals", "projects", BLUE),
            ("📝 Daily Note & Mood", "checkin", GOLD),
            ("🏆 Points & Badges", "points", ORANGE),
            ("⚙ Settings", "settings", MID),
        ]
        for label, scr, col in items:
            btn = make_button(label, bg=col, height=dp(62), font_size=dp(16))
            btn.bind(on_release=lambda _, s=scr: go_screen(s))
            content.add_widget(btn)

        content.add_widget(Card(orientation="vertical", size_hint_y=None, height=dp(86), bg=current_theme()["card"]))
        content.children[0].add_widget(Label(text="Your data is saved automatically in app storage.", color=current_theme()["muted"]))
        content.children[0].add_widget(Label(text="Close and reopen the app safely.", color=current_theme()["muted"]))

        scroll.add_widget(content)
        root.add_widget(scroll)
        root.add_widget(bottom_nav("more"))
        self.add_widget(root)


class ExamsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        t = current_theme()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("📅 Exam Days", back_to="more", color=PURPLE, subtitle="Track subject dates"))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(14), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(SectionTitle("Subject", color=PURPLE))
        self.subject_input = text_field("e.g. Physics")
        content.add_widget(self.subject_input)

        content.add_widget(SectionTitle("Exam Date", color=PURPLE))
        self.date_input = text_field("YYYY-MM-DD")
        content.add_widget(self.date_input)

        add_btn = make_button("➕ Add Exam", bg=PURPLE)
        add_btn.bind(on_release=self.add_exam)
        content.add_widget(add_btn)

        if not data["exams"]:
            empty = Card(orientation="vertical", size_hint_y=None, height=dp(60))
            empty.add_widget(Label(text="No exams added yet.", color=t["muted"]))
            content.add_widget(empty)

        today = date.today()
        for idx, exam in enumerate(data["exams"]):
            row = Card(orientation="horizontal", size_hint_y=None, height=dp(70), spacing=dp(8))
            try:
                ed = date.fromisoformat(exam["date"])
                diff = (ed - today).days
                if diff > 0:
                    info = f"in {diff} day(s)"
                    info_color = TEAL
                elif diff == 0:
                    info = "TODAY!"
                    info_color = RED
                else:
                    info = "passed"
                    info_color = MID
            except Exception:
                info = "invalid date"
                info_color = RED
            col = BoxLayout(orientation="vertical")
            col.add_widget(Label(text=f"📘 {exam['subject']}", color=t["text"], bold=True))
            col.add_widget(Label(text=f"{exam['date']} • {info}", color=info_color))
            row.add_widget(col)
            del_btn = make_button("🗑", bg=RED, height=dp(42), font_size=dp(17))
            del_btn.size_hint_x = None
            del_btn.width = dp(42)
            del_btn.bind(on_release=lambda _, i=idx: delete_exam(i))
            row.add_widget(del_btn)
            content.add_widget(row)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def add_exam(self, *_):
        subject = self.subject_input.text.strip()
        ex_date = self.date_input.text.strip()
        if not subject or not ex_date:
            show_popup("Missing Info", "Please enter subject and date.")
            return
        try:
            date.fromisoformat(ex_date)
        except Exception:
            show_popup("Invalid Date", "Use YYYY-MM-DD format.")
            return
        data["exams"].append({"subject": subject, "date": ex_date})
        save_data()
        show_popup("Saved", f"Exam '{subject}' added!")
        self.on_pre_enter()


class ProjectsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        t = current_theme()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("🎯 Projects & Goals", back_to="more", color=BLUE, subtitle="Manage your bigger targets"))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(14), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(SectionTitle("Title", color=BLUE))
        self.title_input = text_field("e.g. Build routine app")
        content.add_widget(self.title_input)

        content.add_widget(SectionTitle("End Date", color=BLUE))
        self.end_input = text_field("YYYY-MM-DD")
        content.add_widget(self.end_input)

        add_btn = make_button("➕ Add Project", bg=BLUE)
        add_btn.bind(on_release=self.add_project)
        content.add_widget(add_btn)

        if not data["projects"]:
            empty = Card(orientation="vertical", size_hint_y=None, height=dp(60))
            empty.add_widget(Label(text="No projects yet.", color=t["muted"]))
            content.add_widget(empty)

        today = date.today()
        for idx, proj in enumerate(data["projects"]):
            row = Card(orientation="horizontal", size_hint_y=None, height=dp(82), spacing=dp(8))
            try:
                end = date.fromisoformat(proj["end"])
                diff = (end - today).days
                if proj.get("completed"):
                    info = "Completed"
                    info_color = GREEN
                elif diff > 0:
                    info = f"{diff} day(s) left"
                    info_color = TEAL
                elif diff == 0:
                    info = "Due TODAY"
                    info_color = RED
                else:
                    info = "Overdue"
                    info_color = PINK
            except Exception:
                info = "Invalid date"
                info_color = RED

            col = BoxLayout(orientation="vertical")
            col.add_widget(Label(text=f"📌 {proj['title']}", color=t["text"], bold=True))
            col.add_widget(Label(text=info, color=info_color))
            row.add_widget(col)

            if not proj.get("completed"):
                done_btn = make_button("✓", bg=GREEN, height=dp(42), font_size=dp(17))
                done_btn.size_hint_x = None
                done_btn.width = dp(42)
                done_btn.bind(on_release=lambda _, i=idx: self.complete_project(i))
                row.add_widget(done_btn)

            del_btn = make_button("🗑", bg=RED, height=dp(42), font_size=dp(17))
            del_btn.size_hint_x = None
            del_btn.width = dp(42)
            del_btn.bind(on_release=lambda _, i=idx: delete_project(i))
            row.add_widget(del_btn)
            content.add_widget(row)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def add_project(self, *_):
        title = self.title_input.text.strip()
        end_date = self.end_input.text.strip()
        if not title or not end_date:
            show_popup("Missing Info", "Please enter a title and end date.")
            return
        try:
            date.fromisoformat(end_date)
        except Exception:
            show_popup("Invalid Date", "Use YYYY-MM-DD format.")
            return
        data["projects"].append({
            "title": title,
            "start": today_str(),
            "end": end_date,
            "completed": False,
        })
        save_data()
        show_popup("Saved", f"Project '{title}' added!")
        self.on_pre_enter()

    def complete_project(self, index):
        if 0 <= index < len(data["projects"]):
            data["projects"][index]["completed"] = True
            save_data()
            show_popup("Completed", "Project marked complete!")
        self.on_pre_enter()


class CheckinScreen(Screen):
    moods = ["Happy", "Normal", "Tired/Low", "Frustrated", "Sleepy"]

    def on_pre_enter(self):
        self.clear_widgets()
        t = current_theme()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("📝 Daily Note & Mood", back_to="more", color=GOLD, subtitle="Save how your day feels"))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(14), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(SectionTitle("How do you feel today?", color=GOLD))
        self.selected_mood = data.get("notes", {}).get(today_str(), {}).get("mood", "Normal")

        self.mood_buttons = []
        for mood in self.moods:
            is_sel = mood == self.selected_mood
            b = make_button(("✓ " if is_sel else "") + mood, bg=GOLD if is_sel else current_theme()["card"], fg=WHITE if is_sel else t["text"], height=dp(48), font_size=dp(14))
            b.bind(on_release=lambda _, m=mood: self.select_mood(m))
            content.add_widget(b)
            self.mood_buttons.append(b)

        content.add_widget(SectionTitle("Write anything about your day", color=GOLD))
        self.note_input = TextInput(
            text=data.get("notes", {}).get(today_str(), {}).get("note", ""),
            size_hint_y=None,
            height=dp(140),
            multiline=True,
            font_size=dp(15),
        )
        content.add_widget(self.note_input)

        save_btn = make_button("💾 Save Check-in", bg=GOLD)
        save_btn.bind(on_release=self.save_checkin)
        content.add_widget(save_btn)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def select_mood(self, mood):
        self.selected_mood = mood
        self.on_pre_enter()

    def save_checkin(self, *_):
        data["notes"][today_str()] = {
            "mood": self.selected_mood,
            "note": self.note_input.text.strip(),
        }
        save_data()
        show_popup("Saved", "Your daily check-in has been saved!")
        self.on_pre_enter()


class PointsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        t = current_theme()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("🏆 Points & Badges", back_to="more", color=ORANGE, subtitle="Keep going and level up"))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(14), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))

        stats = BoxLayout(size_hint_y=None, height=dp(120), spacing=dp(8))
        left = Card(bg=ORANGE, orientation="vertical")
        left.add_widget(Label(text=str(data["points"]), color=WHITE, bold=True, font_size=dp(28)))
        left.add_widget(Label(text="Points", color=WHITE))
        right = Card(bg=PURPLE, orientation="vertical")
        right.add_widget(Label(text=str(data["level"]), color=WHITE, bold=True, font_size=dp(28)))
        right.add_widget(Label(text="Level", color=WHITE))
        stats.add_widget(left)
        stats.add_widget(right)
        content.add_widget(stats)

        content.add_widget(SectionTitle("Badges Earned", color=ORANGE))
        if not data["badges"]:
            empty = Card(orientation="vertical", size_hint_y=None, height=dp(60))
            empty.add_widget(Label(text="No badges yet - keep going!", color=t["muted"]))
            content.add_widget(empty)
        else:
            for badge in data["badges"][:20]:
                row = Card(orientation="horizontal", size_hint_y=None, height=dp(56))
                row.add_widget(Label(text=badge, color=t["text"], bold=True))
                content.add_widget(row)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)


class SettingsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        t = current_theme()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("⚙ Settings", back_to="more", color=MID, subtitle="Theme and data controls"))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(14), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))

        dark_text = "Switch to Light Mode" if data.get("dark_mode") else "Switch to Dark Mode"
        self.dark_btn = make_button(f"🌓 {dark_text}", bg=MID)
        self.dark_btn.bind(on_release=self.toggle_dark)
        content.add_widget(self.dark_btn)

        content.add_widget(SectionTitle("Data", color=MID))
        save_note = Card(orientation="vertical", size_hint_y=None, height=dp(90))
        save_note.add_widget(Label(text="Data saves automatically in app storage.", color=t["text"]))
        save_note.add_widget(Label(text="Close and reopen safely.", color=t["muted"]))
        content.add_widget(save_note)

        reset_btn = make_button("♻ Reset All Data", bg=RED)
        reset_btn.bind(on_release=self.reset_data)
        content.add_widget(reset_btn)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def toggle_dark(self, *_):
        data["dark_mode"] = not data.get("dark_mode", False)
        set_window_theme()
        save_data()
        self.on_pre_enter()

    def reset_data(self, *_):
        global data
        data = copy.deepcopy(DEFAULT_DATA)
        save_data()
        set_window_theme()
        show_popup("Reset", "All data has been reset.")
        if sm:
            sm.current = "home"


# -------------- Secondary screens (kept simple, but useful) --------------

class ExamsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        t = current_theme()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("📅 Exam Days", back_to="more", color=PURPLE, subtitle="Add and track dates"))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(14), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(SectionTitle("Subject", color=PURPLE))
        self.subject_input = text_field("e.g. Physics")
        content.add_widget(self.subject_input)

        content.add_widget(SectionTitle("Date", color=PURPLE))
        self.date_input = text_field("YYYY-MM-DD")
        content.add_widget(self.date_input)

        add_btn = make_button("➕ Add Exam", bg=PURPLE)
        add_btn.bind(on_release=self.add_exam)
        content.add_widget(add_btn)

        if not data["exams"]:
            empty = Card(orientation="vertical", size_hint_y=None, height=dp(60))
            empty.add_widget(Label(text="No exams added yet.", color=t["muted"]))
            content.add_widget(empty)

        today = date.today()
        for idx, exam in enumerate(data["exams"]):
            try:
                ed = date.fromisoformat(exam["date"])
                days_left = (ed - today).days
                if days_left > 0:
                    status = f"in {days_left} day(s)"
                    color = TEAL
                elif days_left == 0:
                    status = "TODAY!"
                    color = RED
                else:
                    status = "passed"
                    color = MID
            except Exception:
                status = "invalid date"
                color = RED

            row = Card(orientation="horizontal", size_hint_y=None, height=dp(70), spacing=dp(8))
            col = BoxLayout(orientation="vertical")
            col.add_widget(Label(text=f"📘 {exam['subject']}", color=t["text"], bold=True))
            col.add_widget(Label(text=f"{exam['date']} • {status}", color=color))
            row.add_widget(col)
            del_btn = make_button("🗑", bg=RED, height=dp(42), font_size=dp(17))
            del_btn.size_hint_x = None
            del_btn.width = dp(42)
            del_btn.bind(on_release=lambda _, i=idx: delete_exam(i))
            row.add_widget(del_btn)
            content.add_widget(row)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def add_exam(self, *_):
        subject = self.subject_input.text.strip()
        ex_date = self.date_input.text.strip()
        if not subject or not ex_date:
            show_popup("Missing Info", "Please enter subject and date.")
            return
        try:
            date.fromisoformat(ex_date)
        except Exception:
            show_popup("Invalid Date", "Please use YYYY-MM-DD.")
            return
        data["exams"].append({"subject": subject, "date": ex_date})
        save_data()
        show_popup("Saved", f"Exam '{subject}' added!")
        self.on_pre_enter()


class ProjectsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        t = current_theme()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("🎯 Projects & Goals", back_to="more", color=BLUE, subtitle="Keep bigger targets in one place"))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(14), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(SectionTitle("Title", color=BLUE))
        self.title_input = text_field("e.g. Build routine app")
        content.add_widget(self.title_input)

        content.add_widget(SectionTitle("End Date", color=BLUE))
        self.end_input = text_field("YYYY-MM-DD")
        content.add_widget(self.end_input)

        add_btn = make_button("➕ Add Project", bg=BLUE)
        add_btn.bind(on_release=self.add_project)
        content.add_widget(add_btn)

        if not data["projects"]:
            empty = Card(orientation="vertical", size_hint_y=None, height=dp(60))
            empty.add_widget(Label(text="No projects added yet.", color=t["muted"]))
            content.add_widget(empty)

        today = date.today()
        for idx, proj in enumerate(data["projects"]):
            try:
                end = date.fromisoformat(proj["end"])
                days_left = (end - today).days
                if proj.get("completed"):
                    status, color = "Completed", GREEN
                elif days_left > 0:
                    status, color = f"{days_left} day(s) left", TEAL
                elif days_left == 0:
                    status, color = "Due TODAY", RED
                else:
                    status, color = "Overdue", PINK
            except Exception:
                status, color = "Invalid date", RED

            row = Card(orientation="horizontal", size_hint_y=None, height=dp(78), spacing=dp(8))
            col = BoxLayout(orientation="vertical")
            col.add_widget(Label(text=f"📌 {proj['title']}", color=t["text"], bold=True))
            col.add_widget(Label(text=status, color=color))
            row.add_widget(col)

            if not proj.get("completed"):
                done_btn = make_button("✓", bg=GREEN, height=dp(42), font_size=dp(17))
                done_btn.size_hint_x = None
                done_btn.width = dp(42)
                done_btn.bind(on_release=lambda _, i=idx: self.complete_project(i))
                row.add_widget(done_btn)

            del_btn = make_button("🗑", bg=RED, height=dp(42), font_size=dp(17))
            del_btn.size_hint_x = None
            del_btn.width = dp(42)
            del_btn.bind(on_release=lambda _, i=idx: delete_project(i))
            row.add_widget(del_btn)

            content.add_widget(row)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def add_project(self, *_):
        title = self.title_input.text.strip()
        end_date = self.end_input.text.strip()
        if not title or not end_date:
            show_popup("Missing Info", "Please enter title and end date.")
            return
        try:
            date.fromisoformat(end_date)
        except Exception:
            show_popup("Invalid Date", "Please use YYYY-MM-DD.")
            return
        data["projects"].append({"title": title, "start": today_str(), "end": end_date, "completed": False})
        save_data()
        show_popup("Saved", f"Project '{title}' added!")
        self.on_pre_enter()

    def complete_project(self, idx):
        if 0 <= idx < len(data["projects"]):
            data["projects"][idx]["completed"] = True
            save_data()
            show_popup("Completed", "Project marked complete!")
        self.on_pre_enter()


class CheckinScreen(Screen):
    moods = ["Happy", "Normal", "Tired/Low", "Frustrated", "Sleepy"]

    def on_pre_enter(self):
        self.clear_widgets()
        t = current_theme()
        today = today_str()
        current = data.get("notes", {}).get(today, {})
        self.selected_mood = current.get("mood", "Normal")

        root = BoxLayout(orientation="vertical")
        root.add_widget(header("📝 Daily Note & Mood", back_to="more", color=GOLD, subtitle="Save how your day feels"))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(14), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(SectionTitle("How do you feel today?", color=GOLD))
        for mood in self.moods:
            selected = (mood == self.selected_mood)
            b = make_button(("✓ " if selected else "") + mood, bg=GOLD if selected else current_theme()["card"], fg=WHITE if selected else t["text"], height=dp(48), font_size=dp(14))
            b.bind(on_release=lambda _, m=mood: self.select_mood(m))
            content.add_widget(b)

        content.add_widget(SectionTitle("Write anything about your day", color=GOLD))
        self.note_input = TextInput(text=current.get("note", ""), size_hint_y=None, height=dp(140), multiline=True, font_size=dp(15))
        content.add_widget(self.note_input)

        save_btn = make_button("💾 Save Check-in", bg=GOLD)
        save_btn.bind(on_release=self.save_checkin)
        content.add_widget(save_btn)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def select_mood(self, mood):
        self.selected_mood = mood
        self.on_pre_enter()

    def save_checkin(self, *_):
        data.setdefault("notes", {})
        data["notes"][today_str()] = {"mood": self.selected_mood, "note": self.note_input.text.strip()}
        save_data()
        show_popup("Saved", "Your daily check-in has been saved!")
        self.on_pre_enter()


class NamazScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        t = current_theme()
        today = today_str()
        data.setdefault("namaz_log", {})
        data["namaz_log"].setdefault(today, [])

        root = BoxLayout(orientation="vertical")
        root.add_widget(header("🕌 Namaz & Quran", color=ORANGE, subtitle=f"{month_name()} timings for Islamabad"))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(14), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))

        card = Card(orientation="vertical", size_hint_y=None, height=dp(102))
        prayer, prayer_time = get_next_prayer()
        card.add_widget(Label(text=f"Next Prayer: {prayer}", color=t["text"], bold=True, font_size=dp(16)))
        card.add_widget(Label(text=f"At {prayer_time}", color=ORANGE, bold=True, font_size=dp(18)))
        content.add_widget(card)

        for prayer_name, prayer_time in get_today_namaz_times().items():
            done = prayer_name in data["namaz_log"][today]
            row = Card(orientation="horizontal", size_hint_y=None, height=dp(74), spacing=dp(8))
            btn = make_button("✓" if done else "○", bg=GREEN if done else GRAY, height=dp(42), font_size=dp(18))
            btn.size_hint_x = None
            btn.width = dp(42)
            btn.bind(on_release=lambda _, p=prayer_name: toggle_namaz(p))
            row.add_widget(btn)
            col = BoxLayout(orientation="vertical")
            col.add_widget(Label(text=f"{prayer_name}", color=t["text"], bold=True))
            col.add_widget(Label(text=prayer_time, color=t["muted"]))
            row.add_widget(col)
            content.add_widget(row)

        q_done = today in data["quran_log"]
        qrow = Card(orientation="horizontal", size_hint_y=None, height=dp(74), spacing=dp(8))
        qbtn = make_button("✓" if q_done else "○", bg=GREEN if q_done else GRAY, height=dp(42), font_size=dp(18))
        qbtn.size_hint_x = None
        qbtn.width = dp(42)
        qbtn.bind(on_release=lambda *_: toggle_quran())
        qrow.add_widget(qbtn)
        qcol = BoxLayout(orientation="vertical")
        qcol.add_widget(Label(text="📖 Quran Recitation", color=t["text"], bold=True))
        qcol.add_widget(Label(text="Mark once per day", color=t["muted"]))
        qrow.add_widget(qcol)
        content.add_widget(qrow)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)


class PointsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        t = current_theme()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("🏆 Points & Badges", back_to="more", color=ORANGE, subtitle="Motivation and milestones"))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(14), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))

        stats = BoxLayout(size_hint_y=None, height=dp(120), spacing=dp(8))
        card1 = Card(bg=ORANGE, orientation="vertical")
        card1.add_widget(Label(text=str(data["points"]), color=WHITE, bold=True, font_size=dp(30)))
        card1.add_widget(Label(text="Points", color=WHITE))
        card2 = Card(bg=PURPLE, orientation="vertical")
        card2.add_widget(Label(text=str(data["level"]), color=WHITE, bold=True, font_size=dp(30)))
        card2.add_widget(Label(text="Level", color=WHITE))
        stats.add_widget(card1)
        stats.add_widget(card2)
        content.add_widget(stats)

        content.add_widget(SectionTitle("Badges Earned", color=ORANGE))
        if not data["badges"]:
            empty = Card(orientation="vertical", size_hint_y=None, height=dp(60))
            empty.add_widget(Label(text="No badges yet - keep going!", color=t["muted"]))
            content.add_widget(empty)
        else:
            for badge in data["badges"][:20]:
                row = Card(orientation="horizontal", size_hint_y=None, height=dp(52))
                row.add_widget(Label(text=badge, color=t["text"], bold=True))
                content.add_widget(row)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)


class SettingsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        t = current_theme()
        root = BoxLayout(orientation="vertical")
        root.add_widget(header("⚙ Settings", back_to="more", color=MID, subtitle="Theme and data controls"))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(14), spacing=dp(10))
        content.bind(minimum_height=content.setter("height"))

        mode_text = "Switch to Light Mode" if data.get("dark_mode") else "Switch to Dark Mode"
        dark_btn = make_button(f"🌓 {mode_text}", bg=MID)
        dark_btn.bind(on_release=self.toggle_dark)
        content.add_widget(dark_btn)

        note = Card(orientation="vertical", size_hint_y=None, height=dp(92))
        note.add_widget(Label(text="Your data is saved automatically in app storage.", color=t["text"]))
        note.add_widget(Label(text="It stays after closing and reopening the app.", color=t["muted"]))
        content.add_widget(note)

        reset_btn = make_button("♻ Reset All Data", bg=RED)
        reset_btn.bind(on_release=self.reset_data)
        content.add_widget(reset_btn)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def toggle_dark(self, *_):
        data["dark_mode"] = not data.get("dark_mode", False)
        set_window_theme()
        save_data()
        self.on_pre_enter()

    def reset_data(self, *_):
        global data
        data = copy.deepcopy(DEFAULT_DATA)
        save_data()
        set_window_theme()
        show_popup("Reset", "All data has been reset.")
        if sm:
            sm.current = "home"


# ---------------------- APP ----------------------

class RoutineApp(App):
    def build(self):
        global data, DATA_FILE, sm

        self.data_file = os.path.join(self.user_data_dir, "routine_data.json")
        legacy_file = os.path.join(os.getcwd(), "routine_data.json")

        if os.path.exists(self.data_file):
            data = load_data(self.data_file)
        elif os.path.exists(legacy_file):
            data = load_data(legacy_file)
        else:
            data = copy.deepcopy(DEFAULT_DATA)

        data = ensure_defaults(data)
        set_window_theme()

        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(HabitsScreen(name="habits"))
        sm.add_widget(AddHabitScreen(name="add_habit"))
        sm.add_widget(TasksScreen(name="tasks"))
        sm.add_widget(AddTaskScreen(name="add_task"))
        sm.add_widget(NamazScreen(name="namaz"))
        sm.add_widget(ReportsScreen(name="reports"))
        sm.add_widget(MoreScreen(name="more"))
        sm.add_widget(ExamsScreen(name="exams"))
        sm.add_widget(ProjectsScreen(name="projects"))
        sm.add_widget(CheckinScreen(name="checkin"))
        sm.add_widget(PointsScreen(name="points"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.current = "home"
        return sm

    def on_stop(self):
        save_data()


if __name__ == "__main__":
    RoutineApp().run()
