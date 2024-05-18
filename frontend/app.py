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
        login_form = LoginForm(
            self.container, self.login_success, self.show_register_form)
        login_form.pack(fill=tk.BOTH, expand=True)

    def show_register_form(self):
        self.clear_container()
        register_form = RegisterForm(self.container, self.show_login_form)
        register_form.pack(fill=tk.BOTH, expand=True)

    def login_success(self, role, access_token, refresh_token):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.show_hotel_management_form(role, access_token)

    def show_hotel_management_form(self, role, access_token):
        self.clear_container()
        hotel_management_form = HotelManagementForm(
            self.container, role, access_token)
        hotel_management_form.pack(fill=tk.BOTH, expand=True)
        self.show_logout_button()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_logout_button(self):
        self.logout_button = tk.Button(
            self.top_frame, text="Logout", command=self.logout)
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
    def __init__(self, parent, role, access_token):
        super().__init__(parent)

        self.role = role
        self.access_token = access_token

        self.room_treeview = None

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.create_tabs()

    def create_tabs(self):
        self.room_tab = tk.Frame(self.notebook)
        self.booking_tab = tk.Frame(self.notebook)

        self.notebook.add(self.room_tab, text="Rooms")
        self.notebook.add(self.booking_tab, text="Bookings")

        self.room_list(self.room_tab)
        self.booking_list(self.booking_tab)

    def room_list(self, tab):
        # Clear previous widgets
        for widget in tab.winfo_children():
            widget.destroy()

        # Create frame to contain buttons
        button_frame = tk.Frame(tab)
        button_frame.pack(side=tk.TOP, anchor='nw', padx=5, pady=5)

        if self.role == "manager":
            self.add_button = tk.Button(button_frame, text="Add",
                                        command=lambda: self.add_item(tab))
            self.add_button.pack(side=tk.LEFT)

        # Create Treeview for room list
        columns = ("no", "room number", "type", "price", "description")
        self.room_treeview = ttk.Treeview(tab, columns=columns, show='headings')
        self.room_treeview.heading("no", text="NO")
        self.room_treeview.heading("room number", text="Room number")
        self.room_treeview.heading("type", text="Type")
        self.room_treeview.heading("price", text="Price")
        self.room_treeview.heading("description", text="Description")
        self.room_treeview.pack(fill=tk.BOTH, expand=True)

        api_url = "http://127.0.0.1:8000/api/hotel/rooms/"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(api_url, headers=headers)
        rooms = response.json()['data'] if response.status_code == 200 else []

        for idx,room in enumerate(rooms):
            self.room_treeview.insert("", "end", values=(
                idx+1,
                room['room_number'],
                room['room_type'],
                room['room_price'],
                room['room_description']
                )
            )

        if self.role == "manager":
            for child in self.room_treeview.get_children():
                self.room_treeview.item(child, tags=("editable",))

            self.update_button = tk.Button(
                button_frame, text="Update",
                command=self.update_selected_room, state="disabled")
            self.delete_button = tk.Button(
                button_frame, text="Delete",
                command=self.delete_selected_room, state="disabled")
            # self.room_treeview.bind("<ButtonRelease-1>", self.check_selection)
            # self.room_treeview.bind("<ButtonRelease-3>", self.check_selection)

            # Place buttons on top of Treeview
            self.update_button.pack(side=tk.LEFT, padx=5, pady=5)
            self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.room_treeview.bind("<ButtonRelease-1>", self.check_selection)
        self.room_treeview.bind("<ButtonRelease-3>", self.check_selection)
        self.clear_selection_button = tk.Button(
            button_frame, text="Clear Selection",
            command=self.clear_selection, state="disabled")
        self.clear_selection_button.pack(side=tk.LEFT)

    def check_selection(self, event):
        item = self.room_treeview.selection()
        if item and self.role=="manager":
            self.add_button.config(state="disabled")
            self.update_button.config(state="normal")
            self.delete_button.config(state="normal")
            self.clear_selection_button.config(state="normal")
        else:
            self.clear_selection_button.config(state="normal")

    def update_selected_room(self):
        selected_item = self.room_treeview.selection()
        room_id = self.room_treeview.item(selected_item, "values")[0]
        # Implement logic to update room

    def delete_selected_room(self):
        selected_item = self.room_treeview.selection()
        room_id = self.room_treeview.item(selected_item, "values")[0]

    def clear_selection(self):
        self.room_treeview.selection_remove(self.room_treeview.selection())
        if self.role == "manager":
            self.add_button.config(state="normal")
            self.update_button.config(state="disabled")
            self.delete_button.config(state="disabled")
            self.clear_selection_button.config(state="disabled")
        else:
            self.clear_selection_button.config(state="disabled")

    def booking_list(self, tab):
        # Clear previous widgets
        for widget in tab.winfo_children():
            widget.destroy()

        # Create frame to contain buttons
        button_frame = tk.Frame(tab)
        button_frame.pack(side=tk.TOP, anchor='nw', padx=5, pady=5)

        if self.role == "manager":
            self.add_button = tk.Button(button_frame, text="Add",
                                        command=lambda: self.add_item(tab))
            self.add_button.pack(side=tk.LEFT)

        # Create Treeview for room list
        # columns = ("no", "room number", "type", "price", "description")
        # self.room_treeview = ttk.Treeview(tab, columns=columns, show='headings')
        # self.room_treeview.heading("no", text="NO")
        # self.room_treeview.heading("room number", text="Room number")
        # self.room_treeview.heading("type", text="Type")
        # self.room_treeview.heading("price", text="Price")
        # self.room_treeview.heading("description", text="Description")
        # self.room_treeview.pack(fill=tk.BOTH, expand=True)

        # api_url = "http://127.0.0.1:8000/api/hotel/rooms/"
        # headers = {"Authorization": f"Bearer {self.access_token}"}
        # response = requests.get(api_url, headers=headers)
        # rooms = response.json()['data'] if response.status_code == 200 else []

        # for idx,room in enumerate(rooms):
        #     self.room_treeview.insert("", "end", values=(
        #         idx+1,
        #         room['room_number'],
        #         room['room_type'],
        #         room['room_price'],
        #         room['room_description']
        #         )
        #     )

        # if self.role == "manager":
        #     for child in self.room_treeview.get_children():
        #         self.room_treeview.item(child, tags=("editable",))

        #     self.update_button = tk.Button(
        #         button_frame, text="Update",
        #         command=self.update_selected_room, state="disabled")
        #     self.delete_button = tk.Button(
        #         button_frame, text="Delete",
        #         command=self.delete_selected_room, state="disabled")
        #     # self.room_treeview.bind("<ButtonRelease-1>", self.check_selection)
        #     # self.room_treeview.bind("<ButtonRelease-3>", self.check_selection)

        #     # Place buttons on top of Treeview
        #     self.update_button.pack(side=tk.LEFT, padx=5, pady=5)
        #     self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)

        # self.room_treeview.bind("<ButtonRelease-1>", self.check_selection)
        # self.room_treeview.bind("<ButtonRelease-3>", self.check_selection)
        # self.clear_selection_button = tk.Button(
        #     button_frame, text="Clear Selection",
        #     command=self.clear_selection, state="disabled")
        # self.clear_selection_button.pack(side=tk.LEFT)

    def add_item(self, tab):
        if tab==self.room_tab:
            messagebox.showinfo("Message", "Room tab")
        else:
            messagebox.showinfo("Message", "Booking tab")

    def update_room(self, room_id):
        # Implement logic to update a room
        pass

    def delete_room(self, room_id):
        # Implement logic to delete a room
        pass

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
