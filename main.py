import json
import os
from datetime import date, timedelta
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
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle
from kivy.metrics import dp

DATA_FILE = "routine_data.json"
# ================= COLOR THEME =================
LIGHT = {"bg": (0.96, 0.94, 0.92, 1), "card": (1, 1, 1, 1), "text": (0.1, 0.1, 0.1, 1), "muted": (0.5, 0.5, 0.5, 1)}
DARK = {"bg": (0.12, 0.11, 0.10, 1), "card": (0.18, 0.16, 0.15, 1), "text": (0.95, 0.93, 0.90, 1), "muted": (0.6, 0.6, 0.6, 1)}
ORANGE = (0.91, 0.35, 0.05, 1); GOLD = (0.97, 0.66, 0.23, 1); TEAL = (0.18, 0.55, 0.47, 1)
PURPLE = (0.47, 0.31, 0.66, 1); PINK = (0.78, 0.27, 0.36, 1); BLUE = (0.18, 0.43, 0.63, 1); WHITE = (1,1,1,1); GRAY = (0.85,0.82,0.78,1)

# ================= DATA HANDLING =================
def load_data():
    default = {"tasks": [], "habits": [], "namaz_log": {}, "quran_log": [], "points": 0, "level": 1,
               "badges": [], "exams": [], "projects": [], "notes": {}, "dark_mode": False, "last_active": str(date.today())}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            d = json.load(f)
            for k, v in default.items():
                if k not in d: d[k] = v
            return d
    return default

def save_data():
    with open(DATA_FILE, "w") as f: json.dump(data, f, indent=4)

data = load_data()
def theme(): return DARK if data.get("dark_mode") else LIGHT

# ================= GLOBAL NAVIGATION & HELPERS =================
sm = None
def go_screen(name): sm.current = name

def show_popup(title, message):
    t = theme()
    popup = Popup(title=title, content=Label(text=message, color=t["text"], halign="center", valign="middle", font_size=dp(16)),
                  size_hint=(0.8, 0.4), title_color=t["text"], separator_color=ORANGE, title_size=dp(18))
    popup.open()

def add_points(amount):
    data["points"] += amount
    new_level = (data["points"] // 100) + 1
    if new_level > data["level"]:
        data["level"] = new_level
        badge = f"Level {data['level']} Reached"
        if badge not in data["badges"]: data["badges"].append(badge)
        show_popup("Level Up!", f"Congrats! You are now Level {data['level']}!")

def update_streak():
    today = str(date.today())
    last = data.get("last_active", today)
    if last != today:
        if (date.fromisoformat(today) - date.fromisoformat(last)).days > 1:
            data["streak"] = 0
        else:
            data["streak"] = data.get("streak", 0) + 1
        data["last_active"] = today

# ================= POLISHED UI COMPONENTS (INCREASED TEXT SIZE) =================
class ModernCard(BoxLayout):
    def __init__(self, bg=None, radius=15, padding_val=12, **kwargs):
        super().__init__(**kwargs)
        self.padding = padding_val
        self.spacing = 10
        self._bg_color = bg if bg else theme()["card"]
        with self.canvas.before:
            Color(*self._bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
        self.bind(pos=self._update, size=self._update)
    def _update(self, *args): self._rect.pos, self._rect.size = self.pos, self.size

class ModernButton(Button):
    def __init__(self, text, height=dp(55), bg=ORANGE, fg=WHITE, font_size=dp(16), radius=10, **kwargs):
        super().__init__(text=text, size_hint_y=None, height=height, background_normal="", background_color=(0,0,0,0), color=fg, font_size=font_size, bold=True, **kwargs)
        self.radius = radius
        self.bg = bg
        with self.canvas.before:
            Color(*bg)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
        self.bind(pos=self._update, size=self._update)
    def _update(self, *args): self.rect.pos, self.rect.size = self.pos, self.size

class HeaderBar(BoxLayout):
    def __init__(self, title, back_to=None, color=ORANGE, **kwargs):
        super().__init__(orientation="vertical", size_hint_y=None, height=dp(85), padding=[dp(15), dp(20), dp(15), dp(10)], **kwargs)
        with self.canvas.before:
            Color(*color)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update, size=self._update)
        row = BoxLayout(size_hint_y=None, height=dp(45))
        if back_to:
            b = Button(text="< Back", size_hint_x=None, width=dp(80), background_normal="", background_color=(0,0,0,0), color=WHITE, font_size=dp(16), bold=True)
            b.bind(on_release=lambda i: go_screen(back_to))
            row.add_widget(b)
        row.add_widget(Label(text=title, font_size=dp(22), bold=True, color=WHITE, halign="center"))
        self.add_widget(row)
    def _update(self, *args): self.rect.pos, self.rect.size = self.pos, self.size

class BottomNav(BoxLayout):
    def __init__(self, active, **kwargs):
        super().__init__(size_hint_y=None, height=dp(70), spacing=dp(5), padding=dp(5), **kwargs)
        t = theme()
        with self.canvas.before:
            Color(*t["bg"])
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update, size=self._update)
        items = [("Home", "home"), ("Habits", "habits"), ("Tasks", "tasks"), ("Reports", "reports"), ("More", "more")]
        for label, name in items:
            c = ORANGE if name == active else t["muted"]
            btn = Button(text=label, background_normal="", background_color=(0,0,0,0), color=c, font_size=dp(13), bold=(name==active))
            btn.bind(on_release=lambda inst, s=name: go_screen(s))
            self.add_widget(btn)
    def _update(self, *args): self.rect.pos, self.rect.size = self.pos, self.size

