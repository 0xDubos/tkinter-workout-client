import tkinter as tk
from tkinter import messagebox
import requests # Imports the requests library

API_BASE_URL = "http://127.0.0.1:8000/" # Base URL for our API

def fetch_workouts():
    """Fetches all workouts from the API and siplays them in the listbox."""
    try:
        response = requests.get(f"{API_BASE_URL}/workouts")
        # Raise an exception if the request was not successful (e.g 404, 500)
        response.raise_for_status()
        workouts = response.json() # Convert the JSON response to a Python List

        # Clear the current list in the listbox before adding new items
        workouts_listbox.delete(0, tk.END)

        # Add each workout to the listbox
        for workout in workouts:
            # Store the full workout object in a dictionary for later lookup
            workout_data[workout['id']] = workout
            workouts_listbox.insert(tk.END, f"ID: {workout['id']} | {workout['name']} - {workout['weight']} lbs")

    except requests.exceptions.RequestException as e:
        # Handle the connection errors or other request issues
        messagebox.showerror("ERROR", "Could not connect to the API.")

def add_workout():
    """Gets data from Entry widgets and sends it to the API to create a workout."""
    try:
        payload = {
            "name": name_entry.get(),
            "sets": int(sets_entry.get()),
            "reps": int(reps_entry.get()),
            "weight": int(weight_entry.get())
        }
        response = requests.post(f"{API_BASE_URL}/workouts", json=payload)
        response.raise_for_status()
        fetch_workouts() # Refresh the list to shw the new network
    
    except (requests.exceptions.RequestException, ValueError) as e:
        messagebox.showerror("Error", f"Failed to add workout: {e}")

def delete_workout():
    """Deletes the selected workout from the list"""
    try:
        # Gets the currently selected line
        selected_index = workouts_listbox.curselection()[0]
        selected_text = workouts_listbox.get(selected_index)
        # Extract the ID from the text "ID: 1 | ...."
        workout_id = int(selected_text.split(" | ")[0].split(": ")[1])

        response = requests.delete(f"{API_BASE_URL}/workouts/{workout_id}")
        response.raise_for_status()
        fetch_workouts() # Refresh list
    
    except IndexError:
        messagebox.showwarning("WARNING", "Please select a workout to delete.")
    except (requests.exceptions.RequestException, ValueError) as e:
        messagebox.showerror("Error", f"Failed to delete workout: {e}")


# --- GUI Setup --- #
window = tk.Tk()
window.title("Workout Log")

workout_data = {} # Dictionary to store full workout data by ID

# --- Frames for layout --- #
form_frame = tk.Frame(window)
list_frame = tk.Frame(window)
button_frame = tk.Frame(window)

form_frame.pack(pady=10)
list_frame.pack(pady=10) 
button_frame.pack(pady=10) 

# --- Form Widgets --- #
tk.Label(form_frame, text="Name:").grid(row=0, column=0)
name_entry = tk.Entry(form_frame)
name_entry.grid(row=0, column=1)

tk.Label(form_frame, text="Sets:").grid(row=1, column=0)
sets_entry = tk.Entry(form_frame)
sets_entry.grid(row=1, column=1)

tk.Label(form_frame, text="Reps:").grid(row=2, column=0)
reps_entry = tk.Entry(form_frame)
reps_entry.grid(row=2, column=1)

tk.Label(form_frame, text="Weight:").grid(row=3, column=0)
weight_entry = tk.Entry(form_frame)
weight_entry.grid(row=3, column=1)

add_button = tk.Button(form_frame, text="Add Workout", command=add_workout)
add_button.grid(row=4, columnspan=2, pady=10)

# --- Listbox and Buttons --- #
workouts_listbox = tk.Listbox(list_frame, width=60, height=15)
workouts_listbox.pack()

refresh_button = tk.Button(button_frame, text="Refresh Workouts", command=fetch_workouts)
refresh_button.pack(side=tk.LEFT, padx=5)

delete_button = tk.Button(button_frame, text="Delete Selected Workout", command=delete_workout)
delete_button.pack(side=tk.LEFT, padx=5)

# --- Initial load --- #
fetch_workouts()
window.mainloop()