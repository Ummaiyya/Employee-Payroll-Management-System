import pyodbc
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import date
import sys

db_path = r"C:\Users\Dell\Documents\Employee payroll(draft).accdb"
connection = pyodbc.connect(r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
                          fr"DBQ={db_path};")
cursor = connection.cursor()
print("Connected to Database")
#connected to database
console = Console()
def add_employee():
    print("--Personal Information--")
    while True:
        first_name = input("Enter First Name: ").capitalize().strip()
        if first_name.isalpha():
            break
        else:
            print("Name must only contain letters")
    while True:
        last_name = input("Enter Last Name: ").capitalize().strip()
        if last_name.isalpha():
            break
        else:
            print("Name must only contain letters")
    while True:
        gender = input("Enter Gender (Male/Female) :").capitalize().strip()
        if gender == "Male" or gender == "Female":
            break
        else:
            print("Gender must only contain letters")
    print("--Contact Information--")
    while True:
        phone_number = input("Enter Phone Number: ")
        if phone_number.isnumeric():
            break
        else:
            print("Phone number must only contain digits")
    email = input("Enter Email Address: ")
    print("--Work Information--")
    department = input("Enter Department: ").capitalize()
    designation = input("Enter Designation: ").capitalize()
    while True:
        basic_salary = input("Enter Basic Salary: ")
        if basic_salary.isnumeric():
            break
        else:
            print("Salary must only contain digits")
    join_date = date.today()
    try:
      cursor.execute("INSERT INTO EMPLOYEE(first_name,last_name,gender,phone_number,email,department,designation,basic_salary,join_date) VALUES (?,?,?,?,?,?,?,?,?)",(first_name,last_name,gender,phone_number,email,department,designation,basic_salary,join_date))
      connection.commit()
      cursor.execute("SELECT @@IDENTITY")
      emp_id = cursor.fetchone()[0]
      username = first_name
      password = first_name + "123"
      cursor.execute("""
              INSERT INTO LOGIN (username, password)
              VALUES (?,?)
          """, (username,password))
      connection.commit()
      print(f"Login credentials created -> Username: {username}, Password: {password}")
      print("Employee added successfully!")
    except Exception as e:
      print("Error in Saving Employee Information",e)

def view_all_employees():
    console.print("\n                 === Employee List ===")
    cursor.execute("SELECT first_name, last_name, department, designation, basic_salary FROM EMPLOYEE")
    rows = cursor.fetchall()
    table = Table(show_header=True)
    table.add_column("Name")
    table.add_column("Department")
    table.add_column("Designation")
    table.add_column("Salary")
    for row in rows:
     table.add_row(str(row[0])+" "+str(row[1]), str(row[2]), str(row[3]), str(row[4]))

    console.print(table)

def search_employee():
    name=input("Enter Employee Name: ").capitalize().strip()
    cursor.execute("SELECT first_name, last_name, department, designation, basic_salary FROM EMPLOYEE WHERE first_name = ?",
                   (name,))
    row = cursor.fetchone()
    if row:
        table = Table(show_header=True)
        table.add_column("Name")
        table.add_column("Department")
        table.add_column("Designation")
        table.add_column("Salary")
        table.add_row(str(row[0]) + " " + str(row[1]), str(row[2]), str(row[3]), str(row[4]))
        console.print(table)
    else:
        print("Employee not found")

