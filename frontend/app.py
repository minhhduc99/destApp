import requests
import tkinter as tk
from tkinter import messagebox, ttk


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Application")
        self.geometry("400x300")

        self.top_frame = tk.Frame(self)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.access_token = None
        self.refresh_token = None

        self.show_login_form()

    def show_login_form(self):
        self.clear_container()
        login_form = LoginForm(self.container, self.login_success, self.show_register_form)
        login_form.pack(fill=tk.BOTH, expand=True)

    def show_register_form(self):
        self.clear_container()
        register_form = RegisterForm(self.container, self.show_login_form)
        register_form.pack(fill=tk.BOTH, expand=True)

    def login_success(self, role, access_token, refresh_token):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.show_hotel_management_form(role)

    def show_hotel_management_form(self, role):
        self.clear_container()
        hotel_management_form = HotelManagementForm(self.container, role)
        hotel_management_form.pack(fill=tk.BOTH, expand=True)
        self.show_logout_button()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_logout_button(self):
        self.logout_button = tk.Button(self.top_frame, text="Logout", command=self.logout)
        self.logout_button.pack(side=tk.RIGHT, padx=10, pady=10)

    def hide_logout_button(self):
        if hasattr(self, 'logout_button'):
            self.logout_button.pack_forget()

    def logout(self):
        if self.access_token and self.refresh_token:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            data = {"refresh_token": self.refresh_token}
            api_url = "http://127.0.0.1:8000/api/account/logout"
            response = requests.post(api_url, headers=headers, data=data)

            if response.status_code == 200:
                self.hide_logout_button()
                self.access_token = None
                self.refresh_token = None
                self.show_login_form()
                messagebox.showinfo("Message", "You have been logged out successfully")
            else:
                messagebox.showerror("Message", "Failed to logout. Please try again.")


class LoginForm(tk.Frame):
    def __init__(self, parent, on_success, show_register_form):
        super().__init__(parent)

        self.on_success = on_success
        self.show_register_form = show_register_form

        tk.Label(self, text="Username:").grid(row=0, column=0, sticky="e")
        self.username_entry = tk.Entry(self)
        self.username_entry.grid(row=0, column=1)

        tk.Label(self, text="Password:").grid(row=1, column=0, sticky="e")
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.grid(row=1, column=1)

        tk.Button(self, text="Login", command=self.login).grid(
            row=2, column=0, columnspan=2, pady=5)
        tk.Button(self, text="Register", command=self.show_register_form).grid(
            row=3, column=0, columnspan=2)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Call the login API
        api_url = "http://127.0.0.1:8000/api/account/login"
        data = {"username": username, "password": password}
        response = requests.post(api_url, data=data)

        # Check the response
        if response.status_code == 200:
            user_data = response.json()
            access_token = user_data.get('access_token')
            refresh_token = user_data.get('refresh_token')
            role = user_data.get('role', 'receptionist')
            self.on_success(role, access_token, refresh_token)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")


class RegisterForm(tk.Frame):
    def __init__(self, parent, show_login_form):
        super().__init__(parent)

        self.show_login_form = show_login_form

        tk.Label(self, text="Username:").grid(row=0, column=0, sticky="e")
        self.username_entry = tk.Entry(self)
        self.username_entry.grid(row=0, column=1)

        tk.Label(self, text="Password:").grid(row=1, column=0, sticky="e")
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.grid(row=1, column=1)

        tk.Label(self, text="Role:").grid(row=2, column=0, sticky="e")
        self.role_var = tk.StringVar()
        self.role_combobox = ttk.Combobox(
            self, textvariable=self.role_var, values=["manager", "receptionist"]
        )
        self.role_combobox.grid(row=2, column=1, sticky="w")

        tk.Button(self, text="Register", command=self.register).grid(
            row=3, column=0, columnspan=2, pady=5)
        tk.Button(
            self, text="Back to Login", command=self.show_login_form).grid(
                row=4, column=0, columnspan=2)

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_combobox.get()

        # Call the login API
        api_url = "http://127.0.0.1:8000/api/account/register"
        data = {
            "username": username,
            "password": password,
            "role": role
        }
        response = requests.post(api_url, data=data)

        # Check the response
        if response.status_code == 201:
            messagebox.showinfo("Message","Register Successfully",)
            self.show_login_form()
        else:
            messagebox.showerror("Message","Register Failed")


class HotelManagementForm(tk.Frame):
    def __init__(self, parent, role):
        super().__init__(parent)

        tk.Label(self, text="Room List").grid(row=0, column=0, padx=10, pady=10)

        self.rooms = tk.Listbox(self)
        self.rooms.grid(row=1, column=0, padx=10, pady=10)

        # Dummy room data
        self.rooms.insert(tk.END, "Room 101")
        self.rooms.insert(tk.END, "Room 102")
        self.rooms.insert(tk.END, "Room 103")

        self.add_room_button = tk.Button(self, text="Add Room", command=self.add_room)
        self.add_room_button.grid(row=2, column=0, padx=10, pady=10)

        if role != "manager":
            self.add_room_button.grid_remove()

    def add_room(self):
        messagebox.showinfo("Add Room", "Room added successfully!")

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
