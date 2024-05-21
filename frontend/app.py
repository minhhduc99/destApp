from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, ttk
import requests
from tkcalendar import DateEntry


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
        self.username = None
        self.username_label = None

        self.token_expiry = None
        self.token_check_interval = 1000  # Interval to check token expiry in ms

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

    def login_success(self, role, access_token, refresh_token, username, expires_in):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.username = username
        self.token_expiry = expires_in
        self.show_hotel_management_form(role, access_token, username)
        self.start_token_expiry_timer()

    def show_hotel_management_form(self, role, access_token, username):
        self.clear_container()
        hotel_management_form = HotelManagementForm(
            self.container, role, access_token)
        hotel_management_form.pack(fill=tk.BOTH, expand=True)
        self.show_user_name(username)
        self.show_logout_button()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_user_name(self, username):
        if self.username_label:
            self.username_label.destroy()
        self.username_label = tk.Label(self.top_frame, text=f"Welcome, {username}")
        self.username_label.pack(side=tk.LEFT, padx=10, pady=10)

    def hide_user_name(self):
        if hasattr(self, 'username_label'):
            self.username_label.pack_forget()

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
                self.hide_user_name()
                self.access_token = None
                self.refresh_token = None
                self.username = None
                self.show_login_form()
                messagebox.showinfo("Message", "You have been logged out successfully")
            else:
                messagebox.showerror("Message", "Failed to logout. Please try again.")

    def start_token_expiry_timer(self):
        self.check_token_expiry()
        self.after(self.token_check_interval, self.start_token_expiry_timer)

    def check_token_expiry(self):
        if self.token_expiry:
            time_remaining = (self.token_expiry - datetime.now()).total_seconds()
            if time_remaining < 60:  # If less than 1 minute remaining
                self.show_token_expiry_popup()

    def show_token_expiry_popup(self):
        response = messagebox.askyesno("Session Expiry", "Your session is about to expire. Do you want to continue?")
        if response:
            self.refresh_access_token()
        else:
            self.logout()

    def refresh_access_token(self):
        if self.refresh_token:
            api_url = "http://127.0.0.1:8000/api/account/token/refresh"
            data = {"refresh": self.refresh_token}
            response = requests.post(api_url, data=data)

            if response.status_code == 200:
                user_data = response.json()
                self.access_token = user_data.get('access')
                expires_in = datetime.now() + timedelta(seconds=300)
                self.token_expiry = expires_in
                messagebox.showinfo("Message", "Session has been refreshed successfully")
            else:
                messagebox.showerror("Message", "Failed to refresh session. Please log in again.")
                self.logout()

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
            user_name = user_data.get('username')
            access_token = user_data.get('access_token')
            refresh_token = user_data.get('refresh_token')
            role = user_data.get('role', 'receptionist')
            expires_in = datetime.now() + timedelta(seconds=300)
            self.on_success(role, access_token, refresh_token, user_name, expires_in)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")
            self.clear_entries()

    def clear_entries(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)


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
        self.booking_treeview = None
        self.user_treeview = None
        self.room_ids = {}
        self.booking_ids = {}
        self.user_ids = {}

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.create_tabs()
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def create_tabs(self):
        self.room_tab = tk.Frame(self.notebook)
        self.booking_tab = tk.Frame(self.notebook)
        self.statistics_tab = tk.Frame(self.notebook)
        self.users_tab = tk.Frame(self.notebook)

        self.notebook.add(self.room_tab, text="Rooms")
        self.notebook.add(self.booking_tab, text="Bookings")
        if self.role == "manager":
            self.notebook.add(self.statistics_tab, text="Statistics")
            self.notebook.add(self.users_tab, text="Users")

        self.room_list(self.room_tab)

    def on_tab_changed(self, event):
        selected_tab = event.widget.tab(event.widget.index("current"))["text"]
        if selected_tab == "Rooms":
            self.room_list(self.room_tab)
        elif selected_tab == "Bookings":
            self.booking_list(self.booking_tab)
        elif selected_tab == "Statistics":
            self.hotel_statistics(self.statistics_tab)
        elif selected_tab == "Users":
            self.user_list(self.users_tab)

    def room_list(self, tab):
        # Clear previous widgets
        for widget in tab.winfo_children():
            widget.destroy()

        # Create frame to contain buttons
        button_frame = tk.Frame(tab)
        button_frame.pack(side=tk.TOP, anchor='nw', padx=5, pady=5)

        if self.role == "manager":
            self.add_room_button = tk.Button(button_frame, text="Add",
                                        command=self.show_add_room_form)
            self.add_room_button.pack(side=tk.LEFT)

        # Create Treeview for room list
        columns = ("no", "room number", "type", "price", "description", "status")
        self.room_treeview = ttk.Treeview(tab, columns=columns, show='headings')
        self.room_treeview.heading("no", text="NO")
        self.room_treeview.heading("room number", text="Room number")
        self.room_treeview.heading("type", text="Type")
        self.room_treeview.heading("price", text="Price")
        self.room_treeview.heading("description", text="Description")
        self.room_treeview.heading("status", text="Status")
        self.room_treeview.pack(fill=tk.BOTH, expand=True)

        self.load_rooms()

        if self.role == "manager":
            for child in self.room_treeview.get_children():
                self.room_treeview.item(child, tags=("editable",))

            self.update_room_button = tk.Button(
                button_frame, text="Update",
                command=self.show_update_room_form, state="disabled")
            self.delete_room_button = tk.Button(
                button_frame, text="Delete",
                command=self.delete_selected_room, state="disabled")

            # Place buttons on top of Treeview
            self.update_room_button.pack(side=tk.LEFT, padx=5, pady=5)
            self.delete_room_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.room_treeview.bind("<ButtonRelease-1>", self.check_room_selection)
        # self.room_treeview.bind("<ButtonRelease-3>", self.check_selection)
        self.clear_room_selection_button = tk.Button(
            button_frame, text="Clear Selection",
            command=self.clear_room_selection, state="disabled")
        self.clear_room_selection_button.pack(side=tk.LEFT)

    def load_rooms(self):
        api_url = "http://127.0.0.1:8000/api/hotel/rooms/"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(api_url, headers=headers)
        rooms = response.json()['data'] if response.status_code == 200 else []

        self.room_ids = {}
        for idx, room in enumerate(rooms):
            self.room_treeview.insert("", "end", values=(
                idx + 1,
                room['room_number'],
                room['room_type'],
                room['room_price'],
                room['room_description'],
                "Valid" if room['is_valid'] else "Invalid"
            ))
            self.room_ids[idx+1] = room['id']

    def check_room_selection(self, event):
        item = self.room_treeview.selection()
        if item and self.role=="manager":
            self.add_room_button.config(state="disabled")
            self.update_room_button.config(state="normal")
            self.delete_room_button.config(state="normal")
            self.clear_room_selection_button.config(state="normal")
        else:
            self.clear_room_selection_button.config(state="normal")

    def clear_room_selection(self):
        self.room_treeview.selection_remove(self.room_treeview.selection())
        if self.role == "manager":
            self.add_room_button.config(state="normal")
            self.update_room_button.config(state="disabled")
            self.delete_room_button.config(state="disabled")
            self.clear_room_selection_button.config(state="disabled")
        else:
            self.clear_room_selection_button.config(state="disabled")

    def show_add_room_form(self):
        add_room_window = tk.Toplevel(self)
        add_room_window.title("Add Room")

        tk.Label(add_room_window, text="Room Number:").grid(row=0, column=0, padx=5, pady=5)
        room_number_entry = tk.Entry(add_room_window)
        room_number_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(add_room_window, text="Type:").grid(row=1, column=0, padx=5, pady=5)
        type_options = ["Standard", "Single", "Double", "Deluxe"]
        type_entry = ttk.Combobox(add_room_window, state='readonly', values=type_options)
        type_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(add_room_window, text="Price:").grid(row=2, column=0, padx=5, pady=5)
        price_entry = tk.Entry(add_room_window)
        price_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(add_room_window, text="Description:").grid(row=3, column=0, padx=5, pady=5)
        description_entry = tk.Entry(add_room_window)
        description_entry.grid(row=3, column=1, padx=5, pady=5)

        def save_room():
            room_number = room_number_entry.get()
            room_type = type_entry.get()
            room_price = price_entry.get()
            room_description = description_entry.get()

            new_room = {
                "room_number": room_number,
                "room_type": room_type,
                "room_price": room_price,
                "room_description": room_description
            }
            api_url = "http://127.0.0.1:8000/api/hotel/rooms/new"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.post(api_url, headers=headers, json=new_room)
            if response.status_code == 201:
                room_data = response.json()['data']
                new_room_id = len(self.room_treeview.get_children()) + 1
                self.room_treeview.insert("", "end", values=(
                    new_room_id,
                    room_data['room_number'],
                    room_data['room_type'],
                    room_data['room_price'],
                    room_data['room_description'],
                    "Valid" if room_data['is_valid'] else "Invalid"
                ))
                messagebox.showinfo("Success", "Room added successfully")
                add_room_window.destroy()
                self.room_ids[new_room_id] = room_data['id']
            else:
                messagebox.showerror("Error", "Failed to add room")

        save_button = tk.Button(add_room_window, text="Save", command=save_room)
        save_button.grid(row=4, column=0, columnspan=2, pady=10)

    def show_update_room_form(self):
        selected_item = self.room_treeview.selection()
        selected_item_id = self.room_treeview.item(selected_item, "values")[0]
        room_id = self.room_ids.get(int(selected_item_id))

        api_url = f"http://127.0.0.1:8000/api/hotel/rooms/{room_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(api_url, headers=headers)
        if response.status_code != 200:
            messagebox.showerror("Error", "Failed to get room details")
            return

        room_data = response.json()['data']

        update_room_window = tk.Toplevel(self)
        update_room_window.title("Update Room")

        tk.Label(update_room_window, text="Room Number:").grid(row=0, column=0, padx=5, pady=5)
        room_number_entry = tk.Entry(update_room_window)
        room_number_entry.insert(0, room_data['room_number'])
        room_number_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(update_room_window, text="Type:").grid(row=1, column=0, padx=5, pady=5)
        type_entry = tk.Entry(update_room_window)
        type_entry.insert(0, room_data['room_type'])
        type_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(update_room_window, text="Price:").grid(row=2, column=0, padx=5, pady=5)
        price_entry = tk.Entry(update_room_window)
        price_entry.insert(0, room_data['room_price'])
        price_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(update_room_window, text="Description:").grid(row=3, column=0, padx=5, pady=5)
        description_entry = tk.Entry(update_room_window)
        description_entry.insert(0, room_data['room_description'])
        description_entry.grid(row=3, column=1, padx=5, pady=5)

        def save_updated_room():
            updated_room = {
                "room_number": room_number_entry.get(),
                "room_type": type_entry.get(),
                "room_price": price_entry.get(),
                "room_description": description_entry.get()
            }
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.put(api_url, headers=headers, json=updated_room)
            if response.status_code == 200:
                response_data = response.json()['data']
                self.room_treeview.item(selected_item, values=(
                    int(selected_item_id),
                    updated_room['room_number'],
                    updated_room['room_type'],
                    updated_room['room_price'],
                    updated_room['room_description'],
                    "Valid" if response_data['is_valid'] else "Invalid"
                ))
                messagebox.showinfo("Success", "Room updated successfully")
                update_room_window.destroy()
            else:
                messagebox.showerror("Error", "Failed to update room")

        save_button = tk.Button(update_room_window, text="Save", command=save_updated_room)
        save_button.grid(row=4, column=0, columnspan=2, pady=10)

    def delete_selected_room(self):
        selected_item = self.room_treeview.selection()
        selected_item_id = self.room_treeview.item(selected_item, "values")[0]
        room_id = self.room_ids.get(int(selected_item_id))

        api_url = f"http://127.0.0.1:8000/api/hotel/rooms/{room_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.delete(api_url, headers=headers)
        if response.status_code == 204:
            self.room_treeview.delete(selected_item)
            self.room_ids.pop(int(selected_item_id), None)
            self.update_item_numbers()
            self.clear_room_selection()
            messagebox.showinfo("Success", "Room deleted successfully")
        else:
            messagebox.showerror("Error", "Failed to delete room")

    def update_item_numbers(self):
        children = self.room_treeview.get_children()
        for idx, child in enumerate(children, start=1):
            self.room_treeview.item(child, values=(idx,) + self.room_treeview.item(child, "values")[1:])

    def booking_list(self, tab):
        # Clear previous widgets
        for widget in tab.winfo_children():
            widget.destroy()

        # Create frame to contain buttons
        button_frame = tk.Frame(tab)
        button_frame.pack(side=tk.TOP, anchor='nw', padx=5, pady=5)

        self.add_booking_button = tk.Button(button_frame, text="Add",
                                    command=self.show_add_booking_form)
        self.add_booking_button.pack(side=tk.LEFT)

        # Create Treeview for booking list
        columns = ("no", "guest", "booking", "booking_time", "start_time", "end_time", "check_in", "check_out", "status")
        self.booking_treeview = ttk.Treeview(tab, columns=columns, show='headings')
        self.booking_treeview.heading("no", text="NO")
        self.booking_treeview.heading("guest", text="Guest")
        self.booking_treeview.heading("booking", text="Room")
        self.booking_treeview.heading("booking_time", text="Booking Time")
        self.booking_treeview.heading("start_time", text="Start")
        self.booking_treeview.heading("end_time", text="End")
        self.booking_treeview.heading("end_time", text="End")
        self.booking_treeview.heading("check_in", text="Checkin")
        self.booking_treeview.heading("check_out", text="Checkout")
        self.booking_treeview.heading("status", text="Status")
        self.booking_treeview.pack(fill=tk.BOTH, expand=True)

        self.load_bookings()

        for child in self.booking_treeview.get_children():
            self.booking_treeview.item(child, tags=("editable",))

        self.update_booking_button = tk.Button(
            button_frame, text="Update",
            command=self.show_update_booking_form, state="disabled")
        self.checkin_button = tk.Button(button_frame, text="CheckIn", state="disabled",
                                        command=lambda: self.update_booking_status("CheckIn"))
        self.checkin_button.pack(side=tk.LEFT, padx=5)

        self.checkout_button = tk.Button(button_frame, text="CheckOut", state="disabled",
                                         command=lambda: self.update_booking_status("CheckOut"))
        self.checkout_button.pack(side=tk.LEFT, padx=5)
        self.delete_booking_button = tk.Button(
            button_frame, text="Delete",
            command=self.delete_selected_booking, state="disabled")

        # Place buttons on top of Treeview
        self.update_booking_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.delete_booking_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.booking_treeview.bind("<ButtonRelease-1>", self.check_booking_selection)
        # self.booking_treeview.bind("<ButtonRelease-3>", self.check_booking_selection)
        self.clear_booking_selection_button = tk.Button(
            button_frame, text="Clear Selection",
            command=self.clear_booking_selection, state="disabled")
        self.clear_booking_selection_button.pack(side=tk.LEFT)

    def load_bookings(self):
        api_url = "http://127.0.0.1:8000/api/hotel/bookings/"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(api_url, headers=headers)
        bookings = response.json()['data'] if response.status_code == 200 else []

        self.booking_ids = {}
        for idx, booking in enumerate(bookings):
            self.booking_treeview.insert("", "end", values=(
                idx + 1,
                booking['guest'],
                booking['room'],
                datetime.strptime(
                    booking['booking_time'],"%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                booking['start_time'],
				booking['end_time'],
				datetime.strptime(
                    booking['check_in'],"%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ) if booking['check_in'] else "-",
				datetime.strptime(
                    booking['check_out'],"%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ) if booking['check_out'] else "-",
                booking['booking_status']
            ))
            self.booking_ids[idx+1] = booking['id']

    def check_booking_selection(self, event):
        item = self.booking_treeview.selection()
        if item:
            item = self.booking_treeview.item(item)
            values = item["values"]

            # Get the start and end time from the selected booking
            start_time = datetime.strptime(values[4], "%Y-%m-%d").date()
            end_time = datetime.strptime(values[5], "%Y-%m-%d").date()
            current_time = datetime.now().date()
            booking_status = values[8]

            # Check if current time is within start_time and end_time
            if start_time <= current_time <= end_time:
                self.checkin_button.config(state="normal")
                self.checkout_button.config(state="normal")

            if booking_status == "CheckIn":
                self.checkin_button.config(state="disabled")
                self.checkout_button.config(state="normal")
            elif booking_status == "CheckOut":
                self.checkin_button.config(state="disabled")
                self.checkout_button.config(state="disabled")
            else:
                self.checkin_button.config(state="normal")
                self.checkout_button.config(state="normal")

            if booking_status in ("CheckIn", "CheckOut"):
                self.update_booking_button.config(state="disabled")
                self.delete_booking_button.config(state="disabled")
            else:
                self.update_booking_button.config(state="normal")
                self.delete_booking_button.config(state="normal")
            self.add_booking_button.config(state="disabled")
            self.clear_booking_selection_button.config(state="normal")

    def clear_booking_selection(self):
        self.booking_treeview.selection_remove(self.booking_treeview.selection())
        self.add_booking_button.config(state="normal")
        self.update_booking_button.config(state="disabled")
        self.delete_booking_button.config(state="disabled")
        self.clear_booking_selection_button.config(state="disabled")
        self.checkin_button.config(state="disabled")
        self.checkout_button.config(state="disabled")

    def show_add_booking_form(self):
        add_booking_window = tk.Toplevel(self)
        add_booking_window.title("New Booking")

        tk.Label(add_booking_window, text="Guest:").grid(row=0, column=0, padx=5, pady=5)
        guest_entry = tk.Entry(add_booking_window)
        guest_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(add_booking_window, text="Room:").grid(row=1, column=0, padx=5, pady=5)
        # Create combobox for room selection
        room_combobox = ttk.Combobox(add_booking_window, state="readonly")
        room_combobox.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(add_booking_window, text="Start:").grid(row=2, column=0, padx=5, pady=5)
        start_date_var = tk.StringVar()
        start_entry = DateEntry(add_booking_window, textvariable=start_date_var, date_pattern='yyyy-mm-dd')
        start_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(add_booking_window, text="End:").grid(row=3, column=0, padx=5, pady=5)
        end_date_var = tk.StringVar()
        end_entry = DateEntry(add_booking_window, textvariable=end_date_var, date_pattern='yyyy-mm-dd')
        end_entry.grid(row=3, column=1, padx=5, pady=5)

        self.load_rooms_for_booking(room_combobox)

        def save_booking():
            guest = guest_entry.get()
            selected_room_number = room_combobox.get()
            room = None
            for room_id, number in self.room_dict.items():
                if number == int(selected_room_number):
                    room = room_id
                    break
            start_time = start_entry.get()
            end_time = end_entry.get()

            new_booking = {
                "guest": guest,
                "room": room,
                "start_time": start_time,
                "end_time": end_time
            }
            api_url = "http://127.0.0.1:8000/api/hotel/bookings/new"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.post(api_url, headers=headers, json=new_booking)
            if response.status_code == 201:
                booking_data = response.json()['data']
                new_booking_id = len(self.booking_treeview.get_children()) + 1
                self.booking_treeview.insert("", "end", values=(
                    new_booking_id,
                    booking_data['guest'],
					self.get_room_number(booking_data['room']),
                    datetime.strptime(
                        booking_data['booking_time'],"%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
					booking_data['start_time'],
					booking_data['end_time'],
					datetime.strptime(
                        booking_data['check_in'],"%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ) if booking_data['check_in'] else "-",
                    datetime.strptime(
                        booking_data['check_out'],"%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ) if booking_data['check_out'] else "-",
                    booking_data['booking_status']
                ))
                messagebox.showinfo("Success", "Booking added successfully")
                add_booking_window.destroy()
                self.booking_ids[new_booking_id] = booking_data['id']
            else:
                messagebox.showerror("Error", "Failed to add booking")

        save_button = tk.Button(add_booking_window, text="Save", command=save_booking)
        save_button.grid(row=4, column=0, columnspan=2, pady=10)

    def load_rooms_for_booking(self, room_combobox):
        api_url = "http://127.0.0.1:8000/api/hotel/rooms/"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            rooms = response.json()['data']
            room_dict = {room['id']: room['room_number'] for room in rooms if room['is_valid'] is True}
            room_combobox['values'] = list(room_dict.values())
            self.room_dict = room_dict
        else:
            messagebox.showerror("Error", "Failed to load rooms")

    def get_room_number(self, room_id):
        return self.room_dict.get(room_id,None)

    def show_update_booking_form(self):
        selected_item = self.booking_treeview.selection()
        selected_item_id = self.booking_treeview.item(selected_item, "values")[0]
        booking_id = self.booking_ids.get(int(selected_item_id))

        api_url = f"http://127.0.0.1:8000/api/hotel/bookings/{booking_id}/"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(api_url, headers=headers)
        if response.status_code != 200:
            messagebox.showerror("Error", "Failed to get booking details")
            return

        booking_data = response.json()['data']

        update_booking_window = tk.Toplevel(self)
        update_booking_window.title("Update Booking")

        tk.Label(update_booking_window, text="Guest:").grid(row=0, column=0, padx=5, pady=5)
        guest_entry = tk.Entry(update_booking_window)
        guest_entry.insert(0, booking_data['guest'])
        guest_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(update_booking_window, text="Room:").grid(row=1, column=0, padx=5, pady=5)
        room_entry = tk.Entry(update_booking_window)
        room_entry.insert(0, booking_data['room__id'])
        room_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(update_booking_window, text="Start:").grid(row=2, column=0, padx=5, pady=5)
        start_entry = tk.Entry(update_booking_window)
        start_entry.insert(0, booking_data['start_time'])
        start_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(update_booking_window, text="End:").grid(row=3, column=0, padx=5, pady=5)
        end_entry = tk.Entry(update_booking_window)
        end_entry.insert(0, booking_data['end_time'])
        end_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(update_booking_window, text="Checkin:").grid(row=3, column=0, padx=5, pady=5)
        checkin_entry = tk.Entry(update_booking_window)
        checkin_entry.insert(0, booking_data['check_in'])
        checkin_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(update_booking_window, text="Checkout:").grid(row=3, column=0, padx=5, pady=5)
        checkout_entry = tk.Entry(update_booking_window)
        checkout_entry.insert(0, booking_data['check_out'])
        checkout_entry.grid(row=3, column=1, padx=5, pady=5)

        def save_updated_booking():
            selected_room_number = room_entry.get()
            room = None
            for room_id, number in self.room_dict.items():
                if number == int(selected_room_number):
                    room = room_id
                    break
            updated_booking = {
				"guest": guest_entry.get(),
                "room": room,
                "start_time": start_entry.get(),
                "end_time": end_entry.get(),
				"check_in": checkin_entry.get(),
				"check_out": checkout_entry.get()
            }
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.put(api_url, headers=headers, json=updated_booking)
            if response.status_code == 200:
                response_data = response.json()['data']
                self.booking_treeview.item(selected_item, values=(
                    int(selected_item_id),
                    response_data['guest'],
					self.get_room_number(response_data['room']),
					datetime.strptime(
                        response_data['booking_time'],"%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
					response_data['start_time'],
					response_data['end_time'],
					datetime.strptime(
                        response_data['check_in'],"%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ) if response_data['check_in'] else "-",
                    datetime.strptime(
                        response_data['check_out'],"%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ) if response_data['check_out'] else "-",
                    response_data['booking_status']
                ))
                messagebox.showinfo("Success", "Booking updated successfully")
                update_booking_window.destroy()
            else:
                messagebox.showerror("Error", "Failed to update booking")

        save_button = tk.Button(update_booking_window, text="Save", command=save_updated_booking)
        save_button.grid(row=4, column=0, columnspan=2, pady=10)

    def update_booking_status(self, status):
        selected_item = self.booking_treeview.selection()
        selected_item_id = self.booking_treeview.item(selected_item, "values")[0]
        booking_id = self.booking_ids.get(int(selected_item_id))

        api_url = f"http://127.0.0.1:8000/api/hotel/bookings/{booking_id}/action"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        data = {"booking_status": status}
        response = requests.put(api_url, headers=headers, json=data)

        if response.status_code == 200:
            response_data = response.json()['data']
            self.booking_treeview.item(selected_item, values=(
                int(selected_item_id),
                response_data['guest'],
                self.get_room_number(response_data['room']),
                datetime.strptime(
                    response_data['booking_time'],"%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                response_data['start_time'],
                response_data['end_time'],
                datetime.strptime(
                    response_data['check_in'],"%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ) if response_data['check_in'] else "-",
                datetime.strptime(
                    response_data['check_out'],"%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ) if response_data['check_out'] else "-",
                response_data['booking_status']
            ))
            messagebox.showinfo("Success", f"Booking {status} successfully")
        else:
            messagebox.showerror("Error", f"Failed to {status.lower()} booking")

    def delete_selected_booking(self):
        selected_item = self.booking_treeview.selection()
        selected_item_id = self.booking_treeview.item(selected_item, "values")[0]
        booking_id = self.booking_ids.get(int(selected_item_id))

        api_url = f"http://127.0.0.1:8000/api/hotel/bookings/{booking_id}/"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.delete(api_url, headers=headers)
        if response.status_code == 204:
            self.booking_treeview.delete(selected_item)
            self.booking_ids.pop(int(selected_item_id), None)
            self.update_booking_item_numbers()
            self.clear_booking_selection()
            messagebox.showinfo("Success", "Booking deleted successfully")
        else:
            messagebox.showerror("Error", "Failed to delete booking")

    def update_booking_item_numbers(self):
        children = self.booking_treeview.get_children()
        for idx, child in enumerate(children, start=1):
            self.booking_treeview.item(child, values=(idx,) + self.booking_treeview.item(child, "values")[1:])

    def hotel_statistics(self, tab):
        for widget in self.statistics_tab.winfo_children():
            widget.destroy()

        api_url = "http://127.0.0.1:8000/api/hotel/statistics"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            statistics = response.json()['data']
            total_bookings = statistics['total_bookings']
            total_revenue = statistics['total_revenue']
            revenue_by_room_type = statistics['revenue_by_room_type']

            # Display total_bookings
            tk.Label(self.statistics_tab, text=f"Total Bookings: {total_bookings}", anchor='w').pack(fill='x', pady=5)

            # Display total_revenue
            tk.Label(self.statistics_tab, text=f"Total Revenue: ${total_revenue}", anchor='w').pack(fill='x', pady=5)

            # Display revenue_by_room_type
            tk.Label(self.statistics_tab, text="Revenue by Room Type:", anchor='w').pack(fill='x', pady=5)
            for obj in revenue_by_room_type:
                tk.Label(self.statistics_tab, text=f"- {obj['room_type']}: ${obj['total_revenue']}", anchor='w').pack(fill='x', pady=2)
        else:
            messagebox.showerror("Error", "Failed to load statistics")

    def user_list(self, tab):
        for widget in tab.winfo_children():
            widget.destroy()

        # Create frame to contain buttons
        button_frame = tk.Frame(tab)
        button_frame.pack(side=tk.TOP, anchor='nw', padx=5, pady=5)

        # Create Treeview for room list
        columns = ("no", "user", "role")
        self.user_treeview = ttk.Treeview(tab, columns=columns, show='headings')
        self.user_treeview.heading("no", text="NO")
        self.user_treeview.heading("user", text="User")
        self.user_treeview.heading("role", text="Role")
        self.user_treeview.pack(fill=tk.BOTH, expand=True)

        self.load_users()

        for child in self.user_treeview.get_children():
            self.user_treeview.item(child, tags=("editable",))

        self.delete_user_button = tk.Button(
            button_frame, text="Delete",
            command=self.delete_selected_user, state="disabled")

        # Place buttons on top of Treeview
        self.delete_user_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.user_treeview.bind("<ButtonRelease-1>", self.check_user_selection)
        # self.room_treeview.bind("<ButtonRelease-3>", self.check_selection)
        self.clear_user_selection_button = tk.Button(
            button_frame, text="Clear Selection",
            command=self.clear_user_selection, state="disabled")
        self.clear_user_selection_button.pack(side=tk.LEFT)

    def load_users(self):
        api_url = "http://127.0.0.1:8000/api/account/users/"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(api_url, headers=headers)
        users = response.json() if response.status_code == 200 else []

        self.user_ids = {}
        for idx, user in enumerate(users):
            self.user_treeview.insert("", "end", values=(
                idx + 1,
                user['username'],
                user['role']
            ))
            self.user_ids[idx+1] = user['id']

    def check_user_selection(self, event):
        item = self.user_treeview.selection()
        if item:
            self.delete_user_button.config(state="normal")
            self.clear_user_selection_button.config(state="normal")

    def clear_user_selection(self):
        self.user_treeview.selection_remove(self.user_treeview.selection())
        self.delete_user_button.config(state="disabled")
        self.clear_user_selection_button.config(state="disabled")

    def delete_selected_user(self):
        selected_item = self.user_treeview.selection()
        selected_item_id = self.user_treeview.item(selected_item, "values")[0]
        user_id = self.user_ids.get(int(selected_item_id))

        api_url = f"http://127.0.0.1:8000/api/account/users/{user_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.delete(api_url, headers=headers)
        if response.status_code == 204:
            self.user_treeview.delete(selected_item)
            self.user_ids.pop(int(selected_item_id), None)
            self.update_user_item_numbers()
            self.clear_user_selection()
            messagebox.showinfo("Success", "User deleted successfully")
        else:
            messagebox.showerror("Error", "Failed to delete user")

    def update_user_item_numbers(self):
        children = self.user_treeview.get_children()
        for idx, child in enumerate(children, start=1):
            self.user_treeview.item(child, values=(idx,) + self.user_treeview.item(child, "values")[1:])

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
