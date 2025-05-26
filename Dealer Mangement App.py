import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime, timedelta

# Database function


def create_db():
    conn = sqlite3.connect('car_dealer.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dealer TEXT,
            car_model TEXT,
            mr_number TEXT,
            purchase_date TEXT,
            registration_date TEXT  
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

# Add dealer functionality
# Add dealer functionality
def add_dealer():
    dealer_name = new_dealer_entry.get()
    if dealer_name:
        # Check if the dealer already exists in the database
        conn = sqlite3.connect('car_dealer.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM dealers WHERE name = ?', (dealer_name,))
        existing_dealer = cursor.fetchone()
        conn.close()
        
        if existing_dealer:
            messagebox.showwarning("Dealer Exists", f"The dealer '{dealer_name}' already exists!")
        else:
            # If the dealer doesn't exist, add the new dealer
            add_dealer_to_db(dealer_name)
            # Fetch updated dealer list and update combobox
            dealer_list = ["All"] + get_dealers_from_db()
            
            # Update the combobox in the main tab
            filter_combobox["values"] = dealer_list
            filter_combobox.set("All")
            
            # Update the combobox in the Add Car tab
            dealer_combobox["values"] = dealer_list
            dealer_combobox.set("All")
            
            # Clear the new dealer entry field
            new_dealer_entry.delete(0, "end")
            
            messagebox.showinfo("Success", "Dealer added successfully!")
    else:
        messagebox.showwarning("Input Error", "Dealer name is required!")

# Add car functionality
def add_car():
    dealer = dealer_combobox.get()
    car_model = car_model_entry.get()
    purchase_date = purchase_date_entry.get_date().strftime("%Y-%m-%d")
    registration_date = registration_date_entry.get_date().strftime("%Y-%m-%d")
    mr_number = mr_number_entry.get()
    if not mr_number:
        #show yes no dialog box that MR Number is required and put yes or no before commit
        answer = messagebox.askyesno("Input Error", "MR Number is required! Do you want to continue without MR Number?")
        if answer == False:
            mr_number = None
            return
        
    if not all([dealer, car_model, purchase_date, registration_date]):
        messagebox.showwarning("Input Error", "All fields are required!")
        return
    
    conn = sqlite3.connect('car_dealer.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        INSERT INTO cars (dealer, car_model,mr_number, purchase_date, registration_date)
        VALUES (?, ?, ?,? , ?)
    ''', (dealer, car_model,mr_number, purchase_date, registration_date))
    conn.commit()
    conn.close()

    # Clear input fields after adding the car
    dealer_combobox.set("All")  # Reset the dealer combobox
    car_model_entry.delete(0, "end")  # Clear the car model entry
    mr_number_entry.delete(0, "end") # Clear MR Number entry
    
    purchase_date_entry.set_date(datetime.now())  # Reset the purchase date picker to current date
    registration_date_entry.set_date(datetime.now())  # Reset the registration date picker to current date

    update_table()  # Update the table to show the newly added car
    messagebox.showinfo("Success", "Car added successfully!")

# Update table
# Update table function with color coding for expiring cars
def update_table():
    for row in table.get_children():
        table.delete(row)

    conn = sqlite3.connect('car_dealer.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cars order by registration_date')
    cars = cursor.fetchall()
    conn.close()

    for car in cars:
        registration_date = datetime.strptime(car[5], "%Y-%m-%d")
        remaining_days = ( registration_date - datetime.now()).days + 1

        if remaining_days <= 7 and remaining_days >= 0:	
            table.insert("", "end", values=(car[0], car[1], car[2], car[3], car[4],car[5], remaining_days), tags=("expiring",))
        elif remaining_days < 0:
            table.insert("", "end", values=(car[0], car[1], car[2], car[3], car[4],car[5], "Expired"), tags=("expiring",))
        else:
            table.insert("", "end", values=(car[0], car[1], car[2], car[3], car[4],car[5], remaining_days))

# Apply filter functionality
def apply_filter():
    selected_dealer = filter_combobox.get()
    filtered_data = []
    current_date = datetime.now()
    expire_date = current_date + timedelta(days=7)
    conn = sqlite3.connect('car_dealer.db')
    cursor = conn.cursor()
    if selected_dealer == "All":
        cursor.execute('SELECT * FROM cars order by registration_date')
    else:
        cursor.execute('SELECT * FROM cars WHERE dealer = ? order by registration_date', (selected_dealer,))
    filtered_data = cursor.fetchall()
    conn.close()
    
    for row in table.get_children():
        table.delete(row)
        
    for car in filtered_data:
        registration_date = datetime.strptime(car[5], "%Y-%m-%d")
        remaining_days = (registration_date - datetime.now()).days + 1
        if remaining_days <= 7 and remaining_days >= 0:
            table.insert("", "end", values=(car[0], car[1], car[2], car[3], car[4],car[5], remaining_days), tags=("expiring",))
        elif remaining_days < 0:
            table.insert("", "end", values=(car[0], car[1], car[2], car[3], car[4],car[5], "Expired"), tags=("expiring",))
        else:
            table.insert("", "end", values=(car[0], car[1], car[2], car[3], car[4],car[5], remaining_days))

# Show expiring vehicles functionality

# Show expiring vehicles with color coding
def show_expiring_vehicles():
    expiring_data = []
    current_date = datetime.now()
    expire_date = current_date + timedelta(days=7)  # 10 days from now

    conn = sqlite3.connect('car_dealer.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cars order by registration_date')
    all_cars = cursor.fetchall()
    conn.close()

    # Clear the table before inserting new data
    table.delete(*table.get_children())

    for car in all_cars:
        registration_date = datetime.strptime(car[5], "%Y-%m-%d")
        remaining_days = ( registration_date-datetime.now()).days + 1

        if remaining_days <0:
            table.insert("", "end", values=(car[0], car[1], car[2], car[3], car[4],car[5], "Expired"), tags=("expiring",))
        elif remaining_days <= 7:
            table.insert("", "end", values=(car[0], car[1], car[2], car[3], car[4],car[5], remaining_days), tags=("expiring",))
#Edit the selected car when right clicked
def open_edit_window():
    selected_item = table.selection()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select a car to edit!")
        return

    car_data = table.item(selected_item)["values"]

    edit_win = tk.Toplevel(root)
    edit_win.title("Edit Car Details")
    edit_win.geometry("400x380")
    edit_win.configure(bg="white")

    ttk.Label(edit_win, text="Edit Car Details", font=("Helvetica", 16, "bold")).pack(pady=10)

    form_frame = ttk.Frame(edit_win, padding=10)
    form_frame.pack(fill=tk.BOTH, expand=True)

    # Dealer
    ttk.Label(form_frame, text="Dealer:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
    dealer_entry = ttk.Combobox(form_frame, values=get_dealers_from_db(), state="readonly")
    dealer_entry.set(car_data[1])
    dealer_entry.grid(row=0, column=1, pady=5, padx=5)

    # Car Model
    ttk.Label(form_frame, text="Car Model:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
    car_model_entry = ttk.Entry(form_frame)
    car_model_entry.insert(0, car_data[2])
    car_model_entry.grid(row=1, column=1, pady=5, padx=5)

    # MR Number
    ttk.Label(form_frame, text="MR Number:").grid(row=2, column=0, sticky="w", pady=5, padx=5)
    mr_entry = ttk.Entry(form_frame)
    mr_entry.insert(0, car_data[3])
    mr_entry.grid(row=2, column=1, pady=5, padx=5)

    # Purchase Date
    ttk.Label(form_frame, text="Purchase Date:").grid(row=3, column=0, sticky="w", pady=5, padx=5)
    purchase_date_entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd')
    purchase_date_entry.set_date(datetime.strptime(car_data[4], "%Y-%m-%d"))
    purchase_date_entry.grid(row=3, column=1, pady=5, padx=5)

    # registration Date
    ttk.Label(form_frame, text="Last registration Date:").grid(row=4, column=0, sticky="w", pady=5, padx=5)
    registration_date_entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd')
    registration_date_entry.set_date(datetime.strptime(car_data[5], "%Y-%m-%d"))
    registration_date_entry.grid(row=4, column=1, pady=5, padx=5)

    # Save Button
    def save_updates():
        new_dealer = dealer_entry.get()
        new_model = car_model_entry.get()
        new_mr = mr_entry.get()
        new_purchase = purchase_date_entry.get_date().strftime("%Y-%m-%d")
        new_registration = registration_date_entry.get_date().strftime("%Y-%m-%d")

        conn = sqlite3.connect('car_dealer.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE cars SET 
                dealer = ?, 
                car_model = ?, 
                mr_number = ?, 
                purchase_date = ?, 
                registration_date = ?
            WHERE id = ?
        ''', (new_dealer, new_model, new_mr, new_purchase, new_registration, car_data[0]))
        conn.commit()
        conn.close()

        update_table()
        messagebox.showinfo("Success", "Car updated successfully!")
        edit_win.destroy()

    
    tk.Button(edit_win, text="Save Changes", command=save_updates, font=("Helvetica", 15, "bold"), bg="#4CAF50", fg="white", activebackground="#45a049").pack(pady=20)

    
# Delete selected car from database and update table
def delete_car():
    selected_item = table.selection()  # Get selected row
    if selected_item:
        car_id = table.item(selected_item)["values"][0]  # Assuming the first column is the car ID
        conn = sqlite3.connect('car_dealer.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cars WHERE id = ?', (car_id,))
        conn.commit()
        conn.close()
        
        # Remove the row from the table
        table.delete(selected_item)
        messagebox.showinfo("Success", "Car deleted successfully!")
    else:
        messagebox.showwarning("Selection Error", "Please select a car to delete!")

# Create a right-click menu (context menu)
def show_right_click_menu(event):
    # Get the selected row
    item = table.identify('item', event.x, event.y)
    if item:
        table.selection_set(item)  # Select the item clicked
        right_click_menu.post(event.x_root, event.y_root)  # Show the right-click menu


# GUI setup
root = tk.Tk()
root.title("Car Dealer Management")
root.geometry("1300x750")
root.config(bg="#f4f4f9")
# Create the right-click menu
right_click_menu = tk.Menu(root, tearoff=0)
right_click_menu.add_command(label="Edit", command=lambda: open_edit_window())
right_click_menu.add_command(label="Delete", command=delete_car)

# Create database
create_db()

# Create Notebook (tabs)
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Main Tab (Expiring Vehicles)
main_tab = tk.Frame(notebook)
notebook.add(main_tab, text="Vehicles Status", padding=10, sticky="nsew")

# Frame to hold the button and filter widgets in a horizontal line
filter_frame = tk.Frame(main_tab)
filter_frame.pack(pady=10)

# Expiring vehicles button
tk.Button(filter_frame, text="List All Inspection Expiring Vehicles In Upcoming Days", command=show_expiring_vehicles, font=("Helvetica", 12, "bold"), bg="#4169e1", fg="white", activebackground="#4169e1").grid(row=0, column=0, padx=10)

# Filter Combobox for main tab
tk.Label(filter_frame, text="Filter by Dealer:", font=("Helvetica", 12)).grid(row=0, column=1, padx=10)

filter_combobox = ttk.Combobox(filter_frame, state="readonly", width=30, font=("Helvetica", 10))
filter_combobox.grid(row=0, column=2, padx=10)
filter_combobox.set("All")

# Filter Apply Button
tk.Button(filter_frame, text="Apply Filter", command=apply_filter, font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white", activebackground="#45a049").grid(row=0, column=3, padx=10)

# Table for expiring vehicles
columns = ("ID", "Dealer Name", "Car Model", "MR Number", "Purchase Date", "Last Date For registration", "Days Remaining to Expire")

table_frame = tk.Frame(main_tab)
table_frame.pack(fill="both", expand=True)

table_scroll = tk.Scrollbar(table_frame, orient="vertical")
table_scroll.pack(side="right", fill="y")

table = ttk.Treeview(table_frame, columns=columns, show="headings", height=10, yscrollcommand=table_scroll.set)
table_scroll.config(command=table.yview)
# Configure table row colors
table.tag_configure("expiring", foreground="red", font=("Helvetica", 10, "bold"))
for col in columns:
    table.heading(col, text=col, anchor="center")
    table.column(col, width=150, anchor="center")
table.pack(fill="both", expand=True)

# Add Car Tab
add_car_tab = tk.Frame(notebook)
notebook.add(add_car_tab, text="Add Car", padding=10, sticky="nsew")


# Add car frame
frame = tk.Frame(add_car_tab)
frame.pack(pady=20)

tk.Label(frame, text="Dealer Name:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=5)
dealer_combobox = ttk.Combobox(frame, state="readonly", width=40, font=("Helvetica", 12))
dealer_combobox.grid(row=0, column=1, padx=10, pady=5)

tk.Label(frame, text="Car Model:", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=5)
car_model_entry = tk.Entry(frame, font=("Helvetica", 12), width=40)
car_model_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(frame, text="MR Number:", font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=5)
mr_number_entry = tk.Entry(frame, font=("Helvetica", 12), width=40)
mr_number_entry.grid(row=2, column=1, padx=10, pady=5)

tk.Label(frame, text="Purchased Date:", font=("Helvetica", 12)).grid(row=3, column=0, padx=10, pady=5)
purchase_date_entry = DateEntry(frame, font=("Helvetica", 12), width=40, date_pattern="dd-mm-yyyy")
purchase_date_entry.grid(row=3, column=1, padx=10, pady=5)

tk.Label(frame, text="Last Date For registration:", font=("Helvetica", 12)).grid(row=4, column=0, padx=10, pady=5)
registration_date_entry = DateEntry(frame, font=("Helvetica", 12), width=40, date_pattern="dd-mm-yyyy")
registration_date_entry.grid(row=4, column=1, padx=10, pady=5)



# Add Car Button
add_car_button = tk.Button(frame, text="Add Car", font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white", activebackground="#45a049", command=add_car)
add_car_button.grid(row=5, columnspan=2, pady=20)


# Add Dealer Tab
add_dealer_tab = tk.Frame(notebook)
notebook.add(add_dealer_tab, text="Add Dealer", padding=10, sticky="nsew")

# Add dealer frame
dealer_frame = tk.Frame(add_dealer_tab)
dealer_frame.pack(pady=20)

tk.Label(dealer_frame, text="New Dealer Name:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=5)
new_dealer_entry = tk.Entry(dealer_frame, font=("Helvetica", 12), width=40)
new_dealer_entry.grid(row=0, column=1, padx=10, pady=5)

# Add Dealer Button
add_dealer_button = tk.Button(dealer_frame, text="Add Dealer", font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white", activebackground="#ff4229", command=add_dealer)
add_dealer_button.grid(row=1, columnspan=2, pady=20)

# Initial update
dealer_list = ["All"] + get_dealers_from_db()
filter_combobox["values"] = dealer_list
filter_combobox.set("All")
dealer_combobox["values"] = dealer_list
dealer_combobox.set("All")

# Bind right-click event on the table
table.bind("<Button-3>", show_right_click_menu)

# Initial update of the table
update_table()

root.mainloop()