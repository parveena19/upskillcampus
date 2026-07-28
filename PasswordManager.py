"""
=========================================================
            PASSWORD MANAGER -  PROJECT
=========================================================

Language : Python 3.14
GUI      : Tkinter
Database : SQLite

Features
--------
✓ Master Password Login (SHA-256)
✓ Add Password
✓ View Passwords
✓ Search Password
✓ Update Password
✓ Delete Password
✓ Password Generator
✓ Copy Password
✓ Show / Hide Password
✓ Password Strength Indicator
✓ SQLite Auto Database
✓ OOP Design
✓ Responsive Tkinter Layout

=========================================================
"""

import hashlib
import random
import sqlite3
import string
import tkinter as tk

from tkinter import ttk
from tkinter import messagebox


# ==========================================================
# CONFIGURATION
# ==========================================================

DATABASE_NAME = "password_manager.db"

WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 700

APP_TITLE = "Password Manager"


# ==========================================================
# DATABASE
# ==========================================================

class DatabaseManager:

    def __init__(self):

        self.connection = sqlite3.connect(DATABASE_NAME)

        self.cursor = self.connection.cursor()

        self.create_tables()
            # ------------------------------------------------------
    # SAFE APPLICATION EXIT
    # ------------------------------------------------------

    
    # ------------------------------------------------------

    def create_tables(self):

        self.cursor.execute("""

        CREATE TABLE IF NOT EXISTS master_password(

            id INTEGER PRIMARY KEY,

            password_hash TEXT NOT NULL

        )

        """)

        self.cursor.execute("""

        CREATE TABLE IF NOT EXISTS passwords(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            website TEXT NOT NULL,

            username TEXT NOT NULL,

            password TEXT NOT NULL,

            notes TEXT

        )

        """)

        self.connection.commit()

    # ------------------------------------------------------

    def hash_password(self, password):

        return hashlib.sha256(password.encode()).hexdigest()

    # ------------------------------------------------------

    def master_password_exists(self):

        self.cursor.execute(

            "SELECT * FROM master_password LIMIT 1"

        )

        return self.cursor.fetchone() is not None

    # ------------------------------------------------------

    def create_master_password(self, password):

        hashed = self.hash_password(password)

        self.cursor.execute(

            "INSERT INTO master_password(password_hash) VALUES(?)",

            (hashed,)

        )

        self.connection.commit()

    # ------------------------------------------------------

    def verify_master_password(self, password):

        hashed = self.hash_password(password)

        self.cursor.execute(

            "SELECT password_hash FROM master_password LIMIT 1"

        )

        row = self.cursor.fetchone()

        if row is None:

            return False

        return row[0] == hashed

    # ------------------------------------------------------
    def close(self):
        try:
            self.connection.close()

        except sqlite3.Error:
            pass
    
    # ------------------------------------------------------
    # PASSWORD CRUD METHODS
    # ------------------------------------------------------

    def add_password(self, website, username, password, notes):
        """
        Insert a new password record.
        """
        try:
            self.cursor.execute(
                """
                INSERT INTO passwords
                (website, username, password, notes)
                VALUES (?, ?, ?, ?)
                """,
                (website, username, password, notes)
            )

            self.connection.commit()
            return True

        except sqlite3.Error:
            return False

    # ------------------------------------------------------

    def get_all_passwords(self):
        """
        Return all saved passwords.
        """

        self.cursor.execute(
            """
            SELECT
                id,
                website,
                username,
                password,
                notes
            FROM passwords
            ORDER BY website
            """
        )

        return self.cursor.fetchall()
    # ------------------------------------------------------
    # SEARCH PASSWORDS
    # ------------------------------------------------------

    def search_passwords(self, keyword):

        self.cursor.execute(
            """
            SELECT
                id,
                website,
                username,
                password,
                notes
            FROM passwords
            WHERE website LIKE ?
               OR username LIKE ?
            ORDER BY website
            """,
            (f"%{keyword}%", f"%{keyword}%")
        )

        return self.cursor.fetchall()
    # ------------------------------------------------------
    # UPDATE PASSWORD
    # ------------------------------------------------------

    def update_password(self, record_id, website, username, password, notes):

        try:

            self.cursor.execute(
                """
                UPDATE passwords
                SET website=?,
                    username=?,
                    password=?,
                    notes=?
                WHERE id=?
                """,
                (
                    website,
                    username,
                    password,
                    notes,
                    record_id
                )
            )

            self.connection.commit()

            return True

        except sqlite3.Error:

            return False

    # ------------------------------------------------------
    # DELETE PASSWORD
    # ------------------------------------------------------

    def delete_password(self, record_id):

        try:

            self.cursor.execute(
                """
                DELETE FROM passwords
                WHERE id=?
                """,
                (record_id,)
            )

            self.connection.commit()

            return True

        except sqlite3.Error:

            return False
