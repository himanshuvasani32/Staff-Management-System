import sys
import sqlite3
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, \
    QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QDialog, QGridLayout, QDialogButtonBox


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
                remark TEXT
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
        self.setGeometry(100, 100, 1000, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        # Create a table to display staff data
        self.table = QTableWidget()
        self.table.setColumnCount(9)  # Number of columns
        self.table.setHorizontalHeaderLabels(
            ["ID", "Name", "Mobile", "Email", "Role", "Salary", "Joining Date", "Address", "Remark"])

        # Populate the table with staff data from the database
        self.populate_table()

        self.layout.addWidget(self.table)

        # Create buttons and search options
        self.add_button = QPushButton("Add Staff")
        self.edit_button = QPushButton("Edit Staff")
        self.delete_button = QPushButton("Delete Staff")
        # self.search_label = QLabel("Search by Role:")
        # self.search_combo = QComboBox()
        # self.search_combo.addItem("All")
        # self.search_combo.addItem("Manager")
        # self.search_combo.addItem("Employee")
        self.search_button = QPushButton("Search")

        # Connect button clicks to their respective methods
        self.add_button.clicked.connect(self.add_staff)
        self.edit_button.clicked.connect(self.edit_staff)
        self.delete_button.clicked.connect(self.delete_staff)
        self.search_button.clicked.connect(self.search_staff)

        # Arrange buttons and search options in a layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        # button_layout.addWidget(self.search_label)
        # button_layout.addWidget(self.search_combo)
        button_layout.addWidget(self.search_button)

        self.layout.addLayout(button_layout)

        self.central_widget.setLayout(self.layout)

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
        if dialog.exec() == QDialog.accepted:
            self.populate_table()  # Update the table after adding

    def search_staff(self):
        dialog = SearchStaffDialog(self.db_manager, self.populate_table)
        if dialog.exec() == QDialog.accepted:
            self.populate_table()

    def populate_table(self, data=None):
        """
        Populates the table with provided staff data.
        """
        self.table.setRowCount(0)  # Clear existing rows

        # Check if specific data is provided, otherwise fetch all staff data from the database
        if data is None:
            data = self.db_manager.fetch_all("SELECT * FROM staff")

        # Iterate through the data and populate the table rows
        for row_num, (id, name, mobile, email, role, salary, joining_date, address, remark) in enumerate(data):
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

        self.joining_date_label = QLabel("Joining Date:")
        self.joining_date_input = QLineEdit()

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

    def add_new_staff(self):
        """
        Adds the new staff details to the database and updates the table.
        """
        name = self.name_input.text()
        mobile = self.mobile_input.text()
        email = self.email_input.text()
        role = self.role_input.text()
        salary = self.salary_input.text()
        joining_date = self.joining_date_input.text()
        address = self.address_input.text()
        remark = self.remark_input.text()

        self.db_manager.execute(
            "INSERT INTO staff (name, mobile, email, role, salary, joining_date, address, remark) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
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
        self.joining_date = QLineEdit(selected_joining_date)
        self.joining_date.setPlaceholderText("Joining Date")
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

    def update_staff_records(self):
        """
        Update the staff records in the database.
        """
        self.db_manager.execute(
            "UPDATE staff SET name = ?, mobile = ?, email = ?, role = ?, salary = ?, joining_date = ?, address = ?, "
            "remark = ? Where id = ?",
            (self.name.text(), self.mobile.text(), self.email.text(), self.role.text(), self.salary.text(),
             self.joining_date.text(), self.address.text(), self.remark.text(), self.staff_id)
        )
        self.db_manager.connection.commit()
        self.populate_table()
        self.accept()


class DeleteStaffDialog(QDialog):
    """
    Deletes the selected staff member from the database.
    """
    def __init__(self, db_manager, populate_table_callback):
        super().__init__()

        self.db_manager = db_manager
        self.populate_table = populate_table_callback

        self.setWindowTitle("Delete Staff Record")

        delete_staff_layout = QGridLayout()

        confirmation_message = QLabel("Are you sure want to delete the selected staff record?")

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No)
        button_box.accepted.connect(self.delete_staff_record)
        button_box.rejected.connect(self.reject)

        delete_staff_layout.addWidget(confirmation_message, 0, 0, 1, 2)
        delete_staff_layout.addWidget(button_box, 1, 0, 1, 2)

        self.setLayout(delete_staff_layout)

    def delete_staff_record(self):
        # Get the current selected index
        index = window.table.currentRow()
        staff_id = window.table.item(index, 0).text()

        # Delete the staff record using self.db_manager.execute
        self.db_manager.execute("DELETE FROM staff WHERE id = ?", (staff_id,))
        self.db_manager.connection.commit()
        self.populate_table()
        self.accept()


class SearchStaffDialog(QDialog):
    """
    Searches for staff members based on staff name.
    """
    def __init__(self, db_manager, populate_table_callback):
        super().__init__()

        self.db_manager = db_manager
        self.populate_table = populate_table_callback

        self.setWindowTitle("Search Staff Name from the Records")
        self.setFixedSize(300, 150)

        search_staff_layout = QVBoxLayout()

        self.name = QLineEdit()
        self.name.setPlaceholderText("Search with Staff Name...")
        search_staff_layout.addWidget(self.name)

        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_staff_records)
        search_staff_layout.addWidget(search_button)

        self.setLayout(search_staff_layout)

    def search_staff_records(self):
        # staff_data = self.db_manager.fetch_all("SELECT * FROM staff WHERE role = ?", (role,))
        # self.populate_table(staff_data)
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StaffManagementApp()
    window.show()
    sys.exit(app.exec())