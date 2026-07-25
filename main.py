import json
import os
from datetime import date, timedelta

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout

DATA_FILE = "routine_data.json"

# ---------------------------------------------------
# DATA HANDLING (same logic as console/Tkinter versions)
# ---------------------------------------------------

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        return {
            "tasks": [], "namaz_log": {}, "quran_log": [],
            "entertainment_log": [], "points": 0, "level": 1,
            "badges": [], "exams": [], "projects": [], "notes": {}
        }

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

def get_today_namaz_times():
    return NAMAZ_TIMES[date.today().month]

ENTERTAINMENT_TIME = "Flexible - after completing today's tasks"

MOODS = {
    "1": "Happy",
    "2": "Normal",
    "3": "Tired/Low",
    "4": "Frustrated",
    "5": "Sleepy"
}

def show_popup(title, message):
    popup = Popup(title=title, content=Label(text=message),
                   size_hint=(0.8, 0.4))
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
# SCREEN: Main Menu
# ---------------------------------------------------

class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=8)
        layout.add_widget(Label(text="My Daily Routine Manager",
                                 font_size=22, size_hint_y=None, height=60, bold=True))

        buttons = [
            ("View Today's Routine", "view_today"),
            ("Add New Task", "add_task"),
            ("Mark as Done", "mark_done"),
            ("Exam Days", "exams"),
            ("Projects & Goals", "projects"),
            ("Daily Note & Mood", "checkin"),
            ("Weekly Report", "weekly"),
            ("Monthly Report", "monthly"),
            ("Points / Level / Badges", "points"),
        ]
        for text, screen_name in buttons:
            btn = Button(text=text, size_hint_y=None, height=50)
            btn.bind(on_release=lambda inst, s=screen_name: self.go(s))
            layout.add_widget(btn)
        self.add_widget(layout)

    def go(self, screen_name):
        self.manager.current = screen_name


def make_back_button(manager):
    btn = Button(text="< Back to Menu", size_hint_y=None, height=45)
    btn.bind(on_release=lambda inst: setattr(manager, "current", "main"))
    return btn

# ---------------------------------------------------
# SCREEN: View Today's Routine
# ---------------------------------------------------

class ViewTodayScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        root_layout = BoxLayout(orientation="vertical")
        root_layout.add_widget(make_back_button(self.manager))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=10, spacing=4)
        content.bind(minimum_height=content.setter("height"))

        today = str(date.today())
        content.add_widget(Label(text="--- Tasks ---", size_hint_y=None, height=30, bold=True))
        if not data["tasks"]:
            content.add_widget(Label(text="No tasks added yet.", size_hint_y=None, height=30))
        for t in data["tasks"]:
            status = "Done" if today in t["done_dates"] else "Not Done"
            note = f" | Note: {t['note']}" if t.get("note") else ""
            content.add_widget(Label(text=f"{t['name']} - {t['time']} [{status}]{note}",
                                      size_hint_y=None, height=30))

        content.add_widget(Label(text="--- Namaz ---", size_hint_y=None, height=30, bold=True))
        times = get_today_namaz_times()
        done_prayers = data["namaz_log"].get(today, [])
        for p in times:
            status = "Done" if p in done_prayers else "Not Done"
            content.add_widget(Label(text=f"{p} ({times[p]}) [{status}]",
                                      size_hint_y=None, height=30))

        content.add_widget(Label(text="--- Quran ---", size_hint_y=None, height=30, bold=True))
        q_status = "Done" if today in data["quran_log"] else "Not Done"
        content.add_widget(Label(text=f"Quran Recitation [{q_status}]", size_hint_y=None, height=30))

        content.add_widget(Label(text=f"--- Entertainment ({ENTERTAINMENT_TIME}) ---",
                                  size_hint_y=None, height=30, bold=True))
        e_status = "Done" if today in data["entertainment_log"] else "Not Done"
        content.add_widget(Label(text=f"Status: [{e_status}]", size_hint_y=None, height=30))

        scroll.add_widget(content)
        root_layout.add_widget(scroll)
        self.add_widget(root_layout)

# ---------------------------------------------------
# SCREEN: Add New Task
# ---------------------------------------------------

class AddTaskScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=20, spacing=8)
        layout.add_widget(make_back_button(self.manager))

        layout.add_widget(Label(text="Task Name:", size_hint_y=None, height=25))
        self.name_input = TextInput(size_hint_y=None, height=40, multiline=False)
        layout.add_widget(self.name_input)

        layout.add_widget(Label(text="Time (e.g. 5:00 PM):", size_hint_y=None, height=25))
        self.time_input = TextInput(size_hint_y=None, height=40, multiline=False)
        layout.add_widget(self.time_input)

        recur_row = BoxLayout(size_hint_y=None, height=40)
        self.recur_check = CheckBox()
        recur_row.add_widget(self.recur_check)
        recur_row.add_widget(Label(text="Repeats daily"))
        layout.add_widget(recur_row)

        layout.add_widget(Label(text="Note (optional):", size_hint_y=None, height=25))
        self.note_input = TextInput(size_hint_y=None, height=40, multiline=False)
        layout.add_widget(self.note_input)

        save_btn = Button(text="Add Task", size_hint_y=None, height=50)
        save_btn.bind(on_release=self.save_task)
        layout.add_widget(save_btn)

        self.add_widget(layout)

    def save_task(self, instance):
        name = self.name_input.text
        time_val = self.time_input.text
        if not name or not time_val:
            show_popup("Missing Info", "Please enter task name and time.")
            return
        task = {
            "name": name, "time": time_val,
            "recurring": self.recur_check.active,
            "note": self.note_input.text,
            "done_dates": []
        }
        data["tasks"].append(task)
        show_popup("Saved", f"Task '{name}' added!")
        self.name_input.text = ""
        self.time_input.text = ""
        self.note_input.text = ""
        self.recur_check.active = False

# ---------------------------------------------------
# SCREEN: Mark as Done
# ---------------------------------------------------

class MarkDoneScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=20, spacing=8)
        layout.add_widget(make_back_button(self.manager))
        layout.add_widget(Label(text="What do you want to mark done?",
                                 size_hint_y=None, height=40, bold=True))

        options = [
            ("Mark a Task", "mark_task"),
            ("Mark Namaz", "mark_namaz"),
            ("Mark Quran Recitation", None),
            ("Mark Entertainment Time", None),
        ]
        for text, screen_name in options:
            btn = Button(text=text, size_hint_y=None, height=50)
            if screen_name:
                btn.bind(on_release=lambda inst, s=screen_name: setattr(self.manager, "current", s))
            elif text == "Mark Quran Recitation":
                btn.bind(on_release=self.mark_quran)
            elif text == "Mark Entertainment Time":
                btn.bind(on_release=self.mark_entertainment)
            layout.add_widget(btn)

        self.add_widget(layout)

    def mark_quran(self, instance):
        today = str(date.today())
        if today in data["quran_log"]:
            show_popup("Already Done", "Quran already marked done today!")
        else:
            data["quran_log"].append(today)
            add_points(15)
            show_popup("Done", "Quran recitation marked as done!")

    def mark_entertainment(self, instance):
        today = str(date.today())
        if today in data["entertainment_log"]:
            show_popup("Already Done", "Entertainment already marked done today!")
        else:
            data["entertainment_log"].append(today)
            show_popup("Done", "Entertainment marked as done!")


class MarkTaskScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=10, spacing=6)
        back_btn = Button(text="< Back", size_hint_y=None, height=45)
        back_btn.bind(on_release=lambda inst: setattr(self.manager, "current", "mark_done"))
        layout.add_widget(back_btn)

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, spacing=6)
        content.bind(minimum_height=content.setter("height"))

        today = str(date.today())
        for i, t in enumerate(data["tasks"]):
            status = "Done" if today in t["done_dates"] else "Not Done"
            btn = Button(text=f"{t['name']} [{status}]", size_hint_y=None, height=50)
            btn.bind(on_release=lambda inst, idx=i: self.mark(idx))
            content.add_widget(btn)

        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def mark(self, index):
        today = str(date.today())
        if today not in data["tasks"][index]["done_dates"]:
            data["tasks"][index]["done_dates"].append(today)
            add_points(10)
            check_perfect_day()
            show_popup("Done", "Task marked as done!")
        else:
            show_popup("Already Done", "Already marked done today.")
        self.on_pre_enter()


class MarkNamazScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=10, spacing=6)
        back_btn = Button(text="< Back", size_hint_y=None, height=45)
        back_btn.bind(on_release=lambda inst: setattr(self.manager, "current", "mark_done"))
        layout.add_widget(back_btn)

        today = str(date.today())
        if today not in data["namaz_log"]:
            data["namaz_log"][today] = []
        times = get_today_namaz_times()
        self.prayers = list(times.keys())

        for p in self.prayers:
            status = "Done" if p in data["namaz_log"][today] else "Not Done"
            btn = Button(text=f"{p} ({times[p]}) [{status}]", size_hint_y=None, height=50)
            btn.bind(on_release=lambda inst, prayer=p: self.mark(prayer))
            layout.add_widget(btn)

        self.add_widget(layout)

    def mark(self, prayer_name):
        today = str(date.today())
        if prayer_name not in data["namaz_log"][today]:
            data["namaz_log"][today].append(prayer_name)
            add_points(15)
            show_popup("Done", f"{prayer_name} marked as done!")
        else:
            show_popup("Already Done", "Already marked done today.")
        self.on_pre_enter()

# ---------------------------------------------------
# SCREEN: Exam Days
# ---------------------------------------------------

class ExamsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=15, spacing=6)
        layout.add_widget(make_back_button(self.manager))

        layout.add_widget(Label(text="Subject:", size_hint_y=None, height=25))
        self.subject_input = TextInput(size_hint_y=None, height=40, multiline=False)
        layout.add_widget(self.subject_input)

        layout.add_widget(Label(text="Exam Date (YYYY-MM-DD):", size_hint_y=None, height=25))
        self.date_input = TextInput(size_hint_y=None, height=40, multiline=False)
        layout.add_widget(self.date_input)

        add_btn = Button(text="Add Exam", size_hint_y=None, height=45)
        add_btn.bind(on_release=self.add_exam)
        layout.add_widget(add_btn)

        scroll = ScrollView()
        self.list_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=4)
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        scroll.add_widget(self.list_box)
        layout.add_widget(scroll)

        self.add_widget(layout)
        self.refresh_list()

    def refresh_list(self):
        self.list_box.clear_widgets()
        today = date.today()
        if not data["exams"]:
            self.list_box.add_widget(Label(text="No exams added yet.", size_hint_y=None, height=30))
        for exam in data["exams"]:
            try:
                exam_date = date.fromisoformat(exam["date"])
                days_left = (exam_date - today).days
                if days_left > 0:
                    txt = f"{exam['subject']} - in {days_left} day(s) ({exam['date']})"
                elif days_left == 0:
                    txt = f"{exam['subject']} - TODAY!"
                else:
                    txt = f"{exam['subject']} - already passed ({exam['date']})"
            except ValueError:
                txt = f"{exam['subject']} - invalid date format"
            self.list_box.add_widget(Label(text=txt, size_hint_y=None, height=30))

    def add_exam(self, instance):
        subject = self.subject_input.text
        exam_date = self.date_input.text
        if not subject or not exam_date:
            show_popup("Missing Info", "Please enter subject and date.")
            return
        data["exams"].append({"subject": subject, "date": exam_date})
        self.subject_input.text = ""
        self.date_input.text = ""
        self.refresh_list()

# ---------------------------------------------------
# SCREEN: Projects & Goals
# ---------------------------------------------------

class ProjectsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=15, spacing=6)
        layout.add_widget(make_back_button(self.manager))

        layout.add_widget(Label(text="Title:", size_hint_y=None, height=25))
        self.title_input = TextInput(size_hint_y=None, height=40, multiline=False)
        layout.add_widget(self.title_input)

        layout.add_widget(Label(text="Target End Date (YYYY-MM-DD):", size_hint_y=None, height=25))
        self.end_input = TextInput(size_hint_y=None, height=40, multiline=False)
        layout.add_widget(self.end_input)

        add_btn = Button(text="Add Project/Goal", size_hint_y=None, height=45)
        add_btn.bind(on_release=self.add_project)
        layout.add_widget(add_btn)

        scroll = ScrollView()
        self.list_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=4)
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        scroll.add_widget(self.list_box)
        layout.add_widget(scroll)

        self.add_widget(layout)
        self.refresh_list()

    def refresh_list(self):
        self.list_box.clear_widgets()
        today = date.today()
        if not data["projects"]:
            self.list_box.add_widget(Label(text="No projects added yet.", size_hint_y=None, height=30))
        for i, proj in enumerate(data["projects"]):
            status = "Completed" if proj["completed"] else "In Progress"
            try:
                end_date = date.fromisoformat(proj["end"])
                days_left = (end_date - today).days
                info = "" if proj["completed"] else (
                    f" - {days_left}d left" if days_left > 0 else
                    " - due TODAY" if days_left == 0 else " - overdue")
            except ValueError:
                info = ""
            row = BoxLayout(size_hint_y=None, height=45)
            row.add_widget(Label(text=f"{proj['title']} [{status}]{info}"))
            if not proj["completed"]:
                done_btn = Button(text="Complete", size_hint_x=0.4)
                done_btn.bind(on_release=lambda inst, idx=i: self.complete(idx))
                row.add_widget(done_btn)
            self.list_box.add_widget(row)

    def add_project(self, instance):
        title = self.title_input.text
        end = self.end_input.text
        if not title or not end:
            show_popup("Missing Info", "Please enter title and end date.")
            return
        data["projects"].append({"title": title, "start": str(date.today()),
                                  "end": end, "completed": False})
        self.title_input.text = ""
        self.end_input.text = ""
        self.refresh_list()

    def complete(self, index):
        data["projects"][index]["completed"] = True
        self.refresh_list()

# ---------------------------------------------------
# SCREEN: Daily Note & Mood
# ---------------------------------------------------

class CheckinScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=15, spacing=8)
        layout.add_widget(make_back_button(self.manager))
        layout.add_widget(Label(text="How do you feel today?", size_hint_y=None, height=35, bold=True))

        self.selected_mood = "2"
        mood_grid = GridLayout(cols=1, size_hint_y=None, height=180, spacing=4)
        self.mood_buttons = {}
        for key, val in MOODS.items():
            btn = Button(text=val, size_hint_y=None, height=35)
            btn.bind(on_release=lambda inst, k=key: self.pick_mood(k))
            mood_grid.add_widget(btn)
            self.mood_buttons[key] = btn
        layout.add_widget(mood_grid)

        layout.add_widget(Label(text="Write anything about your day:", size_hint_y=None, height=25))
        self.note_input = TextInput(size_hint_y=None, height=120, multiline=True)
        layout.add_widget(self.note_input)

        save_btn = Button(text="Save Check-in", size_hint_y=None, height=50)
        save_btn.bind(on_release=self.save_checkin)
        layout.add_widget(save_btn)

        self.add_widget(layout)

    def pick_mood(self, key):
        self.selected_mood = key
        show_popup("Mood Selected", MOODS[key])

    def save_checkin(self, instance):
        today = str(date.today())
        data["notes"][today] = {
            "mood": MOODS.get(self.selected_mood, "Not specified"),
            "note": self.note_input.text.strip()
        }
        show_popup("Saved", "Your daily check-in has been saved!")

# ---------------------------------------------------
# SCREEN: Weekly Report
# ---------------------------------------------------

class WeeklyReportScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical")
        layout.add_widget(make_back_button(self.manager))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=10, spacing=4)
        content.bind(minimum_height=content.setter("height"))

        today = date.today()
        week_dates = [str(today - timedelta(days=i)) for i in range(7)]
        week_dates.reverse()

        total_tasks_done = 0
        for t in data["tasks"]:
            total_tasks_done += sum(1 for d in t["done_dates"] if d in week_dates)
        content.add_widget(Label(text=f"Tasks completed this week: {total_tasks_done}",
                                  size_hint_y=None, height=30))

        namaz_count = sum(len(data["namaz_log"].get(d, [])) for d in week_dates)
        content.add_widget(Label(text=f"Namaz prayed: {namaz_count} / 35",
                                  size_hint_y=None, height=30))

        quran_count = sum(1 for d in week_dates if d in data["quran_log"])
        content.add_widget(Label(text=f"Quran recitation: {quran_count} / 7 days",
                                  size_hint_y=None, height=30))

        ent_count = sum(1 for d in week_dates if d in data["entertainment_log"])
        content.add_widget(Label(text=f"Entertainment: {ent_count} / 7 days",
                                  size_hint_y=None, height=30))

        content.add_widget(Label(text="--- Moods this week ---", size_hint_y=None, height=30, bold=True))
        for d in week_dates:
            if d in data["notes"]:
                content.add_widget(Label(text=f"{d}: {data['notes'][d]['mood']}",
                                          size_hint_y=None, height=30))

        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)

