import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import platform
import subprocess
import tempfile
import webbrowser
from io import BytesIO

class TravelAssistantApp(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="#e6f0fa")  # Updated to a lighter blue background
        self.pack(fill="both", expand=True)

        font_path = os.path.join(os.path.dirname(__file__), 'DejaVuSans.ttf')
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))

        self.green_line = {
            1: "Nagasandra", 2: "Dasarahalli", 3: "Jalahalli", 4: "Peenya", 5: "Peenya Industry",
            6: "Yeshwanthpur", 7: "Sandal Soap Factory", 8: "Mahalakshmi", 9: "Rajajinagar",
            10: "Kuvempu Road", 11: "Srirampura", 12: "Mantri Square", 13: "Majestic"
        }
        self.purple_line = {
            1: "Challaghatta", 2: "Kengeri", 3: "Jnana Bharathi", 4: "Rajarajeshwari Nagar",
            5: "Nayandahalli", 6: "Mysore Road", 7: "Deepanjali Nagar", 8: "Attiguppe",
            9: "Vijayanagar", 10: "Hosahalli", 11: "Magadi Road", 12: "City Railway Station",
            13: "Majestic", 14: "Cubbon Park", 15: "MG Road", 16: "Trinity", 17: "Halasuru",
            18: "Indiranagar", 19: "SV Road", 20: "Baiyappanahalli"
        }
        self.fare_per_station = 10
        self.time_per_station = 2
        self.available_bikes = 20
        self.rented_bikes = {}
        self.rates = {"hour": 50, "day": 300, "week": 1500}

        self.create_widgets()

    def create_widgets(self):
        title = tk.Label(self, text="Travel Assistant 🌍", font=("Arial", 24, "bold"), bg="#e6f0fa", fg="#2e3f4f")
        title.pack(pady=20)

        booking_frame = tk.Frame(self, bg="#e6f0fa")
        booking_frame.pack(pady=10)

        tk.Label(booking_frame, text="Choose booking type: 🎉", font=("Arial", 12), bg="#e6f0fa").pack(side="left", padx=5)

        self.booking_var = tk.StringVar()
        self.booking_dropdown = ttk.Combobox(booking_frame, textvariable=self.booking_var, state="readonly")
        self.booking_dropdown['values'] = ("Metro 🚇", "Bike Rental 🚴‍♂️")
        self.booking_dropdown.current(0)
        self.booking_dropdown.pack(side="left", padx=5)

        book_button = tk.Button(self, text="Book 📖", command=self.book_service, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
        book_button.pack(pady=10)

        self.metro_frame = tk.LabelFrame(self, text="Metro Booking 🚉", font=("Arial", 14, "bold"), padx=10, pady=10)
        self.create_metro_widgets()

        self.bike_frame = tk.LabelFrame(self, text="Bike Rental Booking 🚲", font=("Arial", 14, "bold"), padx=10, pady=10)
        self.create_bike_widgets()

        self.status_label = tk.Label(self, text="", font=("Arial", 12), fg="green", bg="#e6f0fa")
        self.status_label.pack(pady=10)

        self.book_service()

    def create_metro_widgets(self):
        tk.Label(self.metro_frame, text="Source Line: 🌿", font=("Arial", 12)).grid(row=0, column=0, sticky="e")
        self.source_line_var = tk.StringVar()
        self.source_line = ttk.Combobox(self.metro_frame, textvariable=self.source_line_var, state="readonly")
        self.source_line['values'] = ("Green", "Purple")
        self.source_line.current(0)
        self.source_line.grid(row=0, column=1)
        self.source_line.bind("<<ComboboxSelected>>", self.update_source_stations)

        tk.Label(self.metro_frame, text="Source Station: 📍", font=("Arial", 12)).grid(row=1, column=0, sticky="e")
        self.source_station_var = tk.StringVar()
        self.source_station = ttk.Combobox(self.metro_frame, textvariable=self.source_station_var, state="readonly")
        self.source_station['values'] = list(self.green_line.values())
        self.source_station.current(0)
        self.source_station.grid(row=1, column=1)

        tk.Label(self.metro_frame, text="Destination Line: 🍇", font=("Arial", 12)).grid(row=2, column=0, sticky="e")
        self.dest_line_var = tk.StringVar()
        self.dest_line = ttk.Combobox(self.metro_frame, textvariable=self.dest_line_var, state="readonly")
        self.dest_line['values'] = ("Green", "Purple")
        self.dest_line.current(0)
        self.dest_line.grid(row=2, column=1)
        self.dest_line.bind("<<ComboboxSelected>>", self.update_dest_stations)

        tk.Label(self.metro_frame, text="Destination Station: 📍", font=("Arial", 12)).grid(row=3, column=0, sticky="e")
        self.dest_station_var = tk.StringVar()
        self.dest_station = ttk.Combobox(self.metro_frame, textvariable=self.dest_station_var, state="readonly")
        self.dest_station['values'] = list(self.green_line.values())
        self.dest_station.current(0)
        self.dest_station.grid(row=3, column=1)

        tk.Label(self.metro_frame, text="Number of Passengers: 👨‍👩‍👧‍👦", font=("Arial", 12)).grid(row=4, column=0, sticky="e")
        self.passenger_var = tk.StringVar()
        self.passenger_dropdown = ttk.Combobox(self.metro_frame, textvariable=self.passenger_var, state="readonly")
        self.passenger_dropdown['values'] = [str(i) for i in range(1, 8)]
        self.passenger_dropdown.current(0)
        self.passenger_dropdown.grid(row=4, column=1)

        tk.Button(self.metro_frame, text="Confirm Metro Booking ✅", command=self.confirm_metro, bg="#2196F3", fg="white", font=("Arial", 12)).grid(row=5, column=0, columnspan=2, pady=10)

    def create_bike_widgets(self):
        tk.Label(self.bike_frame, text="Customer Name: 👤", font=("Arial", 12)).grid(row=0, column=0, sticky="e")
        self.bike_customer = tk.Entry(self.bike_frame, font=("Arial", 12))
        self.bike_customer.grid(row=0, column=1)

        tk.Label(self.bike_frame, text="Age: 🎂", font=("Arial", 12)).grid(row=1, column=0, sticky="e")
        self.bike_age = tk.Entry(self.bike_frame, font=("Arial", 12))
        self.bike_age.grid(row=1, column=1)

        tk.Label(self.bike_frame, text=f"Available Bikes: {self.available_bikes} 🚲", font=("Arial", 12)).grid(row=2, column=0, columnspan=2)

        tk.Label(self.bike_frame, text="Rental Type: ⏳", font=("Arial", 12)).grid(row=3, column=0, sticky="e")
        self.bike_rental_type_var = tk.StringVar()
        self.bike_rental_type = ttk.Combobox(self.bike_frame, textvariable=self.bike_rental_type_var, state="readonly")
        self.bike_rental_type['values'] = (f"Hourly (₹{self.rates['hour']}/hr)", f"Daily (₹{self.rates['day']}/day)", f"Weekly (₹{self.rates['week']}/week)")
        self.bike_rental_type.current(0)
        self.bike_rental_type.grid(row=3, column=1)

        tk.Label(self.bike_frame, text="Number of Bikes: 🚴‍♂️", font=("Arial", 12)).grid(row=4, column=0, sticky="e")
        self.bike_count_var = tk.StringVar()
        self.bike_count = ttk.Combobox(self.bike_frame, textvariable=self.bike_count_var, state="readonly")
        self.bike_count['values'] = [str(i) for i in range(1, 6)]
        self.bike_count.current(0)
        self.bike_count.grid(row=4, column=1)

        tk.Label(self.bike_frame, text="Duration: ⏰", font=("Arial", 12)).grid(row=5, column=0, sticky="e")
        self.bike_duration = tk.Entry(self.bike_frame, font=("Arial", 12))
        self.bike_duration.grid(row=5, column=1)

        tk.Button(self.bike_frame, text="Confirm Bike Booking ✅", command=self.confirm_bike, bg="#FF9800", fg="white", font=("Arial", 12)).grid(row=6, column=0, columnspan=2, pady=10)

    def book_service(self):
        booking_type = self.booking_var.get()
        self.metro_frame.pack_forget()
        self.bike_frame.pack_forget()
        if booking_type == "Metro 🚇":
            self.metro_frame.pack(pady=10)
        elif booking_type == "Bike Rental 🚴‍♂️":
            self.bike_frame.pack(pady=10)

    def update_source_stations(self, event=None):
        line = self.source_line_var.get()
        stations = self.green_line if line == "Green" else self.purple_line
        self.source_station['values'] = list(stations.values())
        self.source_station.current(0)

    def update_dest_stations(self, event=None):
        line = self.dest_line_var.get()
        stations = self.green_line if line == "Green" else self.purple_line
        self.dest_station['values'] = list(stations.values())
        self.dest_station.current(0)

    def generate_pdf(self, type_, data):
        filename = "metro_ticket.pdf" if type_ == "metro" else "bike_rental_bill.pdf"
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        width, height = A4
        c.setStrokeColorRGB(0, 0.5, 0)
        c.setLineWidth(2)
        c.rect(50, height - 300, width - 100, 250, stroke=1, fill=0)

        c.setFillColorRGB(0, 0.5, 0)
        c.rect(50, height - 50, width - 100, 30, stroke=0, fill=1)
        c.setFont("DejaVuSans", 16)
        c.setFillColorRGB(1, 1, 1)
        c.drawCentredString(width / 2, height - 45, "Travel Assistant Ticket")

        c.setFillColorRGB(0, 0, 0)
        c.setFont("DejaVuSans", 14)
        c.drawString(70, height - 90, f"{type_.capitalize()} Booking Confirmation ")

        c.setFont("DejaVuSans", 12)
        y = height - 120
        for key, value in data.items():
            c.drawString(70, y, f"{key}: {value}")
            y -= 25

        c.setFont("DejaVuSans", 10)
        c.setFillColorRGB(0.5, 0.5, 0.5)
        c.drawString(70, y - 20, f"Issued on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(70, y - 35, "Thank you for booking with Travel Assistant!")

        c.setStrokeColorRGB(0, 0.5, 0)
        c.setDash(6, 3)
        c.line(50, y - 10, width - 50, y - 10)

        c.showPage()
        c.save()
        
        pdf_data = buffer.getvalue()
        buffer.close()

        # Save PDF to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(pdf_data)
            temp_file_path = temp_file.name

        return filename, temp_file_path

    def open_pdf(self, file_path):
        try:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux and others
                subprocess.run(["xdg-open", file_path])
        except Exception as e:
            try:
                # Fallback to webbrowser
                webbrowser.open(f"file://{file_path}")
            except Exception as e2:
                messagebox.showwarning("Open PDF Error", "Unable to open PDF automatically. Please open it manually from your temporary files.")

    def confirm_metro(self):
        source = self.source_station_var.get()
        dest = self.dest_station_var.get()
        passengers = int(self.passenger_var.get())

        if source == dest:
            messagebox.showerror("Invalid Route", "Source and destination cannot be the same.")
            return

        stations = self.green_line if self.source_line_var.get() == self.dest_line_var.get() == "Green" else self.purple_line
        station_keys = list(stations.keys())
        station_values = list(stations.values())
        src_index = station_values.index(source)
        dest_index = station_values.index(dest)
        num_stations = abs(dest_index - src_index)
        fare = num_stations * self.fare_per_station * passengers
        duration = num_stations * self.time_per_station

        data = {"Source": source, "Destination": dest, "Fare (₹)": fare, "Duration (min)": duration, "Passengers": passengers}
        try:
            filename, temp_file_path = self.generate_pdf("metro", data)
            messagebox.showinfo("Booking Confirmed", f"Metro ticket generated and opened: {filename}")
            self.open_pdf(temp_file_path)
            self.status_label.config(text=f"Metro Booking Confirmed: ₹{fare} for {duration} min travel.", fg="green")
        except Exception as e:
            messagebox.showerror("PDF Error", "Unable to generate or open PDF. Please try again.")
            self.status_label.config(text="Metro Booking Failed.", fg="red")

    def confirm_bike(self):
        name = self.bike_customer.get()
        try:
            age = int(self.bike_age.get())
            duration = int(self.bike_duration.get())
            count = int(self.bike_count_var.get())
        except:
            messagebox.showerror("Invalid Input", "Please enter valid numeric inputs.")
            return

        if age < 18:
            messagebox.showerror("Age Restriction", "You must be at least 18 years old to rent a bike.")
            return
        if count > self.available_bikes:
            messagebox.showerror("Bike Limit", "Not enough bikes available.")
            return

        rental_type_display = self.bike_rental_type_var.get().split()[0].lower()
        rental_type_map = {"hourly": "hour", "daily": "day", "weekly": "week"}
        rental_type = rental_type_map.get(rental_type_display, "hour")
        rate = self.rates[rental_type]
        total = rate * duration * count

        duration_label = "Duration (hours)" if rental_type == "hour" else "Duration (days)" if rental_type == "day" else "Duration (weeks)"

        self.available_bikes -= count
        data = {"Customer Name": name, "Total Cost (₹)": total, "Number of Bikes": count, "Rental Type": rental_type.capitalize(), duration_label: duration}
        try:
            filename, temp_file_path = self.generate_pdf("bike", data)
            messagebox.showinfo("Booking Confirmed", f"Bike rental bill generated and opened: {filename}")
            self.open_pdf(temp_file_path)
            self.status_label.config(text=f"Bike Booking Confirmed: ₹{total}", fg="green")
        except Exception as e:
            messagebox.showerror("PDF Error", "Unable to generate or open PDF. Please try again.")
            self.status_label.config(text="Bike Booking Failed.", fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Travel Assistant 🌍")
    app = TravelAssistantApp(root)
    root.geometry("600x700")
    root.mainloop()