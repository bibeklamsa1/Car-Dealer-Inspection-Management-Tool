import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime, timedelta

# Database functions
def create_db():
    conn = sqlite3.connect('car_dealer.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dealer TEXT,
            car_model TEXT,
            purchase_date TEXT,
            inspection_date TEXT
        )
    ''')
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS dealers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_dealer_to_db(dealer_name):
    conn = sqlite3.connect('car_dealer.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO dealers (name) VALUES (?)', (dealer_name,))
    conn.commit()
    conn.close()

def get_dealers_from_db():
    conn = sqlite3.connect('car_dealer.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM dealers')
    dealers = [row[0] for row in cursor.fetchall()]
    conn.close()
    return dealers

# Add car functionality
def add_car():
    dealer = dealer_combobox.get()
    car_model = car_model_entry.get()
    purchase_date = purchase_date_entry.get_date().strftime("%Y-%m-%d")
    inspection_date = inspection_date_entry.get_date().strftime("%Y-%m-%d")
    if not all([dealer, car_model, purchase_date, inspection_date]):
        messagebox.showwarning("Input Error", "All fields are required!")
        return
    
    conn = sqlite3.connect('car_dealer.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO cars (dealer, car_model, purchase_date, inspection_date)
        VALUES (?, ?, ?, ?)
    ''', (dealer, car_model, purchase_date, inspection_date))
    conn.commit()
    conn.close()

    # Clear input fields after adding the car
    dealer_combobox.set("All")  # Reset the dealer combobox
    car_model_entry.delete(0, "end")  # Clear the car model entry
    purchase_date_entry.set_date(datetime.now())  # Reset the purchase date picker to current date
    inspection_date_entry.set_date(datetime.now())  # Reset the inspection date picker to current date

    update_table()  # Update the table to show the newly added car

# Update table
def update_table():
    for row in table.get_children():
        table.delete(row)
    
    conn = sqlite3.connect('car_dealer.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cars')
    cars = cursor.fetchall()
    for car in cars:
        inspection_date = datetime.strptime(car[4], "%Y-%m-%d")
        remaining_days = (inspection_date - datetime.now()).days
        table.insert("", "end", values=(car[1], car[2], car[3], car[4], remaining_days))
    conn.close()


    
# Add dealer functionality (for Settings tab)
def add_dealer():
    
    dealer_name = new_dealer_entry.get()
    if dealer_name:
        add_dealer_to_db(dealer_name)
        # Fetch updated dealer list and update combobox
        dealer_list = ["All"] + get_dealers_from_db()
        filter_combobox["values"] = dealer_list
        filter_combobox.set("All")
        
        # Update the main tab's dealer combobox with the updated dealer list
        dealer_combobox["values"] = dealer_list
        dealer_combobox.set("All")
        
        new_dealer_entry.delete(0, "end")
        messagebox.showinfo("Success", "Dealer added successfully!")
    else:
        messagebox.showwarning("Input Error", "Dealer name is required!")




# Apply filter functionality
def apply_filter():
    selected_dealer = filter_combobox.get()
    # Apply the filter based on the selected dealer
    filtered_data = []
    conn = sqlite3.connect('car_dealer.db')
    cursor = conn.cursor()
    if selected_dealer == "All":
        cursor.execute('SELECT * FROM cars')
    else:
        cursor.execute('SELECT * FROM cars WHERE dealer = ?', (selected_dealer,))
    filtered_data = cursor.fetchall()
    conn.close()
    
    for row in table.get_children():
        table.delete(row)
        
    for car in filtered_data:
        inspection_date = datetime.strptime(car[4], "%Y-%m-%d")
        remaining_days = (inspection_date - datetime.now()).days
        table.insert("", "end", values=(car[1], car[2], car[3], car[4], remaining_days))

