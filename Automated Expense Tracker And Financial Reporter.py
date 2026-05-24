import os
import json
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Set up the modern visual theme(Main btw)
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

DATA_FILE = "financial_data.json"

def load_data():
    """Loads expense data from a local JSON file."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    """Saves expense data securely to a local JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


class ExpenseTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Enterprise Expense Tracker & Financial Reporter")
        self.geometry("900x600")
        self.expenses = load_data()

        # Configure Grid Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # ---- LEFT PANEL: INPUT FORM ----
        self.form_frame = ctk.CTkFrame(self, width=280, corner_radius=10)
        self.form_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.lbl_title = ctk.CTkLabel(self.form_frame, text="Log Transaction", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_title.pack(pady=15)

        # Amount Input
        self.entry_amount = ctk.CTkEntry(self.form_frame, placeholder_text="Amount ($)")
        self.entry_amount.pack(fill="x", padx=20, pady=10)

        # Category Dropdown
        self.categories = ["Food & Dining", "Utilities & Bills", "Transport", "Entertainment", "Shopping", "Salary/Income", "Other"]
        self.combo_category = ctk.CTkComboBox(self.form_frame, values=self.categories)
        self.combo_category.set("Select Category")
        self.combo_category.pack(fill="x", padx=20, pady=10)

        # Description Input
        self.entry_desc = ctk.CTkEntry(self.form_frame, placeholder_text="Description (e.g., Office Supplies)")
        self.entry_desc.pack(fill="x", padx=20, pady=10)

        # Action Buttons
        self.btn_add = ctk.CTkButton(self.form_frame, text="Add Transaction", command=self.add_transaction)
        self.btn_add.pack(fill="x", padx=20, pady=15)

        self.btn_export = ctk.CTkButton(self.form_frame, text="Export to Excel", fg_color="#27ae60", hover_color="#219653", command=self.export_to_excel)
        self.btn_export.pack(fill="x", padx=20, pady=5)

        # ---- RIGHT PANEL: DASHBOARD & REPORTING ----
        self.dashboard_frame = ctk.CTkFrame(self, corner_radius=10)
        self.dashboard_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.dashboard_frame.grid_columnconfigure(0, weight=1)
        self.dashboard_frame.grid_rowconfigure(1, weight=1)

        self.lbl_dash = ctk.CTkLabel(self.dashboard_frame, text="Financial Analytics Dashboard", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_dash.grid(row=0, column=0, pady=15)

        # Container for the chart
        self.chart_container = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        self.chart_container.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        # Display chart on startup
        self.canvas = None
        self.update_dashboard()

    def add_transaction(self):
        """Validates inputs and records the transaction."""
        amount_raw = self.entry_amount.get()
        category = self.combo_category.get()
        desc = self.entry_desc.get()

        # Input Validation
        try:
            amount = float(amount_raw)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Validation Error", "Please enter a valid positive numeric amount.")
            return

        if category == "Select Category":
            messagebox.showerror("Validation Error", "Please choose a structural business category.")
            return

        # Create structured record
        record = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "category": category,
            "amount": amount,
            "description": desc if desc else "N/A"
        }

        self.expenses.append(record)
        save_data(self.expenses)
        
        # Reset Form & Refresh Analytics
        self.entry_amount.delete(0, 'end')
        self.entry_desc.delete(0, 'end')
        self.combo_category.set("Select Category")
        
        self.update_dashboard()
        messagebox.showinfo("Success", "Transaction recorded successfully.")

    def update_dashboard(self):
        """Aggregates analytics using pandas and updates the matplotlib chart UI."""
        # Clear previous chart canvas
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        if not self.expenses:
            lbl_empty = ctk.CTkLabel(self.chart_container, text="No transactional data available.\nLog records to populate metrics.", font=ctk.CTkFont(size=14))
            lbl_empty.pack(expand=True)
            return

        # Erase existing placeholder elements
        for widget in self.chart_container.winfo_children():
            widget.destroy()

        # Parse data using Pandas DataFrame
        df = pd.DataFrame(self.expenses)
        category_totals = df.groupby("category")["amount"].sum()

        # Generate Matplotlib Chart
        fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('#2b2b2b') # Matches CustomTkinter frame color
        ax.set_facecolor('#2b2b2b')

        # Color totally optional
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f1c40f', '#9b59b6', '#1abc9c', '#e67e22']
        
        wedges, texts, autotexts = ax.pie(
            category_totals, 
            labels=category_totals.index, 
            autopct='%1.1f%%', 
            startangle=140,
            colors=colors[:len(category_totals)],
            textprops=dict(color="w")
        )

        ax.set_title("Distribution Expense Allocation", color="w", fontsize=14, weight="bold")

        # Inject chart into CustomTkinter Frame
        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def export_to_excel(self):
        """Compiles standard reports into a professional Excel file."""
        if not self.expenses:
            messagebox.showwarning("Export Failed", "There is no dataset available to generate an audit report.")
            return

        try:
            filename = f"Financial_Report_{datetime.now().strftime('%Y%m%d')}.xlsx"
            df = pd.DataFrame(self.expenses)
            
            # Reorder columns cleanly
            df = df[["date", "category", "description", "amount"]]
            df.columns = ["Timestamp", "Allocation Category", "Description", "Amount ($)"]

            # Save explicitly to Microsoft Excel format
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name="General Ledger")
                
            messagebox.showinfo("Export Complete", f"Audit-ready ledger exported cleanly to:\n{os.path.abspath(filename)}")
        except Exception as e:
            messagebox.showerror("System Error", f"Failed to compile report: {str(e)}")


if __name__ == "__main__":
    app = ExpenseTrackerApp()
    app.mainloop()