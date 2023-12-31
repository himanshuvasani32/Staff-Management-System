import sys
import sqlite3

from PyQt6.QtCore import QDate, QFile
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, \
    QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QDialog, QGridLayout, QDialogButtonBox, QMessageBox, \
    QDateEdit, QAbstractItemView, QMenuBar, QToolBar, QSizePolicy
from PyQt6.QtGui import QAction, QIcon, QKeySequence


class DatabaseManager:
    def __init__(self):
        self.connection = sqlite3.connect("staff_database.db")
        self.cursor = self.connection.cursor()

        # Create the 'staff' table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS staff (
                id INTEGER PRIMARY KEY,
                name TEXT,
                mobile TEXT,
                email TEXT,
                role TEXT,
                salary REAL,
                joining_date TEXT,
                address TEXT,
                remark TEXT,
                deleted_at TEXT
            )
        ''')
        self.connection.commit()

    def execute(self, query, values=None):
        if values:
            self.cursor.execute(query, values)
        else:
            self.cursor.execute(query)
        self.connection.commit()

    def fetch_all(self, query, values=None):
        if values:
            self.cursor.execute(query, values)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall()

    def close(self):
        self.connection.close()


class StaffManagementApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.db_manager = DatabaseManager()

        # Set up the main window
        self.setWindowTitle("Staff Management System")
        self.setGeometry(100, 100, 1000, 1000)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)


        # Create the Menu bar
        menu_bar = self.menuBar()

        # create file menu
        file_menu = menu_bar.addMenu("File")

        # Create the Toolbar
        toolbar = self.addToolBar("Toolbar")
        toolbar.setMovable(False)

        # Create Add action
        add_action = QAction(QIcon("icons/add.png"),"Add Staff", self)
        add_action.triggered.connect(self.add_staff)
        toolbar.addAction(add_action)
        file_menu.addAction(add_action)

        # Create Edit action
        edit_action = QAction(QIcon("icons/edit.png"), "Edit Staff", self)
        edit_action.triggered.connect(self.edit_staff)
        toolbar.addAction(edit_action)
        file_menu.addAction(edit_action)

        # Create Delete action
        delete_action = QAction(QIcon("icons/delete.png"), "Delete Staff", self)
        delete_action.triggered.connect(self.delete_staff)
        toolbar.addAction(delete_action)
        file_menu.addAction(delete_action)

        # Create Search action
        toolbar.addSeparator()
        search_action = QAction(QIcon("icons/search.png"), "Search Staff", self)
        search_action.triggered.connect(self.search_staff)
        toolbar.addAction(search_action)
        file_menu.addAction(search_action)

        # Setting tooltips and shortcuts for actions
        add_action.setToolTip("Add a new staff member")
        edit_action.setToolTip("Edit staff member details")
        delete_action.setToolTip("Delete selected staff member(s)")
        search_action.setToolTip("Search for staff members")
        add_action.setShortcut(QKeySequence.StandardKey.New)
        edit_action.setShortcut(QKeySequence.StandardKey.Open)
        delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        search_action.setShortcut(QKeySequence.StandardKey.Find)

        self.layout = QVBoxLayout()

        # Create a table to display staff data
        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnCount(9)  # Number of columns
        self.table.setHorizontalHeaderLabels(
            ["ID", "Name", "Mobile", "Email", "Role", "Salary", "Joining Date", "Address", "Remark"])

        # Create a list to store main table data
        self.main_data_list = []

        # Populate the table with staff data from the database
        self.populate_table()

        self.layout.addWidget(self.table)

        # Create buttons and search options
        self.add_button = QPushButton("Add Staff")
        self.edit_button = QPushButton("Edit Staff")
        self.delete_button = QPushButton("Delete Staff")
        self.search_button = QPushButton("Search")

        # Add style to the buttons
        self.apply_button_style(self.add_button)
        self.apply_button_style(self.edit_button)
        self.apply_button_style(self.delete_button)
        self.apply_button_style(self.search_button)

        # Connect button clicks to their respective methods
        self.add_button.clicked.connect(self.add_staff)
        self.edit_button.clicked.connect(self.edit_staff)
        self.delete_button.clicked.connect(self.delete_staff)
        self.search_button.clicked.connect(self.search_staff)

        # Layout for button placment
        button_layout = QGridLayout()
        button_layout.addWidget(self.add_button, 0, 0)
        button_layout.addWidget(self.edit_button, 0, 1)
        button_layout.addWidget(self.delete_button, 0, 2)
        button_layout.addWidget(self.search_button, 0, 3)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        button_layout.addWidget(spacer, 0, 4)

        self.layout.addLayout(button_layout)

        self.central_widget.setLayout(self.layout)

    def apply_button_style(self, button):
        button.setStyleSheet("QPushButton { background-color: #000000; color: white; border-radius: 5px; height: 25px; "
                             "width: 100px; font-weight: bold; }"
                             ":hover { background-color: #ffffff; color: #000000; }")

    def add_staff(self):
        dialog = AddStaffDialog(self.db_manager, self.populate_table)
        if dialog.exec() == QDialog.accepted:
            self.populate_table()  # Update the table after adding

    def edit_staff(self):
        dialog = EditStaffDialog(self.db_manager, self.populate_table)
        if dialog.exec() == QDialog.accepted:
            self.populate_table()  # Update the table after adding

    def delete_staff(self):
        dialog = DeleteStaffDialog(self.db_manager, self.populate_table)
        dialog.exec()

    def search_staff(self):
        dialog = SearchStaffDialog(self.db_manager, self.populate_table, self)
        if dialog.exec() == QDialog.accepted:
            self.populate_table()

    def open_search_dialog(self):
        dialog = SearchStaffDialog(self.db_manager, self.populate_table, self)
        dialog.exec()

    def populate_table(self, data=None, table=None, main_data_list=None):
        """
        Populates the table with provided staff data.
        """
        if table is None:
            table = self.table
            table.setRowCount(0)  # Clear existing rows
        else:
            table.setRowCount(0)  # Clear existing rows

        # Check if specific data is provided, otherwise fetch all staff data from the database
        if data is None:
            data = self.db_manager.fetch_all("SELECT * FROM staff WHERE deleted_at is NULL")
            self.main_data_list = data  # Store main table data

        # Iterate through the data and populate the table rows
        for row_num, (id, name, mobile, email, role, salary, joining_date, address, remark, deleted_at) in enumerate(data):
            self.table.insertRow(row_num)
            self.table.setItem(row_num, 0, QTableWidgetItem(str(id)))
            self.table.setItem(row_num, 1, QTableWidgetItem(name))
            self.table.setItem(row_num, 2, QTableWidgetItem(mobile))
            self.table.setItem(row_num, 3, QTableWidgetItem(email))
            self.table.setItem(row_num, 4, QTableWidgetItem(role))
            self.table.setItem(row_num, 5, QTableWidgetItem(str(salary)))
            self.table.setItem(row_num, 6, QTableWidgetItem(joining_date))
            self.table.setItem(row_num, 7, QTableWidgetItem(address))
            self.table.setItem(row_num, 8, QTableWidgetItem(remark))

            if main_data_list is not None:
                main_data_list.append((id, name, mobile, email, role, salary, joining_date, address, remark))


class AddStaffDialog(QDialog):
    """
       Opens a dialog to add new staff member to the database.
       """
    def __init__(self, db_manager, populate_table_callback):
        super().__init__()

        self.db_manager = db_manager
        self.populate_table = populate_table_callback

        self.setWindowTitle("Add New Staff Details")
        self.setFixedSize(400, 500)

        add_staff_layout = QVBoxLayout()

        self.name_label = QLabel("Name:")
        self.name_input = QLineEdit()

        self.mobile_label = QLabel("Mobile No.:")
        self.mobile_input = QLineEdit()

        self.email_label = QLabel("Email ID:")
        self.email_input = QLineEdit()

        self.role_label = QLabel("Job Role:")
        self.role_input = QLineEdit()

        self.salary_label = QLabel("Salary:")
        self.salary_input = QLineEdit()

        current_date = QDate.currentDate()
        self.joining_date_label = QLabel("Joining Date:")
        self.joining_date_input = QDateEdit(current_date) # Set the current date as the default value
        self.joining_date_input.setMinimumDate(current_date) # Set the minimum date to the current date
        self.joining_date_input.setCalendarPopup(True)

        self.address_label = QLabel("Address:")
        self.address_input = QLineEdit()

        self.remark_label = QLabel("Remark:")
        self.remark_input = QLineEdit()

        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.add_new_staff)

        add_staff_layout.addWidget(self.name_label)
        add_staff_layout.addWidget(self.name_input)
        add_staff_layout.addWidget(self.mobile_label)
        add_staff_layout.addWidget(self.mobile_input)
        add_staff_layout.addWidget(self.email_label)
        add_staff_layout.addWidget(self.email_input)
        add_staff_layout.addWidget(self.role_label)
        add_staff_layout.addWidget(self.role_input)
        add_staff_layout.addWidget(self.salary_label)
        add_staff_layout.addWidget(self.salary_input)
        add_staff_layout.addWidget(self.joining_date_label)
        add_staff_layout.addWidget(self.joining_date_input)
        add_staff_layout.addWidget(self.address_label)
        add_staff_layout.addWidget(self.address_input)
        add_staff_layout.addWidget(self.remark_label)
        add_staff_layout.addWidget(self.remark_input)
        add_staff_layout.addWidget(submit_button)

        self.setLayout(add_staff_layout)

    def validate_mobile(self, mobile_text):
        if not mobile_text.isdigit() or len(mobile_text) != 10:
            return None
        return mobile_text

    def validate_email(self, email_text):
        # Use a basic regular expression for email validation
        import re
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$"
        if not re.match(pattern, email_text):
            return None
        return email_text

    def validate_salary(self, salary_text):
        try:
            salary = float(salary_text)
            if salary <= 0:
                raise ValueError("Salary must be a positive number")
            return salary
        except ValueError:
            return None

    def add_new_staff(self):
        """
        Adds the new staff details to the database and updates the table.
        """
        name = self.name_input.text()
        mobile = self.mobile_input.text()
        email = self.email_input.text()
        role = self.role_input.text()
        salary = self.salary_input.text()
        joining_date = self.joining_date_input.date().toString("dd-MM-yyyy")
        address = self.address_input.text()
        remark = self.remark_input.text()

        # Validate mobile number input
        mobile = self.validate_mobile(self.mobile_input.text())
        if mobile is None:
            # Display an error message to the user
            QMessageBox.critical(self, "Input Error", "Invalid mobile number. Please enter a valid 10-digit number.")
            return

        # Validate email input
        email = self.validate_email(self.email_input.text())
        if email is None:
            # Display an error message to the user
            QMessageBox.critical(self, "Input Error", "Invalid email address. Please enter a valid email address.")
            return

        # Validate salary input
        salary = self.validate_salary(self.salary_input.text())
        if salary is None:
            # Display an error message to the user
            QMessageBox.critical(self, "Input Error", "Invalid salary input. Please enter a valid positive number.")
            return

        self.db_manager.execute(
            "INSERT INTO staff (name, mobile, email, role, salary, joining_date, address, remark, deleted_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL)",
            (name, mobile, email, role, salary, joining_date, address, remark)
        )
        self.db_manager.connection.commit()
        self.populate_table()  # Update the table in the main window
        self.accept()


class EditStaffDialog(QDialog):
    """
    Opens a dialog to edit staff member's details in the database.
    """
    def __init__(self, db_manager, populate_table_callback):
        super().__init__()

        self.db_manager = db_manager
        self.populate_table = populate_table_callback

        # Set the title and fixed size of the dialog
        self.setWindowTitle("Update the Staff Records")
        self.setFixedSize(400, 500)

        # Create a layout for the dialog
        edit_staff_layout = QVBoxLayout()

        # Get the selected row index
        index = window.table.currentRow()

        # Get the selected id
        self.staff_id = window.table.item(index, 0).text()

        # Get the current selected staff name
        selected_name = window.table.item(index, 1).text()
        self.name = QLineEdit(selected_name)
        self.name.setPlaceholderText("Name")
        edit_staff_layout.addWidget(self.name)

        # Get the current selected staff mobile number
        selected_mobile = window.table.item(index, 2).text()
        self.mobile = QLineEdit(selected_mobile)
        self.mobile.setPlaceholderText("Mobile No.")
        edit_staff_layout.addWidget(self.mobile)

        # Get the current selected staff email
        selected_email = window.table.item(index, 3).text()
        self.email = QLineEdit(selected_email)
        self.email.setPlaceholderText("Email ID")
        edit_staff_layout.addWidget(self.email)

        # Get the current selected staff job role
        selected_role = window.table.item(index, 4).text()
        self.role = QLineEdit(selected_role)
        self.role.setPlaceholderText("Job Role")
        edit_staff_layout.addWidget(self.role)

        # Get the current selected staff salary
        selected_salary = window.table.item(index, 5).text()
        self.salary = QLineEdit(selected_salary)
        self.salary.setPlaceholderText("Salary")
        edit_staff_layout.addWidget(self.salary)

        # Get the current selected staff joining date
        selected_joining_date = window.table.item(index, 6).text()
        qdate = QDate.fromString(selected_joining_date, "dd-MM-yyyy")
        self.joining_date = QDateEdit(qdate)
        self.joining_date.setCalendarPopup(True)
        edit_staff_layout.addWidget(self.joining_date)

        # Get the current selected staff address
        selected_address = window.table.item(index, 7).text()
        self.address = QLineEdit(selected_address)
        self.address.setPlaceholderText("Address")
        edit_staff_layout.addWidget(self.address)

        # Get the current selected staff remark
        selected_remark = window.table.item(index, 8).text()
        self.remark = QLineEdit(selected_remark)
        self.remark.setPlaceholderText("Remark")
        edit_staff_layout.addWidget(self.remark)

        # Create an "Update" button and connect it to the update_staff_records method
        update_button = QPushButton("Update")
        update_button.clicked.connect(self.update_staff_records)
        edit_staff_layout.addWidget(update_button)

        # Set the layout for the dialog
        self.setLayout(edit_staff_layout)

    def validate_mobile(self, mobile_text):
        if not mobile_text.isdigit() or len(mobile_text) != 10:
            return None
        return mobile_text

    def validate_email(self, email_text):
        # Use a basic regular expression for email validation
        import re
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$"
        if not re.match(pattern, email_text):
            return None
        return email_text

    def validate_salary(self, salary_text):
        try:
            salary = float(salary_text)
            if salary <= 0:  # Corrected condition here
                raise ValueError("Salary must be a positive number")
            return salary
        except ValueError:
            return None

    def update_staff_records(self):
        """
        Update the staff records in the database.
        """
        # Validate mobile number input
        mobile = self.validate_mobile(self.mobile.text())
        if mobile is None:
            # Display an error message to the user
            QMessageBox.critical(self, "Input Error", "Invalid mobile number. Please enter a valid 10-digit number.")
            return

        # Validate email input
        email = self.validate_email(self.email.text())
        if email is None:
            # Display an error message to the user
            QMessageBox.critical(self, "Input Error", "Invalid email address. Please enter a valid email address.")
            return

        # Validate salary input
        salary = self.validate_salary(self.salary.text())
        if salary is None:
            # Display an error message to the user
            QMessageBox.critical(self, "Input Error", "Invalid salary input. Please enter a valid positive number.")
            return

        self.db_manager.execute(
            "UPDATE staff SET name = ?, mobile = ?, email = ?, role = ?, salary = ?, joining_date = ?, address = ?, "
            "remark = ? Where id = ?",
            (self.name.text(), self.mobile.text(), self.email.text(), self.role.text(), self.salary.text(),
             self.joining_date.date().toString("dd-MM-yyyy"), self.address.text(), self.remark.text(), self.staff_id)
        )
        self.db_manager.connection.commit()
        self.populate_table()
        self.accept()


class DeleteStaffDialog(QDialog):
    def __init__(self, db_manager, main_table_populate_callback):
        super().__init__()

        self.db_manager = db_manager
        self.main_table_populate = main_table_populate_callback

        self.setWindowTitle("Delete Staff Records")
        self.setFixedSize(800, 400)

        delete_staff_layout = QVBoxLayout()

        self.staff_records_table = QTableWidget()
        self.staff_records_table.verticalHeader().setVisible(False)
        self.staff_records_table.setColumnCount(10)  # Number of columns
        self.staff_records_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Mobile", "Email", "Role", "Salary", "Joining Date", "Address", "Remark", "Select"])
        self.staff_records_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.staff_records_table.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.staff_data = self.db_manager.fetch_all("SELECT * FROM staff WHERE deleted_at is NULL")
        self.populate_table(self.staff_data, self.staff_records_table)  # Populate the table with staff data

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No)
        button_box.accepted.connect(self.confirm_deletion)
        button_box.rejected.connect(self.reject)

        delete_staff_layout.addWidget(self.staff_records_table)
        delete_staff_layout.addWidget(button_box)

        self.setLayout(delete_staff_layout)

    def populate_table(self, data, table):
        table.setRowCount(0)  # Clear existing rows

        for row_num, (id, name, mobile, email, role, salary, joining_date, address, remark, deleted_at) in enumerate(data):
            table.insertRow(row_num)
            table.setItem(row_num, 0, QTableWidgetItem(str(id)))
            table.setItem(row_num, 1, QTableWidgetItem(name))
            table.setItem(row_num, 2, QTableWidgetItem(mobile))
            table.setItem(row_num, 3, QTableWidgetItem(email))
            table.setItem(row_num, 4, QTableWidgetItem(role))
            table.setItem(row_num, 5, QTableWidgetItem(str(salary)))
            table.setItem(row_num, 6, QTableWidgetItem(joining_date))
            table.setItem(row_num, 7, QTableWidgetItem(address))
            table.setItem(row_num, 8, QTableWidgetItem(remark))

    def confirm_deletion(self):
        confirmation = QMessageBox.question(self, "Confirmation",
                                            "Are you sure you want to delete the selected staff records?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirmation == QMessageBox.StandardButton.Yes:
            self.delete_selected_staff_records()

    def delete_selected_staff_records(self):
        selected_rows = self.staff_records_table.selectionModel().selectedRows()
        deletion_date = QDate.currentDate().toString("yyyy-MM-dd")

        if not selected_rows:
            return

        selected_ids = []
        for index in selected_rows:
            selected_ids.append(int(self.staff_records_table.item(index.row(), 0).text()))

        if selected_ids:
            for staff_id in selected_ids:
                self.db_manager.execute("UPDATE staff SET deleted_at = ? Where id = ?",
                                        (deletion_date, staff_id))
            self.main_table_populate(self.db_manager.fetch_all("SELECT * FROM staff WHERE deleted_at is NULL"))  # Update main table
            self.accept()


class SearchStaffDialog(QDialog):
    """
    Searches for staff members based on staff name.
    """
    def __init__(self, db_manager, populate_table_callback, parent_window):
        super().__init__(parent=parent_window)

        self.db_manager = db_manager
        self.populate_table = populate_table_callback
        self.parent_window = parent_window

        self.setWindowTitle("Search Staff Name from the Records")
        self.setFixedSize(600, 400)

        search_staff_layout = QVBoxLayout()

        self.name = QLineEdit()
        self.name.setPlaceholderText("Search with Staff Name...")
        self.name.textChanged.connect(self.perform_search)

        self.search_results = QTableWidget()
        self.search_results.verticalHeader().setVisible(False)
        self.search_results.setColumnCount(9)
        self.search_results.setHorizontalHeaderLabels(
            ["ID", "Name", "Mobile", "Email", "Role", "Salary", "Joining Date", "Address", "Remark"])
        self.search_results.setHidden(True)

        self.search_results_main_data = []  # To store main table data corresponding to search results
        self.search_results.cellDoubleClicked.connect(self.search_results_double_clicked)

        clear_button = QPushButton("Clear Results")
        clear_button.clicked.connect(self.clear_search_results)

        search_staff_layout.addWidget(self.name)
        search_staff_layout.addWidget(self.search_results)
        search_staff_layout.addWidget(clear_button)

        self.setLayout(search_staff_layout)

    def perform_search(self, text):
        # Clear previous search results
        self.search_results.setRowCount(0)
        self.search_results_main_data = []

        # Perform real-time search
        searched_name = text.strip()  # Remove leading/trailing whitespace
        if searched_name:
            staff_data = self.db_manager.fetch_all("SELECT * FROM staff WHERE deleted_at is NULL AND "
                                                   "name LIKE ?", (f"%{searched_name}%",))
            self.populate_search_table(staff_data)  # Populate search results table
            self.search_results.setHidden(False)
        else:
            self.search_results.setHidden(True)

    def clear_search_results(self):
        # Clear the search field and results
        self.name.clear()
        self.search_results.setRowCount(0)
        self.search_results.setHidden(True)

    def search_results_double_clicked(self, row, column):
        # When a search result is double-clicked, get the corresponding row data
        selected_row_data = self.search_results_main_data[row]

        # Iterate through the main_data_list to find the matching data
        for idx, row_data in enumerate(self.parent_window.main_data_list):
            if row_data == selected_row_data:
                # Select the corresponding row in the main table
                self.parent_window.table.selectRow(idx)
                break

        # Close the search dialog
        self.accept()

    def populate_search_table(self, data=None):
        """
        Populates the search results table with provided staff data.
        """
        self.search_results.setRowCount(0)  # Clear existing rows

        for row_data in data:
            row_num = self.search_results.rowCount()  # Get the next row index
            self.search_results.insertRow(row_num)

            for col_num, value in enumerate(row_data):
                self.search_results.setItem(row_num, col_num, QTableWidgetItem(str(value)))

            # Store the corresponding row data in the main table for each search result
            self.search_results_main_data.append(row_data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StaffManagementApp()
    window.show()
    sys.exit(app.exec())