# Show expiring vehicles functionality
def show_expiring_vehicles():
    expiring_data = []
    current_date = datetime.now()
    expire_date = current_date + timedelta(days=10)  # 5 days from now
    
    conn = sqlite3.connect('car_dealer.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cars')
    all_cars = cursor.fetchall()

    for car in all_cars:
        inspection_date = datetime.strptime(car[4], "%Y-%m-%d")
        
        if current_date <= inspection_date <= expire_date:
            expiring_data.append(car)
        print("expiring_date",expire_date)
        print("current_date",current_date)	
        print("inspection_date",all_cars[0][4])
    conn.close()
    
    for row in table.get_children():
        table.delete(row)
        
    for car in expiring_data:
        inspection_date = datetime.strptime(car[4], "%Y-%m-%d")
        remaining_days = (inspection_date - datetime.now()).days
        table.insert("", "end", values=(car[1], car[2], car[3], car[4], remaining_days))

# GUI setup
root = tk.Tk()
root.title("Car Dealer Management")
root.geometry("800x600")

# Create database
create_db()

# Create Notebook (tabs)
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Main Tab
main_tab = tk.Frame(notebook)
notebook.add(main_tab, text="Main")

# Add car frame
frame = tk.Frame(main_tab)
frame.pack(pady=10)

tk.Label(frame, text="Dealer:", font=("Helvetica", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
dealer_combobox = ttk.Combobox(frame, state="readonly")
dealer_combobox.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame, text="Car Model:", font=("Helvetica", 10)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
car_model_entry = tk.Entry(frame)
car_model_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame, text="Purchase Date:", font=("Helvetica", 10)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
purchase_date_entry = DateEntry(frame, date_pattern="yyyy-mm-dd")
purchase_date_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame, text="Expire Inspection Date:", font=("Helvetica", 10)).grid(row=3, column=0, padx=5, pady=5, sticky="e")
inspection_date_entry = DateEntry(frame, date_pattern="yyyy-mm-dd")
inspection_date_entry.grid(row=3, column=1, padx=5, pady=5)

tk.Button(frame, text="Add Car", command=add_car, font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white", activebackground="#45a049").grid(row=4, column=0, columnspan=2, pady=10)

# Filter Section
filter_frame = tk.Frame(main_tab)
filter_frame.pack(pady=10)

tk.Label(filter_frame, text="Filter by Dealer:", font=("Helvetica", 10)).pack(side="left", padx=5)
filter_combobox = ttk.Combobox(filter_frame, state="readonly")
filter_combobox.pack(side="left", padx=5)

# Initialize dealer dropdown
dealer_list = ["All"] + get_dealers_from_db()
filter_combobox["values"] = dealer_list
filter_combobox.set("All")

tk.Button(filter_frame, text="Apply Filter", command=apply_filter, font=("Helvetica", 12, "bold"), bg="#008CBA", fg="white", activebackground="#007BB5").pack(side="left", padx=5)

# Expiring vehicles button
tk.Button(main_tab, text="Show Expiring Vehicles", command=show_expiring_vehicles, font=("Helvetica", 12, "bold"), bg="#FF5733", fg="white", activebackground="#ff4229").pack(pady=10)

# Table
columns = ("Dealer", "Car Model", "Purchase Date", "Inspection Date", "Remaining to Expire")
table = ttk.Treeview(main_tab, columns=columns, show="headings", height=10)
for col in columns:
    table.heading(col, text=col)
    table.column(col, width=150)
table.pack(fill="both", expand=True)

# Update table after table is created
update_table()  # Now the table is fully initialized before updating it

# Settings Tab
settings_tab = tk.Frame(notebook)
notebook.add(settings_tab, text="Settings")

# Add dealer section in Settings tab
tk.Label(settings_tab, text="Add Dealer:", font=("Helvetica", 12)).pack(pady=10)
new_dealer_entry = tk.Entry(settings_tab, font=("Helvetica", 12))
new_dealer_entry.pack(pady=5)

tk.Button(settings_tab, text="Add Dealer", command=add_dealer, font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white", activebackground="#45a049").pack(pady=5)



if __name__ == "__main__":
        dealer_list = ["All"] + get_dealers_from_db()
        filter_combobox["values"] = dealer_list
        filter_combobox.set("All")
        
        # Update the main tab's dealer combobox with the updated dealer list
        dealer_combobox["values"] = dealer_list
        dealer_combobox.set("All")
        
        
root.mainloop()