# ==========================================================
# PASSWORD GENERATOR
# ==========================================================

class PasswordGenerator:

    @staticmethod
    def generate(length=16):

        characters = (

            string.ascii_letters +

            string.digits +

            "!@#$%^&*()_+-=?"

        )

        return "".join(

            random.choice(characters)

            for _ in range(length)

        )


# ==========================================================
# PASSWORD STRENGTH
# ==========================================================

class PasswordStrength:

    @staticmethod
    def check(password):

        score = 0

        if len(password) >= 8:
            score += 1

        if any(c.isupper() for c in password):
            score += 1

        if any(c.islower() for c in password):
            score += 1

        if any(c.isdigit() for c in password):
            score += 1

        if any(c in "!@#$%^&*()_+-=?" for c in password):
            score += 1

        if score <= 2:
            return "Weak"

        elif score == 3:
            return "Medium"

        elif score == 4:
            return "Strong"

        return "Very Strong"


# ==========================================================
# APPLICATION
# ==========================================================

class PasswordManagerApp(tk.Tk):

    def __init__(self):

        super().__init__()

        self.db = DatabaseManager()

        self.title(APP_TITLE)

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        self.minsize(900, 600)

        self.configure(bg="#f5f5f5")

        self.current_frame = None

        self.show_login()
        self.protocol(
        "WM_DELETE_WINDOW",
        self.on_closing
)
    def on_closing(self):
    
        if messagebox.askokcancel(
                "Exit",
                "Are you sure you want to exit Password Manager?"
            ):
    
                try:
                    self.db.close()
                except Exception:
                    pass
    
                self.destroy()
    

    # ------------------------------------------------------

    def clear_window(self):

        if self.current_frame is not None:

            self.current_frame.destroy()

    # ------------------------------------------------------

    def show_login(self):

        self.clear_window()

        self.current_frame = LoginFrame(self)

        self.current_frame.pack(

            fill="both",

            expand=True

        )

    # ------------------------------------------------------

    def show_dashboard(self):

        self.clear_window()

        self.current_frame = DashboardFrame(self)

        self.current_frame.pack(

            fill="both",

            expand=True

        )
        # ==========================================================
# LOGIN FRAME
# ==========================================================

