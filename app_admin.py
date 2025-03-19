"""
Student name(s): Erica Wang, Anna Szczuka, Sreeyutha Ratala
Student email(s): ewang2@caltech.edu, aszczuka@caltech.edu, sratala@caltech.edu

************************************************************************************************************************
The program is a command-line application designed to interact with a MySQL database that stores retail transaction
data. This application allows different types of users (store managers, business owners, economists, and researchers) to
query the data and extract meaningful insights. The database consists of four main tables: Customer, Store, Product, and
Transaction, each containing information relevant to retail analytics.

This application provides various query functionalities that allow users to analyze consumer behavior, such as
determining spending trends by demographic groups, identifying the most common payment methods, and evaluating store
foot traffic. The program also includes an administrative interface where authorized users can insert, update, and
manage the data stored in the database. Additionally, it implements secure database connections and basic error
handling.

The user interacts with the program via a menu-driven interface that allows them to select queries and retrieve data in
meaningful ways.
************************************************************************************************************************
"""

import sys  # to print error messages to sys.stderr
import mysql.connector
# To get error codes from the connector, useful for user-friendly
# error-handling
import mysql.connector.errorcode as errorcode
from tabulate import tabulate
import datetime
from abstracted import check_user_or_pass, print_divider, print_lines, print_section_header

# Debugging flag to print errors when debugging that shouldn't be visible
# to an actual client. ***Set to False when done testing.***
DEBUG = True

# ----------------------------------------------------------------------
# SQL Utility Functions
# # ----------------------------------------------------------------------
        
import getpass  # Secure password input

def get_conn():
     """"
     Returns a connected MySQL connector instance, if connection is successful.
     If unsuccessful, exits.
     """
     try:
         conn = mysql.connector.connect(
           host='localhost',
           user='admin',
           # Find port in MAMP or MySQL Workbench GUI or with
           # SHOW VARIABLES WHERE variable_name LIKE 'port';
           port='3306',  # this may change!
           password='admin_pw', # adminpw
           database='retaildb'
         )
         print('Successfully connected.')
         return conn
     except mysql.connector.Error as err:
         # Remember that this is specific to _database_ users, not
         # application users. So is probably irrelevant to a client in your
         # simulated program. Their user information would be in a users table
         # specific to your database; hence the DEBUG use.
         if err.errno == errorcode.ER_ACCESS_DENIED_ERROR and DEBUG:
             sys.stderr('Incorrect username or password when connecting to DB.')
         elif err.errno == errorcode.ER_BAD_DB_ERROR and DEBUG:
             sys.stderr('Database does not exist.')
         elif DEBUG:
             sys.stderr(err)
         else:
             # A fine catchall client-facing message.
             sys.stderr('An error occurred, please contact the administrator.')
         sys.exit(1)


# ----------------------------------------------------------------------
# Functions for Command-Line Options/Query Execution
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# Admin Functionalities
# ----------------------------------------------------------------------

# Adding transaction changes inventory for all 
def add_new_transaction(conn):
    """
    Allows an admin to add a new transaction manually into the database.
    """
    cursor = conn.cursor()
    print_section_header("Transaction Page")
    print("Adding a New Transaction")

    # Ask the user to input the data for the transaction they want to add. Here are a few examples.
    purchase_id = input("Enter Purchase ID: ").strip()
    try:
        customer_id = int(input("Enter Customer ID: ").strip())
    except ValueError:
        print("Invalid input for Store ID. Please enter a valid number.")
        return
    try:
        store_id = int(input("Enter Store ID: ").strip())
    except ValueError:
        print("Invalid input for Store ID. Please enter a valid number.")
        return
    try:
        product_id = int(input("Enter Product ID: ").strip())
    except ValueError:
        print("Invalid input for Store ID. Please enter a valid number.")
        return
    
    store_location = input("Enter Store Location: ").strip()
    purchased_product_price_usd = input("Enter Product Price: ").strip()

    # We can ensure the data ia of the correct data type as follows. We will force constraints when adding
    # data in this way.
    try:
        discount_percent = int(input("Enter Discount Percentage (0 if none): ").strip())
    except ValueError:
        print("Invalid input for discount percentage. Please enter a valid number.")
        return

    # Here are some more attributes the admin can add data to.
    payment_method = input("Enter Payment Method (Credit, Debit, Cash, etc.): ").strip()
    txn_date = input("Enter Transaction Date (YYYY-MM-DD): ").strip()


     # Get today's date
    current_date = datetime.date.today()

    # Convert txn_date string to a date object
    try:
        txn_date_obj = datetime.datetime.strptime(txn_date, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date format. Please enter the date in YYYY-MM-DD format.")
        return

    # Check if txn_date is today's date or a previous date
    if txn_date_obj > current_date:
        print("Error: Transaction date cannot be in the future.")
        return

    cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM customer WHERE customer_id = %s) AS customer_exists,
                (SELECT COUNT(*) FROM store WHERE store_id = %s) AS store_exists,
                (SELECT COUNT(*) FROM store WHERE store_id = %s AND store_location = %s) AS location_exists,
                (SELECT COUNT(*) FROM inventory WHERE product_id = %s AND store_id = %s) AS product_exists
        """, (customer_id, store_id, store_id, store_location, product_id, store_id))

    customer_exists, store_exists, location_exists, product_exists = cursor.fetchone()

    if not customer_exists:
        print("Error: Customer ID does not exist.")
        return
    if not store_exists:
        print("Error: Store ID does not exist.")
        return
    if not location_exists:
        print("Error: Store Location does not exist.")
        print("Error: Please enter a valid Store Location.")
        return
    if not product_exists:
        print("Error: Product ID does not exist for this store.")
        return

    query = """
            INSERT INTO purchase (purchase_id, product_id, store_id, customer_id, store_location, payment_method, discount_percent, txn_date, purchased_product_price_usd)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
    try:
        cursor.execute(query,
                       (purchase_id, product_id, store_id, customer_id, store_location, payment_method, discount_percent, txn_date, purchased_product_price_usd))
        conn.commit()
        print("Purchase successfully added.")
    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
    finally:
        cursor.close()

