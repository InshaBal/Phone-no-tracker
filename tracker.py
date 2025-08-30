import tkinter as tk
from tkinter import ttk
import tkintermapview
import phonenumbers
import sqlite3
from phonenumbers import geocoder, carrier
from tkinter import messagebox
from opencage.geocoder import OpenCageGeocode

key = 'c43216dbcf764abf9b5f80a47309bd9a'

root = tk.Tk()
root.geometry("600x800")
root.title("Phone Number Tracker")
root.configure(bg='#eaf6ff')  # Soft blue background

# SQLite database setup
conn = sqlite3.connect('search_history.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY,
        phone_number TEXT,
        location TEXT,
        service_provider TEXT,
        latitude REAL,
        longitude REAL,
        address TEXT
    )
''')
conn.commit()

# Header
header_frame = tk.Frame(root, bg='#3498db', pady=15)
header_frame.pack(fill=tk.X)

label1 = tk.Label(header_frame, text="📱 Phone Number Tracker", font=('Segoe UI', 20, 'bold'),
                  bg='#3498db', fg='white')
label1.pack()

# Input area
input_frame = tk.Frame(root, pady=20, bg='#eaf6ff')
input_frame.pack(pady=20)

number_label = tk.Label(input_frame, text="Enter Phone Number (with country code):",
                        font=('Segoe UI', 12), bg='#eaf6ff')
number_label.grid(row=0, column=0, padx=10)

number = tk.Entry(input_frame, font=('Segoe UI', 14), width=25, bd=2, relief="solid")
number.grid(row=0, column=1, padx=10)

# Button frame
button_frame = tk.Frame(root, bg='#eaf6ff')
button_frame.pack(pady=20)

style = ttk.Style()
style.configure("TButton", font=('Segoe UI', 12, 'bold'), padding=6)
style.map('TButton', foreground=[('active', 'white')],
          background=[('active', '#2980b9')])

# Result display box
result_display = tk.Text(root, height=8, width=50, font=('Segoe UI', 12),
                         bd=2, relief="solid", bg='white')
result_display.pack(pady=10)

# Function to handle search
def getResult():
    num = number.get().strip()
    try:
        num1 = phonenumbers.parse(num)
        location = geocoder.description_for_number(num1, "en")
        service_provider = carrier.name_for_number(num1, "en")

        ocg = OpenCageGeocode(key)
        query = str(location)
        result = ocg.geocode(query)

        if result and len(result) > 0:
            lat = result[0]['geometry']['lat']
            lng = result[0]['geometry']['lng']
            formatted_address = result[0]['formatted']

            # Clear old maps if any
            for widget in map_frame.winfo_children():
                widget.destroy()

            map_widget = tkintermapview.TkinterMapView(map_frame, width=480, height=400, corner_radius=10)
            map_widget.set_position(lat, lng)
            map_widget.set_marker(lat, lng, text="Phone Location")
            map_widget.set_zoom(12)
            map_widget.pack()

            result_display.delete("1.0", tk.END)
            result_display.insert(tk.END, f"Location: {location}\n")
            result_display.insert(tk.END, f"Service Provider: {service_provider}\n")
            result_display.insert(tk.END, f"Latitude: {lat}\nLongitude: {lng}\n")
            result_display.insert(tk.END, f"Address: {formatted_address}\n")

            c.execute('''
                INSERT INTO history (phone_number, location, service_provider, latitude, longitude, address)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (num, location, service_provider, lat, lng, formatted_address))
            conn.commit()
        else:
            messagebox.showerror("Error", "No results found for the location.")

    except phonenumbers.NumberParseException:
        messagebox.showerror("Invalid Number", "The phone number entered is not valid.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Map Frame - defined once for reuse
map_frame = tk.LabelFrame(root, bg='#eaf6ff', padx=10, pady=10)
map_frame.pack(pady=20)

# Search button
search_button = ttk.Button(button_frame, text="Search", command=getResult, style="TButton")
search_button.pack(side=tk.LEFT, padx=10)

# History window
def view_history():
    history_window = tk.Toplevel(root)
    history_window.title("Search History")
    history_window.geometry("500x300")

    c.execute('SELECT * FROM history')
    rows = c.fetchall()

    history_text = tk.Text(history_window, wrap=tk.WORD, font=('Segoe UI', 12))
    history_text.pack(fill=tk.BOTH, expand=1)

    for row in rows:
        history_text.insert(tk.END, f"Phone Number: {row[1]}\nLocation: {row[2]}\n")
        history_text.insert(tk.END, f"Service Provider: {row[3]}\nLatitude: {row[4]}\nLongitude: {row[5]}\n")
        history_text.insert(tk.END, f"Address: {row[6]}\n\n")

# History button
history_button = ttk.Button(button_frame, text="View History", command=view_history, style="TButton")
history_button.pack(side=tk.RIGHT, padx=10)

root.mainloop()

