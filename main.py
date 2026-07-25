import tkinter as tk
from tkinter import messagebox
import json
import os

# ================= WINDOW =================
root = tk.Tk()
root.title("📅 Daily Routine App")
root.geometry("600x500")
root.config(bg="#1e1e2f")

# ================= COLORS =================
bg_color = "#1e1e2f"
frame_color = "#2b2b3c"
btn_color = "#3a3a5a"
text_color = "white"

# ================= FILE =================
FILE_NAME = "tasks.json"

# ================= FUNCTIONS =================
def add_task():
    task = entry.get()
    if task != "":
        listbox.insert(tk.END, "🕒 " + task)
        entry.delete(0, tk.END)
        save_tasks()
    else:
        messagebox.showwarning("Warning", "Enter a task!")

def delete_task():
    try:
        selected = listbox.curselection()[0]
        listbox.delete(selected)
        save_tasks()
    except:
        messagebox.showwarning("Warning", "Select a task!")

def mark_done():
    try:
        selected = listbox.curselection()[0]
        task = listbox.get(selected)
        listbox.delete(selected)
        listbox.insert(selected, "✅ " + task[2:])
        save_tasks()
    except:
        messagebox.showwarning("Warning", "Select a task!")

def save_tasks():
    tasks = listbox.get(0, tk.END)
    with open(FILE_NAME, "w") as f:
        json.dump(tasks, f)

def load_tasks():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as f:
            tasks = json.load(f)
            for task in tasks:
                listbox.insert(tk.END, task)

# ================= UI =================
title = tk.Label(root, text="📅 My Daily Routine",
                 bg=bg_color, fg=text_color, font=("Arial", 20))
title.pack(pady=10)

frame = tk.Frame(root, bg=frame_color)
frame.pack(pady=10)

listbox = tk.Listbox(frame, width=50, height=15,
                     bg="#2d2d2d", fg="white", font=("Arial", 12))
listbox.pack(side="left")

scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side="right", fill="y")

listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=listbox.yview)

entry = tk.Entry(root, width=40, font=("Arial", 12))
entry.pack(pady=10)

# ================= BUTTONS =================
btn_frame = tk.Frame(root, bg=bg_color)
btn_frame.pack()

tk.Button(btn_frame, text="➕ Add Task", command=add_task,
          bg=btn_color, fg="white").pack(side="left", padx=5)

tk.Button(btn_frame, text="✅ Done", command=mark_done,
          bg=btn_color, fg="white").pack(side="left", padx=5)

tk.Button(btn_frame, text="❌ Delete", command=delete_task,
          bg=btn_color, fg="white").pack(side="left", padx=5)

# ================= LOAD =================
load_tasks()

# ================= RUN =================
root.mainloop()