def delete_employee():
    first_name=input("Enter Employee First Name: ").capitalize().strip()
    last_name=input("Enter Employee Last Name: ").capitalize().strip()
    cursor.execute("SELECT * FROM EMPLOYEE WHERE first_name=? AND last_name=?", (first_name, last_name))
    employee = cursor.fetchone()
    if not employee:
        print(f"No employee found with name: {first_name}{last_name}")
        return
    confirm = input(f"Are you sure you want to delete {first_name}{last_name} and all their data? (y/n): ")
    if confirm.lower() != "y":
        print("Deletion cancelled.")
        return
    deletions = [
        ("EMPLOYEE", "first_name, last_name", (first_name, last_name)),
        ("LOGIN", "username", (first_name,)),
        ("ATTENDANCE", "employee_name", (first_name,last_name)),
        ("PAYROLL", "employee_name", (first_name,last_name))]
    for table, column, values in deletions:
        placeholders = " AND ".join([f"{col.strip()}=?" for col in column.split(",")])
        cursor.execute(f"DELETE FROM {table} WHERE {placeholders}", values)

    connection.commit()
    print(f"All data for employee {first_name}{last_name} has been deleted successfully.")

def mark_attendance():
    cursor.execute("SELECT emp_id, first_name, last_name FROM EMPLOYEE")
    employees = cursor.fetchall()

    for emp in employees:
        emp_id = emp[0]
        first_name = emp[1]
        last_name = emp[2]
        full_name = emp[1] + " " + emp[2]
        status = input(f"Attendance for {full_name} (P/A): ").upper()
        cursor.execute(
            "INSERT INTO ATTENDANCE (emp_id,first_name,last_name, at_date, at_status) VALUES (?,?,?,?,?)",
            (emp_id, first_name, last_name, date.today(), status))
    connection.commit()
    print("Attendance marked for all employees.")

def overtime():
    emp_id = input("Enter Employee ID: ")
    cursor.execute("""SELECT basic_salary, first_name, last_name FROM EMPLOYEE WHERE emp_id = ?""",(emp_id,))
    emp_data = cursor.fetchone()

    if emp_data is None:
        print("Employee not found!")
        return

    basic_salary, first_name, last_name = emp_data
    cursor.execute("""SELECT overtime_rate FROM SETTINGS""")
    data = cursor.fetchone()
    overtime_rate = data[0]

    print(f"Name: {first_name} {last_name}")
    print(f"Basic Salary: {basic_salary}")

    overtime_hours = float(input("Enter overtime hours: "))
    bonus = float(input("Enter bonus (0 if none): "))
    deduction = float(input("Enter deductions (0 if none): "))
    month=input("Enter month (1-12): ")
    year = input("Enter year: ")
    cursor.execute("""INSERT INTO PAYROLL 
        (emp_id, overtime_hours, bonus, deduction, month, year)
        VALUES (?, ?, ?, ?, ?, ?)""", (emp_id, overtime_hours, bonus, deduction, month,year))
    connection.commit()
    print("Payroll saved with date successfully!")

def settings():
    cursor.execute("SELECT tax_rate, fixed_bonus, late_deduction,overtime_rate, working_days_per_month FROM SETTINGS")
    data = cursor.fetchone()
    tax_rate, fixed_bonus, late_deduction,overtime_rate, working_days_per_month = data
    print(f"""
           SETTINGS:
           [1] Tax Rate {tax_rate}
           [2] Fixed Bonus {fixed_bonus}
           [3] Late Deduction {late_deduction}
           [4] Overtime Rate {overtime_rate}
           [5] Working Days per Month {working_days_per_month}
           [0] Logout""")
    while True:
        choice1=input("Would you like to update any setting? (y/n): ")
        if choice1 == "y":
            choice = input("Please choose a setting you would like to update: (1-5) ")
            if choice == 1:
                print(f"Tax Rate {tax_rate}")
                tax_rate = float(input("Enter tax rate: "))
            if choice == 2:
                print(f"Fixed Bonus {fixed_bonus}")
                fixed_bonus = float(input("Enter fixed bonus: "))
            if choice == 3:
                print(f"Late Deduction {late_deduction}")
                late_deduction = float(input("Enter Late Deduction: "))
            if choice == 4:
                print(f"Overtime Rate {overtime_rate}")
                overtime_rate = float(input("Enter overtime rate: "))
            if choice == 5:
                print(f"Working days per month {working_days_per_month}")
                working_days_per_month = float(input("Enter working days per month: "))
            if choice == 0:
                continue
        elif choice1 == "n":
            admin_dashboard()
