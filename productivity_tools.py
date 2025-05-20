import tkinter as tk
from tkinter import ttk, messagebox
import time
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
import platform
import subprocess

class ProductivityTools:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent, bg='#E6ECF0')
        self.frame.pack(fill="both", expand=True)
        self.level = tk.StringVar(value='Easy')
        self.text_samples = {
            "Easy": "The quick brown fox jumps over the lazy dog.",
            "Medium": "Python is an interpreted high-level general-purpose programming language.",
            "Hard": "Concurrency and parallelism are not the same, but they are related concepts in computing."
        }
        self.start_time = None
        self.correct_chars = 0
        self.incorrect_chars = 0
        self.backspace_count = 0
        self.typing_started = False
        self.init_ui()

    def init_ui(self):
        # Configure ttk style
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 12, 'bold'), padding=8)
        style.configure('TRadiobutton', font=('Arial', 10), padding=4)
        style.configure('TLabel', font=('Arial', 12), background='#E6ECF0', foreground='#333333')

        # Title
        tk.Label(self.frame, text="📝 Typing Test", font=("Arial", 20, 'bold'), bg='#E6ECF0', fg='#263238').pack(pady=10)

        # Level selection
        level_frame = tk.Frame(self.frame, bg='#E6ECF0')
        level_frame.pack(fill='x', pady=5, padx=15)
        tk.Label(level_frame, text="Select Difficulty:", font=("Arial", 14, 'bold'), bg='#E6ECF0', fg='#263238').pack(side='left', padx=5)
        for lvl in ['Easy', 'Medium', 'Hard']:  # Removed 'Custom'
            ttk.Radiobutton(level_frame, text=lvl, variable=self.level, value=lvl, command=self.set_text_sample).pack(side="left", padx=10)

        # Text display
        self.text_display = tk.Label(self.frame, text=self.text_samples['Easy'], wraplength=600, font=("Arial", 14), bg='#FFFFFF', fg='#333333', bd=2, relief='ridge', padx=10, pady=10)
        self.text_display.pack(fill='x', padx=15, pady=10)

        # Input box
        input_frame = tk.Frame(self.frame, bg='#E6ECF0')
        input_frame.pack(fill='x', padx=15, pady=10)
        tk.Label(input_frame, text="Your Input:", font=("Arial", 12), bg='#E6ECF0', fg='#263238').pack(side='left', padx=5)
        self.input_box = tk.Text(input_frame, height=3, width=60, font=("Arial", 12), bd=2, relief='ridge')
        self.input_box.pack(side='left', fill='x', expand=True, padx=5)
        self.input_box.bind("<Key>", self.on_key_press)

        # Buttons
        button_frame = tk.Frame(self.frame, bg='#E6ECF0')
        button_frame.pack(pady=10)
        self.submit_button = tk.Button(button_frame, text="✅ Submit Test", font=("Arial", 14, 'bold'), bg='#4CAF50', fg='white', command=self.calculate_results, relief='flat', width=12)
        self.submit_button.pack(side='left', padx=10)
        self.reset_button = tk.Button(button_frame, text="🔄 Reset Test", font=("Arial", 14, 'bold'), bg='#2196F3', fg='white', command=self.reset_test, relief='flat', width=12)
        self.reset_button.pack(side='left', padx=10)
        self.submit_button.bind("<Enter>", lambda e: self.animate_button(self.submit_button, 1.1))
        self.submit_button.bind("<Leave>", lambda e: self.animate_button(self.submit_button, 1.0))
        self.reset_button.bind("<Enter>", lambda e: self.animate_button(self.reset_button, 1.1))
        self.reset_button.bind("<Leave>", lambda e: self.animate_button(self.reset_button, 1.0))

        # Result label
        self.result_label = tk.Label(self.frame, text="", font=("Arial", 12), bg='#E6ECF0', fg='#263238')
        self.result_label.pack(pady=10)

        self.set_text_sample()
        self.plot_previous_scores()

    def animate_button(self, button, scale):
        button.configure(font=("Arial", int(14 * scale), 'bold'))

    def reset_test(self):
        self.input_box.delete("1.0", "end")
        self.typing_started = False
        self.start_time = None
        self.correct_chars = 0
        self.incorrect_chars = 0
        self.backspace_count = 0
        self.result_label.config(text="")
        messagebox.showinfo("Reset", "Typing test reset successfully! 🚀")

    def set_text_sample(self):
        level = self.level.get()
        self.text_display.config(text=self.text_samples[level])

    def on_key_press(self, event):
        if not self.typing_started:
            self.start_time = time.time()
            self.typing_started = True
        if event.keysym == "BackSpace":
            self.backspace_count += 1
        self.update_live_stats()

    def update_live_stats(self):
        typed_text = self.input_box.get("1.0", "end-1c")
        target_text = self.text_display.cget("text")
        correct = 0
        incorrect = 0
        for i, c in enumerate(typed_text):
            if i < len(target_text):
                if c == target_text[i]:
                    correct += 1
                else:
                    incorrect += 1
            else:
                incorrect += 1
        self.correct_chars = correct
        self.incorrect_chars = incorrect
        elapsed_time = time.time() - self.start_time if self.start_time else 1
        wpm = (len(typed_text) / 5) / (elapsed_time / 60)
        cpm = len(typed_text) / (elapsed_time / 60)
        self.result_label.config(
            text=f"🚀 WPM: {wpm:.2f} | CPM: {cpm:.2f} | Correct: {correct} | Incorrect: {incorrect} | Backspaces: {self.backspace_count}"
        )

    def calculate_results(self):
        if not self.typing_started:
            messagebox.showwarning("No Input", "Please start typing before submitting! ⚠️")
            return
        end_time = time.time()
        elapsed = end_time - self.start_time
        typed_text = self.input_box.get("1.0", "end-1c")
        target_text = self.text_display.cget("text")
        correct = 0
        incorrect = 0
        for i, c in enumerate(typed_text):
            if i < len(target_text):
                if c == target_text[i]:
                    correct += 1
                else:
                    incorrect += 1
            else:
                incorrect += 1
        self.correct_chars = correct
        self.incorrect_chars = incorrect
        wpm = (len(typed_text) / 5) / (elapsed / 60)
        cpm = len(typed_text) / (elapsed / 60)
        result = f"⏱ Time: {elapsed:.2f}s\n🚀 WPM: {wpm:.2f}\n📈 CPM: {cpm:.2f}\n✅ Correct: {correct}\n❌ Incorrect: {incorrect}\n🔙 Backspace Used: {self.backspace_count}"
        messagebox.showinfo("Typing Result", result)
        self.save_score(wpm)
        self.plot_previous_scores()
        self.typing_started = False
        self.start_time = None
        self.backspace_count = 0

    def save_score(self, wpm):
        scores_file = "typing_scores.json"
        data = []
        try:
            if os.path.exists(scores_file):
                with open(scores_file, "r") as file:
                    data = json.load(file)
        except (json.JSONDecodeError, IOError):
            data = []
        data.append({"timestamp": datetime.now().isoformat(), "wpm": wpm})
        with open(scores_file, "w") as file:
            json.dump(data, file, indent=4)

    def plot_previous_scores(self):
        scores_file = "typing_scores.json"
        if not os.path.exists(scores_file):
            return
        try:
            with open(scores_file, "r") as file:
                data = json.load(file)
        except (json.JSONDecodeError, IOError):
            return
        timestamps = [datetime.fromisoformat(d["timestamp"]) for d in data]
        wpms = [d["wpm"] for d in data]
        if not timestamps or not wpms:
            return
        plt.figure(figsize=(6, 4))
        plt.plot(timestamps, wpms, marker='o', color='#3B5998')
        plt.title("Typing Speed Over Time", fontsize=14, fontweight='bold')
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("WPM", fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.grid(True)
        plt.savefig('typing_scores.png')
        plt.close()

class FeedbackSystem:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent, bg='#E6ECF0')
        self.frame.pack(fill="both", expand=True)
        self.feedbacks = []
        self.professor_list = [
            "Arjun Sharma", "Priya Patel", "Rahul Gupta", "Anjali Nair",
            "Vikram Singh", "Sneha Reddy", "Kiran Malhotra", "Divya Joshi",
            "Rohan Desai", "Meera Iyer"
        ]
        self.rating_buttons = []
        self.init_ui()

    def init_ui(self):
        style = ttk.Style()
        style.configure('TCombobox', font=('Arial', 12), padding=4)
        style.configure('TLabel', font=('Arial', 12), background='#E6ECF0', foreground='#333333')

        tk.Label(self.frame, text="📚 Professor Feedback System", font=("Arial", 20, 'bold'), bg='#E6ECF0', fg='#263238').pack(pady=10)

        # Professor selection
        prof_frame = tk.Frame(self.frame, bg='#E6ECF0')
        prof_frame.pack(fill='x', padx=15, pady=10)
        tk.Label(prof_frame, text="👩‍🏫 Pick a Professor:", font=("Arial", 14), bg='#E6ECF0', fg='#263238').pack(side='left', padx=5)
        self.prof_var = tk.StringVar()
        prof_dropdown = ttk.Combobox(prof_frame, textvariable=self.prof_var, values=self.professor_list, state="readonly", width=25)
        prof_dropdown.pack(side='left', padx=10)

        # Star rating
        rating_frame = tk.Frame(self.frame, bg='#E6ECF0')
        rating_frame.pack(fill='x', padx=15, pady=10)
        tk.Label(rating_frame, text="🌟 Star Rating (1-5):", font=("Arial", 14), bg='#E6ECF0', fg='#263238').pack(side='left', padx=5)
        self.rating_var = tk.IntVar()
        self.rating_var.trace("w", self.update_rating_color)
        emojis = ["😡", "😕", "😐", "😊", "😍"]
        descriptions = ["1 - Very Bad", "2 - Bad", "3 - Okay", "4 - Good", "5 - Excellent"]
        for i, (emoji, desc) in enumerate(zip(emojis, descriptions), 1):
            btn = tk.Radiobutton(
                rating_frame,
                text=f"{emoji} {desc}",
                variable=self.rating_var,
                value=i,
                font=("Arial", 12),
                indicatoron=0,
                width=12,
                bg="#FFFFFF",
                fg='#333333',
                selectcolor="#4CAF50",
                relief="ridge"
            )
            btn.pack(side="left", padx=5)
            self.rating_buttons.append(btn)

        # Reason input
        reason_frame = tk.Frame(self.frame, bg='#E6ECF0')
        reason_frame.pack(fill='x', padx=15, pady=10)
        tk.Label(reason_frame, text="💬 Why this rating?", font=("Arial", 14), bg='#E6ECF0', fg='#263238').pack(side='left', padx=5)
        self.reason_entry = tk.Entry(reason_frame, width=40, font=("Arial", 12), bd=2, relief='ridge')
        self.reason_entry.pack(side='left', padx=10, fill='x', expand=True)

        # Comment input
        comment_frame = tk.Frame(self.frame, bg='#E6ECF0')
        comment_frame.pack(fill='x', padx=15, pady=10)
        tk.Label(comment_frame, text="📝 Extra Feedback (Optional):", font=("Arial", 14), bg='#E6ECF0', fg='#263238').pack(side='left', padx=5)
        self.comment_text = tk.Text(comment_frame, height=3, width=40, font=("Arial", 12), bd=2, relief='ridge')
        self.comment_text.pack(side='left', padx=10, fill='x', expand=True)

        # Buttons
        button_frame = tk.Frame(self.frame, bg='#E6ECF0')
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="✅ Submit Feedback", font=("Arial", 14, 'bold'), bg='#4CAF50', fg='white', command=self.submit_feedback, relief='flat', width=15).pack(side="left", padx=10)
        tk.Button(button_frame, text="📋 View Feedback", font=("Arial", 14, 'bold'), bg='#2196F3', fg='white', command=self.view_feedback, relief='flat', width=15).pack(side="left", padx=10)
        tk.Button(button_frame, text="📜 Print Feedback", font=("Arial", 14, 'bold'), bg='#FF9800', fg='white', command=self.print_feedback, relief='flat', width=15).pack(side="left", padx=10)

    def update_rating_color(self, *args):
        selected_rating = self.rating_var.get()
        for i, btn in enumerate(self.rating_buttons, 1):
            if i == selected_rating and selected_rating != 0:
                btn.config(bg="#4CAF50", fg="white")
            else:
                btn.config(bg="#FFFFFF", fg="#333333")

    def validate_rating(self):
        return 1 <= self.rating_var.get() <= 5

    def submit_feedback(self):
        professor = self.prof_var.get()
        if not professor:
            messagebox.showwarning("Invalid Input", "Please select a professor. ⚠️")
            return
        if not self.validate_rating():
            messagebox.showwarning("Invalid Input", "Please select a rating (1-5). ⚠️")
            return
        rating = self.rating_var.get()
        reason = self.reason_entry.get().strip()
        if not reason:
            messagebox.showwarning("Invalid Input", "Please provide a reason for the rating. ⚠️")
            return
        comment = self.comment_text.get("1.0", tk.END).strip()
        feedback = {
            "professor": professor,
            "rating": rating,
            "reason": reason,
            "comment": comment
        }
        self.feedbacks.append(feedback)
        feedback_str = f"🌟 {rating}/5 for {professor}: {reason}"
        if comment:
            feedback_str += f" | {comment}"
        messagebox.showinfo("Feedback Submitted", f"✅ Submitted:\n{feedback_str}")
        self.prof_var.set("")
        self.rating_var.set(0)
        self.reason_entry.delete(0, tk.END)
        self.comment_text.delete("1.0", tk.END)

    def view_feedback(self):
        if not self.feedbacks:
            messagebox.showinfo("Feedback Summary", "📅 No feedback submitted yet.")
            return
        summary_window = tk.Toplevel(self.frame)
        summary_window.title("Feedback Summary")
        summary_window.geometry("600x400")
        summary_window.configure(bg='#E6ECF0')

        # Create a canvas with a scrollbar
        canvas = tk.Canvas(summary_window, bg='#E6ECF0')
        scrollbar = tk.Scrollbar(summary_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#E6ECF0')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=600)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Title (removing the border by not using relief="solid")
        tk.Label(scrollable_frame, text="📋 Feedback Summary", font=("Arial", 18, 'bold'), bg='#263238', fg='white', pady=10).pack(fill="x")

        # Group feedback by professor
        professors = {}
        for feedback in self.feedbacks:
            prof = feedback["professor"]
            if prof not in professors:
                professors[prof] = {"ratings": [], "reasons": [], "comments": []}
            professors[prof]["ratings"].append(feedback["rating"])
            professors[prof]["reasons"].append(feedback["reason"])
            if feedback["comment"]:
                professors[prof]["comments"].append(feedback["comment"])

        # Display feedback for each professor
        for idx, (prof, data) in enumerate(professors.items()):
            avg_rating = sum(data["ratings"]) / len(data["ratings"])
            stars = "★" * int(round(avg_rating))
            bg_color = '#F0F4F8' if idx % 2 == 0 else '#FFFFFF'

            # Professor frame
            prof_frame = tk.Frame(scrollable_frame, bg=bg_color, bd=1, relief="solid")
            prof_frame.pack(fill="x", padx=10, pady=5)

            # Professor name and average rating
            tk.Label(prof_frame, text=f"👩‍🏫 {prof}", font=("Arial", 14, 'bold'), bg=bg_color, fg='#263238', anchor="w").pack(fill="x", padx=10, pady=5)
            tk.Label(prof_frame, text=f"🌟 Average: {avg_rating:.1f}/5 ({len(data['ratings'])} reviews) {stars}", font=("Arial", 12), bg=bg_color, fg='#4CAF50', anchor="w").pack(fill="x", padx=15)

            # Reasons
            tk.Label(prof_frame, text="💬 Reasons:", font=("Arial", 12, 'bold'), bg=bg_color, fg='#333333', anchor="w").pack(fill="x", padx=15)
            for reason in data["reasons"]:
                tk.Label(prof_frame, text=f"  • {reason}", font=("Arial", 10), bg=bg_color, fg='#555555', anchor="w", wraplength=500).pack(fill="x", padx=20)

            # Comments
            if data["comments"]:
                tk.Label(prof_frame, text="📝 Comments:", font=("Arial", 12, 'bold'), bg=bg_color, fg='#333333', anchor="w").pack(fill="x", padx=15)
                for comment in data["comments"]:
                    tk.Label(prof_frame, text=f"  • {comment}", font=("Arial", 10), bg=bg_color, fg='#555555', anchor="w", wraplength=500).pack(fill="x", padx=20)

    def print_feedback(self):
        if not self.feedbacks:
            messagebox.showinfo("Print Feedback", "📅 No feedback to print.")
            return

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors

            # Create PDF file
            pdf_file = f"feedback_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            output_dir = "feedback_reports"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            pdf_path = os.path.join(output_dir, pdf_file)

            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            styles = getSampleStyleSheet()
            custom_style = ParagraphStyle(
                name='Custom',
                parent=styles['Normal'],
                fontSize=12,
                leading=14,
                textColor=colors.black,
            )
            story = []

            # Title
            story.append(Paragraph(" Professor Feedback Summary", styles['Title']))
            story.append(Spacer(1, 12))

            # Date and Time
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", custom_style))
            story.append(Spacer(1, 12))

            # Group feedback by professor
            professors = {}
            for feedback in self.feedbacks:
                prof = feedback["professor"]
                if prof not in professors:
                    professors[prof] = {"ratings": [], "reasons": [], "comments": []}
                professors[prof]["ratings"].append(feedback["rating"])
                professors[prof]["reasons"].append(feedback["reason"])
                if feedback["comment"]:
                    professors[prof]["comments"].append(feedback["comment"])

            # Create paragraphs for each professor
            for prof, data in professors.items():
                avg_rating = sum(data["ratings"]) / len(data["ratings"])
                stars = "★ " * int(round(avg_rating))
                
                # Professor heading
                story.append(Paragraph(f"Professor: {prof}", styles['Heading2']))
                story.append(Spacer(1, 6))
                
                # Average rating
                story.append(Paragraph(f"Average Rating: {avg_rating:.1f}/5 ({len(data['ratings'])} reviews) {stars}", custom_style))
                story.append(Spacer(1, 6))
                
                # Reasons
                story.append(Paragraph("Reasons:", styles['Heading4']))
                for reason in data["reasons"]:
                    story.append(Paragraph(f"• {reason}", custom_style))
                
                # Comments
                if data["comments"]:
                    story.append(Paragraph("Comments:", styles['Heading4']))
                    for comment in data["comments"]:
                        story.append(Paragraph(f"• {comment}", custom_style))
                
                story.append(Spacer(1, 12))

            # Footer (simplified without a box-like appearance)
            story.append(Paragraph("Thank you for your feedback! ", styles['Normal']))

            # Build PDF
            doc.build(story)
            messagebox.showinfo("Feedback Printed", f"Feedback summary has been saved as {pdf_file} 📄")

            # Open the PDF
            pdf_abs_path = os.path.abspath(pdf_path)
            system = platform.system()
            try:
                if system == "Windows":
                    os.startfile(pdf_abs_path)
                elif system == "Darwin":
                    subprocess.run(["open", pdf_abs_path], check=True)
                else:
                    subprocess.run(["xdg-open", pdf_abs_path], check=True)
            except Exception as open_error:
                messagebox.showwarning("File Error", f"PDF generated but failed to open: {open_error}")

        except ImportError:
            messagebox.showwarning("Export Error", "Please install reportlab to export to PDF (pip install reportlab).")
        except PermissionError:
            messagebox.showwarning("File Error", "Permission denied while generating PDF. Check folder permissions.")
        except Exception as e:
            messagebox.showwarning("Export Error", f"Failed to export: {e}")

class AttendanceTracker:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent, bg='#E6ECF0')
        self.frame.pack(fill="both", expand=True)
        self.students = {}
        self.TOTAL_CLASSES = 60
        self.current_student_index = 0
        self.init_ui()

    def init_ui(self):
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 12, 'bold'), padding=8)
        style.configure('TRadiobutton', font=('Arial', 10), padding=4)
        style.configure('TLabel', font=('Arial', 12), background='#E6ECF0', foreground='#333333')
        style.configure('Treeview', font=('Arial', 10))
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))

        tk.Label(self.frame, text="📘 Attendance Tracker", font=("Arial", 20, 'bold'), bg='#E6ECF0', fg='#263238').pack(pady=10)

        # Add Students Section
        student_frame = tk.Frame(self.frame, bg='#E6ECF0')
        student_frame.pack(fill='x', padx=15, pady=10)
        tk.Label(student_frame, text="👤 Enter Student Name:", font=("Arial", 14), bg='#E6ECF0', fg='#263238').pack(side='left', padx=5)
        self.student_entry = tk.Entry(student_frame, width=25, font=("Arial", 12), bd=2, relief='ridge')
        self.student_entry.pack(side='left', padx=10)
        tk.Button(student_frame, text="➕ Add Student", font=("Arial", 12, 'bold'), bg='#4CAF50', fg='white', command=self.add_student, relief='flat').pack(side='left', padx=10)

        # Mark Attendance Section
        attendance_frame = tk.Frame(self.frame, bg='#E6ECF0')
        attendance_frame.pack(fill='x', padx=15, pady=10)
        self.current_student_label = tk.Label(attendance_frame, text="No students added yet.", font=("Arial", 14), bg='#E6ECF0', fg='#263238')
        self.current_student_label.pack(side='left', padx=5)
        self.attendance_var = tk.StringVar(value="P")
        tk.Radiobutton(attendance_frame, text="✅ Present", variable=self.attendance_var, value="P", font=("Arial", 12)).pack(side="left", padx=10)
        tk.Radiobutton(attendance_frame, text="❌ Absent", variable=self.attendance_var, value="A", font=("Arial", 12)).pack(side="left", padx=10)
        tk.Button(attendance_frame, text="➡️ Mark Attendance", font=("Arial", 12, 'bold'), bg='#2196F3', fg='white', command=self.mark_attendance, relief='flat').pack(side='left', padx=10)

        # Report Section
        self.report_frame = tk.Frame(self.frame, bg='#E6ECF0')
        self.report_frame.pack(fill="both", expand=True, padx=15, pady=10)
        self.tree = ttk.Treeview(self.report_frame, columns=("Name", "Attendance", "Percentage", "Status"), show="headings")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Attendance", text="Attendance")
        self.tree.heading("Percentage", text="Percentage")
        self.tree.heading("Status", text="Status")
        self.tree.column("Name", width=200)
        self.tree.column("Attendance", width=120)
        self.tree.column("Percentage", width=120)
        self.tree.column("Status", width=150)
        self.tree.pack(side='left', fill="both", expand=True)
        self.scrollbar = ttk.Scrollbar(self.report_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", self.on_double_click)
        self.show_report()

    def is_valid_name(self, name):
        return name.isalpha()

    def add_student(self):
        name = self.student_entry.get().strip()
        if not name:
            messagebox.showwarning("Invalid Input", "Please enter a student name. ⚠️")
            return
        if not self.is_valid_name(name):
            messagebox.showwarning("Invalid Input", "Only alphabets are allowed in the name! ⚠️")
            return
        if name in self.students:
            messagebox.showwarning("Duplicate Entry", "⚠️ Student already added.")
            return
        self.students[name] = 0
        self.student_entry.delete(0, tk.END)
        messagebox.showinfo("Success", f"Student {name} added successfully! ✅")
        if len(self.students) == 1:
            self.current_student_index = 0
            self.current_student_label.config(text=f"Marking for: {list(self.students.keys())[0]}")
        self.show_report()

    def mark_attendance(self):
        if not self.students:
            messagebox.showwarning("No Students", "⚠️ No students available to mark attendance.")
            return
        student_names = list(self.students.keys())
        current_student = student_names[self.current_student_index]
        status = self.attendance_var.get()
        if status == 'P':
            self.students[current_student] += 1
        self.current_student_index += 1
        if self.current_student_index >= len(student_names):
            messagebox.showinfo("Done", "Attendance marking completed for all students! ✅")
            self.current_student_index = 0
            self.current_student_label.config(text=f"Marking for: {student_names[0]}")
        else:
            next_student = student_names[self.current_student_index]
            self.current_student_label.config(text=f"Marking for: {next_student}")
        self.show_report()

    def show_report(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, (name, present) in enumerate(self.students.items()):
            percentage = (present / self.TOTAL_CLASSES) * 100
            status = "⚠️ Low Attendance" if percentage < 75 else "✅ OK"
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert("", "end", values=(name, f"{present}/{self.TOTAL_CLASSES}", f"{percentage:.2f}%", status), tags=(tag,))
        self.tree.tag_configure('even', background='#F0F4F8')
        self.tree.tag_configure('odd', background='#FFFFFF')

    def on_double_click(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        item_values = self.tree.item(selected_item[0], "values")
        selected_student = item_values[0]
        student_names = list(self.students.keys())
        if selected_student in student_names:
            self.current_student_index = student_names.index(selected_student)
            self.current_student_label.config(text=f"Marking for: {selected_student}")

class ProductivityApp:
    def __init__(self, parent):
        self.parent = parent
        self.root = parent.winfo_toplevel()
        self.root.state('zoomed')
        self.container = tk.Frame(self.parent, bg='#3B5998')
        self.container.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = tk.Frame(self.container, bg='#263238', width=200)
        self.sidebar.pack(side='left', fill='y')
        tk.Label(self.sidebar, text="🚀 Productivity Hub", font=("Arial", 16, 'bold'), bg='#263238', fg='white').pack(pady=15)
        self.tool_var = tk.StringVar(value="Typing Test")
        tools = ["Typing Test", "Feedback System", "Attendance Tracker"]
        for tool in tools:
            btn = tk.Button(self.sidebar, text=tool, font=("Arial", 12, 'bold'), bg='#4CAF50', fg='white', relief='flat', width=15, command=lambda t=tool: self.switch_tool(t))
            btn.pack(pady=10, padx=5)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg='#45A049'))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg='#4CAF50'))

        # Main content
        self.content_frame = tk.Frame(self.container, bg='#E6ECF0')
        self.content_frame.pack(side='left', fill="both", expand=True)
        self.typing_frame = tk.Frame(self.content_frame, bg='#E6ECF0')
        self.feedback_frame = tk.Frame(self.content_frame, bg='#E6ECF0')
        self.attendance_frame = tk.Frame(self.content_frame, bg='#E6ECF0')
        self.typing_tool = ProductivityTools(self.typing_frame)
        self.feedback_tool = FeedbackSystem(self.feedback_frame)
        self.attendance_tool = AttendanceTracker(self.attendance_frame)
        self.switch_tool("Typing Test")

    def switch_tool(self, tool=None):
        if tool:
            self.tool_var.set(tool)
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.pack_forget()
        selected_tool = self.tool_var.get()
        if selected_tool == "Typing Test":
            self.typing_frame.pack(fill="both", expand=True)
        elif selected_tool == "Feedback System":
            self.feedback_frame.pack(fill="both", expand=True)
        elif selected_tool == "Attendance Tracker":
            self.attendance_frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    root.state('zoomed')
    app = ProductivityApp(root)
    root.mainloop()