class LoginFrame(tk.Frame):

    def __init__(self, app):
        super().__init__(app, bg="#f5f5f5")

        self.app = app

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        container = tk.Frame(self, bg="white", bd=1, relief="solid")
        container.grid(row=0, column=0, padx=40, pady=40)

        title = tk.Label(
            container,
            text="Password Manager",
            font=("Segoe UI", 22, "bold"),
            bg="white"
        )
        title.pack(pady=(25, 10))

        subtitle = tk.Label(
            container,
            text="Secure Master Login",
            font=("Segoe UI", 11),
            bg="white",
            fg="gray40"
        )
        subtitle.pack()

        self.first_time = not self.app.db.master_password_exists()

        if self.first_time:

            info = tk.Label(
                container,
                text="Create your Master Password",
                font=("Segoe UI", 11),
                bg="white"
            )
            info.pack(pady=(25, 5))

            tk.Label(
                container,
                text="Master Password",
                bg="white",
                anchor="w"
            ).pack(fill="x", padx=40)

            self.password_entry = tk.Entry(
                container,
                show="*",
                width=35
            )
            self.password_entry.pack(padx=40, pady=5)

            tk.Label(
                container,
                text="Confirm Password",
                bg="white",
                anchor="w"
            ).pack(fill="x", padx=40)

            self.confirm_entry = tk.Entry(
                container,
                show="*",
                width=35
            )
            self.confirm_entry.pack(padx=40, pady=5)

        else:

            info = tk.Label(
                container,
                text="Enter Master Password",
                font=("Segoe UI", 11),
                bg="white"
            )
            info.pack(pady=(25, 5))

            tk.Label(
                container,
                text="Master Password",
                bg="white",
                anchor="w"
            ).pack(fill="x", padx=40)

            self.password_entry = tk.Entry(
                container,
                show="*",
                width=35
            )
            self.password_entry.pack(padx=40, pady=5)

        self.show_var = tk.BooleanVar(value=False)

        tk.Checkbutton(
            container,
            text="Show Password",
            variable=self.show_var,
            bg="white",
            command=self.toggle_password
        ).pack(pady=10)

        self.login_button = tk.Button(
            container,
            text="Continue",
            width=20,
            command=self.authenticate
        )
        self.login_button.pack(pady=(10, 25))

        self.password_entry.focus()

    # --------------------------------------------------

    def toggle_password(self):

        if self.show_var.get():
            self.password_entry.config(show="")

            if self.first_time:
                self.confirm_entry.config(show="")
        else:
            self.password_entry.config(show="*")

            if self.first_time:
                self.confirm_entry.config(show="*")

    # --------------------------------------------------

    def authenticate(self):

        password = self.password_entry.get().strip()

        if password == "":
            messagebox.showerror(
                "Error",
                "Master Password cannot be empty."
            )
            return

        if self.first_time:

            confirm = self.confirm_entry.get().strip()

            if password != confirm:
                messagebox.showerror(
                    "Error",
                    "Passwords do not match."
                )
                return

            if len(password) < 8:
                messagebox.showwarning(
                    "Weak Password",
                    "Master Password should contain at least 8 characters."
                )
                return

            try:
                self.app.db.create_master_password(password)

                messagebox.showinfo(
                    "Success",
                    "Master Password created successfully."
                )

                self.app.show_dashboard()

            except Exception as error:

                messagebox.showerror(
                    "Database Error",
                    str(error)
                )

        else:

            if self.app.db.verify_master_password(password):

                self.app.show_dashboard()

            else:

                messagebox.showerror(
                    "Login Failed",
                    "Incorrect Master Password."
                )
 # ==========================================================
# DASHBOARD FRAME
# ==========================================================