def admin_dashboard():
    title = (
        "     EMPLOYEE PAYROLL MANAGEMENT SYSTEM    \n"
        "              ADMIN DASHBOARD"
        )

    console.print(Panel(title, expand=False, border_style="blue", padding=(1, 1)))
    print("""
    Main Menu:
    [1] Employee Management
    [2] Attendance Management  
    [3] Payroll Processing
    [4] System Settings
    [0] Logout""")
    choice1 = input("    Enter you choice:")
    if choice1 == "1":
        print(""" EMPLOYEE MANAGEMENT
        [1] Add Employee
        [2] View Employees
        [3] Delete Employee
        [0] Back
              """)
        choice2 = input("    Enter you choice:")
        if choice2 == "1":
            add_employee()
        elif choice2 == "2":
            view_all_employees()
        elif choice2 == "3":
            delete_employee()
        elif choice2 == "0":
            admin_dashboard()
        else:
         print("Invalid Choice")
    elif choice1 == "2":
        print(""" ATTENDANCE MANAGEMENT
                [1] Mark Attendance
                [2] Search Employee
                [0] Back
                      """)
        choice2 = input("    Enter you choice:")
        if choice2 == "1":
            search_employee()
        elif choice2 == "2":
            mark_attendance()
        elif choice2 == "0":
            admin_dashboard()
    elif choice1 == "3":
        print(""" PAYROLL PROCESSING
                [1] Overtime Hours/Bonus/Deduction Entry
                [0] Back """)
        choice2 = input("    Enter you choice:")
        if choice2 == "1":
            overtime()
        elif choice2 == "0":
            admin_dashboard()
    if choice1 == "4":
        print(""" SYSTEM SETTINGS
                        [1] Settings
                        [0] Back """)
        choice2 = input("    Enter you choice:")
        if choice2 == "1":
            settings()
    elif choice1 == "0":
        print("Logging out...")
        connection.close()
        sys.exit()

def profile(username):
    cursor.execute("SELECT emp_id FROM LOGIN WHERE username=?", (username,))
    row= cursor.fetchone()
    emp_id = row[0]
    cursor.execute("""
            SELECT emp_id, first_name, last_name, basic_salary, department, join_date, designation
            FROM EMPLOYEE
            WHERE emp_id=?
        """, (emp_id,))
    data=cursor.fetchone()
    emp_id, first_name, last_name, basic_salary, department, join_date, designation = data

    print(f"Employee ID: {emp_id}")
    print(f"Full Name: {first_name} {last_name}")
    print(f"Department: {department}")
    print(f"Designation: {designation}")
    print(f"Join Date: {join_date}")
    print(f"Basic Salary: {basic_salary}")
    input("Press Enter to go back...")
    employee_dashboard(username)

def att(username):
    cursor.execute("SELECT emp_id FROM LOGIN WHERE username=?", (username,))
    row = cursor.fetchone()
    emp_id = row[0]
    cursor.execute("""SELECT emp_id, first_name, last_name,at_status,at_date FROM ATTENDANCE WHERE emp_id=?""", (emp_id,))
    rows = cursor.fetchall()
    print(f"{'Date':<12} {'Employee':<20} {'Status':<6}")
    print("-" * 40)
    for row in rows:
        emp_id, first_name, last_name, status, at_date = row
        date_str = at_date.strftime("%d-%m-%Y")  # format datetime nicely
        full_name = f"{first_name} {last_name}"
        print(f"{date_str:<12} {full_name:<20} {status:<6}")
    input("Press Enter to go back...")
    employee_dashboard(username)

