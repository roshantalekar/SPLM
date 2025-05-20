import tkinter as tk
from tkinter import messagebox, ttk
import json
from datetime import datetime
import csv
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
import platform
import subprocess
import tempfile
import webbrowser
from io import BytesIO

class Transaction:
    """Represents a single finance transaction."""
    def __init__(self, desc, amount, category, date):
        self.desc = desc
        self.amount = amount
        self.category = category
        self.date = date
    
    def to_string(self):
        """Format transaction for display."""
        return f"{self.desc} ({self.category}): ₹{self.amount:.2f} on {self.date}"
    
    def to_dict(self):
        """Convert transaction to dictionary for JSON storage."""
        return {
            "desc": self.desc,
            "amount": self.amount,
            "category": self.category,
            "date": self.date
        }

class FinanceTracker:
    """Main application class for tracking finances against a monthly salary."""
    def __init__(self, parent):
        self.parent = parent
        self.salary = 0.0
        self.transactions = []
        self.movie_keywords = ['movie', 'cinema', 'film', 'ticket', 'theater']
        self.shopping_keywords = ['shop', 'buy', 'purchase', 'store', 'mall']
        self.grocery_keywords = ['grocery', 'food', 'vegetable', 'fruit', 'market']
        self.setup_salary_screen()
    
    def setup_salary_screen(self):
        """Set up the screen to input monthly salary."""
        self.salary_frame = tk.Frame(self.parent, bg="#f0f0f0")
        self.salary_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(self.salary_frame, text="Finance Tracker", font=("Helvetica", 20, "bold"), bg="#f0f0f0").pack(pady=20)
        tk.Label(self.salary_frame, text="Enter your monthly salary (₹):", font=("Helvetica", 14), bg="#f0f0f0").pack()
        self.salary_entry = tk.Entry(self.salary_frame, font=("Helvetica", 12), width=20, bd=2, relief="groove")
        self.salary_entry.pack(pady=10, ipady=5)
        self.salary_entry.bind("<Return>", lambda event: self.set_salary())
        
        # Enhanced button
        tk.Button(self.salary_frame, text="Set Salary", font=("Helvetica", 12, "bold"), 
                 bg="#4CAF50", fg="white", width=15, height=2, 
                 bd=0, relief="flat", activebackground="#45a049",
                 command=self.set_salary).pack(pady=15)
        
        self.load_data()  # Initialize with empty data
    
    def set_salary(self):
        """Validate and set the monthly salary, then load main UI."""
        try:
            salary = float(self.salary_entry.get().strip())
            if salary <= 0:
                messagebox.showwarning("Input Error", "Salary must be a positive number!")
                return
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid salary amount!")
            return
        
        self.salary = salary
        self.salary_frame.destroy()
        self.setup_main_ui()
    
    def validate_input(self, text):
        """Ensure input doesn't contain invalid characters for CSV/JSON."""
        return all(c not in ",;\n" for c in text)
    
    def categorize_finance(self, desc):
        """Determine finance category based on description keywords."""
        desc_lower = desc.lower()
        for keyword in self.movie_keywords:
            if keyword in desc_lower:
                return "Movies"
        for keyword in self.shopping_keywords:
            if keyword in desc_lower:
                return "Shopping"
        for keyword in self.grocery_keywords:
            if keyword in desc_lower:
                return "Groceries"
        return "Uncategorized"
    
    def setup_main_ui(self):
        """Initialize the main user interface."""
        self.frame = tk.Frame(self.parent, bg="#f0f0f0")
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Financial Summary
        total_spent = sum(t.amount for t in self.transactions)
        remaining = self.salary - total_spent
        tk.Label(self.frame, text="Finance Tracker", font=("Helvetica", 18, "bold"), bg="#f0f0f0").pack(pady=10)
        tk.Label(self.frame, text=f"Salary:{self.salary:.2f} | Spent:{total_spent:.2f} | Remaining:{remaining:.2f}", 
                 font=("Helvetica", 12), bg="#f0f0f0").pack(pady=5)
        
        # Entry Frame
        entry_frame = tk.Frame(self.frame, bg="#f0f0f0")
        entry_frame.pack(fill="x", padx=10, pady=10)
        entry_frame.columnconfigure(1, weight=1)
        
        tk.Label(entry_frame, text="Description:", font=("Helvetica", 12), bg="#f0f0f0").grid(row=0, column=0, sticky="w")
        self.desc_entry = tk.Entry(entry_frame, font=("Helvetica", 12), bd=2, relief="groove")
        self.desc_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5, ipady=5)
        self.desc_entry.bind("<Return>", lambda event: self.add_transaction())
        
        tk.Label(entry_frame, text="Amount:", font=("Helvetica", 12), bg="#f0f0f0").grid(row=0, column=2, sticky="w")
        self.amount_entry = tk.Entry(entry_frame, font=("Helvetica", 12), width=12, bd=2, relief="groove")
        self.amount_entry.grid(row=0, column=3, padx=5, pady=5, ipady=5)
        self.amount_entry.bind("<Return>", lambda event: self.add_transaction())
        
        tk.Label(entry_frame, text="Category:", font=("Helvetica", 12), bg="#f0f0f0").grid(row=1, column=0, sticky="w")
        self.category_var = tk.StringVar()
        categories = ["Movies", "Shopping", "Groceries", "Uncategorized"]
        self.category_menu = ttk.Combobox(entry_frame, textvariable=self.category_var, values=categories, 
                                        font=("Helvetica", 12), width=15, state="readonly")
        self.category_menu.grid(row=1, column=1, padx=5, pady=5, ipady=2)
        self.category_menu.set("Uncategorized")
        
        # Enhanced buttons
        tk.Button(entry_frame, text="Add Finance", font=("Helvetica", 12, "bold"), 
                 bg="#2196F3", fg="white", width=12, height=2, 
                 bd=0, relief="flat", activebackground="#1e88e5",
                 command=self.add_transaction).grid(row=0, column=4, padx=5, pady=5)
        tk.Button(entry_frame, text="Clear Form", font=("Helvetica", 12, "bold"), 
                 bg="#f44336", fg="white", width=12, height=2, 
                 bd=0, relief="flat", activebackground="#e53935",
                 command=self.clear_form).grid(row=0, column=5, padx=5, pady=5)
        
        # Transaction List Frame
        list_frame = tk.Frame(self.frame, bg="#f0f0f0")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.trans_listbox = tk.Listbox(list_frame, height=10, font=("Helvetica", 12), bd=2, relief="groove")
        self.trans_listbox.pack(side="left", fill="both", expand=True)
        self.trans_listbox.bind("<Delete>", lambda event: self.delete_transaction())
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.trans_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.trans_listbox.config(yscrollcommand=scrollbar.set)
        
        # Buttons Frame
        btn_frame = tk.Frame(self.frame, bg="#f0f0f0")
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        # Enhanced buttons
        tk.Button(btn_frame, text="Delete Finance", font=("Helvetica", 12, "bold"), 
                 bg="#f44336", fg="white", width=15, height=2, 
                 bd=0, relief="flat", activebackground="#e53935",
                 command=self.delete_transaction).pack(side="left", padx=5, pady=5)
        tk.Button(btn_frame, text="View Summary", font=("Helvetica", 12, "bold"), 
                 bg="#2196F3", fg="white", width=15, height=2, 
                 bd=0, relief="flat", activebackground="#1e88e5",
                 command=self.view_summary).pack(side="left", padx=5, pady=5)
        tk.Button(btn_frame, text="Export to PDF", font=("Helvetica", 12, "bold"), 
                 bg="#4CAF50", fg="white", width=15, height=2, 
                 bd=0, relief="flat", activebackground="#45a049",
                 command=self.export_to_pdf).pack(side="left", padx=5, pady=5)
        tk.Button(btn_frame, text="Set New Salary", font=("Helvetica", 12, "bold"), 
                 bg="#FFC107", fg="black", width=15, height=2, 
                 bd=0, relief="flat", activebackground="#FFB300",
                 command=self.reset_salary).pack(side="left", padx=5, pady=5)
        
        self.update_transaction_list()
    
    def clear_form(self):
        """Clear all input fields."""
        self.desc_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.category_var.set("Uncategorized")
    
    def add_transaction(self):
        """Add a new finance to the list."""
        desc = self.desc_entry.get().strip()
        try:
            amount = float(self.amount_entry.get().strip())
            if not desc or amount <= 0:
                messagebox.showwarning("Input Error", "Please enter a valid description and positive amount!")
                return
            if not self.validate_input(desc):
                messagebox.showwarning("Input Error", "Description cannot contain commas, semicolons, or newlines!")
                return
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid amount!")
            return
        
        total_spent = sum(t.amount for t in self.transactions)
        if amount > (self.salary - total_spent):
            messagebox.showwarning("Insufficient Funds", f"Finance (₹{amount:.2f}) exceeds remaining salary (₹{self.salary - total_spent:.2f})!")
            return
        
        # Determine category
        category = self.categorize_finance(desc)
        if self.category_var.get() != "Uncategorized":
            category = self.category_var.get()  # Override with user-selected category if specified
        
        # Create and store transaction
        date = datetime.now().strftime("%Y-%m-%d")
        transaction = Transaction(desc, amount, category, date)
        self.transactions.append(transaction)
        self.trans_listbox.insert(tk.END, transaction.to_string())
        
        # Clear entries
        self.clear_form()
        
        # Update UI and check salary
        self.check_salary()
        self.update_ui()
        messagebox.showinfo("Success", f"Finance of ₹{amount:.2f} for {desc} ({category}) added!")
    
    def delete_transaction(self):
        """Delete the selected transaction."""
        try:
            selected_idx = self.trans_listbox.curselection()[0]
            self.trans_listbox.delete(selected_idx)
            self.transactions.pop(selected_idx)
            self.update_ui()
            messagebox.showinfo("Success", "Finance deleted successfully!")
        except IndexError:
            messagebox.showwarning("Selection Error", "Please select a finance to delete!")
    
    def view_summary(self):
        """Display finances grouped by category and financial summary."""
        total_spent = sum(t.amount for t in self.transactions)
        remaining = self.salary - total_spent
        
        # Group finances by category
        cat_dict = {"Movies": [], "Shopping": [], "Groceries": [], "Uncategorized": []}
        for t in self.transactions:
            cat_dict[t.category].append((t.amount, t.desc, t.date))
        
        summary = "Finances by Category:\n"
        for category in cat_dict:
            items = cat_dict[category]
            if items:
                summary += f"\n{category}:\n"
                for i, (amount, desc, date) in enumerate(items, 1):
                    summary += f"  {i}. ₹{amount:.2f} - {desc} on {date}\n"
        
        summary += f"\nTotal Spent: ₹{total_spent:.2f}\nRemaining: ₹{remaining:.2f}"
        messagebox.showinfo("Summary", summary or "No finances yet.")
    
    def check_salary(self):
        """Warn if total finances exceed salary."""
        total_spent = sum(t.amount for t in self.transactions)
        if total_spent > self.salary:
            messagebox.showwarning("Salary Alert", f"Finances (₹{total_spent:.2f}) have exceeded your salary (₹{self.salary:.2f})!")
    
    def reset_salary(self):
        """Return to salary input screen to set a new salary."""
        self.frame.destroy()
        self.setup_salary_screen()
    
    def update_transaction_list(self):
        """Update the transaction listbox."""
        self.trans_listbox.delete(0, tk.END)
        for t in self.transactions:
            self.trans_listbox.insert(tk.END, t.to_string())
    
    def update_ui(self):
        """Update financial summary display."""
        total_spent = sum(t.amount for t in self.transactions)
        remaining = self.salary - total_spent
        for widget in self.frame.winfo_children():
            if isinstance(widget, tk.Label) and "Salary" in widget.cget("text"):
                widget.config(text=f"Salary: ₹{self.salary:.2f} | Spent: ₹{total_spent:.2f} | Remaining: ₹{remaining:.2f}")
        self.update_transaction_list()
    
    def save_data(self):
        """Disabled: Do not save data to JSON file."""
        pass
    
    def load_data(self):
        """Initialize with empty data, do not load from JSON file."""
        self.salary = 0.0
        self.transactions = []
    
    def generate_pdf(self):
        """Generate a PDF file with transaction details as a table."""
        filename = "finance_feedback.pdf"
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30, bottomMargin=30, leftMargin=30, rightMargin=30)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        normal_style = ParagraphStyle(
            name='Normal',
            fontSize=10,
            leading=12,
            spaceAfter=6,
        )
        
        # Title
        story.append(Paragraph("Finance Tracker Report", title_style))
        story.append(Spacer(1, 12))
        
        # Export Date
        story.append(Paragraph(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        story.append(Spacer(1, 12))
        
        # Financial Summary
        total_spent = sum(t.amount for t in self.transactions)
        remaining = self.salary - total_spent
        story.append(Paragraph(f"Salary: {self.salary:.2f} | Total Spent: {total_spent:.2f} | Remaining:{remaining:.2f}", normal_style))
        story.append(Spacer(1, 12))
        
        # Table Header
        data = [["Description", "Amount", "Category", "Date"]]
        
        # Table Data
        for t in self.transactions:
            desc = t.desc[:20] + ("..." if len(t.desc) > 20 else "")
            data.append([desc, f"{t.amount:.2f}", t.category, t.date])
        
        # Create Table with border
        table = Table(data, colWidths=[150, 100, 100, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),  # Added outer border
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        story.append(table)
        story.append(Spacer(1, 12))
        
        # Footer
        story.append(Paragraph("Generated by Finance Tracker", normal_style))
        
        # Build PDF
        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()

        # Save PDF to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(pdf_data)
            temp_file_path = temp_file.name

        return filename, temp_file_path

    def open_pdf(self, file_path):
        """Open the PDF file using the default system viewer."""
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

    def export_to_pdf(self):
        """Export transactions to a PDF file."""
        try:
            if not self.transactions:
                messagebox.showwarning("No Data", "No transactions to export!")
                return
            filename, temp_file_path = self.generate_pdf()
            self.open_pdf(temp_file_path)
            messagebox.showinfo("Success", f"Transactions exported to {filename} and opened!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export transactions to PDF: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Finance Tracker")
    root.geometry("800x600")
    app = FinanceTracker(root)
    root.mainloop()