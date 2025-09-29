import tkinter as tk
from tkinter import messagebox
import requests

# Configuration
USER_SERVICE_URL = "http://127.0.0.1:8000"
WORKOUT_SERVICE_URL = "http://127.0.0.1:8001"

class WorkoutApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Workout Log Client")
        self.token = None  # Store the user's access token here
        self.workout_data = {} # Dictionary to store full workout data by ID

        # This frame will hold whatever screen is currently active
        self.container = tk.Frame(root)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)

        self._setup_login_screen()

    def _clear_frame(self):
        """Destroys all widgets in the container frame."""
        for widget in self.container.winfo_children():
            widget.destroy()

    def _get_auth_headers(self):
        """Returns the authorization headers if a token exists."""
        if not self.token:
            messagebox.showerror("Error", "You are not logged in.")
            return None
        return {"Authorization": f"Bearer {self.token}"}

    # Login Screen
    def _setup_login_screen(self):
        self._clear_frame()
        self.root.title("Login")

        login_frame = tk.Frame(self.container)
        login_frame.pack()

        tk.Label(login_frame, text="Username:").grid(row=0, column=0, sticky="w", pady=2)
        self.username_entry = tk.Entry(login_frame)
        self.username_entry.grid(row=0, column=1, pady=2)

        tk.Label(login_frame, text="Password:").grid(row=1, column=0, sticky="w", pady=2)
        self.password_entry = tk.Entry(login_frame, show="*") # show="*" hides the password
        self.password_entry.grid(row=1, column=1, pady=2)

        login_button = tk.Button(login_frame, text="Login", command=self.handle_login)
        login_button.grid(row=2, columnspan=2, pady=10)

    def handle_login(self):
        """Sends login credentials to the /token endpoint."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        try:
            response = requests.post(
                f"{USER_SERVICE_URL}/token",
                data={"username": username, "password": password}
            )
            response.raise_for_status()
            self.token = response.json()["access_token"]
            self._setup_main_screen()
        except requests.exceptions.RequestException as e:
                messagebox.showerror("Login Failed", f"An error occurred: {e}")

    # Main Application Screen
    def _setup_main_screen(self):
        """Builds the main UI for adding, viewing, and deleting workouts."""
        self._clear_frame()
        self.root.title("Workout Log")

        form_frame = tk.Frame(self.container)
        list_frame = tk.Frame(self.container)
        button_frame = tk.Frame(self.container)

        form_frame.pack(pady=10)
        list_frame.pack(pady=10)
        button_frame.pack(pady=10)

        # Form Widgets
        tk.Label(form_frame, text="Name:").grid(row=0, column=0)
        self.name_entry = tk.Entry(form_frame)
        self.name_entry.grid(row=0, column=1)

        tk.Label(form_frame, text="Sets:").grid(row=1, column=0)
        self.sets_entry = tk.Entry(form_frame)
        self.sets_entry.grid(row=1, column=1)

        tk.Label(form_frame, text="Reps:").grid(row=2, column=0)
        self.reps_entry = tk.Entry(form_frame)
        self.reps_entry.grid(row=2, column=1)

        tk.Label(form_frame, text="Weight (lbs):").grid(row=3, column=0)
        self.weight_entry = tk.Entry(form_frame)
        self.weight_entry.grid(row=3, column=1)

        add_button = tk.Button(form_frame, text="Add Workout", command=self.add_workout)
        add_button.grid(row=4, columnspan=2, pady=10)

        # Listbox and Buttons
        self.workouts_listbox = tk.Listbox(list_frame, width=60, height=15)
        self.workouts_listbox.pack()

        refresh_button = tk.Button(button_frame, text="Refresh Workouts", command=self.fetch_workouts)
        refresh_button.pack(side=tk.LEFT, padx=5)

        delete_button = tk.Button(button_frame, text="Delete Selected", command=self.delete_workout)
        delete_button.pack(side=tk.LEFT, padx=5)
        
        # Initial data load
        self.fetch_workouts()

    def fetch_workouts(self):
        headers = self._get_auth_headers()
        if not headers: return

        try:
            response = requests.get(f"{WORKOUT_SERVICE_URL}/workouts", headers=headers)
            response.raise_for_status()
            workouts = response.json()
            
            self.workouts_listbox.delete(0, tk.END)
            self.workout_data.clear()
            for workout in workouts:
                self.workout_data[workout['id']] = workout
                display_text = f"ID: {workout['id']} | {workout['name']} ({workout['sets']}x{workout['reps']}) - {workout['weight']} lbs"
                self.workouts_listbox.insert(tk.END, display_text)
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Could not fetch workouts: {e}")
            
    def add_workout(self):
        headers = self._get_auth_headers()
        if not headers: return

        try:
            payload = {
                "name": self.name_entry.get(),
                "sets": int(self.sets_entry.get()),
                "reps": int(self.reps_entry.get()),
                "weight": int(self.weight_entry.get())
            }
            response = requests.post(f"{WORKOUT_SERVICE_URL}/workouts/", headers=headers, json=payload)
            response.raise_for_status()
            self.fetch_workouts()
        except (requests.exceptions.RequestException, ValueError) as e:
            messagebox.showerror("Error", f"Failed to add workout: {e}")

    def delete_workout(self):
        headers = self._get_auth_headers()
        if not headers: return

        try:
            selected_index = self.workouts_listbox.curselection()[0]
            selected_text = self.workouts_listbox.get(selected_index)
            workout_id = int(selected_text.split(" | ")[0].split(": ")[1])
            
            response = requests.delete(f"{WORKOUT_SERVICE_URL}/workouts/{workout_id}", headers=headers)
            response.raise_for_status()
            self.fetch_workouts()
        except IndexError:
            messagebox.showwarning("Warning", "Please select a workout to delete.")
        except (requests.exceptions.RequestException, ValueError) as e:
            messagebox.showerror("Error", f"Failed to delete workout: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WorkoutApp(root)
    root.mainloop()
