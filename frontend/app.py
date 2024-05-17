import requests
import tkinter as tk
from tkinter import messagebox, ttk

class LoginForm(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Login Form")

        self.username_label = tk.Label(self, text="Username:")
        self.username_label.grid(row=0, column=0, sticky="e")
        self.username_entry = tk.Entry(self)
        self.username_entry.grid(row=0, column=1)

        self.password_label = tk.Label(self, text="Password:")
        self.password_label.grid(row=1, column=0, sticky="e")
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.grid(row=1, column=1)

        self.login_button = tk.Button(self, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=5)

        self.register_button = tk.Button(self, text="Register", command=self.show_register_form)
        self.register_button.grid(row=3, column=0, columnspan=2)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Call the login API
        api_url = "http://127.0.0.1:8000/api/account/login"
        data = {"username": username, "password": password}
        response = requests.post(api_url, data=data)

        # Check the response
        if response.status_code == 200:
            messagebox.showinfo("Login Successful", "Welcome, {}".format(username))
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def show_register_form(self):
        self.destroy()
        register_form = RegisterForm()
        register_form.mainloop()

class RegisterForm(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Register Form")

        self.username_label = tk.Label(self, text="Username:")
        self.username_label.grid(row=0, column=0, sticky="e")
        self.username_entry = tk.Entry(self)
        self.username_entry.grid(row=0, column=1)

        self.password_label = tk.Label(self, text="Password:")
        self.password_label.grid(row=1, column=0, sticky="e")
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.grid(row=1, column=1)

        self.role_label = tk.Label(self, text="Role:")
        self.role_label.grid(row=2, column=0, sticky="e")
        self.role_var = tk.StringVar()
        self.role_combobox = ttk.Combobox(self, textvariable=self.role_var,
                                          values=["manager", "receptionist"])
        self.role_combobox.grid(row=2, column=1, sticky="w")

        self.register_button = tk.Button(self, text="Register", command=self.register)
        self.register_button.grid(row=3, column=0, columnspan=2, pady=5)

        self.back_button = tk.Button(self, text="Back to Login", command=self.show_login_form)
        self.back_button.grid(row=4, column=0, columnspan=2)

        self.dropdown_shown = False

    def show_dropdown(self, event):
        self.role_combobox.focus_set()
        self.role_combobox.event_generate('<Down>')

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
            messagebox.showinfo("Register Successfully",)
        else:
            messagebox.showerror("Register Failed",)

    def show_login_form(self):
        self.destroy()
        login_form = LoginForm()
        login_form.mainloop()

if __name__ == "__main__":
    login_form = LoginForm()
    login_form.mainloop()
