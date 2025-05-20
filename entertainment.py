import tkinter as tk
from tkinter import messagebox, ttk
import random
import pygame
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import time

class Entertainment:
    def __init__(self, parent, music_base_dir="music"):
        self.parent = parent
        self.frame = tk.Frame(parent, bg="#1E1E2F")
        self.frame.pack(fill="both", expand=True)
        
        self.music_base_dir = os.path.abspath(music_base_dir)
        
        self.audio_initialized = False
        try:
            pygame.mixer.init()
            self.current_audio = None
            self.audio_initialized = True
            self.laugh_channel = pygame.mixer.Channel(1)  # For sound effects
        except Exception as e:
            messagebox.showerror("Audio Error", f"Failed to initialize audio: {e}\nMusic playback disabled.")
            print(f"Failed to initialize pygame mixer: {e}")
            pygame.mixer.quit()
            self.current_audio = None
        
        self.accent_color = "#FF6F61"
        self.font_size = 12
        
        self.current_volume = 0.5  # Default volume at 50%
        
        self.tracks_display = {}
        self.track_lists_with_paths = {}
        
        style = ttk.Style()
        style.configure("TButton", font=("Comic Sans MS", 16, "bold"), padding=10, background="#FF6F61", foreground="#FF0000")
        style.map("TButton", background=[("active", "#FF8A80")], foreground=[("active", "#FF0000")])
        style.configure("Small.TButton", font=("Comic Sans MS", 12, "bold"), padding=6)
        style.configure("Trivia.TButton", font=("Comic Sans MS", 14, "bold"), padding=10, background="#FFFF00", foreground="#42A5F5")
        style.map("Trivia.TButton", background=[("active", "#FFD700")], foreground=[("active", "#64B5F6")])
        style.configure("Joke.TButton", font=("Comic Sans MS", 14, "bold"), padding=10, background="#FFD54F", foreground="black")
        style.map("Joke.TButton", background=[("active", "#FFE082")], foreground=[("active", "black")])
        style.configure("Trivia.TRadiobutton", font=("Comic Sans MS", 12), background="#1E1E2F", foreground="white")
        style.configure("Custom.Horizontal.TProgressbar", background="#FF6F61", troughcolor="#2D2D44")

        self.header_frame = tk.Frame(self.frame, bg="#2D2D44")
        self.header_frame.pack(fill="x", pady=(10, 5))
        
        self.feature_frame = tk.Frame(self.header_frame, bg="#2D2D44")
        self.feature_frame.pack(side="left", padx=20)
        tk.Label(self.feature_frame, text="🎮 Select Feature:", bg="#2D2D44", fg="white", font=("Comic Sans MS", 16, "bold")).pack(side="left", padx=5)
        self.feature_var = tk.StringVar(value="Music Player")
        features = ["Music Player", "Trivia Challenge", "Joke Cracker"]
        self.feature_menu = tk.OptionMenu(self.feature_frame, self.feature_var, *features, command=self.switch_feature)
        self.feature_menu.config(font=("Comic Sans MS", 14), bg="#FF6F61", fg="white", activebackground="#FF8A80", activeforeground="white")
        self.feature_menu.pack(side="left", padx=10)

        self.title_label = tk.Label(self.frame, text="🎉 Entertainment Hub", font=("Comic Sans MS", 30, "bold"), bg="#1E1E2F", fg="#FF6F61")
        self.title_label.pack(pady=20)

        self.content_frame = tk.Frame(self.frame, bg="#1E1E2F")
        self.content_frame.pack(fill="both", expand=True)
        
        self.initialize_game_state()
        
        self.feature_frames = {}
        self.setup_music_player()
        self.setup_trivia()
        self.setup_joke_cracker()
        
        self.switch_feature(self.feature_var.get())
        
        self.parent.bind('<Up>', self.increase_volume)
        self.parent.bind('<Down>', self.decrease_volume)

        self.parent.winfo_toplevel().protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.stop_music()
        if self.audio_initialized:
            pygame.mixer.quit()
        self.parent.winfo_toplevel().destroy()

    def destroy(self):
        print("Destroying Entertainment module, stopping music")
        self.stop_music()
        if self.audio_initialized:
            try:
                pygame.mixer.quit()
                print("Pygame mixer quit successfully")
            except Exception as e:
                print(f"Error quitting pygame mixer: {e}")
        self.frame.destroy()

    def initialize_game_state(self):
        self.music_playing = False
        self.music_progress_id = None
        self.current_track_index = 0
        self.current_joke_index = -1
        self.favorite_jokes = []
        self.trivia_leaderboard = []
        self.trivia_score = 0
        self.current_question = 0
        self.streak = 0
        self.trivia_time_left = 15
        self.trivia_timer_id = None

    def switch_feature(self, feature):
        self.stop_music()
        for frame in self.feature_frames.values():
            frame.pack_forget()
        if feature in self.feature_frames:
            self.feature_frames[feature].pack(fill="both", expand=True, padx=20, pady=15)
            self.title_label.configure(text=f"🎉 {feature}")
        else:
            self.title_label.configure(text="🎉 Entertainment Hub - Feature Not Found")

    def setup_music_player(self):
        music_frame = tk.LabelFrame(self.content_frame, text="🎵 Music Player", font=("Comic Sans MS", 20, "bold"), bg="#2D2D44", fg="#FF6F61", padx=15, pady=15, bd=4, relief="ridge")
        self.feature_frames["Music Player"] = music_frame
        
        playlist_frame = tk.Frame(music_frame, bg="#2D2D44")
        playlist_frame.pack(fill="x", pady=5)
        tk.Label(playlist_frame, text="🎧 Select Playlist:", bg="#2D2D44", fg="white", font=("Comic Sans MS", 16, "bold")).pack(side="left", padx=10)
        self.playlist_var = tk.StringVar(value="Relaxing")
        playlists = ["Relaxing", "Party", "Mood", "Study", "Workout"]
        playlist_menu = tk.OptionMenu(playlist_frame, self.playlist_var, *playlists, command=self.update_track_list)
        playlist_menu.config(font=("Comic Sans MS", 14), bg="#FF6F61", fg="white", activebackground="#FF8A80", activeforeground="white", width=15)
        playlist_menu.pack(side="left", padx=10)

        control_frame = tk.Frame(music_frame, bg="#2D2D44")
        control_frame.pack(fill="x", pady=5)
        buttons = [
            ("▶ Play", self.toggle_music_playback),
            ("⏹ Stop", self.stop_music),
            ("⏭️ Skip", self.skip_track),
            ("🎭 Mood", self.suggest_music)
        ]
        for text, cmd in buttons:
            btn = ttk.Button(control_frame, text=text, command=cmd, width=15, style="TButton")
            btn.pack(side="left", padx=10)

        options_frame = tk.Frame(music_frame, bg="#2D2D44")
        options_frame.pack(fill="x", pady=5)
        self.repeat_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="🔁 Repeat", variable=self.repeat_var, style="TCheckbutton").pack(side="left", padx=10)
        self.shuffle_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="🔀 Shuffle", variable=self.shuffle_var, command=self.update_current_track, style="TCheckbutton").pack(side="left", padx=10)

        self.now_playing_label = tk.Label(music_frame, text="", bg="#2D2D44", fg="#FFD54F", font=("Comic Sans MS", 12, "italic"))
        self.now_playing_label.pack(pady=5)
        self.current_track_label = tk.Label(music_frame, text="🎵 Current Track: None", bg="#25253A", fg="#FFD54F", font=("Comic Sans MS", 16, "bold"), pady=5, padx=10, bd=2, relief="raised")
        self.current_track_label.pack(pady=5)
        self.progress = ttk.Progressbar(music_frame, length=400, mode="determinate", style="Custom.Horizontal.TProgressbar")
        self.progress.pack(pady=5)

        self.track_list_label = tk.Label(music_frame, text="🎼 Track List: (Select a playlist to view tracks)", bg="#2D2D44", fg="#FFD54F", font=("Comic Sans MS", 16, "bold"), pady=5, padx=20, anchor="w", justify="left")
        self.track_list_label.pack(pady=5, fill="x")

    def increase_volume(self, event):
        self.current_volume = min(1.0, self.current_volume + 0.05)
        self.update_volume()
        print(f"Volume increased to {self.current_volume * 100}%")

    def decrease_volume(self, event):
        self.current_volume = max(0.0, self.current_volume - 0.05)
        self.update_volume()
        print(f"Volume decreased to {self.current_volume * 100}%")

    def update_volume(self):
        if not self.audio_initialized:
            return
        try:
            pygame.mixer.music.set_volume(self.current_volume)
            print(f"Pygame volume updated to: {self.current_volume}")
        except Exception as e:
            print(f"Error updating pygame volume: {e}")

    def setup_trivia(self):
        trivia_frame = tk.LabelFrame(self.content_frame, text="❓ Trivia Challenge", font=("Comic Sans MS", 20, "bold"), bg="#2D2D44", fg="#42A5F5", padx=15, pady=15, bd=4, relief="ridge")
        self.feature_frames["Trivia Challenge"] = trivia_frame
        
        intro_label = tk.Label(trivia_frame, text="🎓 Test your knowledge with fun trivia questions! 🎓", font=("Comic Sans MS", 16, "italic"), bg="#2D2D44", fg="white", wraplength=500)
        intro_label.pack(pady=15)
        
        category_frame = tk.Frame(trivia_frame, bg="#2D2D44")
        category_frame.pack(fill="x", pady=10)
        tk.Label(category_frame, text="📚 Choose Category:", bg="#2D2D44", fg="white", font=("Comic Sans MS", 16, "bold")).pack(side="left", padx=10)
        self.trivia_category_var = tk.StringVar(value="General")
        category_menu = tk.OptionMenu(category_frame, self.trivia_category_var, "General", "Science", "History", "Pop Culture")
        category_menu.config(font=("Comic Sans MS", 14), bg="#42A5F5", fg="white", activebackground="#64B5F6", activeforeground="white", width=15)
        category_menu.pack(side="left", padx=10)
        
        button_frame = tk.Frame(trivia_frame, bg="#2D2D44")
        button_frame.pack(fill="x", pady=20)
        ttk.Button(button_frame, text="🏆 Start Trivia", command=self.start_trivia, style="Trivia.TButton", width=20).pack(pady=10)
        ttk.Button(button_frame, text="🌟 View Leaderboard", command=self.show_trivia_leaderboard, style="Trivia.TButton", width=20).pack(pady=10)

    def start_trivia(self):
        trivia_window = tk.Toplevel(self.parent)
        trivia_window.title("Trivia Challenge")
        trivia_window.geometry("600x700")
        trivia_window.configure(bg="#1E1E2F")
        
        def on_closing():
            if self.trivia_timer_id:
                trivia_window.after_cancel(self.trivia_timer_id)
                self.trivia_timer_id = None
            trivia_window.destroy()
        
        trivia_window.protocol("WM_DELETE_WINDOW", on_closing)
        
        questions = {
            "General": [
                ("What is the largest planet in our Solar System? 🌍", ["Earth", "Mars", "Jupiter", "Saturn"], 2, "It's the fifth planet from the Sun."),
                ("Which artist painted the Mona Lisa? 🎨", ["Vincent van Gogh", "Leonardo da Vinci", "Pablo Picasso", "Michelangelo"], 1, "He was a Renaissance genius."),
                ("What gas do plants absorb from the atmosphere? 🌱", ["Oxygen", "Nitrogen", "Carbon Dioxide", "Helium"], 2, "It's used in photosynthesis.")
            ],
            "Science": [
                ("What is the chemical symbol for gold? ⚗️", ["Ag", "Au", "Fe", "Cu"], 1, "Think of the Latin word 'Aurum'."),
                ("What planet is known as the Red Planet? 🪐", ["Venus", "Mars", "Jupiter", "Mercury"], 1, "It's named after a Roman god of war"),
                ("What is the powerhouse of the cell? 🧬", ["Nucleus", "Mitochondria", "Ribosome", "Golgi"], 1, "It produces ATP.")
            ],
            "History": [
                ("In which year did the Titanic sink? 🚢", ["1912", "1905", "1920", "1898"], 0, "It was early in the 20th century."),
                ("Who was the first president of the United States? 🇺🇸", ["Thomas Jefferson", "George Washington", "Abraham Lincoln", "John Adams"], 1, "He served from 1789 to 1797."),
                ("What ancient wonder was located in Egypt? 🏛️", ["Hanging Gardens", "Colossus of Rhodes", "Great Pyramid", "Lighthouse of Alexandria"], 2, "It's a tomb for a pharaoh.")
            ],
            "Pop Culture": [
                ("Who played Harry Potter in the movies? ⚡", ["Daniel Radcliffe", "Rupert Grint", "Elijah Wood", "Tom Felton"], 0, "He was a child actor in the early 2000s."),
                ("What band sang 'Bohemian Rhapsody'? 🎸", ["The Beatles", "Queen", "The Rolling Stones", "Led Zeppelin"], 1, "Think of Freddie Mercury."),
                ("What movie features a lion named Simba? 🦁", ["The Jungle Book", "Madagascar", "The Lion King", "Zootopia"], 2, "It's a Disney classic.")
            ]
        }
        
        category = self.trivia_category_var.get()
        question_list = questions.get(category, questions["General"])
        
        self.trivia_score = 0
        self.current_question = 0
        self.streak = 0
        self.trivia_time_left = 15
        self.trivia_timer_id = None
        
        header_frame = tk.Frame(trivia_window, bg="#2D2D44", bd=4, relief="ridge")
        header_frame.pack(fill="x", padx=15, pady=15)
        
        progress_label = tk.Label(header_frame, text=f"Question {self.current_question + 1}/{len(question_list)}", font=("Comic Sans MS", 14, "bold"), bg="#2D2D44", fg="white")
        progress_label.pack(side="left", padx=15)
        
        self.trivia_timer_label = tk.Label(header_frame, text=f"⏳ Time: {self.trivia_time_left}s", font=("Comic Sans MS", 14, "bold"), bg="#2D2D44", fg="#FFD54F")
        self.trivia_timer_label.pack(side="right", padx=15)
        
        score_label = tk.Label(header_frame, text=f"🌟 Score: {self.trivia_score}", font=("Comic Sans MS", 14, "bold"), bg="#2D2D44", fg="#FF6F61")
        score_label.pack(side="right", padx=15)
        
        progress_bar = ttk.Progressbar(trivia_window, length=500, mode="determinate", maximum=len(question_list), style="Custom.Horizontal.TProgressbar")
        progress_bar.pack(pady=15)
        progress_bar["value"] = self.current_question
        
        question_frame = tk.Frame(trivia_window, bg="#1E90FF", bd=4, relief="sunken")
        question_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        question_label = tk.Label(question_frame, text=question_list[0][0], font=("Comic Sans MS", 18, "bold"), bg="#1E90FF", fg="black", wraplength=500, justify="center")
        question_label.pack(pady=25)
        
        answer_var = tk.IntVar(value=-1)
        answer_frame = tk.Frame(question_frame, bg="#1E90FF")
        answer_frame.pack(pady=15)
        
        for i, option in enumerate(question_list[0][1]):
            rb = ttk.Radiobutton(answer_frame, text=option, variable=answer_var, value=i, style="Trivia.TRadiobutton")
            rb.grid(row=i, column=0, sticky="w", padx=30, pady=10)
        
        feedback_label = tk.Label(trivia_window, text="", font=("Comic Sans MS", 14, "italic"), bg="#1E1E2F", fg="white")
        feedback_label.pack(pady=15)
        
        button_frame = tk.Frame(trivia_window, bg="#1E1E2F")
        button_frame.pack(pady=20)
        
        def start_trivia_timer():
            if self.trivia_time_left > 0:
                self.trivia_time_left -= 1
                self.trivia_timer_label.configure(text=f"⏳ Time: {self.trivia_time_left}s")
                self.trivia_timer_id = trivia_window.after(1000, start_trivia_timer)
            else:
                feedback_label.configure(text="⏰ Time's up! Moving to next question.", fg="#FF6F61")
                self.streak = 0
                self.current_question += 1
                next_question()

        def show_trivia_hint():
            if self.trivia_score >= 5:
                self.trivia_score -= 5
                score_label.configure(text=f"🌟 Score: {self.trivia_score}")
                hint = question_list[self.current_question][3]
                feedback_label.configure(text=f"💡 Hint: {hint}", fg="#42A5F5")
            else:
                feedback_label.configure(text="📉 Need 5 points for a hint!", fg="#FF6F61")

        def next_question():
            if self.current_question < len(question_list):
                progress_label.configure(text=f"Question {self.current_question + 1}/{len(question_list)}")
                progress_bar["value"] = self.current_question
                question_label.configure(text=question_list[self.current_question][0])
                answer_var.set(-1)
                for i, widget in enumerate(answer_frame.winfo_children()):
                    widget.configure(text=question_list[self.current_question][1][i])
                feedback_label.configure(text="")
                self.trivia_time_left = 15
                self.trivia_timer_label.configure(text=f"⏳ Time: {self.trivia_time_left}s")
                if self.trivia_timer_id:
                    trivia_window.after_cancel(self.trivia_timer_id)
                start_trivia_timer()
            else:
                if self.trivia_timer_id:
                    trivia_window.after_cancel(self.trivia_timer_id)
                    self.trivia_timer_id = None
                max_score = len(question_list) * 10
                self.trivia_leaderboard.append(self.trivia_score)
                messagebox.showinfo("Trivia Result", f"🎉 Trivia Complete!\nYour Score: {self.trivia_score}/{max_score} 🎖️")
                trivia_window.destroy()

        def check_answer():
            if answer_var.get() == -1:
                feedback_label.configure(text="⚠️ Please select an answer!", fg="#FFD54F")
                return
            correct = answer_var.get() == question_list[self.current_question][2]
            if correct:
                self.trivia_score += 10
                self.streak += 1
                feedback_label.configure(text="🎉 Correct!", fg="#00FF00")
                score_label.configure(text=f"🌟 Score: {self.trivia_score}")
            else:
                self.streak = 0
                feedback_label.configure(text=f"❌ Wrong! Correct answer: {question_list[self.current_question][1][question_list[self.current_question][2]]}.", fg="#FF0000")
            if self.trivia_timer_id:
                trivia_window.after_cancel(self.trivia_timer_id)
            self.current_question += 1
            next_question()

        ttk.Button(button_frame, text="✅ Submit Answer", command=check_answer, style="Trivia.TButton", width=20).pack(side="left", padx=15)
        ttk.Button(button_frame, text="💡 Hint (-5 points)", command=show_trivia_hint, style="Trivia.TButton", width=20).pack(side="left", padx=15)
        
        start_trivia_timer()

    def show_trivia_leaderboard(self):
        leaderboard_window = tk.Toplevel(self.parent)
        leaderboard_window.title("Trivia Leaderboard")
        leaderboard_window.geometry("500x500")
        leaderboard_window.configure(bg="#1E1E2F")
        
        tk.Label(leaderboard_window, text="🏆 Trivia Hall of Fame 🏆", font=("Comic Sans MS", 20, "bold"), bg="#1E1E2F", fg="#42A5F5").pack(pady=20)
        
        canvas = tk.Canvas(leaderboard_window, bg="#2D2D44", highlightthickness=0)
        scrollbar = ttk.Scrollbar(leaderboard_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#2D2D44")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        scrollbar.pack(side="right", fill="y")
        
        if not self.trivia_leaderboard:
            tk.Label(scrollable_frame, text="😎 No scores yet! Play to claim the top spot!", font=("Comic Sans MS", 14, "italic"), bg="#2D2D44", fg="white").pack(pady=20)
        else:
            sorted_scores = sorted(self.trivia_leaderboard, reverse=True)[:10]
            for i, score in enumerate(sorted_scores, 1):
                rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🌟"
                tk.Label(
                    scrollable_frame,
                    text=f"{rank_emoji} {i}. Score: {score}",
                    font=("Comic Sans MS", 16, "bold" if i <= 3 else "normal"),
                    bg="#2D2D44",
                    fg="#FFD700" if i == 1 else "#C0C0C0" if i == 2 else "#CD7F32" if i == 3 else "white"
                ).pack(pady=10)
        
        button_frame = tk.Frame(leaderboard_window, bg="#1E1E2F")
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="🔄 Reset Leaderboard", command=lambda: self.reset_trivia_leaderboard(leaderboard_window), style="Trivia.TButton", width=20).pack()

    def reset_trivia_leaderboard(self, leaderboard_window):
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset the trivia leaderboard?"):
            self.trivia_leaderboard = []
            leaderboard_window.destroy()
            self.show_trivia_leaderboard()

    def setup_joke_cracker(self):
        joke_frame = tk.LabelFrame(self.content_frame, text="😂 Joke Cracker", font=("Comic Sans MS", 20, "bold"), bg="#2D2D44", fg="#FFD54F", padx=15, pady=15, bd=4, relief="ridge")
        self.feature_frames["Joke Cracker"] = joke_frame
        
        intro_label = tk.Label(joke_frame, text="🎉 Get ready to laugh with some hilarious jokes! 😄", font=("Comic Sans MS", 16, "italic"), bg="#2D2D44", fg="white", wraplength=500)
        intro_label.pack(pady=15)
        
        category_frame = tk.Frame(joke_frame, bg="#2D2D44")
        category_frame.pack(fill="x", pady=10)
        tk.Label(category_frame, text="🎭 Joke Category:", bg="#2D2D44", fg="white", font=("Comic Sans MS", 16, "bold")).pack(side="left", padx=10)
        self.joke_category_var = tk.StringVar(value="Puns")
        category_menu = tk.OptionMenu(category_frame, self.joke_category_var, "Puns", "One-Liners", "Dad Jokes", command=self.reset_joke_index)
        category_menu.config(font=("Comic Sans MS", 14), bg="#FFD54F", fg="black", activebackground="#FFE082", activeforeground="black", width=15)
        category_menu.pack(side="left", padx=10)
        
        joke_display_frame = tk.Frame(joke_frame, bg="#FFD54F", bd=4, relief="sunken")
        joke_display_frame.pack(fill="both", expand=True, padx=10, pady=15)
        self.joke_label = tk.Label(joke_display_frame, text="😂 Click 'Next' to get started! 😄", font=("Comic Sans MS", 16, "bold"), wraplength=450, bg="#FFD54F", fg="black", justify="center", padx=15, pady=25)
        self.joke_label.pack(pady=15)
        
        button_frame = tk.Frame(joke_frame, bg="#2D2D44")
        button_frame.pack(fill="x", pady=15)
        buttons = [
            ("➡️ Next", self.tell_joke),
            ("⬅️ Prev", self.tell_previous_joke),
            ("⭐ Rate", self.rate_joke),
            ("❤️ Favorite", self.add_to_favorites),
            ("📜 Favorites", self.view_favorites)
        ]
        for idx, (text, cmd) in enumerate(buttons):
            btn = ttk.Button(button_frame, text=text, command=cmd, style="Joke.TButton", width=15)
            btn.grid(row=0, column=idx, padx=10, pady=10, sticky="ew")

    def reset_joke_index(self, *args):
        self.current_joke_index = -1
        self.joke_label.configure(text="😂 Click 'Next' to get started! 😄")

    def tell_joke(self):
        jokes = {
            "Puns": [
                "I used to be a baker, but I couldn’t make enough dough! 🍞😂",
                "I’m reading a book on anti-gravity—it’s hard to put down! 📖😆",
                "The math teacher was hungry for some pi! 🥧➗"
            ],
            "One-Liners": [
                "I told my computer I needed a break, now it won’t stop sending me Kit Kats! 🍫💻",
                "I’m on a seafood diet—I see food, and I eat it! 🍽️🐟",
                "I’m friends with all electricians—we get a real charge out of it! ⚡👥"
            ],
            "Dad Jokes": [
                "Why don’t skeletons fight in school? They don’t have the guts for it! 💀🏫",
                "How does a penguin build its house? Igloos it together! 🐧🏠",
                "What do you call cheese that isn’t yours? Nacho cheese! 🧀😂"
            ]
        }
        category = self.joke_category_var.get()
        joke_list = jokes.get(category, ["No jokes available!"])
        self.current_joke_index = (self.current_joke_index + 1) % len(joke_list)
        self.joke_label.configure(text=joke_list[self.current_joke_index])
        if self.audio_initialized:
            try:
                laugh_sound = pygame.mixer.Sound(array=[5000, 4000, 3000])
                self.laugh_channel.play(laugh_sound)
            except Exception as e:
                print(f"Error playing laugh sound: {e}")

    def tell_previous_joke(self):
        jokes = {
            "Puns": [
                "I used to be a baker, but I couldn’t make enough dough! 🍞😂",
                "I’m reading a book on anti-gravity—it’s hard to put down! 📖😆",
                "The math teacher was hungry for some pi! 🥧➗"
            ],
            "One-Liners": [
                "I told my computer I needed a break, now it won’t stop sending me Kit Kats! 🍫💻",
                "I’m on a seafood diet—I see food, and I eat it! 🍽️🐟",
                "I’m friends with all electricians—we get a real charge out of it! ⚡👥"
            ],
            "Dad Jokes": [
                "Why don’t skeletons fight in school? They don’t have the guts for it! 💀🏫",
                "How does a penguin build its house? Igloos it together! 🐧🏠",
                "What do you call cheese that isn’t yours? Nacho cheese! 🧀😂"
            ]
        }
        category = self.joke_category_var.get()
        joke_list = jokes.get(category, ["No jokes available!"])
        self.current_joke_index = (self.current_joke_index - 1) % len(joke_list)
        self.joke_label.configure(text=joke_list[self.current_joke_index])

    def rate_joke(self):
        rating_window = tk.Toplevel(self.parent)
        rating_window.title("Rate Joke")
        rating_window.geometry("400x300")
        rating_window.configure(bg="#1E1E2F")
        
        tk.Label(rating_window, text="🌟 Rate this joke (1-5 stars):", font=("Comic Sans MS", 16, "bold"), bg="#1E1E2F", fg="#FFD54F").pack(pady=20)
        rating_var = tk.IntVar(value=3)
        tk.Scale(rating_window, from_=1, to=5, orient="horizontal", variable=rating_var, bg="#2D2D44", fg="white", troughcolor="#FFD54F", length=300, font=("Comic Sans MS", 12)).pack(pady=20)
        
        def submit_rating():
            rating = rating_var.get()
            messagebox.showinfo("Rating", f"🌟 You rated this joke {rating} stars!")
            rating_window.destroy()
        
        ttk.Button(rating_window, text="⭐ Submit", command=submit_rating, style="Joke.TButton", width=15).pack(pady=20)

    def add_to_favorites(self):
        current_joke = self.joke_label.cget("text")
        if current_joke and current_joke not in self.favorite_jokes and current_joke != "😂 Click 'Next' to get started! 😄":
            self.favorite_jokes.append(current_joke)
            messagebox.showinfo("Favorites", "❤️ Joke added to favorites!")

    def view_favorites(self):
        if not self.favorite_jokes:
            messagebox.showinfo("Favorites", "❤️ No favorite jokes yet!")
            return
        
        pdf_file = "favorite_jokes.pdf"
        try:
            doc = SimpleDocTemplate(pdf_file, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            story.append(Paragraph("Favorite Jokes 😂", styles['Title']))
            story.append(Spacer(1, 12))
            
            for idx, joke in enumerate(self.favorite_jokes, 1):
                story.append(Paragraph(f"{idx}. {joke}", styles['BodyText']))
                story.append(Spacer(1, 12))
            
            doc.build(story)
            messagebox.showinfo("Favorites", f"📜 Favorite jokes saved to {pdf_file}!")
        except IOError as e:
            messagebox.showerror("Error", f"Failed to save favorite jokes to PDF: {e}")
            return
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while saving PDF: {e}")
            return
        
        favorites_window = tk.Toplevel(self.parent)
        favorites_window.title("Favorite Jokes")
        favorites_window.geometry("500x500")
        favorites_window.configure(bg="#1E1E2F")
        
        tk.Label(favorites_window, text="😂 Favorite Jokes", font=("Comic Sans MS", 20, "bold"), bg="#1E1E2F", fg="#FFD54F").pack(pady=20)
        
        canvas = tk.Canvas(favorites_window, bg="#2D2D44", highlightthickness=0)
        scrollbar = ttk.Scrollbar(favorites_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#2D2D44")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        scrollbar.pack(side="right", fill="y")
        
        for idx, joke in enumerate(self.favorite_jokes, 1):
            tk.Label(scrollable_frame, text=f"{idx}. {joke}", font=("Comic Sans MS", 14), bg="#2D2D44", fg="white", wraplength=450, justify="left").pack(pady=10, padx=15)

    def update_track_list(self, *args):
        if self.music_playing:
            self.stop_music()
        
        playlist = self.playlist_var.get()
        playlist_dir = os.path.join(self.music_base_dir, playlist.lower())
        
        tracks = []
        track_paths = []
        try:
            if not os.path.isdir(playlist_dir):
                messagebox.showwarning("Warning", f"🎵 Playlist directory '{playlist}' not found!")
                self.track_list_label.configure(text="🎼 Track List: No tracks available")
                self.tracks_display[playlist] = ["No tracks available"]
                self.track_lists_with_paths[playlist] = []
                return
            
            files = [f for f in os.listdir(playlist_dir) if f.lower().endswith('.mp3')]
            if not files:
                messagebox.showwarning("Warning", f"🎵 No MP3 files found in '{playlist}' playlist!")
                self.track_list_label.configure(text="🎼 Track List: No tracks available")
                self.tracks_display[playlist] = ["No tracks available"]
                self.track_lists_with_paths[playlist] = []
                return
            
            files.sort()
            tracks = [os.path.splitext(f)[0].replace('_', ' ').title() for f in files]
            track_paths = [os.path.join(playlist_dir, f) for f in files]
            
            self.tracks_display[playlist] = tracks
            self.track_lists_with_paths[playlist] = track_paths
            
            track_list_text = "\n".join(f"{i+1}. {track}" for i, track in enumerate(tracks))
            self.track_list_label.configure(text=f"🎼 Track List:\n{track_list_text}")
            self.current_track_index = 0
            self.update_current_track()
        except OSError as e:
            messagebox.showerror("Error", f"Failed to access playlist directory: {e}")
            self.track_list_label.configure(text="🎼 Track List: Error loading tracks")
            self.tracks_display[playlist] = ["Error loading tracks"]
            self.track_lists_with_paths[playlist] = []

    def update_current_track(self):
        playlist = self.playlist_var.get()
        tracks = self.tracks_display.get(playlist, ["No tracks available"])
        if not tracks or tracks == ["No tracks available"] or tracks == ["Error loading tracks"]:
            self.current_track_label.configure(text="🎵 Current Track: None")
            return
        if self.shuffle_var.get():
            indices = list(range(len(tracks)))
            random.shuffle(indices)
            tracks = [tracks[i] for i in indices]
        try:
            track = tracks[self.current_track_index % len(tracks)]
            self.current_track_label.configure(text=f"🎵 Current Track: {track}")
        except ZeroDivisionError:
            self.current_track_label.configure(text="🎵 Current Track: None")

    def toggle_music_playback(self):
        if not self.audio_initialized:
            messagebox.showerror("Error", "🎵 Audio device not initialized. Music playback is disabled.")
            return
        if not self.music_playing:
            self.play_music()
            self.feature_frames["Music Player"].winfo_children()[1].winfo_children()[0].configure(text="⏸️ Pause")
            self.music_playing = True
        else:
            self.pause_music()
            self.feature_frames["Music Player"].winfo_children()[1].winfo_children()[0].configure(text="▶ Play")
            self.music_playing = False

    def validate_audio_file(self, file_path):
        if not os.path.exists(file_path):
            return False, f"File does not exist: {file_path}"
        if not file_path.lower().endswith('.mp3'):
            return False, f"File is not an MP3: {file_path}"
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.unload()
            return True, "File is valid"
        except Exception as e:
            return False, f"Invalid audio file: {e}"

    def play_music(self):
        if not self.audio_initialized:
            messagebox.showerror("Error", "🎵 Audio device not initialized. Music playback is disabled.")
            return
        playlist = self.playlist_var.get()
        tracks = self.track_lists_with_paths.get(playlist, [])
        if not tracks:
            messagebox.showerror("Error", "🎵 No tracks available for this playlist! Please select a playlist.")
            return
        track_path = tracks[self.current_track_index % len(tracks)]
        
        is_valid, validation_message = self.validate_audio_file(track_path)
        if not is_valid:
            messagebox.showerror("Error", f"🎵 Could not play track: {validation_message}")
            print(f"Validation failed for {track_path}: {validation_message}")
            return
        
        try:
            if self.current_audio:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                print(f"Stopped previous track: {self.current_audio}")
            
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.set_volume(self.current_volume)
            pygame.mixer.music.play()
            print(f"Playing track: {track_path} at volume {self.current_volume}")
            self.current_audio = track_path
            
            sound = pygame.mixer.Sound(track_path)
            track_duration = sound.get_length() * 1000
            self.progress.configure(maximum=track_duration, value=0)
            
            self.now_playing_label.configure(text=f"🎶 Now Playing: {playlist} Playlist")
            self.update_current_track()
            if self.music_progress_id:
                self.frame.after_cancel(self.music_progress_id)
                self.music_progress_id = None
            self.music_progress_id = self.frame.after(100, lambda: self.update_music_progress(track_duration))
        except Exception as e:
            messagebox.showerror("Error", f"🎵 Could not play track: {e}")
            print(f"Error playing track {track_path}: {e}")
            self.current_audio = None
            self.music_playing = False
            self.feature_frames["Music Player"].winfo_children()[1].winfo_children()[0].configure(text="▶ Play")

    def pause_music(self):
        if not self.audio_initialized:
            messagebox.showerror("Error", "🎵 Audio device not initialized. Music playback is disabled.")
            return
        if self.music_progress_id:
            self.frame.after_cancel(self.music_progress_id)
            self.music_progress_id = None
        try:
            pygame.mixer.music.pause()
            self.now_playing_label.configure(text="⏸️ Paused")
            print("Music paused")
        except Exception as e:
            print(f"Error pausing music: {e}")

    def stop_music(self):
        if not self.audio_initialized:
            print("Audio not initialized, skipping stop_music")
            return
        if self.music_progress_id:
            self.frame.after_cancel(self.music_progress_id)
            self.music_progress_id = None
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            print("Music stopped and unloaded")
        except Exception as e:
            print(f"Error stopping music: {e}")
        self.current_audio = None
        self.music_playing = False
        self.now_playing_label.configure(text="")
        self.current_track_label.configure(text="🎵 Current Track: None")
        self.progress.configure(value=0)
        if "Music Player" in self.feature_frames:
            try:
                self.feature_frames["Music Player"].winfo_children()[1].winfo_children()[0].configure(text="▶ Play")
            except Exception as e:
                print(f"Error updating play button: {e}")

    def update_music_progress(self, track_duration):
        if not self.audio_initialized or not self.music_playing or not self.current_audio:
            self.music_progress_id = None
            return
        try:
            current_pos = pygame.mixer.music.get_pos()
            if current_pos >= 0:
                self.progress.configure(value=min(current_pos, track_duration))
                self.music_progress_id = self.frame.after(100, lambda: self.update_music_progress(track_duration))
            else:
                self.music_progress_id = self.frame.after(100, lambda: self.update_music_progress(track_duration))
            if current_pos >= track_duration - 100:
                self.progress.configure(value=track_duration)
                print("Track finished playing naturally")
                self.handle_track_end()
        except Exception as e:
            print(f"Error in update_music_progress: {e}")
            self.music_playing = False
            self.feature_frames["Music Player"].winfo_children()[1].winfo_children()[0].configure(text="▶ Play")
            self.music_progress_id = None

    def handle_track_end(self):
        self.now_playing_label.configure(text="🎉 Finished Playing")
        if self.repeat_var.get():
            self.progress.configure(value=0)
            if not self.shuffle_var.get():
                self.current_track_index = self.current_track_index
            else:
                self.current_track_index = random.randint(0, len(self.track_lists_with_paths.get(self.playlist_var.get(), [])) - 1)
            self.update_current_track()
            self.play_music()
        else:
            self.current_track_index += 1
            if self.current_track_index < len(self.track_lists_with_paths.get(self.playlist_var.get(), [])):
                self.progress.configure(value=0)
                self.update_current_track()
                self.play_music()
            else:
                self.current_audio = None
                self.feature_frames["Music Player"].winfo_children()[1].winfo_children()[0].configure(text="▶ Play")
                self.music_playing = False
                print("Playback stopped after track finished")

    def skip_track(self):
        if not self.audio_initialized:
            messagebox.showerror("Error", "🎵 Audio device not initialized. Music playback is disabled.")
            return
        self.current_track_index += 1
        self.update_current_track()
        if self.music_playing:
            self.progress.configure(value=0)
            self.now_playing_label.configure(text=f"🎶 Now Playing: {self.playlist_var.get()} Playlist")
            if self.music_progress_id:
                self.frame.after_cancel(self.music_progress_id)
                self.music_progress_id = None
            self.play_music()

    def suggest_music(self):
        moods = {"Stressed": "Relaxing", "Energetic": "Party", "Focused": "Study", "Active": "Workout", "Neutral": "Mood"}
        current_mood = random.choice(list(moods.keys()))
        suggested_playlist = moods[current_mood]
        self.playlist_var.set(suggested_playlist)
        self.update_track_list()
        messagebox.showinfo("Mood-Based Suggestion", f"🎉 Based on your mood ({current_mood}), we suggest the {suggested_playlist} playlist! 😊")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Entertainment Hub")
    root.state('zoomed')
    app = Entertainment(root)
    root.mainloop()