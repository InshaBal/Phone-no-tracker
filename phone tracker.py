import tkinter as tk
from tkinter import ttk, messagebox
import tkintermapview
import phonenumbers
import sqlite3
from phonenumbers import geocoder, carrier
from opencage.geocoder import OpenCageGeocode
import pyttsx3
import speech_recognition as sr
from urllib.request import urlopen
from io import BytesIO
from PIL import Image, ImageTk

# Voice engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# API Key for OpenCage
key = 'c43216dbcf764abf9b5f80a47309bd9a'

# Dark mode colors
bg_color = "#1e1e2f"
fg_color = "#ffffff"
entry_bg = "#2d2d44"
button_bg = "#9b59b6"
text_bg = "#2d2d44"

# Main window
root = tk.Tk()
root.geometry("700x900")
root.title("📍 Phone Number Tracker")
root.configure(bg=bg_color)

# Database
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
header_frame = tk.Frame(root, bg=button_bg, pady=15)
header_frame.pack(fill=tk.X)
label1 = tk.Label(header_frame, text="📱 Phone Number Tracker", font=('Segoe UI', 22, 'bold'), bg=button_bg, fg='white')
label1.pack()

# Input area
input_frame = tk.Frame(root, pady=25, bg=bg_color)
input_frame.pack()

number_label = tk.Label(input_frame, text="Enter Phone Number (with country code):", font=('Segoe UI', 12), bg=bg_color, fg=fg_color)
number_label.grid(row=0, column=0, padx=10)

number = tk.Entry(input_frame, font=('Segoe UI', 14), width=25, bg=entry_bg, fg='white', insertbackground='white')
number.grid(row=0, column=1, padx=10)

flag_label = tk.Label(input_frame, bg=bg_color)
flag_label.grid(row=0, column=2, padx=10)

# Buttons
button_frame = tk.Frame(root, bg=bg_color)
button_frame.pack(pady=10)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def show_flag(country_code):
    try:
        url = f"https://flagcdn.com/w40/{country_code.lower()}.png"
        response = urlopen(url)
        img_data = response.read()
        image = Image.open(BytesIO(img_data))
        photo = ImageTk.PhotoImage(image)
        flag_label.config(image=photo)
        flag_label.image = photo
    except:
        flag_label.config(image='')

def getResult():
    num = number.get().strip()
    try:
        num1 = phonenumbers.parse(num)
        country_code = phonenumbers.region_code_for_number(num1)
        show_flag(country_code)

        location = geocoder.description_for_number(num1, "en")
        service_provider = carrier.name_for_number(num1, "en")

        ocg = OpenCageGeocode(key)
        result = ocg.geocode(str(location))

        if result:
            lat = result[0]['geometry']['lat']
            lng = result[0]['geometry']['lng']
            formatted_address = result[0]['formatted']

            speak(f"The number belongs to {location}. Provider is {service_provider}.")

            map_frame = tk.LabelFrame(root, bg=bg_color)
            map_frame.pack(pady=10)

            map_widget = tkintermapview.TkinterMapView(map_frame, width=500, height=400, corner_radius=12)
            map_widget.set_position(lat, lng)
            map_widget.set_marker(lat, lng, text="📍 Location")
            map_widget.set_zoom(10)
            map_widget.pack()

            result_display.delete("1.0", tk.END)
            result_display.insert(tk.END, f"Location: {location}\nService Provider: {service_provider}\n")
            result_display.insert(tk.END, f"Latitude: {lat}\nLongitude: {lng}\nAddress: {formatted_address}")

            c.execute('''INSERT INTO history (phone_number, location, service_provider, latitude, longitude, address)
                         VALUES (?, ?, ?, ?, ?, ?)''', (num, location, service_provider, lat, lng, formatted_address))
            conn.commit()
        else:
            messagebox.showerror("Error", "Location not found.")

    except phonenumbers.NumberParseException:
        messagebox.showerror("Invalid", "Please enter a valid phone number.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Speak the phone number with country code")
        audio = r.listen(source)
    try:
        spoken_text = r.recognize_google(audio)
        number.delete(0, tk.END)
        number.insert(0, spoken_text)
        getResult()
    except:
        messagebox.showerror("Voice Error", "Could not recognize the spoken input.")

def view_history():
    history_window = tk.Toplevel(root)
    history_window.title("📂 Search History")
    history_window.geometry("600x400")
    history_window.configure(bg=bg_color)

    history_text = tk.Text(history_window, wrap=tk.WORD, bg=text_bg, fg='white', font=('Segoe UI', 12))
    history_text.pack(fill=tk.BOTH, expand=1)

    c.execute('SELECT * FROM history')
    rows = c.fetchall()
    for row in rows:
        history_text.insert(tk.END, f"Phone Number: {row[1]}\nLocation: {row[2]}\n")
        history_text.insert(tk.END, f"Service: {row[3]}\nLat: {row[4]} | Lng: {row[5]}\nAddress: {row[6]}\n\n")

# Buttons
search_button = tk.Button(button_frame, text="🔍 Search", font=("Segoe UI", 12, 'bold'), bg=button_bg, fg='white', width=15, command=getResult)
search_button.pack(side=tk.LEFT, padx=10)



history_button = tk.Button(button_frame, text="📁 View History", font=("Segoe UI", 12, 'bold'), bg=button_bg, fg='white', width=15, command=view_history)
history_button.pack(side=tk.LEFT, padx=10)

# Output box
result_display = tk.Text(root, height=7, width=60, font=('Segoe UI', 12), bg=text_bg, fg='white', bd=2, relief="flat")
result_display.pack(pady=15)

root.mainloop()