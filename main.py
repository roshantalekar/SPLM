import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import face_recognition
import numpy as np
import bcrypt
import os
import logging
import speech_recognition as sr
import pyttsx3
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from pygame import mixer
from PIL import Image, ImageTk

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Import modules with error handling
try:
    from modules.task_manager import TaskManager
except ImportError:
    logging.warning("TaskManager module not found.")
    TaskManager = None

try:
    from modules.finance_tracker import FinanceTracker
except ImportError:
    logging.warning("FinanceTracker module not found.")
    FinanceTracker = None

try:
    from modules.fitness_assistant import FitnessAssistant
except ImportError:
    logging.warning("FitnessAssistant module not found.")
    FitnessAssistant = None

try:
    from modules.travel_assistant import TravelAssistantApp
except ImportError:
    logging.warning("TravelAssistantApp module not found.")
    TravelAssistantApp = None

try:
    from modules.productivity_tools import ProductivityApp
except ImportError:
    logging.warning("ProductivityApp module not found.")
    ProductivityApp = None

try:
    from modules.entertainment import Entertainment
except ImportError:
    logging.warning("Entertainment module not found.")
    Entertainment = None

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)
        self.widget.bind("<Destroy>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window:
            return
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="#FFFFDD", foreground="black",
                        relief="solid", borderwidth=1, font=("Arial", 10), padx=5, pady=2)
        label.pack()

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class CustomButton(tk.Button):
    def __init__(self, master=None, tooltip_text="", bg_color="#4CAF50", **kwargs):
        super().__init__(master, **kwargs)
        self.default_bg = bg_color
        self.configure(
            font=("Arial", 12, "bold"),
            bg=bg_color,
            fg="white",
            activebackground="#388E3C",
            activeforeground="white",
            borderwidth=0,
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2",
            anchor="center"
        )
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        if tooltip_text:
            Tooltip(self, tooltip_text)

    def on_enter(self, event):
        self.configure(bg="#388E3C")

    def on_leave(self, event):
        self.configure(bg=self.default_bg)

class VoiceControl:
    def __init__(self, app):
        self.app = app
        self.recognizer = sr.Recognizer()
        self.microphone_available = self.check_microphone()
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 160)  # Slightly faster speech
            logging.info("Text-to-speech engine initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize text-to-speech engine: {e}")
            self.engine = None
        self.is_listening = False
        self.executor = None
        self.adjusted_noise = False

    def check_microphone(self):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Reduced duration
            return True
        except Exception as e:
            logging.error(f"Microphone check failed: {e}")
            return False

    def speak(self, text):
        logging.info(f"Attempting to speak: {text}")
        if self.engine is None:
            logging.warning("Text-to-speech engine not available. Cannot speak.")
            self.app.root.after(0, lambda: messagebox.showinfo("Audio Issue", "Text-to-speech is not available. Please check your audio settings."))
            return

        def _speak():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
                logging.info("Successfully spoke the text.")
            except Exception as e:
                logging.error(f"Text-to-speech error: {e}")
                self.app.root.after(0, lambda: messagebox.showerror("Audio Error", f"Failed to speak: {e}"))

        if threading.current_thread() is threading.main_thread():
            _speak()
        else:
            self.app.root.after(0, _speak)

    def listen(self, callback, timeout_seconds=10, retries=1):
        def _listen():
            try:
                if not self.adjusted_noise:
                    with sr.Microphone() as source:
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Reduced duration
                        self.adjusted_noise = True
                        logging.info("Adjusted for ambient noise.")
                self.app.root.after(0, lambda: self.speak("Listening..."))
                self._start_listening(callback, timeout_seconds, retries)
            except Exception as e:
                self.app.root.after(0, lambda: self.speak("An error occurred. Please try again."))
                logging.error(f"Voice recognition setup error: {e}")
                self.app.root.after(0, lambda: callback(None))

        if self.executor is None or self.executor._shutdown:
            self.executor = ThreadPoolExecutor(max_workers=1)
        self.executor.submit(_listen)

    def _start_listening(self, callback, timeout_seconds, retries):
        try:
            with sr.Microphone() as source:
                logging.info("Listening for audio input...")
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=5)  # Reduced timeouts
                logging.info("Audio captured, recognizing...")
                command = self.recognizer.recognize_google(audio, language="en-US").lower()  # Specify language
                logging.info(f"Recognized command: {command}")
                self.app.root.after(0, lambda: callback(command))
        except sr.WaitTimeoutError:
            self.app.root.after(0, lambda: self.speak("No input heard. Please try again."))
            logging.warning("No input heard (timeout).")
            self.app.root.after(0, lambda: callback(None))
        except sr.UnknownValueError:
            if retries > 0:
                self.app.root.after(0, lambda: self.speak("Couldn't understand. Please repeat."))
                logging.warning("Could not understand the audio. Retrying...")
                self.app.root.after(1000, lambda: self._start_listening(callback, timeout_seconds, retries - 1))
            else:
                self.app.root.after(0, lambda: self.speak("Sorry, I couldn't understand that. Please try again."))
                logging.warning("Could not understand the audio after retries.")
                self.app.root.after(0, lambda: callback(None))
        except sr.RequestError as e:
            self.app.root.after(0, lambda: self.speak("Microphone or network issue. Please check your setup."))
            logging.error(f"Speech recognition error: {e}")
            self.app.root.after(0, lambda: callback(None))
        except Exception as e:
            self.app.root.after(0, lambda: self.speak("An error occurred. Please try again."))
            logging.error(f"Voice recognition error: {e}")
            self.app.root.after(0, lambda: callback(None))

    def start_listening(self):
        logging.info("Starting voice control listening.")
        if not self.is_listening:
            self.is_listening = True
            logging.info("Listening started in a separate thread.")
        else:
            logging.warning("Voice control is already listening.")

    def stop_listening(self):
        logging.info("Stopping voice control listening.")
        self.is_listening = False
        if self.executor is not None:
            self.executor.shutdown(wait=True)
        try:
            if self.engine:
                self.engine.stop()
                if self.engine._inLoop:
                    self.engine.endLoop()
                logging.info("Voice control stopped successfully.")
        except Exception as e:
            logging.error(f"Error stopping voice control: {e}")

    def __del__(self):
        self.stop_listening()

