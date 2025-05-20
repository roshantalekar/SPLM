import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import pandas as pd
from datetime import date, datetime, time

class TaskManager:
    def __init__(self, root):
        self.root = root
        self.tasks = []
        self.user_triggered_view = False

        # Colors and styles
        self.style = ttk.Style()
        self.style.theme_use("clam")  # Use 'clam' theme for more customization

        # Define vibrant blue color scheme
        self.bg_color = "#E6F0FA"  # Light blue background
        self.frame_color = "#FFFFFF"  # White frames with shadow
        self.accent_color = "#2196F3"  # Vibrant blue for buttons
        self.hover_color = "#1E88E5"  # Darker blue for hover
        self.heading_color = "#1565C0"  # Deep blue for headings
        self.text_color = "#212121"  # Dark gray for text
        self.progress_bar_color = "#4CAF50"  # Green for progress bar

        # Configure root background
        self.root.configure(bg=self.bg_color)

        # Style configurations
        self.style.configure("TLabel", font=("Arial", 12), foreground=self.text_color, background=self.bg_color)
        self.style.configure("Heading.TLabel", font=("Arial", 16, "bold"), foreground=self.heading_color, background=self.bg_color)
        self.style.configure("TFrame", background=self.bg_color)

        # Custom button style with hover effect
        self.style.configure("Custom.TButton", font=("Arial", 10, "bold"), background=self.accent_color, foreground="white", borderwidth=1, relief="flat", padding=5)
        self.style.map("Custom.TButton", background=[("active", self.hover_color)], foreground=[("active", "white")])

        # Frame style with subtle shadow effect
        self.style.configure("Shadow.TFrame", background=self.frame_color, relief="raised", borderwidth=2)

        # Treeview style
        self.style.configure("Treeview", font=("Arial", 11), background="#F5F5F5", foreground=self.text_color, fieldbackground="#F5F5F5", rowheight=30)
        self.style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#BBDEFB", foreground=self.heading_color)
        self.style.map("Treeview", background=[("selected", "#90CAF9")])

        # Priority tags with vibrant colors
        self.style.configure("HighPriority.Treeview", foreground="#D32F2F")  # Red
        self.style.configure("MediumPriority.Treeview", foreground="#1976D2")  # Blue
        self.style.configure("LowPriority.Treeview", foreground="#FBC02D")  # Yellow

        # Progress bar style
        self.style.configure("Custom.Horizontal.TProgressbar", troughcolor=self.bg_color, background=self.progress_bar_color, thickness=20)

        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10", style="Shadow.TFrame")
        self.main_frame.pack(fill="both", expand=True)

        # Title
        ttk.Label(self.main_frame, text="📋 Smart Task Manager", style="Heading.TLabel").pack(pady=10)

        # Menu Buttons
        self.menu_frame = ttk.LabelFrame(self.main_frame, text="Menu", padding="10", style="Shadow.TFrame")
        self.menu_frame.pack(fill="x", pady=5)

        menu_buttons = ttk.Frame(self.menu_frame, style="Shadow.TFrame")
        menu_buttons.pack(fill="x")
        buttons = [
            ("➕ Add Tasks", self.show_add_task),
            ("📋 View Tasks", self.show_task_list),
            ("✅ Mark Done", self.show_mark_done),
            ("🗑️ Delete Task", self.show_delete_task),
            ("🏠 Main Menu", self.return_to_main_menu),
        ]
        for text, command in buttons:
            btn = ttk.Button(menu_buttons, text=text, command=command, style="Custom.TButton")
            btn.pack(side="left", padx=5)

        # Dynamic Frame for Actions
        self.action_frame = ttk.Frame(self.main_frame, style="Shadow.TFrame")
        self.action_frame.pack(fill="both", expand=True, pady=5)

        self.show_task_list(initial_load=True)

    def show_add_task(self):
        for widget in self.action_frame.winfo_children():
            widget.destroy()

        add_frame = ttk.LabelFrame(self.action_frame, text="Add New Task", padding="10", style="Shadow.TFrame")
        add_frame.pack(fill="x", pady=5)

        task_row1 = ttk.Frame(add_frame)
        task_row1.pack(fill="x", pady=5)
        ttk.Label(task_row1, text="Task:", background=self.frame_color).pack(side="left", padx=5)
        self.task_var = tk.StringVar()
        ttk.Entry(task_row1, textvariable=self.task_var, width=40).pack(side="left", padx=5)

        task_row2 = ttk.Frame(add_frame)
        task_row2.pack(fill="x", pady=5)
        ttk.Label(task_row2, text="Due Date:", background=self.frame_color).pack(side="left", padx=5)
        self.due_date_var = DateEntry(task_row2, date_pattern="dd/mm/yyyy", state="readonly", mindate=date.today(), background="#BBDEFB", foreground=self.text_color)
        self.due_date_var.pack(side="left", padx=5)

        ttk.Label(task_row2, text="Due Time:", background=self.frame_color).pack(side="left", padx=5)
        self.time_var = tk.StringVar(value="12:00 AM")
        time_options = []
        for hour in range(12):
            for minute in range(0, 60, 15):
                for period in ["AM", "PM"]:
                    hour_display = 12 if hour == 0 else hour
                    time_options.append(f"{hour_display}:{minute:02d} {period}")
        time_combobox = ttk.Combobox(task_row2, textvariable=self.time_var, state="readonly", values=time_options, width=10)
        time_combobox.pack(side="left", padx=5)

        ttk.Label(task_row2, text="Custom Time (HH:MM AM/PM):", background=self.frame_color).pack(side="left", padx=5)
        self.custom_time_var = tk.StringVar()
        ttk.Entry(task_row2, textvariable=self.custom_time_var, width=12).pack(side="left", padx=5)

        ttk.Label(task_row2, text="Priority:", background=self.frame_color).pack(side="left", padx=5)
        self.priority_var = tk.StringVar(value="Medium")
        priority_combobox = ttk.Combobox(task_row2, textvariable=self.priority_var, state="readonly", values=["Low", "Medium", "High"])
        priority_combobox.pack(side="left", padx=5)

        task_row3 = ttk.Frame(add_frame)
        task_row3.pack(fill="x", pady=5)
        ttk.Label(task_row3, text="Category:", background=self.frame_color).pack(side="left", padx=5)
        self.add_category_var = tk.StringVar(value="Work")
        category_combobox = ttk.Combobox(task_row3, textvariable=self.add_category_var, state="readonly", values=["Work", "Personal", "Urgent", "Other"])
        category_combobox.pack(side="left", padx=5)

        ttk.Label(task_row3, text="Notes:", background=self.frame_color).pack(side="left", padx=5)
        self.notes_var = tk.StringVar()
        ttk.Entry(task_row3, textvariable=self.notes_var, width=20).pack(side="left", padx=5)

        button_row = ttk.Frame(add_frame)
        button_row.pack(fill="x", pady=5)
        ttk.Button(button_row, text="➕ Add Task", command=self.add_task, style="Custom.TButton").pack(side="left", padx=5)
        ttk.Button(button_row, text="⬅ Back to Menu", command=lambda: self.show_task_list(initial_load=False), style="Custom.TButton").pack(side="left", padx=5)

    def add_task(self):
        task = self.task_var.get().strip()
        due_date = self.due_date_var.get_date()
        time_12hr = self.time_var.get().strip()
        custom_time = self.custom_time_var.get().strip()

        if not task:
            messagebox.showwarning("Input Error", "Please enter a task!")
            if not self.tasks:
                messagebox.showinfo("Info", "No tasks found.")
            return

        if due_date < date.today():
            messagebox.showwarning("Invalid Date", "The selected date has already passed!")
            return

        selected_time = custom_time if custom_time else time_12hr

        try:
            time_obj = datetime.strptime(selected_time, "%I:%M %p")
            time_24hr = time_obj.strftime("%H:%M")
            time_display = selected_time
        except ValueError:
            messagebox.showwarning("Input Error", "Invalid time format! Use HH:MM AM/PM (e.g., 02:30 PM)")
            return

        if due_date == date.today():
            current_time = datetime.now().time()
            selected_time_obj = time_obj.time()
            if selected_time_obj < current_time:
                messagebox.showwarning("Invalid Time", "The selected time has already passed for today!")
                return

        task_obj = {
            "task": task,
            "done": False,
            "due": self.due_date_var.get(),
            "time": time_24hr,
            "time_display": time_display,
            "priority": self.priority_var.get(),
            "category": self.add_category_var.get(),
            "notes": self.notes_var.get().strip() or "No notes"
        }
        self.tasks.append(task_obj)
        messagebox.showinfo("Success", "Task added successfully!")
        
        self.task_var.set("")
        self.due_date_var.set_date(date.today())
        self.time_var.set("12:00 AM")
        self.custom_time_var.set("")
        self.priority_var.set("Medium")
        self.add_category_var.set("Work")
        self.notes_var.set("")
        self.show_task_list(initial_load=False)

    def show_task_list(self, initial_load=False):
        for widget in self.action_frame.winfo_children():
            widget.destroy()

        task_list_frame = ttk.LabelFrame(self.action_frame, text="Task List", padding="10", style="Shadow.TFrame")
        task_list_frame.pack(fill="both", expand=True, pady=5)

        search_frame = ttk.Frame(task_list_frame)
        search_frame.pack(fill="x")
        ttk.Label(search_frame, text="Search tasks:", background=self.frame_color).pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side="left", padx=5)
        self.search_var.trace("w", self.update_task_list)

        ttk.Label(search_frame, text="Filter by Category:", background=self.frame_color).pack(side="left", padx=5)
        self.category_var = tk.StringVar(value="All")
        self.category_dropdown = ttk.Combobox(search_frame, textvariable=self.category_var, state="readonly", values=["All"])
        self.category_dropdown.pack(side="left", padx=5)
        self.category_dropdown.bind("<<ComboboxSelected>>", self.update_task_list)

        progress_frame = ttk.Frame(task_list_frame)
        progress_frame.pack(fill="x", pady=5)
        self.progress = ttk.Progressbar(progress_frame, length=300, mode="determinate", style="Custom.Horizontal.TProgressbar")
        self.progress.pack(fill="x", pady=5)
        self.progress_label = ttk.Label(progress_frame, text="Completed: 0/0 (0%)", background=self.frame_color)
        self.progress_label.pack(pady=5)

        self.tree = ttk.Treeview(task_list_frame, columns=("ID", "Status", "Task", "Priority", "Due Date", "Time", "Category", "Notes"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Task", text="Task")
        self.tree.heading("Priority", text="Priority")
        self.tree.heading("Due Date", text="Due Date")
        self.tree.heading("Time", text="Time")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Notes", text="Notes")
        self.tree.column("ID", width=50)
        self.tree.column("Status", width=80)
        self.tree.column("Task", width=300)
        self.tree.column("Priority", width=80)
        self.tree.column("Due Date", width=100)
        self.tree.column("Time", width=100)
        self.tree.column("Category", width=100)
        self.tree.column("Notes", width=150)
        self.tree.pack(fill="both", expand=True)

        # Add alternate row colors
        self.tree.tag_configure("oddrow", background="#E3F2FD")
        self.tree.tag_configure("evenrow", background="#FFFFFF")

        # Add hover effect for Treeview rows
        self.tree.bind("<Enter>", lambda e: self.tree.config(cursor="hand2"))
        self.tree.bind("<Leave>", lambda e: self.tree.config(cursor=""))

        if not initial_load:
            self.user_triggered_view = True
        self.update_task_list()

    def update_task_list(self, *args):
        for item in self.tree.get_children():
            self.tree.delete(item)

        search_term = self.search_var.get().lower()
        selected_category = self.category_var.get()
        filtered_tasks = [
            t for t in self.tasks
            if (not search_term or search_term in t["task"].lower()) and
            (selected_category == "All" or t["category"] == selected_category)
        ]

        priority_order = {"High": 1, "Medium": 2, "Low": 3}
        category_order = {"Urgent": 1, "Work": 2, "Personal": 3, "Other": 4}
        filtered_tasks.sort(key=lambda x: (priority_order.get(x["priority"], 3), category_order.get(x["category"], 4)))

        categories = ["All"] + sorted(set(task["category"] for task in self.tasks if task["category"]))
        self.category_dropdown["values"] = categories
        if selected_category not in categories:
            self.category_var.set("All")

        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for task in self.tasks if task["done"])
        progress = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        self.progress["value"] = progress
        self.progress_label.config(text=f"Completed: {completed_tasks}/{total_tasks} ({progress:.1f}%)")

        for idx, t in enumerate(filtered_tasks, 1):
            status = "✓" if t["done"] else "✗"
            due_str = t["due"] if t["due"] else "No Due Date"
            time_str = t["time_display"] if t["time_display"] else "No Time"
            priority = t["priority"]
            row_tags = ("oddrow" if idx % 2 else "evenrow",)
            if priority == "High":
                row_tags += ("HighPriority",)
            elif priority == "Medium":
                row_tags += ("MediumPriority",)
            elif priority == "Low":
                row_tags += ("LowPriority",)
            self.tree.insert("", "end", values=(
                idx,
                status,
                t["task"],
                priority,
                due_str,
                time_str,
                t["category"],
                t["notes"]
            ), tags=row_tags)

        if self.user_triggered_view and not filtered_tasks:
            messagebox.showinfo("Info", "No tasks found.")
        self.user_triggered_view = False

    def show_mark_done(self):
        for widget in self.action_frame.winfo_children():
            widget.destroy()

        mark_frame = ttk.LabelFrame(self.action_frame, text="Mark Task as Done", padding="10", style="Shadow.TFrame")
        mark_frame.pack(fill="both", expand=True, pady=5)

        self.tree = ttk.Treeview(mark_frame, columns=("ID", "Status", "Task", "Priority"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Task", text="Task")
        self.tree.heading("Priority", text="Priority")
        self.tree.column("ID", width=50)
        self.tree.column("Status", width=80)
        self.tree.column("Task", width=300)
        self.tree.column("Priority", width=80)
        self.tree.pack(fill="both", expand=True)

        self.tree.tag_configure("oddrow", background="#E3F2FD")
        self.tree.tag_configure("evenrow", background="#FFFFFF")

        mark_row = ttk.Frame(mark_frame)
        mark_row.pack(fill="x", pady=5)
        ttk.Label(mark_row, text="Enter task number to mark as done:", background=self.frame_color).pack(side="left", padx=5)
        self.mark_id_var = tk.IntVar(value=1)
        ttk.Entry(mark_row, textvariable=self.mark_id_var, width=5).pack(side="left", padx=5)
        ttk.Button(mark_row, text="✅ Mark as Done", command=self.mark_done, style="Custom.TButton").pack(side="left", padx=5)

        priority_order = {"High": 1, "Medium": 2, "Low": 3}
        category_order = {"Urgent": 1, "Work": 2, "Personal": 3, "Other": 4}
        sorted_tasks = sorted(self.tasks, key=lambda x: (priority_order.get(x["priority"], 3), category_order.get(x["category"], 4)))
        for idx, t in enumerate(sorted_tasks, 1):
            status = "✓" if t["done"] else "✗"
            priority = t["priority"]
            row_tags = ("oddrow" if idx % 2 else "evenrow",)
            if priority == "High":
                row_tags += ("HighPriority",)
            elif priority == "Medium":
                row_tags += ("MediumPriority",)
            elif priority == "Low":
                row_tags += ("LowPriority",)
            self.tree.insert("", "end", values=(idx, status, t["task"], priority), tags=row_tags)

    def mark_done(self):
        num = self.mark_id_var.get() - 1
        if 0 <= num < len(self.tasks):
            self.tasks[num]["done"] = True
            messagebox.showinfo("Success", "Task marked as done.")
            self.show_task_list(initial_load=False)
        else:
            messagebox.showwarning("Invalid ID", "Invalid task number.")

    def show_delete_task(self):
        for widget in self.action_frame.winfo_children():
            widget.destroy()

        delete_frame = ttk.LabelFrame(self.action_frame, text="Delete Task", padding="10", style="Shadow.TFrame")
        delete_frame.pack(fill="both", expand=True, pady=5)

        self.tree = ttk.Treeview(delete_frame, columns=("ID", "Status", "Task", "Priority"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Task", text="Task")
        self.tree.heading("Priority", text="Priority")
        self.tree.column("ID", width=50)
        self.tree.column("Status", width=80)
        self.tree.column("Task", width=300)
        self.tree.column("Priority", width=80)
        self.tree.pack(fill="both", expand=True)

        self.tree.tag_configure("oddrow", background="#E3F2FD")
        self.tree.tag_configure("evenrow", background="#FFFFFF")

        delete_row = ttk.Frame(delete_frame)
        delete_row.pack(fill="x", pady=5)
        ttk.Label(delete_row, text="Enter task number to delete:", background=self.frame_color).pack(side="left", padx=5)
        self.delete_id_var = tk.IntVar(value=1)
        ttk.Entry(delete_row, textvariable=self.delete_id_var, width=5).pack(side="left", padx=5)
        ttk.Button(delete_row, text="🗑️ Delete Task", command=self.delete_task, style="Custom.TButton").pack(side="left", padx=5)

        priority_order = {"High": 1, "Medium": 2, "Low": 3}
        category_order = {"Urgent": 1, "Work": 2, "Personal": 3, "Other": 4}
        sorted_tasks = sorted(self.tasks, key=lambda x: (priority_order.get(x["priority"], 3), category_order.get(x["category"], 4)))
        for idx, t in enumerate(sorted_tasks, 1):
            status = "✓" if t["done"] else "✗"
            priority = t["priority"]
            row_tags = ("oddrow" if idx % 2 else "evenrow",)
            if priority == "High":
                row_tags += ("HighPriority",)
            elif priority == "Medium":
                row_tags += ("MediumPriority",)
            elif priority == "Low":
                row_tags += ("LowPriority",)
            self.tree.insert("", "end", values=(idx, status, t["task"], priority), tags=row_tags)

    def delete_task(self):
        num = self.delete_id_var.get() - 1
        if 0 <= num < len(self.tasks):
            self.tasks.pop(num)
            messagebox.showinfo("Success", "Task deleted.")
            self.show_task_list(initial_load=False)
        else:
            messagebox.showwarning("Invalid ID", "Invalid task number.")

    def return_to_main_menu(self):
        self.show_task_list(initial_load=False)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Smart Task Manager")
    root.geometry("800x600")
    app = TaskManager(root)
    root.mainloop()