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

import sys 
import mysql.connector
import mysql.connector.errorcode as errorcode
from tabulate import tabulate
import datetime
from abstracted import check_user_or_pass, print_section_header

DEBUG = True

# ----------------------------------------------------------------------
# SQL Utility Functions
# # ----------------------------------------------------------------------
        
import getpass

def get_conn():
     """"
     Returns a connected MySQL connector instance, if connection is successful.
     If unsuccessful, exits.
     """
     try:
         conn = mysql.connector.connect(
           host='localhost',
           user='admin',
           port='3306',  
           password='admin_pw', 
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

def get_store_chain_admin(conn, store_id):
    """
    Given a store_id, retrieves the corresponding store chain name
    """
    cursor = conn.cursor()
    cursor.execute("SELECT store_id_to_store_chain(%s);", (store_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

# ----------------------------------------------------------------------
# Admin Functionalities
# ----------------------------------------------------------------------

# Adding transaction changes inventory for all 
        
def get_next_purchase_id(conn):
    """
    Retrieves the next available purchase ID by finding the highest purchase_id
    in the purchase table and incrementing it.
    """
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT MAX(CAST(purchase_id AS UNSIGNED)) "
                       "FROM purchase;")  
        result = cursor.fetchone()

        # If there are no purchases in the database, start from 1
        next_purchase_id = (int(result[0]) + 1) if result[0] is not None else 1
        return next_purchase_id

    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
        return None  

    finally:
        cursor.close()

def get_next_customer_id(conn):
    """
    Retrieves available customer ID by finding the highest customer ID
    """
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT MAX(customer_id) FROM purchase;")  
        result = cursor.fetchone()

        return result[0]

    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
        return None  

    finally:
        cursor.close()


def view_possible_purchases(conn):
    """
    Displays under what conditions an admin can insert 
    """
    cursor = conn.cursor()

    # Query to display existing products, stores, and store locations
    query = """
        SELECT product_id, store_id, store_location FROM purchase;
    """
    try:
        cursor.execute(query)
        results = cursor.fetchall()

        if not results:
            print("No available stores at the moment.")
        else:
            headers = ["Product ID", "Store ID", "Store Location"]
            page_size = 10 
            total_rows = len(results)
            total_pages = (total_rows + page_size - 1) // page_size 
            start = 0
            page_num = 1

            while start < total_rows:
                end = start + page_size
                table = [list(row) for row in results[start:end]]
                print_section_header("Store Performance Page")
                
                print("You are viewing possible product, store, "
                      "and store location input: ")
                print(tabulate(table, headers=headers, tablefmt="pretty"))

                print(f"\nPage {page_num} of {total_pages}")

                if end >= total_rows:
                    break
                
                user_input = input("\nPress 'N' to view next page, or any "
                                   "other key to exit: ").strip().lower()
                if user_input != 'n':
                    break

                start += page_size 
                page_num += 1  
    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
    finally:
        cursor.close()


def check_input_validity(conn, user_input, input_type):
    cursor = conn.cursor()
    
    if not user_input.isdigit():
        print(f"Invalid input for {input_type}. Please enter a valid number.")
        return 0
    
    user_input = int(user_input)
    if input_type == "customer_id":
        cursor.execute("SELECT COUNT(*) FROM customer WHERE "
                       "customer_id = %s", (user_input,))
        exists = cursor.fetchone()[0]
        if not exists:
            print(f"Customer ID {user_input} does not exist. "
                  "Please enter a valid ID.")
            return 0
    
    if input_type == "store_id":
        cursor.execute("SELECT COUNT(*) FROM store WHERE "
                       "store_id = %s", (user_input,))
        exists = cursor.fetchone()[0]
        if not exists:
            print(f"Store ID {user_input} does not exist. "
                  "Please enter a valid ID.")
            return 0
    
    if input_type == "purchase_id":
        if user_input >= 10**7:  # Ensures the number is less than 7 digits
            print("Purchase ID must be less than 7 digits.")
            return 0
        cursor.execute("SELECT COUNT(*) FROM purchase WHERE "
                       "purchase_id = %s", (user_input,))
        exists = cursor.fetchone()[0]
        if exists:
            print(f"Purchase ID {user_input} is already taken. "
                  "Please try again. ")
            return 0
        
    if input_type == "product_id":
        if user_input >= 10**7:  # Ensures the number is less than 7 digits
            print("Product ID must be less than 7 digits.")
            return 0
        
    if input_type == "purchased_product_price_usd":
        if user_input >= 100000 or user_input < 0:  
            print("Error: Value must be a numeric amount of type (6, 2).")
            return 0
        
    if input_type == "discount_percent":
        if user_input > 100:
            print("Discount Percent can not be greater than 100%")
            return 0
    return 1
        
def get_input_transaction(conn):
    cursor = conn.cursor()
    # 2 indicates successful inputs, 1 indicates stop transaction, 
    # 0 indicates restart inputs
    flag = 2
    
    while True:
        purchase_id = input("Enter Purchase ID (or r to restart "
                            "inputs and q to stop transaction): ").strip()
        if purchase_id.lower() == "r":
            print("Restarting transaction...\n")
            return (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        if purchase_id.lower() == "q":
            print("Quitting transaction...\n")
            return (1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        if check_input_validity(conn, purchase_id, "purchase_id"):
            break
            
    while True:
        customer_id = input("Enter Customer ID (or r to restart "
                            "inputs and q to stop transaction): ").strip()
        if customer_id.lower() == "r":
            print("Restarting transaction...\n")
            return (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        if customer_id.lower() == "q":
            print("Quitting transaction...\n")
            return (1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        if check_input_validity(conn, customer_id, "customer_id"):
            break
    
    while True:
        store_id = input("Enter Store ID (or r to restart inputs "
                         "and q to stop transaction): ").strip()
        if store_id.lower() == "r":
            print("Restarting transaction...\n")
            return (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        if store_id.lower() == "q":
            print("Quitting transaction...\n")
            return (1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        if check_input_validity(conn, store_id, "store_id"):
            break
        
    while True:
        store_location = input("Enter Store Location (or r to restart "
                               "inputs and q to stop transaction): ").strip()
        if store_location.lower() == "r":
            print("Restarting transaction...\n")
            return (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        if store_location.lower() == "q":
            print("Quitting transaction...\n")
            return (1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        cursor.execute(
            "SELECT COUNT(*) FROM store WHERE store_id = %s AND "
            "store_location = %s",
            (store_id, store_location),
        )
        exists = cursor.fetchone()[0]
        if not exists:
            print(f"Store ID {store_id} does not have a location at "
                  f"'{store_location}'. Please enter a valid store location. ")
            continue
        break
    
    while True: 
        product_id = input("Enter Product ID (or r to restart inputs "
                           "and q to stop transaction): ").strip()
        if product_id.lower() == "r":
            print("Restarting transaction...\n")
            return (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        if product_id.lower() == "q":
            print("Quitting transaction...\n")
            return (1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        if not check_input_validity(conn, product_id, "product_id"):
            continue
        
        cursor.execute("""
            SELECT COUNT(*)
            FROM inventory i
            WHERE i.product_id = %s 
            AND i.store_id = %s 
            AND i.store_location = %s
        """, (product_id, store_id, store_location))

        product_exists = cursor.fetchone()[0]
        if not product_exists:
            print(f" Product ID does not exist for this store at this "
                  "location. Please choose a product that is sold at "
                  f"{store_id} ({get_store_chain_admin(conn, store_id)}), "
                  f"{store_location}")
            continue
        break
    
    while True: 
        purchased_product_price_usd = input("Enter Product Price: ").strip()
        if check_input_validity(conn, purchased_product_price_usd, 
                                "purchased_product_price_usd"):
            break

    # We can ensure the data ia of the correct data type as follows. We will 
    # force constraints when adding data in this way.
    while True:
        discount_percent = input("Enter Discount Percentage "
                                 "(0 if none): ").strip()
        if check_input_validity(conn, discount_percent, "discount_percent"):
            break

    # Here are some more attributes the admin can add data to.
    payment_methods = {"Credit Card", "Debit Card", "Cash"}
    while True:
        payment_method = input("Enter Payment Method (Credit Card, "
                               "Debit Card, Cash): ").strip()
        if payment_method not in payment_methods:
            print("Invalid payment method. Please check spelling and"
                  "capitalization. ")
            continue
        break
        
    while True:
        txn_date = input("Enter Transaction Date (YYYY-MM-DD): ").strip()

        current_date = datetime.date.today()
        # Convert txn_date string to a date object
        try:
            txn_date_obj = datetime.datetime.strptime(txn_date, 
                                                      "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Please enter the date in "
                  "YYYY-MM-DD format.")
            continue

        # Check if txn_date is today's date or a previous date
        if txn_date_obj > current_date:
            print("Transaction date cannot be in the future. "
                  "Please try again. ")
            continue
        break
    return (flag, purchase_id, product_id, store_id, customer_id, 
            store_location, payment_method, discount_percent, 
            txn_date, purchased_product_price_usd)

def add_new_transaction(conn):
    """
    Allows an admin to add a new transaction manually into the database.
    """
    while True: 
        cursor = conn.cursor()
        print_section_header("Purchase Page")
        print("Adding a New Purchase.")
        print("\n1) This must be at an existing store by an existing customer.")
        print("\n2) The product must be sold at said store.")
        print(f"\n3) The next available purchase ID is "
              f"{get_next_purchase_id(conn)}")
        print(f"\n4) The available customer IDs are 1 - "
              f"{get_next_customer_id(conn)}\n")

        see = input("To see possible store, store location, product combos "
                    "enter y. Else enter any key.\n").strip().lower()
        if see == "y":
            view_possible_purchases(conn)
        
        (flag, purchase_id, product_id, store_id, customer_id, store_location,
            payment_method, discount_percent, txn_date, 
            purchased_product_price_usd) = get_input_transaction(conn)
        if flag == 0:
            # restart inputs
            continue
        if flag == 1:
            # quit transaction
            break
        
        query = """
                INSERT INTO purchase 
                    (purchase_id, product_id, store_id, customer_id, 
                     store_location, payment_method, discount_percent, 
                    txn_date, purchased_product_price_usd)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
        try:
            cursor.execute(query,
                        (purchase_id, product_id, store_id, customer_id, 
                         store_location, payment_method, discount_percent, 
                         txn_date, purchased_product_price_usd))
            conn.commit()
            print("Purchase successfully added.")
            break
        except mysql.connector.Error as err:
            sys.stderr.write(f"Error: {err}\n")
            continue
        finally:
            cursor.close()

def view_store_performance(conn):
    """
    Displays store performance reports including revenue, total transactions,
    and average foot traffic per store.
    """
    cursor = conn.cursor()

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
            headers = ["Store ID", "Location", "Total Transactions", 
                       "Total Revenue ($)", "Avg Foot Traffic"]
            page_size = 10 
            total_rows = len(results)
            total_pages = (total_rows + page_size - 1) // page_size 
            start = 0
            page_num = 1

            while start < total_rows:
                end = start + page_size
                table = [list(row) for row in results[start:end]]
                print_section_header("Store Performance Page")
                
                print("You are viewing the store performance report:")
                print(tabulate(table, headers=headers, tablefmt="pretty"))

                print(f"\nPage {page_num} of {total_pages}")

                if end >= total_rows:
                    break
                
                user_input = input("\nPress 'N' to view next page, or any "
                                   "other key to exit: ").strip().lower()
                if user_input != 'n':
                    break

                start += page_size 
                page_num += 1  
    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
    finally:
        cursor.close()

def view_materialized_store_sales(conn):
    """
    View the materialized view of store sales statistics.
    Result shows 10 rows per page. Press N to move onto next page 
    or any other key to quit
    """
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

        headers = ["Store ID", "Total Sales ($)", "Num Purchases", 
                   "Avg Discount (%)", "Min Price ($)", "Max Price ($)"]

        page_size = 10 
        total_rows = len(results)
        total_pages = (total_rows + page_size - 1) // page_size 
        start = 0
        page_num = 1

        while start < total_rows:
            end = start + page_size
            print_section_header("View Page")
            table = [list(row) for row in results[start:end]]
            
            print("\nStore Sales Statistics")
            print(tabulate(table, headers=headers, tablefmt="pretty"))

            print(f"\nPage {page_num} of {total_pages}")

            if end >= total_rows:
                break
            
            user_input = input("\nPress 'N' to view next page, or any "
                               "other key to exit: ").strip().lower()
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
            user_response = input("Type b to go back to main menu. Else "
                                  "type any key to retry \n").strip().lower()
            if user_response == "b":
                break
            continue
        password = input("Enter password: ")
        if not check_user_or_pass(conn, password, "password", 0):
            user_response = input("Type b to go back to main menu. Else "
                                  "type any key to retry \n").strip().lower()
            if user_response == "b":
                break
            continue
        
        first_name = input("Enter first name: ")
        if first_name == "":
            print("You did not enter a first name. Please try again. ")
            continue
        last_name = input("Enter last name: ")
        if last_name == "":
            print("You did not enter a last name. Please try again. ")
            continue
        employee_type = input("Enter identity (researcher, engineer, "
                              "or maintenance): ").lower()
        if employee_type == "":
            print("You did not enter an identity. Please try again. ")
            continue
        employee_types = {"researcher", "engineer", "maintenance"}
        if employee_type not in employee_types:
            print("This identity does not exist. Please check your "
                  "spelling and choose from the options listed. ")
            continue
        
        query = """
            CALL sp_add_user(%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            cursor.execute(query, (username, password, 1, first_name, 
                                   last_name, None, None, employee_type))
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
            user_response = input("Type b to go back to main menu. Else "
                                  "type any key to retry \n").strip().lower()
            if user_response == "b":
                break
            continue
        
        password = input("Enter password: ")
        if not check_user_or_pass(conn, password, "password", 1):
            user_response = input("Type b to go back to main menu. Else "
                                  "type any key to retry \n").strip().lower()
            if user_response == "b":
                break
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
                print("You are registered as a client. "
                      "Please use the client interface.")
                # return 1  # Regular user
            else:
                print("Invalid username or password.")
                continue
                # return 0  # Authentication failed

        except mysql.connector.Error as err:
            sys.stderr.write(f"Error: {err}\n")
        finally:
            cursor.close()
        ans = input("\nPress Enter to try logging in again or "
                    "type exit to return to the main page: ")
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
    # Here are some examples of admin functionalities that would be 
    # useful in our application.
    # Updating a customer's information could be a spot for some client 
    # admin interaction.
    # There are also specific statistics only admins can view such as 
    # store performance reports, as if competitors get access to this 
    # information, that might cause issues as that could be private info.
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
    