class LoginPage:
    def __init__(self, root, on_successful_login):
        self.root = root
        self.on_successful_login = on_successful_login
        self.root.title("Smart Personal Life Manager - Login")
        self.root.geometry("400x550")
        self.root.configure(bg="#FFFFFF")
        self.show_password = False
        self.voice_control = VoiceControl(self)
        self.failed_attempts = 0
        self.max_attempts = 3
        self.lockout_duration = 30
        self.is_locked = False

        self.users = {
            "software": {
                "password": bcrypt.hashpw("123".encode('utf-8'), bcrypt.gensalt())
            }
        }

        self.face_encodings = {}
        self.face_image_paths = {
            "User 1": "user1.jpg",
            "User 2": "user2.jpg",
            "User 3": "user3.jpg"
        }

        self.user_names = {
            "User 1": "AUSTIN",
            "User 2": "ROSHAN",
            "User 3": "SAHIL"
        }

        # Main login frame
        self.login_frame = tk.Frame(self.root, bg="#FFFFFF")
        self.login_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        tk.Label(
            self.login_frame,
            text="Smart Personal Life Manager Login",
            font=("Arial", 22, "bold"),
            bg="#FFFFFF",
            fg="#333333"
        ).pack(pady=20)

        # Username Entry
        username_frame = tk.Frame(self.login_frame, bg="#FFFFFF")
        username_frame.pack(pady=5)
        tk.Label(
            username_frame,
            text="Username",
            font=("Arial", 12),
            bg="#FFFFFF",
            fg="#333333",
            anchor="center"
        ).pack()
        self.username_entry = tk.Entry(
            username_frame,
            font=("Arial", 12),
            width=25,
            bg="#F5F5F5",
            fg="black",
            insertbackground="black",
            relief="flat",
            bd=2,
            highlightthickness=1,
            highlightbackground="black"
        )
        self.username_entry.pack(pady=5, ipady=5, anchor="center")
        self.username_entry.config(validate="key", validatecommand=(self.root.register(self.limit_input), "%P", 20))
        self.username_entry.bind("<Return>", lambda event: self.submit_login())
        self.username_entry.bind("<Escape>", lambda event: self.clear_entries())

        # Password Entry
        password_frame = tk.Frame(self.login_frame, bg="#FFFFFF")
        password_frame.pack(pady=5)
        tk.Label(
            password_frame,
            text="Password",
            font=("Arial", 12),
            bg="#FFFFFF",
            fg="#333333",
            anchor="center"
        ).pack()
        self.password_entry = tk.Entry(
            password_frame,
            font=("Arial", 12),
            width=25,
            bg="#F5F5F5",
            fg="black",
            insertbackground="black",
            relief="flat",
            bd=2,
            highlightthickness=1,
            highlightbackground="black",
            show="*"
        )
        self.password_entry.pack(pady=5, ipady=5, anchor="center")
        self.password_entry.config(validate="key", validatecommand=(self.root.register(self.limit_input), "%P", 20))
        self.password_entry.bind("<Return>", lambda event: self.submit_login())
        self.password_entry.bind("<Escape>", lambda event: self.clear_entries())

        # Eye Button (for toggling password visibility)
        self.eye_button = tk.Button(
            password_frame,
            text="👁",
            command=self.toggle_password,
            bg="#F5F5F5",
            fg="black",
            font=("Arial", 12),
            relief="flat",
            width=3,
            activebackground="#E0E0E0",
            activeforeground="black"
        )
        self.eye_button.pack(pady=2, anchor="center")
        Tooltip(self.eye_button, "Toggle password visibility")

        # Attempts and Timer Labels
        self.attempts_label = tk.Label(
            self.login_frame,
            text=f"Attempts remaining: {self.max_attempts - self.failed_attempts}",
            font=("Arial", 10),
            bg="#FFFFFF",
            fg="#333333"
        )
        self.attempts_label.pack(pady=5)

        self.timer_label = tk.Label(
            self.login_frame,
            text="",
            font=("Arial", 10, "bold"),
            bg="#FFFFFF",
            fg="#FF5555"
        )
        self.timer_label.pack(pady=5)

        # Buttons
        self.submit_button = CustomButton(
            self.login_frame,
            text="Submit",
            command=self.password_login,
            bg_color="#4CAF50",
            tooltip_text="Submit username and password",
            width=15
        )
        self.submit_button.pack(pady=10)

        self.voice_login_button = CustomButton(
            self.login_frame,
            text="Voice Login",
            command=self.start_voice_login,
            bg_color="#FF9800",
            tooltip_text="Login using voice commands",
            width=15
        )
        self.voice_login_button.pack(pady=10)
        if not self.voice_control.microphone_available:
            self.voice_login_button.config(state="disabled")
            Tooltip(self.voice_login_button, "Voice login disabled: No microphone detected")

        self.face_login_button = CustomButton(
            self.login_frame,
            text="Face Login",
            command=self.face_login,
            bg_color="#2196F3",
            tooltip_text="Login using facial recognition",
            width=15
        )
        self.face_login_button.pack(pady=10)

        # Preload face encodings in a separate thread
        self.face_encodings_thread = threading.Thread(target=self.load_face_encodings, daemon=True)
        self.face_encodings_thread.start()

    def limit_input(self, input_text, max_length):
        return len(input_text) <= int(max_length)

    def toggle_password(self):
        self.show_password = not self.show_password
        self.password_entry.config(show="" if self.show_password else "*")
        self.eye_button.config(text="🙈" if self.show_password else "👁")

    def clear_entries(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    def update_attempts_label(self):
        self.attempts_label.config(text=f"Attempts remaining: {self.max_attempts - self.failed_attempts}")

    def start_lockout_timer(self):
        self.is_locked = True
        self.submit_button.config(state="disabled")
        self.face_login_button.config(state="disabled")
        self.voice_login_button.config(state="disabled")
        self.username_entry.config(state="disabled")
        self.password_entry.config(state="disabled")
        self.eye_button.config(state="disabled")
        remaining_time = self.lockout_duration

        def update_timer():
            nonlocal remaining_time
            if remaining_time > 0:
                self.timer_label.config(text=f"Try again in {remaining_time} seconds")
                remaining_time -= 1
                self.root.after(1000, update_timer)
            else:
                self.timer_label.config(text="")
                self.is_locked = False
                self.failed_attempts = 0
                self.update_attempts_label()
                self.submit_button.config(state="normal")
                self.face_login_button.config(state="normal")
                if self.voice_control.microphone_available:
                    self.voice_login_button.config(state="normal")
                self.username_entry.config(state="normal")
                self.password_entry.config(state="normal")
                self.eye_button.config(state="normal")
                messagebox.showinfo("Info", "You can now try logging in again.")

        self.timer_label.config(text=f"Too many failed attempts. Try again in {remaining_time} seconds")
        self.root.after(1000, update_timer)

    def submit_login(self):
        self.password_login()

    def load_face_encodings(self):
        valid_images = False
        for user, path in self.face_image_paths.items():
            if not os.path.exists(path):
                logging.error(f"Face image {path} not found for {user}. Please ensure the file exists in the project directory.")
                continue
            encoding = self.load_face_encoding(path)
            if encoding is not None:
                self.face_encodings[user] = encoding
                valid_images = True
                logging.info(f"Successfully loaded face encoding for {user} from {path}. Encoding shape: {encoding.shape}")
            else:
                logging.warning(f"Failed to generate encoding for {path}. No face detected in the image.")
        if not valid_images:
            logging.error("No valid face images found. Disabling face login.")
            self.root.after(0, lambda: self.face_login_button.config(state="disabled"))
            self.root.after(0, lambda: messagebox.showerror("Face Login Error", "No valid face images found. Please ensure user1.jpg, user2.jpg, and user3.jpg are in the project directory and contain detectable faces."))

    def load_face_encoding(self, image_path):
        try:
            image = face_recognition.load_image_file(image_path)
            image = cv2.resize(image, (0, 0), fx=0.5, fy=0.5)
            encodings = face_recognition.face_encodings(image, model="small")
            if not encodings:
                logging.warning(f"No faces found in {image_path}.")
                return None
            return encodings[0]
        except Exception as e:
            logging.error(f"Error loading face encoding for {image_path}: {e}")
            return None

    def test_camera(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logging.error("Camera test failed: Unable to access webcam.")
            return False
        cap.release()
        logging.info("Camera test successful: Webcam is accessible.")
        return True

    def capture_face(self):
        # Test camera availability
        if not self.test_camera():
            self.root.after(0, lambda: messagebox.showerror("Camera Error", "Unable to access webcam. Please ensure your camera is connected, not in use by another application, and you have granted necessary permissions."))
            return None

        # Open the camera
        cap = cv2.VideoCapture(0)
        start_time = time.time()
        timeout = 1  # Short timeout for immediate detection

        try:
            while True:
                if time.time() - start_time > timeout:
                    cap.release()
                    cv2.destroyAllWindows()
                    logging.info("No face detected within 1 second.")
                    return None

                ret, frame = cap.read()
                if not ret:
                    logging.error("Failed to capture frame from webcam.")
                    self.root.after(0, lambda: messagebox.showerror("Error", "Failed to capture image from webcam."))
                    cap.release()
                    cv2.destroyAllWindows()
                    return None

                # Reduce resolution to speed up detection, matching load_face_encoding
                small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
                rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

                # Detect faces
                face_locations = face_recognition.face_locations(rgb_frame, model="small")
                if face_locations:
                    logging.info(f"Face detected at locations: {face_locations}")
                    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations, model="small")
                    cap.release()
                    cv2.destroyAllWindows()
                    if face_encodings:
                        logging.info(f"Successfully captured face encoding. Encoding shape: {face_encodings[0].shape}")
                        return face_encodings[0]
                    else:
                        logging.warning("No face encodings generated from detected face.")
                        self.root.after(0, lambda: messagebox.showerror("Error", "Unable to generate face encoding. Please try again."))
                        return None

                # Display the frame with instructions
                cv2.putText(frame, "Align your face (Press 'q' to cancel)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imshow("Face Login", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    cap.release()
                    cv2.destroyAllWindows()
                    return None

        except Exception as e:
            logging.error(f"Face capture failed: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Face capture failed: {e}"))
            cap.release()
            cv2.destroyAllWindows()
            return None

    def face_login(self):
        if self.is_locked:
            messagebox.showerror("Error", "Account is temporarily locked. Please wait and try again.")
            return

        self.submit_button.config(state="disabled")
        self.face_login_button.config(state="disabled")
        self.voice_login_button.config(state="disabled")

        # Check if face encodings are loaded
        if not self.face_encodings or all(encoding is None for encoding in self.face_encodings.values()):
            logging.error("No face data available for recognition.")
            self.root.after(0, lambda: messagebox.showerror("Error", "No face data available for recognition. Please ensure user1.jpg, user2.jpg, and user3.jpg are in the project directory and contain detectable faces."))
            self.submit_button.config(state="normal")
            self.face_login_button.config(state="normal")
            self.voice_login_button.config(state="normal")
            return

        # Capture face
        current_face_encoding = self.capture_face()
        if current_face_encoding is None:
            self.failed_attempts += 1
            self.update_attempts_label()
            # Play beep sound in a separate thread
            def play_beep():
                try:
                    beep_path = os.path.join(os.path.dirname(__file__), "beep.wav")
                    logging.info(f"Attempting to load beep sound from: {beep_path}")
                    if not os.path.exists(beep_path):
                        raise FileNotFoundError(f"beep.wav not found at {beep_path}")
                    mixer.init()
                    sound = mixer.Sound(beep_path)
                    logging.info("Successfully loaded beep.wav")
                    for _ in range(3):
                        sound.play()
                        time.sleep(1)
                    mixer.quit()
                except FileNotFoundError as e:
                    logging.warning(f"Failed to load beep.wav: {e}. Using system beep as fallback.")
                    for _ in range(3):
                        print('\a')  # System beep
                        time.sleep(1)
                except Exception as e:
                    logging.error(f"Error playing beep sound: {e}. Using system beep as fallback.")
                    for _ in range(3):
                        print('\a')  # System beep
                        time.sleep(1)

            beep_thread = threading.Thread(target=play_beep, daemon=True)
            beep_thread.start()

            # Show error message immediately
            if self.failed_attempts >= self.max_attempts:
                self.start_lockout_timer()
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", "No face detected. Please ensure your face is visible, well-lit, and centered in the frame."))
            self.submit_button.config(state="normal")
            self.face_login_button.config(state="normal")
            self.voice_login_button.config(state="normal")
            return

        # Compare captured face with stored encodings
        match_found = False
        matched_user = None
        for user, encoding in self.face_encodings.items():
            if encoding is None:
                continue
            # Calculate face distance for debugging
            face_distance = face_recognition.face_distance([encoding], current_face_encoding)[0]
            logging.info(f"Comparing with {user}: Face distance = {face_distance}")
            match = face_recognition.compare_faces([encoding], current_face_encoding, tolerance=0.6)[0]  # Increased tolerance
            logging.info(f"Match result with {user}: {match}")
            if match:
                match_found = True
                matched_user = user
                break

        if match_found:
            self.failed_attempts = 0
            self.update_attempts_label()
            personalized_name = self.user_names.get(matched_user, matched_user)
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Welcome {personalized_name}! Opening app..."))
            self.login_frame.destroy()
            self.on_successful_login()
        else:
            self.failed_attempts += 1
            self.update_attempts_label()
            # Play beep sound in a separate thread
            def play_beep():
                try:
                    beep_path = os.path.join(os.path.dirname(__file__), "beep.wav")
                    logging.info(f"Attempting to load beep sound from: {beep_path}")
                    if not os.path.exists(beep_path):
                        raise FileNotFoundError(f"beep.wav not found at {beep_path}")
                    mixer.init()
                    sound = mixer.Sound(beep_path)
                    logging.info("Successfully loaded beep.wav")
                    for _ in range(3):
                        sound.play()
                        time.sleep(1)
                    mixer.quit()
                except FileNotFoundError as e:
                    logging.warning(f"Failed to load beep.wav: {e}. Using system beep as fallback.")
                    for _ in range(3):
                        print('\a')  # System beep
                        time.sleep(1)
                except Exception as e:
                    logging.error(f"Error playing beep sound: {e}. Using system beep as fallback.")
                    for _ in range(3):
                        print('\a')  # System beep
                        time.sleep(1)

            beep_thread = threading.Thread(target=play_beep, daemon=True)
            beep_thread.start()

            # Show error message immediately
            if self.failed_attempts >= self.max_attempts:
                self.start_lockout_timer()
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", "Face not recognized. Please try again."))
            self.submit_button.config(state="normal")
            self.face_login_button.config(state="normal")
            self.voice_login_button.config(state="normal")

    def password_login(self):
        if self.is_locked:
            messagebox.showerror("Error", "Account is temporarily locked. Please wait and try again.")
            return

        self.submit_button.config(state="disabled")
        self.face_login_button.config(state="disabled")
        self.voice_login_button.config(state="disabled")

        username = self.username_entry.get().strip()
        if not username:
            self.failed_attempts += 1
            self.update_attempts_label()
            if self.failed_attempts >= self.max_attempts:
                self.start_lockout_timer()
            else:
                messagebox.showerror("Error", "Username cannot be empty.")
            self.submit_button.config(state="normal")
            self.face_login_button.config(state="normal")
            self.voice_login_button.config(state="normal")
            return

        if username not in self.users:
            self.failed_attempts += 1
            self.update_attempts_label()
            if self.failed_attempts >= self.max_attempts:
                self.start_lockout_timer()
            else:
                messagebox.showerror("Error", "Invalid username. Please check and try again.")
                self.username_entry.delete(0, tk.END)
                self.password_entry.delete(0, tk.END)
            self.submit_button.config(state="normal")
            self.face_login_button.config(state="normal")
            self.voice_login_button.config(state="normal")
            return

        password = self.password_entry.get().strip()
        if not password:
            self.failed_attempts += 1
            self.update_attempts_label()
            if self.failed_attempts >= self.max_attempts:
                self.start_lockout_timer()
            else:
                messagebox.showerror("Error", "Password cannot be empty.")
            self.submit_button.config(state="normal")
            self.face_login_button.config(state="normal")
            self.voice_login_button.config(state="normal")
            return

        password_encoded = password.encode('utf-8')
        if bcrypt.checkpw(password_encoded, self.users[username]["password"]):
            self.failed_attempts = 0
            self.update_attempts_label()
            messagebox.showinfo("Success", "Login successful! Welcome to SPLM.")
            self.login_frame.destroy()
            self.on_successful_login()
        else:
            self.failed_attempts += 1
            self.update_attempts_label()
            if self.failed_attempts >= self.max_attempts:
                self.start_lockout_timer()
            else:
                messagebox.showerror("Error", "Invalid password. Please try again.")
                self.password_entry.delete(0, tk.END)
            self.submit_button.config(state="normal")
            self.face_login_button.config(state="normal")
            self.voice_login_button.config(state="normal")

    def start_voice_login(self):
        if self.is_locked:
            messagebox.showerror("Error", "Account is temporarily locked. Please wait and try again.")
            return

        logging.info("Voice Login button clicked, starting voice login.")
        self.submit_button.config(state="disabled")
        self.voice_login_button.config(state="disabled")
        self.face_login_button.config(state="disabled")
        self.voice_control.start_listening()
        self.voice_control.speak("Please say your username clearly.")
        self.voice_control.listen(self.handle_username, timeout_seconds=10)  # Reduced timeout

    def handle_username(self, username):
        if not username:
            self.failed_attempts += 1
            self.update_attempts_label()
            if self.failed_attempts >= self.max_attempts:
                self.start_lockout_timer()
                self.voice_control.stop_listening()
                self.submit_button.config(state="normal")
                self.voice_login_button.config(state="normal")
                self.face_login_button.config(state="normal")
            else:
                self.voice_control.speak("No username detected. Please try again.")
                self.voice_control.listen(self.handle_username, timeout_seconds=10)
            return

        self.username_entry.delete(0, tk.END)
        self.username_entry.insert(0, username)
        logging.info(f"Voice login: Username recognized as '{username}'")

        self.voice_control.speak("Please say your password clearly.")
        self.voice_control.listen(self.handle_password, timeout_seconds=10)  # Reduced timeout

    def handle_password(self, password):
        if not password:
            self.failed_attempts += 1
            self.update_attempts_label()
            if self.failed_attempts >= self.max_attempts:
                self.start_lockout_timer()
                self.voice_control.stop_listening()
                self.submit_button.config(state="normal")
                self.voice_login_button.config(state="normal")
                self.face_login_button.config(state="normal")
            else:
                self.voice_control.speak("No password detected. Please try again.")
                self.voice_control.listen(self.handle_password, timeout_seconds=10)
            return

        self.voice_control.stop_listening()
        self.submit_button.config(state="normal")
        self.voice_login_button.config(state="normal")
        self.face_login_button.config(state="normal")

        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)
        logging.info(f"Voice login: Password recognized as '{password}'")
        self.password_login()

class SPLMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Personal Life Manager (SPLM)")
        self.root.geometry("900x700")
        self.root.configure(bg="#FFFFFF")
        self.root.resizable(True, True)

        self.task_manager = None
        self.finance_tracker = None
        self.fitness_assistant = None
        self.travel_assistant = None
        self.productivity_tools = None
        self.entertainment = None

        self.style = ttk.Style()
        self.style.configure("TFrame", background="#FFFFFF")
        self.style.configure("TLabel", background="#FFFFFF", font=("Arial", 12))

        self.main_frame = tk.Frame(self.root, bg="#FFFFFF")
        self.setup_main_app()

        self.show_login()

    def show_login(self):
        self.main_frame.pack_forget()
        self.login_page = LoginPage(self.root, self.show_main_app)

    def show_main_app(self):
        self.main_frame.pack(fill="both", expand=True)
        self.root.title("Smart Personal Life Manager (SPLM)")
        self.root.geometry("900x700")

    def logout(self):
        self.main_frame.pack_forget()
        self.show_login()

    def close_app(self):
        self.root.destroy()

    def go_back_to_home(self):
        self.clear_content()
        self.welcome_label = tk.Label(
            self.content_frame,
            text="Welcome to SPLM!\nSelect a module from the sidebar.",
            font=("Arial", 16),
            bg="#FFFFFF",
            fg="#333333",
            justify="center"
        )
        self.welcome_label.pack(expand=True)

    def setup_main_app(self):
        self.header_frame = tk.Frame(self.main_frame, bg="#3F51B5", height=80)
        self.header_frame.pack(fill="x")
        self.header_frame.pack_propagate(False)

        tk.Label(
            self.header_frame,
            text="🌟 SPLM - Your Life, Organized!",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#3F51B5",
            pady=20
        ).pack(side="left", padx=20)

        self.sidebar = tk.Frame(self.main_frame, width=250, bg="#F5F5F5")
        self.sidebar.pack(fill="y", side="left")
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar,
            text="Menu",
            font=("Arial", 16, "bold"),
            fg="#333333",
            bg="#F5F5F5",
            pady=10
        ).pack(fill="x")

        button_configs = [
            ("📋 Task Manager", self.open_task_manager, "#4CAF50", "Manage your tasks"),
            ("💰 Finance Tracker", self.open_finance_tracker, "#2196F3", "Track your finances"),
            ("🏋 Fitness Assistant", self.open_fitness_assistant, "#F44336", "Plan your workouts"),
            ("✈ Travel Assistant", self.open_travel_assistant, "#FFC107", "Organize your trips"),
            ("🔧 Productivity Tools", self.open_productivity_tools, "#9C27B0", "Boost your productivity"),
            ("🎮 Entertainment", self.open_entertainment, "#FF5722", "Enjoy games and media"),
            ("🚪 Logout", self.logout, "#607D8B", "Exit to login screen")
        ]

        for text, command, color, tooltip in button_configs:
            btn = CustomButton(
                self.sidebar,
                text=text,
                command=command,
                bg_color=color,
                width=20,
                tooltip_text=tooltip
            )
            btn.pack(pady=8, padx=10, fill="x")

        self.content_frame = tk.Frame(self.main_frame, bg="#FFFFFF", bd=2, relief="flat")
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.welcome_label = tk.Label(
            self.content_frame,
            text="Welcome to SPLM!\nSelect a module from the sidebar.",
            font=("Arial", 16),
            bg="#FFFFFF",
            fg="#333333",
            justify="center"
        )
        self.welcome_label.pack(expand=True)

    def clear_content(self):
        # Stop music if entertainment module is active
        if self.entertainment:
            try:
                self.entertainment.stop_music()
                logging.info("Music stopped before switching modules.")
            except Exception as e:
                logging.error(f"Error stopping music: {e}")
        # Clear all widgets in the content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def task_manager_add_task(self, task_name):
        if self.task_manager:
            pass
        logging.info(f"Task Manager: Adding task {task_name}")

    def task_manager_list_tasks(self):
        if self.task_manager:
            return []
        return ["Task 1", "Task 2"]

    def task_manager_complete_task(self, task_name):
        if self.task_manager:
            pass
        logging.info(f"Task Manager: Completing task {task_name}")

    def task_manager_delete_task(self, task_name):
        if self.task_manager:
            pass
        logging.info(f"Task Manager: Deleting task {task_name}")

    def finance_tracker_add_expense(self, amount, category):
        if self.finance_tracker:
            pass
        logging.info(f"Finance Tracker: Adding expense {amount} for {category}")

    def finance_tracker_show_budget(self):
        if self.finance_tracker:
            return 0
        return "1000"

    def finance_tracker_list_transactions(self):
        if self.finance_tracker:
            return []
        return ["50 for food", "20 for transport"]

    def finance_tracker_set_budget(self, amount):
        if self.finance_tracker:
            pass
        logging.info(f"Finance Tracker: Setting budget to {amount}")

    def fitness_assistant_log_workout(self, activity, duration):
        if self.fitness_assistant:
            pass
        logging.info(f"Fitness Assistant: Logging workout {activity} for {duration} minutes")

    def fitness_assistant_show_goals(self):
        if self.fitness_assistant:
            return []
        return ["Run 5km", "100 push-ups"]

    def fitness_assistant_suggest_workout(self):
        if self.fitness_assistant:
            return ""
        return "30-minute yoga session"

    def fitness_assistant_track_calories(self, amount):
        if self.fitness_assistant:
            pass
        logging.info(f"Fitness Assistant: Tracking {amount} calories")

    def travel_assistant_plan_trip(self, destination):
        if self.travel_assistant:
            pass
        logging.info(f"Travel Assistant: Planning trip to {destination}")

    def travel_assistant_show_trips(self):
        if self.travel_assistant:
            return []
        return ["Paris", "Tokyo"]

    def travel_assistant_add_itinerary_item(self, item):
        if self.travel_assistant:
            pass
        logging.info(f"Travel Assistant: Adding itinerary item {item}")

    def travel_assistant_check_weather(self, destination):
        if self.travel_assistant:
            return ""
        return "Sunny, 25°C"

    def productivity_tools_start_timer(self, minutes):
        if self.productivity_tools:
            pass
        logging.info(f"Productivity Tools: Starting timer for {minutes} minutes")

    def productivity_tools_add_note(self, note_content):
        if self.productivity_tools:
            pass
        logging.info(f"Productivity Tools: Adding note {note_content}")

    def productivity_tools_show_todo_list(self):
        if self.productivity_tools:
            return []
        return ["Finish report", "Call client"]

    def productivity_tools_set_reminder(self, task, time_str):
        if self.productivity_tools:
            pass
        logging.info(f"Productivity Tools: Setting reminder for {task} at {time_str}")

    def entertainment_play_music(self):
        if self.entertainment:
            pass
        logging.info("Entertainment: Playing music")

    def entertainment_suggest_movie(self):
        if self.entertainment:
            return ""
        return "The Matrix"

    def entertainment_open_game(self, game_name):
        if self.entertainment:
            pass
        logging.info(f"Entertainment: Opening game {game_name}")

    def entertainment_pause_media(self):
        if self.entertainment:
            pass
        logging.info("Entertainment: Pausing media")

    def open_task_manager(self):
        self.clear_content()
        if TaskManager:
            self.task_manager = TaskManager(self.content_frame)
        else:
            tk.Label(
                self.content_frame,
                text="Task Manager module is not available.",
                font=("Arial", 12),
                bg="#FFFFFF",
                fg="#FF0000"
            ).pack(expand=True)

    def open_finance_tracker(self):
        self.clear_content()
        if FinanceTracker:
            self.finance_tracker = FinanceTracker(self.content_frame)
        else:
            tk.Label(
                self.content_frame,
                text="Finance Tracker module is not available.",
                font=("Arial", 12),
                bg="#FFFFFF",
                fg="#FF0000"
            ).pack(expand=True)

    def open_fitness_assistant(self):
        self.clear_content()
        if FitnessAssistant:
            self.fitness_assistant = FitnessAssistant(self.content_frame)
        else:
            tk.Label(
                self.content_frame,
                text="Fitness Assistant module is not available.",
                font=("Arial", 12),
                bg="#FFFFFF",
                fg="#FF0000"
            ).pack(expand=True)

    def open_travel_assistant(self):
        self.clear_content()
        if TravelAssistantApp:
            self.travel_assistant = TravelAssistantApp(self.content_frame)
        else:
            tk.Label(
                self.content_frame,
                text="Travel Assistant module is not available.",
                font=("Arial", 12),
                bg="#FFFFFF",
                fg="#FF0000"
            ).pack(expand=True)

    def open_productivity_tools(self):
        self.clear_content()
        if ProductivityApp:
            self.productivity_tools = ProductivityApp(self.content_frame)
        else:
            tk.Label(
                self.content_frame,
                text="Productivity Tools module is not available.",
                font=("Arial", 12),
                bg="#FFFFFF",
                fg="#FF0000"
            ).pack(expand=True)

    def open_entertainment(self):
        self.clear_content()
        if Entertainment:
            self.entertainment = Entertainment(self.content_frame)
        else:
            tk.Label(
                self.content_frame,
                text="Entertainment module is not available.",
                font=("Arial", 12),
                bg="#FFFFFF",
                fg="#FF0000"
            ).pack(expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = SPLMApp(root)
    root.mainloop()