# ---------------------------------------------------
# SCREEN: Monthly Report
# ---------------------------------------------------

class MonthlyReportScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical")
        layout.add_widget(make_back_button(self.manager))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=10, spacing=4)
        content.bind(minimum_height=content.setter("height"))

        today = date.today()
        month_prefix = today.strftime("%Y-%m")
        days_passed = today.day

        total_tasks_done = 0
        for t in data["tasks"]:
            total_tasks_done += sum(1 for d in t["done_dates"] if d.startswith(month_prefix))
        content.add_widget(Label(text=f"Tasks completed this month: {total_tasks_done}",
                                  size_hint_y=None, height=30))

        namaz_count = sum(len(p) for d, p in data["namaz_log"].items() if d.startswith(month_prefix))
        content.add_widget(Label(text=f"Namaz prayed: {namaz_count} / {days_passed * 5}",
                                  size_hint_y=None, height=30))

        quran_count = sum(1 for d in data["quran_log"] if d.startswith(month_prefix))
        content.add_widget(Label(text=f"Quran recitation: {quran_count} / {days_passed} days",
                                  size_hint_y=None, height=30))

        ent_count = sum(1 for d in data["entertainment_log"] if d.startswith(month_prefix))
        content.add_widget(Label(text=f"Entertainment: {ent_count} / {days_passed} days",
                                  size_hint_y=None, height=30))

        completed_projects = sum(1 for p in data["projects"] if p["completed"])
        content.add_widget(Label(text=f"Projects completed: {completed_projects} / {len(data['projects'])}",
                                  size_hint_y=None, height=30))

        content.add_widget(Label(text="--- Moods this month ---", size_hint_y=None, height=30, bold=True))
        for d, entry in data["notes"].items():
            if d.startswith(month_prefix):
                content.add_widget(Label(text=f"{d}: {entry['mood']}", size_hint_y=None, height=30))

        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)

# ---------------------------------------------------
# SCREEN: Points / Level / Badges
# ---------------------------------------------------

class PointsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=15, spacing=8)
        layout.add_widget(make_back_button(self.manager))

        layout.add_widget(Label(text=f"Points: {data['points']}", size_hint_y=None, height=35, font_size=18))
        layout.add_widget(Label(text=f"Level: {data['level']}", size_hint_y=None, height=35, font_size=18))
        layout.add_widget(Label(text="Badges Earned:", size_hint_y=None, height=30, bold=True))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, spacing=4)
        content.bind(minimum_height=content.setter("height"))
        if not data["badges"]:
            content.add_widget(Label(text="No badges yet - keep going!", size_hint_y=None, height=30))
        else:
            for b in data["badges"]:
                content.add_widget(Label(text=f"- {b}", size_hint_y=None, height=30))
        scroll.add_widget(content)
        layout.add_widget(scroll)

        self.add_widget(layout)

# ---------------------------------------------------
# MAIN APP
# ---------------------------------------------------

class RoutineApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name="main"))
        sm.add_widget(ViewTodayScreen(name="view_today"))
        sm.add_widget(AddTaskScreen(name="add_task"))
        sm.add_widget(MarkDoneScreen(name="mark_done"))
        sm.add_widget(MarkTaskScreen(name="mark_task"))
        sm.add_widget(MarkNamazScreen(name="mark_namaz"))
        sm.add_widget(ExamsScreen(name="exams"))
        sm.add_widget(ProjectsScreen(name="projects"))
        sm.add_widget(CheckinScreen(name="checkin"))
        sm.add_widget(WeeklyReportScreen(name="weekly"))
        sm.add_widget(MonthlyReportScreen(name="monthly"))
        sm.add_widget(PointsScreen(name="points"))
        return sm

    def on_stop(self):
        save_data()


if __name__ == "__main__":
    RoutineApp().run()