def view_store_performance(conn):
    """
    Displays store performance reports including revenue, total transactions,
    and average foot traffic per store.
    """
    cursor = conn.cursor()
    print_section_header("Store Performance Page")

    # Query to display the store performance reports including revenue, total transactions,
    # and average foot traffic per store.
    query = """
        WITH purchase_summary AS (
            SELECT store_id,
                store_location,
                COUNT(*) AS total_transactions,
                SUM(purchased_product_price_usd) AS total_revenue
            FROM purchase
            GROUP BY store_id, store_location
        ),
        popularity_summary AS (
            SELECT store_id,
                store_location,
                AVG(foot_traffic) AS avg_foot_traffic
            FROM popularity
            GROUP BY store_id, store_location
        )
        SELECT s.store_id, 
            s.store_location,
            COALESCE(p.total_transactions, 0) AS total_transactions,
            COALESCE(p.total_revenue, 0)      AS total_revenue,
            COALESCE(pop.avg_foot_traffic, 0) AS avg_foot_traffic
        FROM store s
        LEFT JOIN purchase_summary p 
            ON s.store_id = p.store_id 
            AND s.store_location = p.store_location
        LEFT JOIN popularity_summary pop
            ON s.store_id = pop.store_id
            AND s.store_location = pop.store_location;
    """
    try:
        cursor.execute(query)
        results = cursor.fetchall()

        if not results:
            print("No store performance data available.")
        else:
            headers = ["Store ID", "Location", "Total Transactions", "Total Revenue ($)", "Avg Foot Traffic"]
            table = [list(row) for row in results]

            print("\nStore Performance Report:")
            print(tabulate(table, headers=headers, tablefmt="pretty"))
    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
    finally:
        cursor.close()
        conn.close()

def view_materialized_store_sales(conn):
    """
    View the materialized view of store sales statistics.
    Result shows 10 rows per page. Press N to move onto next page 
    or any other key to quit
    """
    print_section_header("View Page")
    cursor = conn.cursor()
    query = """
        SELECT store_id, total_sales, 
        num_purchases, 
        avg_discount, 
        min_price, max_price
        FROM mv_store_sales_stats;
    """
    try:
        cursor.execute(query)
        results = cursor.fetchall()

        if not results:
            print("No sales data available.")
            return

        headers = ["Store ID", "Total Sales ($)", "Num Purchases", "Avg Discount (%)", "Min Price ($)", "Max Price ($)"]

        page_size = 10 
        total_rows = len(results)
        total_pages = (total_rows + page_size - 1) // page_size 
        start = 0
        page_num = 1

        while start < total_rows:
            end = start + page_size
            table = [list(row) for row in results[start:end]]
            
            print("\nStore Sales Statistics")
            print(tabulate(table, headers=headers, tablefmt="pretty"))

            print(f"\nPage {page_num} of {total_pages}")

            if end >= total_rows:
                break
            
            user_input = input("\nPress 'N' to view next page, or any other key to exit: ").strip().lower()
            if user_input != 'n':
                break

            start += page_size 
            page_num += 1  

    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
    finally:
        cursor.close()