class DashboardFrame(tk.Frame):

    def __init__(self, app):
        super().__init__(app, bg="#f5f5f5")

        self.app = app

        # Make the layout responsive
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ---------------- Header ----------------

        header = tk.Frame(self, bg="#1f4e79", height=60)
        header.pack(fill="x")

        title = tk.Label(
            header,
            text="Password Manager Dashboard",
            font=("Segoe UI", 18, "bold"),
            bg="#1f4e79",
            fg="white"
        )

        title.pack(side="left", padx=20, pady=15)

        logout_btn = tk.Button(
            header,
            text="Logout",
            command=self.logout
        )

        logout_btn.pack(side="right", padx=20, pady=15)

        # ---------------- Main Area ----------------

        body = tk.Frame(self, bg="#f5f5f5")
        body.pack(fill="both", expand=True, padx=20, pady=20)

        # ==================================================
        # SEARCH BAR
        # ==================================================

        search_frame = tk.Frame(body, bg="#f5f5f5")

        search_frame.pack(fill="x", pady=10)

        tk.Label(
            search_frame,
            text="Search:",
            bg="#f5f5f5",
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")

        self.search_entry = tk.Entry(
            search_frame,
            width=35
        )

        self.search_entry.pack(
            side="left",
            padx=10
        )

        tk.Button(
            search_frame,
            text="Search",
            command=self.search_password
        ).pack(side="left", padx=5)

        tk.Button(
            search_frame,
            text="Show All",
            command=self.load_passwords
        ).pack(side="left")

        table_frame = tk.Frame(body)

        table_frame.pack(
            fill="both",
            expand=True,
            pady=10
        )

        scrollbar = ttk.Scrollbar(table_frame)

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.tree = ttk.Treeview(
            table_frame,
            yscrollcommand=scrollbar.set,
            columns=(
                "ID",
                "Website",
                "Username",
                "Password",
                "Notes"
            ),
            show="headings"
        )

        scrollbar.config(command=self.tree.yview)

        self.tree.heading("ID", text="ID")
        self.tree.heading("Website", text="Website")
        self.tree.heading("Username", text="Username")
        self.tree.heading("Password", text="Password")
        self.tree.heading("Notes", text="Notes")

        self.tree.column("ID", width=60, anchor="center")
        self.tree.column("Website", width=180)
        self.tree.column("Username", width=180)
        self.tree.column("Password", width=220)
        self.tree.column("Notes", width=250)

        self.tree.pack(
            fill="both",
            expand=True
        )

        self.selected_id = None

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.on_row_selected
        )

        # ==================================================
        # STATUS BAR
        # ==================================================

        self.status_var = tk.StringVar(value="Ready")

        status_bar = tk.Label(
            self,
            textvariable=self.status_var,
            anchor="w",
            relief="sunken",
            bd=1,
            padx=10
        )

        status_bar.pack(
            side="bottom",
            fill="x"
        )

        # ==================================================
        # ENTRY FORM
        # ==================================================

        form = tk.LabelFrame(
            body,
            text="Password Details",
            padx=15,
            pady=15
        )

        form.pack(fill="x", pady=10)

        tk.Label(
            form,
            text="Website"
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.website_entry = tk.Entry(form, width=30)

        self.website_entry.grid(
            row=0,
            column=1,
            padx=5,
            pady=5
        )

        tk.Label(
            form,
            text="Username"
        ).grid(row=0, column=2, padx=5)

        self.username_entry = tk.Entry(form, width=30)

        self.username_entry.grid(
            row=0,
            column=3,
            padx=5,
            pady=5
        )

        tk.Label(
            form,
            text="Password"
        ).grid(row=1, column=0, padx=5)

        self.password_entry = tk.Entry(
            form,
            width=30,
            show="*"
        )

        self.password_entry.grid(
            row=1,
            column=1,
            padx=5,
            pady=5
        )

        self.strength_label = tk.Label(
            form,
            text="Strength: Weak",
            fg="red",
            font=("Segoe UI", 10, "bold")
        )

        self.strength_label.grid(
            row=1,
            column=2,
            sticky="w",
            padx=(15, 0)
        )

        self.password_entry.bind(
            "<KeyRelease>",
            self.update_strength
        )

        tool_frame = tk.Frame(form)

        tool_frame.grid(
            row=2,
            column=1,
            sticky="w",
            pady=5
        )

        self.show_password = False

        tk.Button(
            tool_frame,
            text="Generate",
            command=self.generate_password,
            width=12
        ).pack(side="left", padx=2)

        tk.Button(
            tool_frame,
            text="Show/Hide",
            command=self.toggle_password,
            width=12
        ).pack(side="left", padx=2)

        tk.Button(
            tool_frame,
            text="Copy",
            width=12,
            command=self.copy_password
        ).pack(side="left", padx=2)

        tk.Label(
            form,
            text="Notes"
        ).grid(row=2, column=2, padx=5)

        self.notes_entry = tk.Entry(form, width=30)

        self.notes_entry.grid(
            row=2,
            column=3,
            padx=5,
            pady=5
        )

        self.add_button = tk.Button(
            form,
            text="Add Password",
            width=18,
            command=self.add_password
        )

        self.add_button.grid(
            row=3,
            column=0,
            columnspan=4,
            pady=15
        )

        self.update_button = tk.Button(
            form,
            text="Update",
            width=15,
            command=self.update_password
        )

        self.update_button.grid(
            row=4,
            column=1,
            pady=8
        )

        self.delete_button = tk.Button(
            form,
            text="Delete",
            width=15,
            command=self.delete_password
        )

        self.delete_button.grid(
            row=4,
            column=2,
            pady=8
        )

        self.load_passwords()

        self.bind_all("<Control-n>", lambda e: self.clear_form())

        self.bind_all("<Control-f>", lambda e: self.search_entry.focus())

        self.bind_all("<Escape>", lambda e: self.clear_form())

    # --------------------------------------------------
    # LOAD PASSWORDS
    # --------------------------------------------------

    def load_passwords(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)

            records = self.app.db.get_all_passwords()

            for row in records:
                self.tree.insert("", "end", values=row)

            self.update_status()
        except Exception as error:
            messagebox.showerror(
                "Database Error",
                str(error)
            )
    # --------------------------------------------------
    # ADD PASSWORD
    # --------------------------------------------------

    def add_password(self):

        website = self.website_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        notes = self.notes_entry.get().strip()

        if not website or not username or not password:

            messagebox.showwarning(
                "Missing Data",
                "Website, Username and Password are required."
            )
            return

        success = self.app.db.add_password(
            website,
            username,
            password,
            notes
        )

        if success:

            messagebox.showinfo(
                "Success",
                "Password added successfully."
            )

            self.website_entry.delete(0, tk.END)
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.notes_entry.delete(0, tk.END)

            self.load_passwords()
            self.update_status()

        else:

            messagebox.showerror(
                "Database Error",
                "Unable to save password."
            )
    # --------------------------------------------------
    # SEARCH
    # --------------------------------------------------

    def search_password(self):
        
        keyword = self.search_entry.get().strip()
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)

            rows = self.app.db.search_passwords(keyword)

            for row in rows:
                self.tree.insert("", "end", values=row)

            self.update_status()

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                str(error)
            )
    # --------------------------------------------------
    # TREE SELECTION
    # --------------------------------------------------

    def on_row_selected(self, event):

        selected = self.tree.selection()

        if not selected:
            return

        values = self.tree.item(selected)["values"]

        if not values:
            return

        self.selected_id = values[0]

        self.website_entry.delete(0, tk.END)
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.notes_entry.delete(0, tk.END)

        self.website_entry.insert(0, values[1])
        self.username_entry.insert(0, values[2])
        self.password_entry.insert(0, values[3])
        self.notes_entry.insert(0, values[4])
        # ---------------- Main Area ----------------

        body = tk.Frame(self, bg="#f5f5f5")
        body.pack(fill="both", expand=True, padx=20, pady=20)

        # ==================================================
        # SEARCH BAR
        # ==================================================

        search_frame = tk.Frame(body, bg="#f5f5f5")

        search_frame.pack(fill="x", pady=10)

        tk.Label(
            search_frame,
            text="Search:",
            bg="#f5f5f5",
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")

        self.search_entry = tk.Entry(
            search_frame,
            width=35
        )

        self.search_entry.pack(
            side="left",
            padx=10
        )

        tk.Button(
            search_frame,
            text="Search",
            command=self.search_password
        ).pack(side="left", padx=5)

        tk.Button(
            search_frame,
            text="Show All",
            command=self.load_passwords
        ).pack(side="left")

        table_frame = tk.Frame(body)

        table_frame.pack(
            fill="both",
            expand=True,
            pady=10
        )

        scrollbar = ttk.Scrollbar(table_frame)

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.tree = ttk.Treeview(
            table_frame,
            yscrollcommand=scrollbar.set,
            columns=(
                "ID",
                "Website",
                "Username",
                "Password",
                "Notes"
            ),
            show="headings"
        )

        scrollbar.config(command=self.tree.yview)

        self.tree.heading("ID", text="ID")
        self.tree.heading("Website", text="Website")
        self.tree.heading("Username", text="Username")
        self.tree.heading("Password", text="Password")
        self.tree.heading("Notes", text="Notes")

        self.tree.column("ID", width=60, anchor="center")
        self.tree.column("Website", width=180)
        self.tree.column("Username", width=180)
        self.tree.column("Password", width=220)
        self.tree.column("Notes", width=250)

        self.tree.pack(
            fill="both",
            expand=True
        )

        self.selected_id = None

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.on_row_selected
        )
        # Load records when dashboard opens
        self.load_passwords()

        # ==================================================
        # STATUS BAR
        # ==================================================

        self.status_var = tk.StringVar(value="Ready")

        status_bar = tk.Label(
                self,
                textvariable=self.status_var,
                anchor="w",
                relief="sunken",
                bd=1,
                padx=10
            )

        status_bar.pack(
                side="bottom",
                fill="x"
            )

        self.status_var.set("Ready")

        # ==================================================
        # ENTRY FORM
        # ==================================================

        form = tk.LabelFrame(
                body,
                text="Password Details",
                padx=15,
                pady=15
            )

        form.pack(fill="x", pady=10)

        # Website

        tk.Label(
                form,
                text="Website"
            ).grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.website_entry = tk.Entry(form, width=30)

        self.website_entry.grid(
                row=0,
                column=1,
                padx=5,
                pady=5
            )

        # Username

        tk.Label(
                form,
                text="Username"
            ).grid(row=0, column=2, padx=5)

        self.username_entry = tk.Entry(form, width=30)

        self.username_entry.grid(
                row=0,
                column=3,
                padx=5,
                pady=5
            )

        # Password

        tk.Label(
                form,
                text="Password"
            ).grid(row=1, column=0, padx=5)

        self.password_entry = tk.Entry(
                form,
                width=30,
                show="*"
            )

        self.password_entry.grid(
                row=1,
                column=1,
                padx=5,
                pady=5
            )

        # ==================================================
        # PASSWORD STRENGTH
        # ==================================================

        self.strength_label = tk.Label(
                form,
                text="Strength: Weak",
                fg="red",
                font=("Segoe UI", 10, "bold")
            )

        self.strength_label.grid(
                row=1,
                column=2,
                sticky="w",
                padx=(15, 0)
            )

        self.password_entry.bind(
                "<KeyRelease>",
                self.update_strength
            )

        # ==================================================
        # PASSWORD TOOLS
        # ==================================================

        tool_frame = tk.Frame(form)

        tool_frame.grid(
            row=2,
            column=1,
            sticky="w",
            pady=5
        )

        self.show_password = False

        tk.Button(
            tool_frame,
            text="Generate",
            command=self.generate_password,
            width=12
        ).pack(side="left", padx=2)

        tk.Button(
            tool_frame,
            text="Show/Hide",
            command=self.toggle_password,
            width=12
        ).pack(side="left", padx=2)

        tk.Button(
            tool_frame,
            text="Copy",
            width=12,
            command=self.copy_password
        ).pack(side="left", padx=2)

        # Notes

        tk.Label(
            form,
            text="Notes"
        ).grid(row=1, column=2, padx=5)

        self.notes_entry = tk.Entry(form, width=30)

        self.notes_entry.grid(
            row=1,
            column=3,
            padx=5,
            pady=5
        )

        # Add Button

        self.add_button = tk.Button(
            form,
            text="Add Password",
            width=18,
            command=self.add_password
        )

        self.add_button.grid(
            row=2,
            column=0,
            columnspan=4,
            pady=15
        )
        self.update_button = tk.Button(
            form,
            text="Update",
            width=15,
            command=self.update_password
        )

        self.update_button.grid(
            row=3,
            column=1,
            pady=8
        )

        self.delete_button = tk.Button(
            form,
            text="Delete",
            width=15,
            command=self.delete_password
        )

        self.delete_button.grid(
            row=3,
            column=2,
            pady=8
        )

        welcome = tk.Label(
            self,
            text="Welcome to your Password Manager",
            font=("Segoe UI", 20, "bold"),
            bg="#f5f5f5"
        )

        welcome.pack(pady=(10, 25))

        info = tk.Label(
            self,
            text=(
                "Dashboard initialized successfully.\n\n"
                "The password management features\n"
                "will be added in the next parts."
            ),
            font=("Segoe UI", 12),
            bg="#f5f5f5",
            fg="gray30",
            justify="center"
        )

        info.pack()

        self.status = tk.Label(
            self,
            text="Ready",
            anchor="w",
            bg="#f5f5f5",
            fg="green"
        )

        self.status.pack(side="bottom", fill="x", pady=15)
    # --------------------------------------------------
    # CLEAR FORM
    # --------------------------------------------------

    def clear_form(self):

        self.selected_id = None

        self.website_entry.delete(0, tk.END)

        self.username_entry.delete(0, tk.END)

        self.password_entry.delete(0, tk.END)

        self.notes_entry.delete(0, tk.END)
        self.website_entry.focus()
         # --------------------------------------------------
        # GENERATE PASSWORD
        # --------------------------------------------------
        
    def generate_password(self):
        
        password = PasswordGenerator.generate(16)
        
        self.password_entry.delete(0, tk.END)
        
        self.password_entry.insert(0, password)
        self.update_strength()
        
        # --------------------------------------------------
        # SHOW / HIDE PASSWORD
        # --------------------------------------------------
        
    def toggle_password(self):
        
        if self.show_password:
        
                self.password_entry.config(show="*")
        
                self.show_password = False
        
        else:
        
                self.password_entry.config(show="")
        
                self.show_password = True
                # --------------------------------------------------
        # PASSWORD STRENGTH
        # --------------------------------------------------
        
    def update_strength(self, event=None):
        
        password = self.password_entry.get()
        
        strength = PasswordStrength.check(password)
        
        colors = {
                "Weak": "red",
                "Medium": "orange",
                "Strong": "blue",
                "Very Strong": "green"
            }
        
        self.strength_label.config(
                text=f"Strength: {strength}",
                fg=colors.get(strength, "black")
            )
        
        # --------------------------------------------------
        # COPY PASSWORD
        # --------------------------------------------------
        
    def copy_password(self):
        
        password = self.password_entry.get()
        
        if password == "":
        
                messagebox.showwarning(
                    "Empty Password",
                    "No password available to copy."
                )
        
                return
        
        self.clipboard_clear()
        
        self.clipboard_append(password)
        
        self.update()
        
        messagebox.showinfo(
                "Copied",
                "Password copied to clipboard."
            )
    def logout(self):

        if messagebox.askyesno(
            "Logout",
            "Do you want to logout?"
        ):
            self.app.show_login()
    def update_status(self):
        """Update status bar with record count."""

        try:
            total = len(self.tree.get_children())

            self.status_label.config(
                text=f"Total Records: {total}"
        )

        except Exception:
            pass        
       
    # --------------------------------------------------
    # UPDATE PASSWORD
    # --------------------------------------------------

    def update_password(self):

        if self.selected_id is None:

            messagebox.showwarning(
                "No Selection",
                "Please select a password to update."
            )

            return

        website = self.website_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        notes = self.notes_entry.get().strip()

        if not website or not username or not password:

            messagebox.showwarning(
                "Missing Data",
                "Website, Username and Password are required."
            )

            return

        success = self.app.db.update_password(
            self.selected_id,
            website,
            username,
            password,
            notes
        )

        if success:

            messagebox.showinfo(
                "Success",
                "Password updated successfully."
            )

            self.clear_form()
            self.load_passwords()
            self.update_status()

        else:

            messagebox.showerror(
                "Database Error",
                "Unable to update password."
            )

    # --------------------------------------------------
    # DELETE PASSWORD
    # --------------------------------------------------

    def delete_password(self):

        if self.selected_id is None:

            messagebox.showwarning(
                "No Selection",
                "Please select a password to delete."
            )

            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this password?"
        )

        if not confirm:
            return

        success = self.app.db.delete_password(
            self.selected_id
        )

        if success:

            messagebox.showinfo(
                "Deleted",
                "Password deleted successfully."
            )

            self.clear_form()
            self.load_passwords()
            self.update_status()

        else:

            messagebox.showerror(
                "Database Error",
                "Unable to delete password."
            )
# ==========================================================
# APPLICATION ENTRY
# ==========================================================

def main():
    app = PasswordManagerApp()
    app.mainloop()


if __name__ == "__main__":
    main()               