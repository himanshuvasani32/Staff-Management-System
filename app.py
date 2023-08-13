import sys
import sqlite3
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, \
    QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QDialog


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
        self.search_label = QLabel("Search by Role:")
        self.search_combo = QComboBox()
        self.search_combo.addItem("All")
        self.search_combo.addItem("Manager")
        self.search_combo.addItem("Employee")
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
        button_layout.addWidget(self.search_label)
        button_layout.addWidget(self.search_combo)
        button_layout.addWidget(self.search_button)

        self.layout.addLayout(button_layout)

        self.central_widget.setLayout(self.layout)

    def add_staff(self):
        dialog = AddStaffDialog(self.db_manager, self.populate_table)
        dialog.exec()


    def edit_staff(self):
        """
        Opens a dialog to edit staff member's details in the database.
        """
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            id = int(self.table.item(selected_row, 0).text())
            name = self.table.item(selected_row, 1).text()
            mobile = self.table.item(selected_row, 2).text()
            email = self.table.item(selected_row, 3).text()
            role = self.table.item(selected_row, 4).text()
            salary = float(self.table.item(selected_row, 5).text())
            joining_date = self.table.item(selected_row, 6).text()
            address = self.table.item(selected_row, 7).text()
            remark = self.table.item(selected_row, 8).text()

            # TODO: Implement logic to open an edit dialog and update staff data
            # Update the staff record in the database using self.db_manager.execute(...)
            pass

    def delete_staff(self):
        """
        Deletes the selected staff member from the database.
        """
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            id = int(self.table.item(selected_row, 0).text())

            # TODO: Implement logic to delete staff record from the database
            # Delete the staff record using self.db_manager.execute(...)
            self.db_manager.execute("DELETE FROM staff WHERE id = ?", (id,))
            self.db_manager.connection.commit()
            self.populate_table()

    def search_staff(self):
        """
        Searches for staff members based on selected role.
        """
        role = self.search_combo.currentText()
        if role == "All":
            self.populate_table()  # Show all staff
        else:
            staff_data = self.db_manager.fetch_all("SELECT * FROM staff WHERE role = ?", (role,))
            self.populate_table(staff_data)

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

        self.add_staff_layout = QVBoxLayout()

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

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.add_new_staff)

        self.add_staff_layout.addWidget(self.name_label)
        self.add_staff_layout.addWidget(self.name_input)
        self.add_staff_layout.addWidget(self.mobile_label)
        self.add_staff_layout.addWidget(self.mobile_input)
        self.add_staff_layout.addWidget(self.email_label)
        self.add_staff_layout.addWidget(self.email_input)
        self.add_staff_layout.addWidget(self.role_label)
        self.add_staff_layout.addWidget(self.role_input)
        self.add_staff_layout.addWidget(self.salary_label)
        self.add_staff_layout.addWidget(self.salary_input)
        self.add_staff_layout.addWidget(self.joining_date_label)
        self.add_staff_layout.addWidget(self.joining_date_input)
        self.add_staff_layout.addWidget(self.address_label)
        self.add_staff_layout.addWidget(self.address_input)
        self.add_staff_layout.addWidget(self.remark_label)
        self.add_staff_layout.addWidget(self.remark_input)
        self.add_staff_layout.addWidget(self.submit_button)

        self.setLayout(self.add_staff_layout)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StaffManagementApp()
    window.show()
    sys.exit(app.exec())