def create_account_admin(conn):
    while True: 
        print_section_header("Create Account")
        cursor = conn.cursor()
        username = input("Enter username: ")
        if not check_user_or_pass(conn, username, "username", 0):
            continue
        password = input("Enter password: ")
        if not check_user_or_pass(conn, password, "password", 0):
            continue
        
        first_name = input("Enter first name: ")
        if first_name == "":
            print("You did not enter a first name. Please try again. ")
            continue
        last_name = input("Enter last name: ")
        if last_name == "":
            print("You did not enter a last name. Please try again. ")
            continue
        employee_type = input("Enter identity (researcher, engineer, or maintenance): ").lower()
        if employee_type == "":
            print("You did not enter an identity. Please try again. ")
            continue
        employee_types = {"researcher", "engineer", "maintenance"}
        if employee_type not in employee_types:
            print("This identity does not exist. Please check your spelling and choose from the options listed. ")
            continue
        
        query = """
            CALL sp_add_user(%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            cursor.execute(query, (username, password, 1, first_name, last_name, None, None, employee_type))
            conn.commit()
            print(f"User account created successfully. ")
            break

        except mysql.connector.Error as err:
            sys.stderr.write(f"Error: {err}\n")
        finally:
            cursor.close()
        
# ----------------------------------------------------------------------
# Functions for Logging Users In
# ----------------------------------------------------------------------
# Note: There's a distinction between database users (admin and client)
# and application users (e.g. members registered to a store). You can
# choose how to implement these depending on whether you have app.py or
# app-client.py vs. app-admin.py (in which case you don't need to
# support any prompt functionality to conditionally login to the sql database)

def login_interface(conn):
    while True:
        cursor = conn.cursor()
        print_section_header("Login Page")
        print("Welcome! Please log in as an administrator.")
        
        username = input("Enter username: ")
        if not check_user_or_pass(conn, username, "username", 1):
            continue
        
        password = input("Enter password: ")
        if not check_user_or_pass(conn, password, "password", 1):
            continue
        
        
        query = """
            SELECT authenticate(%s, %s)
        """
        try:
            cursor.execute(query, (username, password))
            result = cursor.fetchone()
            
            if result and result[0] == 2:
                print("Admin login successful!")
                show_admin_options()
                # return 2  # Admin user
            elif result and result[0] == 1:
                print("You are registered as a client. Please use the client interface.")
                # return 1  # Regular user
            else:
                print("Invalid username or password.")
                continue
                # return 0  # Authentication failed

        except mysql.connector.Error as err:
            sys.stderr.write(f"Error: {err}\n")
        finally:
            cursor.close()
        ans = input("\nPress Enter to try logging in again or type exit to return to the main page: ")
        if ans == "exit":
            break

# ----------------------------------------------------------------------
# Command-Line Functionality
# ----------------------------------------------------------------------

# Another example of where we allow you to choose to support admin vs.
# client features  in the same program, or
# separate the two as different app_client.py and app_admin.py programs
# using the same database.
def show_admin_options():
    """
    Displays options specific for admins, such as adding new data <x>,
    modifying <x> based on a given id, removing <x>, etc.
    """
    # Here are some examples of admin functionalities that would be useful in our application.
    # Updating a customer's information could be a spot for some client admin interaction.
    # There are also specific statistics only admins can view such as store performance reports,
    # as if competitors get access to this information, that might cause issues as that could be private info.
    while True:
        print_section_header("Menu Page")
        print('What would you like to do? ')
        print('  (1) - Add a New Transaction')
        print('  (2) - View Store Specific Performance Reports')
        print('  (3) - View Store Chain Performance Reports')
        print('  (q) - quit')
        print()
        ans = input('Enter an option: ').lower()
        if ans == '1':
            add_new_transaction(conn)
        elif ans == '2':
            view_store_performance(conn)
        elif ans == '3':
            view_materialized_store_sales(conn)
        elif ans == 'q':
            quit_ui()
        else:
            print("Invalid option. Please try again.")
            
        input("\nPress Enter to return to the Admin Menu...")

def quit_ui():
    """
    Quits the program, printing a goodbye message to the user.
    """
    # We can also add some bullet points here to summarize some cool statistics from the data and leave the user off
    # with something interesting about retail data!
    print('Good bye!')
    exit()


def main(conn):
    """
    Main function for starting things up.
    """
    while True:
        print_section_header("Administration Page")
        print("Would you like to: ")
        print("1. Create an account")
        print("2. Login")
        print("3. Exit")
        
        choice = input("Enter your choice (1/2/3): ").strip()
        
        if choice == '1':
            create_account_admin(conn)
        elif choice == '2':
            login_interface(conn)
        elif choice == '3':
            break
        input("\nPress Enter to return to the main menu...")

if __name__ == '__main__':
    # This conn is a global object that other functions can access.
    # You'll need to use cursor = conn.cursor() each time you are
    # about to execute a query with cursor.execute(<sqlquery>)
    conn = get_conn()
    main(conn)
    conn.close()
    