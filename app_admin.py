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
           user='ewang_admin',
           # Find port in MAMP or MySQL Workbench GUI or with
           # SHOW VARIABLES WHERE variable_name LIKE 'port';
           port='3306',  # this may change!
           password='admin3', # adminpw
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


def add_new_transaction(conn):
    """
    Allows an admin to add a new transaction manually into the database.
    """
    cursor = conn.cursor()

    print("\nAdding a New Transaction")

    # Ask the user to input the data for the transaction they want to add. Here are a few examples.
    purchase_id = input("Enter Purchase ID: ").strip()
    customer_id = input("Enter Customer ID: ").strip()
    store_id = input("Enter Store ID: ").strip()
    product_id = input("Enter Product ID: ").strip()

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

    # make sure the referenced entities exist
    cursor.execute("SELECT COUNT(*) FROM customer WHERE customer_id = %s", (customer_id,))
    if cursor.fetchone()[0] == 0:
        print("Error: Customer ID does not exist.")
        return

    cursor.execute("SELECT COUNT(*) FROM store WHERE store_id = %s", (store_id,))
    if cursor.fetchone()[0] == 0:
        print("Error: Store ID does not exist.")
        return

    cursor.execute("SELECT COUNT(*) FROM product WHERE product_id = %s AND store_id = %s", (product_id, store_id))
    if cursor.fetchone()[0] == 0:
        print("Error: Product ID does not exist for this store.")
        return

    query = """
            INSERT INTO purchase (purchase_id, product_id, store_id, customer_id, payment_method, discount_percent, txn_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """

    try:
        cursor.execute(query,
                       (purchase_id, product_id, store_id, customer_id, payment_method, discount_percent, txn_date))
        conn.commit()
        print("Purchase successfully added.")
    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
    finally:
        cursor.close()


def update_customer_info(conn):
    """
    Allows the admin to update a customer's information.
    """
    cursor = conn.cursor()

    customer_id = input("\nEnter Customer ID to update: ").strip()
    updates = []
    params = []

    new_age = input("Enter new age (leave blank to keep current value): ").strip()
    new_gender = input("Enter new gender (M/F/X) (leave blank to keep current value): ").strip()
    new_income = input("Enter new annual income (leave blank to keep current value): ").strip()

    # Here is an example of how we plan to address updates in our table as this is bound to happen
    # for customer retail data.
    if new_age:
        try:
            new_age = int(new_age)
            updates.append("age = %s")
            params.append(new_age)
        except ValueError:
            print("Invalid age format. Please enter a number.")
            return

    if new_gender:
        if new_gender in ['M', 'F', 'X']:
            updates.append("gender = %s")
            params.append(new_gender)
        else:
            print("Invalid gender input. Use 'M', 'F', or 'X'.")
            return

    if new_income:
        try:
            new_income = float(new_income)
            updates.append("annual_income_usd = %s")
            params.append(new_income)
        except ValueError:
            print("Invalid income format. Please enter a number.")
            return

    if not updates:
        print("No changes made.")
        return

    # Construct update query dynamically
    query = f"UPDATE customer SET {', '.join(updates)} WHERE customer_id = %s"
    params.append(customer_id)

    # We will use the parameters and updates to create the SQL query and execute it with the cursor.
    try:
        cursor.execute(query, params)
        conn.commit()
        print("Customer information updated successfully.")
    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
    finally:
        cursor.close()


def delete_transaction_record(conn):
    """
    Allows the admin to delete a transaction record.
    """
    cursor = conn.cursor()

    purchase_id = input("\nEnter the Purchase ID to delete: ").strip()

    try:
        # Check if the purchase exists
        cursor.execute("SELECT COUNT(*) FROM purchase WHERE purchase_id = %s", (purchase_id,))
        if cursor.fetchone()[0] == 0:
            print("Error: Purchase ID does not exist.")
            return

        # Delete the purchase record
        cursor.execute("DELETE FROM purchase WHERE purchase_id = %s", (purchase_id,))
        conn.commit()
        print("Purchase record deleted successfully.")
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
        print("\nStore Performance Report:")
        print("---------------------------------------------------------------")
        print("Store ID | Location | Total Transactions | Total Revenue ($) | Avg Foot Traffic")
        print("---------------------------------------------------------------")
        for row in results:
            print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]:.2f} | {row[4]:.2f}")
        print("---------------------------------------------------------------")
    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
    finally:
        cursor.close()

def delete_client_account(conn):
    """
    Allows the admin to delete a client account
    """
    cursor = conn.cursor()
    
    username = input("\nEnter the username to delete: ").strip()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM user_info WHERE username = %s", (username,))
        result = cursor.fetchone()
        
        if result is None:
            print("Error: User does not exist.")
            return
        
        cursor.execute("SELECT is_admin FROM user_info WHERE username = %s", (username,))
        result = cursor.fetchone()
        
        is_admin = result[0]  # Fetch is_admin value
        print(is_admin)
        if is_admin == 1:
            print("Error: Cannot delete an admin account.")
            return
        
        # Delete the purchase record
        cursor.execute("DELETE FROM user_info WHERE username = %s", (username,))
        conn.commit()
        print("Client account deleted successfully.")
    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
    finally:
        cursor.close()

def create_account_admin(conn):
    cursor = conn.cursor()
    username = input("Enter username: ")
    password = input("Enter password: ")
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    employee_type = input("Enter identity (researcher, engineer, or maintenance): ")
    
    query = """
        CALL sp_add_user(%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    try:
        cursor.execute(query, (username, password, 1, first_name, last_name, None, None, None, employee_type))
        conn.commit()
        check_query = "SELECT username, is_admin FROM user_info WHERE username = %s"
        cursor.execute(check_query, (username,))
        result = cursor.fetchone()

        if result:
            print(f"User '{result[0]}' created successfully with admin status: {result[1]}")
        else:
            print("Failed to create the admin account.")

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
        print("Welcome! Please log in as an administrator.")
        username = input("Enter username: ")
        password = input("Enter password: ")
        
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
                # return 0  # Authentication failed

        except mysql.connector.Error as err:
            sys.stderr.write(f"Error: {err}\n")
        finally:
            cursor.close()
        input("\nPress Enter to try logging in again...")

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
        print('What would you like to do? ')
        print('  (1) - Add a New Transaction')
        print('  (2) - Update a Customer\'s Information')
        print('  (3) - Delete a Transaction Record')
        print('  (4) - View Store Performance Reports')
        print('  (5) - Delete a Client Account')
        print('  (q) - quit')
        print()
        ans = input('Enter an option: ').lower()
        if ans == '1':
            add_new_transaction(conn)
        elif ans == '2':
            update_customer_info(conn)
        elif ans == '3':
            delete_transaction_record(conn)
        elif ans == '4': 
            view_store_performance(conn)
        elif ans == '5':
            delete_client_account(conn)
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
        print("\n=== Administration Page ===")
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
    
