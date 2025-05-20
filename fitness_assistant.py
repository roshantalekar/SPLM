import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import matplotlib.pyplot as plt
import json
import os
import pandas as pd
import platform
import subprocess

class FitnessAssistant:
    def __init__(self, parent):
        self.parent = parent
        self.root = self.parent.winfo_toplevel()
        self.root.state('zoomed')
        self.parent.configure(bg='#e6ecf0')
        self.frame = tk.Frame(parent, bg='#e6ecf0')
        self.frame.pack(fill="both", expand=True)
        
        self.workouts = []
        self.health_goals = {'steps': 10000, 'calories': 2000, 'workouts': 5}
        self.hydration_goal = 2000

        style = ttk.Style()
        style.configure("Custom.TCombobox", font=("Helvetica", 12))

        tk.Label(self.frame, text="Fitness Assistant", font=("Helvetica", 28, "bold"), 
                 bg='#e6ecf0', fg='#2c3e50').pack(pady=30)

        workout_frame = tk.Frame(self.frame, bg='#e6ecf0')
        workout_frame.pack(fill="x", padx=30, pady=20)
        
        tk.Label(workout_frame, text="Workout:", font=("Helvetica", 14), 
                 bg='#e6ecf0', fg='#34495e').pack(side="left", padx=10)
        self.workout_var = tk.StringVar()
        self.workout_combobox = ttk.Combobox(workout_frame, textvariable=self.workout_var, 
                                            state="readonly", font=("Helvetica", 12), 
                                            width=25, style="Custom.TCombobox")
        self.workout_combobox['values'] = (
            "Strength Training", "Cardio", "High-Intensity Interval Training (HIIT)", 
            "Bodyweight Exercises", "Mixed Routine", "Flexibility and Mobility", 
            "Plyometric Training", "Core Training"
        )
        self.workout_combobox.pack(side="left", expand=True, fill="x", padx=10, ipady=5)
        
        tk.Label(workout_frame, text="Mins:", font=("Helvetica", 14), 
                 bg='#e6ecf0', fg='#34495e').pack(side="left", padx=10)
        self.duration_var = tk.StringVar()
        self.duration_combobox = ttk.Combobox(workout_frame, textvariable=self.duration_var, 
                                             state="readonly", font=("Helvetica", 12), 
                                             width=5, style="Custom.TCombobox")
        self.duration_combobox['values'] = (10, 20, 30, 40, 50, 60, 90, 120)
        self.duration_combobox.pack(side="left", padx=10, ipady=5)
        
        tk.Label(workout_frame, text="Intensity:", font=("Helvetica", 14), 
                 bg='#e6ecf0', fg='#34495e').pack(side="left", padx=10)
        self.intensity_var = tk.StringVar()
        self.intensity_combobox = ttk.Combobox(workout_frame, textvariable=self.intensity_var, 
                                              state="readonly", font=("Helvetica", 12), 
                                              width=10, style="Custom.TCombobox")
        self.intensity_combobox['values'] = ("Low", "Medium", "High")
        self.intensity_combobox.pack(side="left", padx=10, ipady=5)
        
        tk.Button(workout_frame, text="Log Workout", command=self.log_workout, 
                  font=("Helvetica", 14, "bold"), bg='#2ecc71', fg='white', 
                  bd=0, relief="flat", activebackground='#27ae60', 
                  width=12, height=1).pack(side="left", padx=15, pady=10)

        btn_frame = tk.Frame(self.frame, bg='#e6ecf0')
        btn_frame.pack(fill="x", padx=30, pady=20)
        actions = [
            ("Delete Workout", self.delete_workout, '#e74c3c', '#c0392b'),
            ("Total Duration", self.view_total_duration, '#3498db', '#2980b9'),
            ("Analytics", self.show_analytics, '#f1c40f', '#e67e22'),
            ("Goals", self.view_health_goals, '#9b59b6', '#8e44ad'),
            ("Set Goals", self.open_goals_settings, '#1abc9c', '#16a085'),
            ("Progress", self.check_goal_progress, '#34495e', '#2c3e50'),
            ("Get Plan", self.get_fitness_plan, '#e67e22', '#d35400'),
            ("Export", self.export_workouts, '#7f8c8d', '#6c7a89')
        ]
        for text, cmd, bg_color, active_bg in actions:
            tk.Button(btn_frame, text=text, command=cmd, font=("Helvetica", 12), 
                      bg=bg_color, fg='white', bd=0, relief="flat", 
                      activebackground=active_bg, width=12, height=1).pack(side="left", padx=10, pady=5)

        list_frame = tk.Frame(self.frame, bg='#e6ecf0')
        list_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        self.workout_listbox = tk.Listbox(list_frame, height=15, font=("Helvetica", 12), 
                                         bd=2, relief="groove", bg='#ffffff')
        self.workout_listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.workout_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.workout_listbox.config(yscrollcommand=scrollbar.set)

        self.load_data()

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(self.frame, textvariable=self.status_var, font=("Helvetica", 12), 
                 bg='#e6ecf0', fg='#7f8c8d').pack(side="bottom", fill="x", pady=10)

    def calculate_bmi(self, weight, height):
        return weight / ((height / 100) ** 2)

    def get_workout_plan(self, goal):
        plans = {
            "gain": "🏋️ Strength Training: Squats, Deadlifts, Bench Press, Pull-ups (4-5 times/week)",
            "lose": "🏃 Cardio + HIIT: Running, Jump Rope, Cycling, Bodyweight Exercises (5 times/week)",
            "maintain": "🧘 Mixed Routine: Strength + Cardio (3-4 times/week)"
        }
        return plans.get(goal, "🧘 Mixed Routine: Strength + Cardio (3-4 times/week)")

    def get_calories(self, goal, weight):
        calorie_multipliers = {"gain": 35, "lose": 25, "maintain": 30}
        calories = weight * calorie_multipliers.get(goal, 30)
        diets = {
            "gain": "High Protein Diet",
            "lose": "Caloric Deficit Diet",
            "maintain": "Balanced Diet"
        }
        return f"🍽️ {calories} kcal/day ({diets.get(goal, 'Balanced Diet')})"

    def log_workout(self):
        workout_type = self.workout_var.get()
        intensity = self.intensity_var.get()
        duration_text = self.duration_var.get()
        try:
            duration = float(duration_text) if duration_text else 0
            if not workout_type or not intensity or duration <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Input Error", "Please select valid workout details!")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        workout = f"{timestamp} | {workout_type} | {duration} mins | {intensity}"
        self.workouts.append((timestamp, workout_type, duration, intensity))
        self.workout_listbox.insert(tk.END, workout)
        self.workout_combobox.set("")
        self.duration_combobox.set("")
        self.intensity_combobox.set("")
        self.save_data()
        self.update_status("Workout logged!")

    def delete_workout(self):
        try:
            idx = self.workout_listbox.curselection()[0]
            self.workout_listbox.delete(idx)
            self.workouts.pop(idx)
            self.save_data()
            self.update_status("Workout deleted!")
        except IndexError:
            messagebox.showwarning("Selection Error", "Please select a workout!")

    def view_total_duration(self):
        total = sum(duration for _, _, duration, _ in self.workouts)
        messagebox.showinfo("Total Duration", f"Total: {total} minutes")
        self.update_status("Duration displayed")

    def show_analytics(self):
        if not self.workouts:
            messagebox.showinfo("No Data", "No workout data!")
            return

        types = {}
        for _, workout_type, duration, _ in self.workouts:
            types[workout_type] = types.get(workout_type, 0) + duration
        
        analytics_message = "Workout Analytics Report\n\n"
        analytics_message += "Time by Workout Type:\n"
        total_duration = sum(types.values())
        for workout_type, duration in types.items():
            percentage = (duration / total_duration) * 100 if total_duration > 0 else 0
            analytics_message += f"- {workout_type}: {duration} mins ({percentage:.1f}%)\n"
        
        analytics_message += "\n"
        analytics_message += "Workout Count by Intensity:\n"
        intensities = {"Low": 0, "Medium": 0, "High": 0}
        for _, _, _, intensity in self.workouts:
            intensities[intensity] += 1
        for intensity, count in intensities.items():
            analytics_message += f"- {intensity}: {count} workouts\n"

        try:
            # Increase figure size to accommodate larger chart (6x6 to 7.8x7.8 for 30% increase)
            plt.figure(figsize=(7.8, 7.8))
            labels = list(types.keys())
            values = list(types.values())
            def custom_autopct(pct, allvals, labels):
                absolute = int(round(pct * sum(allvals) / 100.0))
                return f"{labels.pop(0)}\n{pct:.1f}%"
            plt.pie(values, autopct=lambda pct: custom_autopct(pct, values, labels[:]), 
                    pctdistance=0.7, textprops={'fontsize': 12}, 
                    colors=['#3498db', '#e74c3c', '#2ecc71', '#f1c40f', '#9b59b6', '#1abc9c', '#34495e', '#e67e22'])
            plt.title('Workout Time by Type', fontsize=16)
            plt.savefig('workout_pie.png')
            plt.close()
        except Exception as e:
            messagebox.showwarning("Analytics Error", f"Failed to save pie chart: {e}")
            return

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import inch
            pdf_file = f"analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            output_dir = "analytics_reports"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            pdf_path = os.path.join(output_dir, pdf_file)
            
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            styles = getSampleStyleSheet()
            styles['Title'].fontSize = 20
            styles['Normal'].fontSize = 14
            styles['Normal'].leading = 18  # Increase line spacing for better readability
            story = []

            # Add title with increased spacing below
            story.append(Paragraph("Workout Analytics Report", styles['Title']))
            story.append(Spacer(1, 36))  # Increased spacing after title

            # Split the message into sections and add spacing between lines
            sections = analytics_message.split("\n\n")
            for section in sections:
                lines = section.split("\n")
                for i, line in enumerate(lines):
                    if line.strip():
                        story.append(Paragraph(line, styles['Normal']))
                    # Add spacing after each line, but not after the last line in a section
                    if i < len(lines) - 1:
                        story.append(Spacer(1, 12))
                # Add larger spacing between sections
                story.append(Spacer(1, 24))

            # Add the pie chart with increased size (30% larger: 300 to 390 points)
            if os.path.exists('workout_pie.png'):
                story.append(Image('workout_pie.png', width=390, height=390))
                story.append(Spacer(1, 36))  # Increased spacing after the chart
            else:
                story.append(Paragraph("Pie chart unavailable", styles['Normal']))
                story.append(Spacer(1, 36))

            doc.build(story)

            system = platform.system()
            pdf_abs_path = os.path.abspath(pdf_path)
            try:
                if system == "Windows":
                    os.startfile(pdf_abs_path)
                elif system == "Darwin":
                    subprocess.run(["open", pdf_abs_path], check=True)
                else:
                    subprocess.run(["xdg-open", pdf_abs_path], check=True)
            except Exception as open_error:
                messagebox.showwarning("File Error", f"PDF generated but failed to open: {open_error}")

            self.update_status("Analytics PDF generated and opened")
        except PermissionError:
            messagebox.showwarning("File Error", "Permission denied while generating PDF. Check folder permissions.")
        except Exception as e:
            messagebox.showwarning("File Error", f"Failed to generate PDF: {e}")

        try:
            if os.path.exists('workout_pie.png'):
                os.remove('workout_pie.png')
        except Exception as e:
            messagebox.showwarning("Cleanup Error", f"Failed to remove temporary file workout_pie.png: {e}")

    def view_health_goals(self):
        goals = f"Goals:\nSteps: {self.health_goals['steps']}\nCalories: {self.health_goals['calories']} kcal\nWorkouts: {self.health_goals['workouts']}\nHydration: {self.hydration_goal} ml"
        messagebox.showinfo("Health Goals", goals)
        self.update_status("Goals displayed")

    def open_goals_settings(self):
        window = tk.Toplevel(self.frame)
        window.title("Set Goals")
        window.geometry("350x300")
        window.configure(bg='#e6ecf0')
        
        entries = {}
        for goal, value in [('Steps', self.health_goals['steps']), 
                          ('Calories (kcal)', self.health_goals['calories']),
                          ('Workouts', self.health_goals['workouts']),
                          ('Hydration (ml)', self.hydration_goal)]:
            tk.Label(window, text=goal, font=("Helvetica", 12), bg='#e6ecf0', fg='#34495e').pack(pady=5)
            entry = tk.Entry(window, font=("Helvetica", 12), bd=2, relief="groove")
            entry.insert(0, value)
            entry.pack(pady=5, padx=20, ipady=5)
            entries[goal] = entry

        def save():
            try:
                self.health_goals['steps'] = int(entries['Steps'].get())
                self.health_goals['calories'] = int(entries['Calories (kcal)'].get())
                self.health_goals['workouts'] = int(entries['Workouts'].get())
                self.hydration_goal = int(entries['Hydration (ml)'].get())
                self.save_data()
                messagebox.showinfo("Success", "Goals updated!")
                window.destroy()
                self.update_status("Goals updated")
            except ValueError:
                messagebox.showwarning("Input Error", "Enter valid numbers!")

        tk.Button(window, text="Save Goals", command=save, font=("Helvetica", 14), 
                  bg='#2ecc71', fg='white', bd=0, relief="flat", 
                  activebackground='#27ae60', width=15, height=2).pack(pady=20)

    def check_goal_progress(self):
        progress = (len(self.workouts) / self.health_goals['workouts']) * 100 if self.health_goals['workouts'] > 0 else 0
        messagebox.showinfo("Progress", f"Workout Progress: {progress:.1f}% ({len(self.workouts)}/{self.health_goals['workouts']})")
        self.update_status("Progress checked")

    def get_fitness_plan(self):
        window = tk.Toplevel(self.frame)
        window.title("Fitness Plan")
        window.geometry("350x350")
        window.configure(bg='#e6ecf0')
        
        tk.Label(window, text="Name:", font=("Helvetica", 12), bg='#e6ecf0', fg='#34495e').pack(pady=5)
        name_entry = tk.Entry(window, font=("Helvetica", 12), bd=2, relief="groove")
        name_entry.pack(pady=5, padx=20, ipady=5)
        
        tk.Label(window, text="Weight (kg):", font=("Helvetica", 12), bg='#e6ecf0', fg='#34495e').pack(pady=5)
        weight_entry = tk.Entry(window, font=("Helvetica", 12), bd=2, relief="groove")
        weight_entry.pack(pady=5, padx=20, ipady=5)
        
        tk.Label(window, text="Height (cm):", font=("Helvetica", 12), bg='#e6ecf0', fg='#34495e').pack(pady=5)
        height_entry = tk.Entry(window, font=("Helvetica", 12), bd=2, relief="groove")
        height_entry.pack(pady=5, padx=20, ipady=5)
        
        tk.Label(window, text="Goal:", font=("Helvetica", 12), bg='#e6ecf0', fg='#34495e').pack(pady=5)
        goal_var = tk.StringVar()
        goal_combobox = ttk.Combobox(window, textvariable=goal_var, state="readonly", font=("Helvetica", 12), 
                                     values=("Gain", "Lose", "Maintain"), style="Custom.TCombobox")
        goal_var.set("Maintain")
        goal_combobox.pack(pady=5, padx=20, ipady=5)

        def generate_plan():
            try:
                name = name_entry.get().strip()
                weight = float(weight_entry.get())
                height = float(height_entry.get())
                goal = goal_var.get().lower()
                if not name or not goal or goal not in ["gain", "lose", "maintain"]:
                    raise ValueError
                bmi = self.calculate_bmi(weight, height)
                plan = f"👋 Hello {name},\n📊 BMI: {bmi:.1f}\n{self.get_workout_plan(goal)}\n{self.get_calories(goal, weight)}"
                messagebox.showinfo("Fitness Plan", plan)
                window.destroy()
                self.update_status("Plan generated")
            except ValueError:
                messagebox.showwarning("Input Error", "Please enter valid details!")

        tk.Button(window, text="Generate Plan", command=generate_plan, font=("Helvetica", 14), 
                  bg='#3498db', fg='white', bd=0, relief="flat", 
                  activebackground='#2980b9', width=15, height=2).pack(pady=20)

    def save_data(self):
        try:
            with open("fitness_data.json", "w") as f:
                json.dump({
                    'workouts': self.workouts,
                    'health_goals': self.health_goals, 
                    'hydration_goal': self.hydration_goal
                }, f, indent=2)
        except PermissionError:
            messagebox.showwarning("File Error", "Permission denied while saving data. Check file permissions.")
        except Exception as e:
            messagebox.showwarning("File Error", f"Failed to save data: {e}")

    def load_data(self):
        try:
            if os.path.exists("fitness_data.json"):
                with open("fitness_data.json", "r") as f:
                    data = json.load(f)
                    loaded_workouts = data.get('workouts', [])
                    self.workouts = []
                    for workout in loaded_workouts:
                        if not isinstance(workout, (list, tuple)) or len(workout) != 4:
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                            workout_type = "Unknown"
                            duration = 0
                            intensity = "Unknown"
                        else:
                            timestamp, workout_type, duration, intensity = workout
                            try:
                                duration = float(duration)
                            except (ValueError, TypeError):
                                duration = 0
                            if not isinstance(workout_type, str):
                                workout_type = "Unknown"
                            if not isinstance(intensity, str):
                                intensity = "Unknown"
                        self.workouts.append((timestamp, workout_type, duration, intensity))
                        self.workout_listbox.insert(tk.END, f"{timestamp} | {workout_type} | {duration} mins | {intensity}")
                    self.health_goals = data.get('health_goals', self.health_goals)
                    self.hydration_goal = data.get('hydration_goal', self.hydration_goal)
        except json.JSONDecodeError:
            messagebox.showwarning("File Error", "Corrupted data file. Starting with empty data.")
            self.workouts = []
        except PermissionError:
            messagebox.showwarning("File Error", "Permission denied while loading data. Check file permissions.")
        except Exception as e:
            messagebox.showwarning("File Error", f"Unable to load workout data: {e}")

    def export_workouts(self):
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors

            pdf_file = "fitness.pdf"
            output_dir = "workout_reports"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            pdf_path = os.path.join(output_dir, pdf_file)

            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            story.append(Paragraph("Workout Report", styles['Title']))
            story.append(Spacer(1, 12))

            if not self.workouts:
                story.append(Paragraph("No workouts logged yet.", styles['Normal']))
            else:
                data = [["Date", "Type", "Duration (mins)", "Intensity"]]
                for timestamp, workout_type, duration, intensity in self.workouts:
                    data.append([timestamp, workout_type, str(duration), intensity])

                table = Table(data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                story.append(table)

            doc.build(story)
            messagebox.showinfo("Success", f"Exported to {pdf_file}!")

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
                messagebox.showwarning("File Error", f"PDF exported but failed to open: {open_error}")

            self.update_status("Workouts exported to PDF")
        except ImportError:
            messagebox.showwarning("Export Error", "Please install reportlab to export to PDF (pip install reportlab).")
        except PermissionError:
            messagebox.showwarning("File Error", "Permission denied while exporting PDF. Check file permissions.")
        except Exception as e:
            messagebox.showwarning("Export Error", f"Failed to export: {e}")

    def update_status(self, message):
        self.status_var.set(message)
        self.frame.after(3000, lambda: self.status_var.set("Ready"))

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Fitness Assistant")
    app = FitnessAssistant(root)
    root.mainloop()