# ================= SCREENS =================
class HomeScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        update_streak()
        t = theme()
        root = BoxLayout(orientation="vertical")
        root.add_widget(HeaderBar("Assalam-o-Alaikum", color=ORANGE))
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(12))
        content.bind(minimum_height=content.setter("height"))
        
        card = ModernCard(orientation="horizontal", height=dp(150), padding=dp(15), bg=t["card"])
        col1 = BoxLayout(orientation="vertical")
        col1.add_widget(Label(text=f"Streak: {data.get('streak', 0)} 🔥", font_size=dp(18), color=ORANGE, bold=True))
        col1.add_widget(Label(text=f"Points: {data['points']}", font_size=dp(16), color=PURPLE))
        col1.add_widget(Label(text=f"Level: {data['level']}", font_size=dp(16), color=GOLD))
        col2 = BoxLayout(orientation="vertical", size_hint_x=None, width=dp(100))
        col2.add_widget(Label(text="50%", font_size=dp(30), color=TEAL, bold=True))
        card.add_widget(col1); card.add_widget(col2)
        content.add_widget(card)

        content.add_widget(Label(text="Pomodoro Timer", font_size=dp(20), bold=True, color=ORANGE))
        pcard = ModernCard(orientation="horizontal", height=dp(90), bg=t["card"])
        pcard.add_widget(Label(text="25:00", font_size=dp(32), color=PINK, bold=True))
        btn = ModernButton("Start Focus", height=dp(55), bg=PINK)
        btn.bind(on_release=lambda i: show_popup("Timer", "Pomodoro started! (Mock feature)"))
        pcard.add_widget(btn)
        content.add_widget(pcard)

        scroll.add_widget(content)
        root.add_widget(scroll)
        root.add_widget(BottomNav("home"))
        self.add_widget(root)

class MoreScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(HeaderBar("More Options", color=PURPLE))
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(12))
        content.bind(minimum_height=content.setter("height"))
        
        for label, sc, c in [("Exam Days", "exams", PINK), ("Projects", "projects", BLUE), ("Daily Note", "checkin", GOLD), ("Namaz & Quran", "namaz", ORANGE)]:
            btn = ModernButton(label, height=dp(70), bg=c, font_size=dp(18))
            btn.bind(on_release=lambda inst, s=sc: go_screen(s))
            content.add_widget(btn)

        dm = "Light Mode" if data.get("dark_mode") else "Dark Mode"
        btn = ModernButton(f"Switch to {dm}", height=dp(70), bg=(0.4,0.4,0.4,1), font_size=dp(18))
        btn.bind(on_release=self.toggle_dark)
        content.add_widget(btn)

        exp = ModernButton("Export Data to Desktop", height=dp(70), bg=(0.1,0.6,0.3,1), font_size=dp(18))
        exp.bind(on_release=self.export_data)
        content.add_widget(exp)

        scroll.add_widget(content)
        root.add_widget(scroll)
        root.add_widget(BottomNav("more"))
        self.add_widget(root)

    def toggle_dark(self, inst):
        data["dark_mode"] = not data.get("dark_mode", False)
        save_data()
        self.on_pre_enter()

    def export_data(self, inst):
        desktop = os.path.join(os.path.expanduser("~"), "Desktop", "my_routine_backup.txt")
        with open(desktop, "w") as f:
            f.write(f"Data exported on: {date.today()}\n")
            f.write(json.dumps(data, indent=4))
        show_popup("Exported!", f"Saved to: {desktop}")

class NamazScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(HeaderBar("Namaz & Quran", back_to="more", color=ORANGE))
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(12))
        content.bind(minimum_height=content.setter("height"))
        content.add_widget(Label(text="Tap to toggle today's prayers", font_size=dp(16), color=theme()["text"]))
        for p in ["Fajr", "Zuhr", "Asr", "Maghrib", "Isha"]:
            card = ModernCard(orientation="horizontal", height=dp(70))
            card.add_widget(Label(text=p, font_size=dp(18), bold=True, color=theme()["text"]))
            btn = ModernButton("✔", height=dp(40), width=dp(40), bg=TEAL, font_size=dp(16))
            btn.size_hint_x = None
            card.add_widget(btn)
            content.add_widget(card)
        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

class ExamsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(HeaderBar("Exams", back_to="more", color=PINK))
        root.add_widget(Label(text="Add Exam Screen", font_size=dp(18), color=theme()["text"]))
        self.add_widget(root)

class ProjectsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(HeaderBar("Projects", back_to="more", color=BLUE))
        root.add_widget(Label(text="Project Tracker", font_size=dp(18), color=theme()["text"]))
        self.add_widget(root)

class CheckinScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(HeaderBar("Daily Note", back_to="more", color=GOLD))
        root.add_widget(Label(text="Mood Tracker", font_size=dp(18), color=theme()["text"]))
        self.add_widget(root)

# ================= MAIN APP =================
class RoutineApp(App):
    def build(self):
        global sm
        Window.clearcolor = theme()["bg"]
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(NamazScreen(name="namaz"))
        sm.add_widget(MoreScreen(name="more"))
        sm.add_widget(ExamsScreen(name="exams"))
        sm.add_widget(ProjectsScreen(name="projects"))
        sm.add_widget(CheckinScreen(name="checkin"))
        return sm
    def on_stop(self): save_data()

if __name__ == "__main__": RoutineApp().run()