def final_payroll(username):
    cursor.execute("SELECT emp_id FROM LOGIN WHERE username = ?", (username,))
    row = cursor.fetchone()

    if not row:
        print("User not found.")
        return
    emp_id = row[0]
    cursor.execute("""
        SELECT first_name, last_name, basic_salary 
        FROM EMPLOYEE 
        WHERE emp_id = ?
    """, (emp_id,))
    emp_data = cursor.fetchone()

    if not emp_data:
        print("Employee not found.")
        return

    first_name, last_name, basic_salary = emp_data
    name = first_name + " " + last_name
    month = int(input("Enter month (1-12): "))
    year = int(input("Enter year (e.g. 2025): "))

    cursor.execute("""
        SELECT 
            SUM(bonus) AS total_bonus,
            SUM(deduction) AS total_deduction,
            SUM(overtime_hours) AS total_overtime
        FROM PAYROLL 
        WHERE emp_id = ? AND [month] = ? AND [year] = ?
    """, (emp_id, month, year))

    payroll = cursor.fetchone()

    if payroll is None:
        print(f"No payroll found for {month}-{year}.")
        return

    total_bonus = payroll[0] or 0
    total_deduction = payroll[1] or 0
    total_overtime = payroll[2] or 0
    cursor.execute("SELECT overtime_rate,fixed_bonus,tax_rate FROM SETTINGS")
    setting = cursor.fetchone()
    overtime_rate, fixed_bonus, tax_rate = setting
    overtime_rate = float(overtime_rate)
    fixed_bonus = float(fixed_bonus)
    tax_rate = float(tax_rate)
    overtime_salary = total_overtime * overtime_rate
    gross_salary = basic_salary + total_bonus + fixed_bonus + overtime_salary - total_deduction
    tax_amount = (tax_rate/100) * gross_salary
    net_salary = gross_salary - tax_amount

    cursor.execute("""INSERT INTO FINAL_PAYROLL 
        (emp_id, [month], [year], basic_salary, total_bonus, total_deduction, overtime_salary, tax_amount, net_salary)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
    (emp_id, month, year, basic_salary,
     total_bonus, total_deduction,overtime_salary,tax_amount, net_salary))
    connection.commit()
    print("\n===PAYROLL DONE===")
    print(f"Payroll for {name} - {month}/{year}")
    print(f"Basic Salary       : {basic_salary}")
    print(f"Total Bonus        : {total_bonus}")
    print(f"Fixed Bonus        : {fixed_bonus}")
    print(f"Total Deductions   : {total_deduction}")
    print(f"Overtime Hours     : {total_overtime}")
    print(f"Overtime Pay       : {overtime_salary}")
    print(f"Tax Amount         : {tax_amount}")
    print(f"Net Salary         : {net_salary}")
    input("Press Enter to go back...")
    employee_dashboard(username)
def employee_dashboard(username):
    title = (
        "     EMPLOYEE PAYROLL MANAGEMENT SYSTEM    \n"
        "              EMPLOYEE DASHBOARD"
    )
    console.print(Panel(title, expand=False, border_style="blue", padding=(1, 1)))
    print("""
        Main Menu:
        [1] View Profile
        [2] View Attendance 
        [3] View Payroll 
        [0] Logout""")
    choice = input("        Enter you choice:")
    if choice == "1":
        profile(username)
    elif choice == "2":
        att(username)
    elif choice == "3":
        final_payroll(username)
    elif choice == "0":
        print("Logging out...")
        connection.close()
        sys.exit()
    else:
        print("Employee not found")

def login_dashboard():
 while True:
    text = "LOGIN"
    width = 50
    print("═" * width)
    print(text.center(width))
    print("═" * width)
    username = input("Username: ")
    password = input("Password: ")
    cursor.execute("SELECT * FROM LOGIN WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()
    if result:
        if username == "admin" and password == "admin123":
            admin_dashboard()
        elif username == result[2] and password == result[3]:
            employee_dashboard(username)
    else:
        print("Invalid username or password.")
        continue

login_dashboard()