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
import re
from abstracted import check_user_or_pass, print_divider, print_lines, print_section_header


# Debugging flag to print errors when debugging that shouldn't be visible
# to an actual client. ***Set to False when done testing.***
DEBUG = True

# ----------------------------------------------------------------------
# SQL Utility Functions
# # ----------------------------------------------------------------------
        
import getpass  # Secure password input

# conn = get_conn()  # Call function to log in dynamically
def get_conn():
     """"
     Returns a connected MySQL connector instance, if connection is successful.
     If unsuccessful, exits.
     """
     try:
         conn = mysql.connector.connect(
           host='localhost',
           user='client',
           # Find port in MAMP or MySQL Workbench GUI or with
           # SHOW VARIABLES WHERE variable_name LIKE 'port';
           port='3306',  # this may change!
           password='client_pw', # adminpw
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

def transition(conn, type_stats):
    while True:
        print_section_header("Transition Page")
        print("We hope you had a great analysis!")
        print("\n What would you like to do now? ")
        print(f"  (a) - Continue analyzing {type_stats} statistics")
        print("  (b) - Go back to main page")
        print("  (c) - Quit")
        
        ans = input("Enter an option: ").lower()
        if ans == 'a':
            if type_stats == "age":
                get_age_stats(conn)
            elif type_stats == "gender":
                get_gender_stats(conn)
            else:
                get_store_stats(conn)
        elif ans == 'b':
            show_client_options(conn)
        elif ans == 'c':
            quit_ui()
        else:
            print("Invalid option. Please try again. ")
        # input("\nPress Enter to return to the Client Menu...")
        

def most_popular_payment_method(conn):
    """
    Finds the most commonly used payment method for each store.
    """
    cursor = conn.cursor()
    print_section_header("Store Analysis Page")
    print("Welcome!You are viewing the most popular payment methods per store. ")
    query = """
        SELECT p.store_id, 
            p.store_location, 
            p.payment_method, 
            COUNT(*) AS usage_count
        FROM purchase p
        GROUP BY p.store_id, p.store_location, p.payment_method
        ORDER BY p.store_id, p.store_location, usage_count DESC;
    """
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        if results:
            headers = ["Store ID", "Store Location", "Payment Method", "Usage Count"]
            print("\nMost Popular Payment Methods Per Store:")
            print(tabulate(results, headers=headers, tablefmt="pretty"))  # Clean and formatted output
        else:
            print("\nNo results found.\n")
    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
    finally:
        cursor.close()

def get_total_purchases_per_age_group(conn):
    cursor = conn.cursor()
    print_section_header("Age Analysis Page")
    print("Welcome! You are viewing the total number of purchases by age group.")

    query = """
            SELECT
                age_range,
                SUM(total_sales) AS total_sales
            FROM sales_summary_by_age_group
            GROUP BY age_range
            ORDER BY total_sales DESC;
            """
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        if results:
            headers = ["Age Group", "Total Purchases"]
            print("\n" + tabulate(results, headers=headers, tablefmt="grid") + "\n")
        else:
            print("\nNo results found.\n")
    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
    finally:
        cursor.close()
        
def get_age_stats(conn):
    """
    Displays a table of retail statistics grouped by age.
    After viewing the table, the user can ask further questions related to age or gender statistics.
    """
    while True:
        print_section_header("Age Menu")
        print("Welcome! You are analyzing age statisicts! ")
        print("\nChoose the type of age analysis you want to perform:")
        print("  (a) - Get minimum and maximum age groups for each product category")
        print("  (b) - Get most popular store chain among age groups based on number of total purchases")
        print("  (c) - Compare purchase of wants versus needs among age groups")
        print("  (d) - Get total purchases based on age group")
        print("  (e) - Return to menu page")
        print("  (f) - Quit")
        
        ans = input("Enter an option: ").lower()
        if ans == 'a':
            get_min_max_buyers_per_product(conn)
            transition(conn, "age")
        elif ans == 'b':
            get_most_popular_store_chains_per_age_group(conn)
            transition(conn, "age")
        elif ans == 'c':
            get_wants_versus_needs_per_age_group(conn)
            transition(conn, "age")
        elif ans == 'd':
            get_total_purchases_per_age_group(conn)
            transition(conn, "age")
        elif ans == 'e':
            show_client_options(conn)
        elif ans == 'f':
            quit_ui()
        else:
            print("Invalid option. Please try again. ")
        # input("\nPress Enter to return to the Client Menu...")
            
        # print("Get most store chain where most items were purchased based on age group: ")

def get_total_avg_per_gender(conn):
    cursor = conn.cursor()
    print_section_header("Gender Analysis Page")
    print("Welcome! You are viewing the total number of purchases and average purchase price by gender.")
    query = """
                SELECT c.gender, 
                        COUNT(p.purchase_id) AS total_purchases,
                        AVG(p.purchased_product_price_usd) AS avg_spent_per_transaction
                FROM customer c
                JOIN purchase p 
                    ON c.customer_id = p.customer_id
                GROUP BY c.gender;
            """
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        print("\nRetail Statistics by Gender:")
        if results:
            headers = ["Gender", "Total Purchases", "Avg Spent Per Transaction ($)"]
            print("\n" + tabulate(results, headers=headers, tablefmt="pretty")) 
        else:
            print("\nNo results found.\n")

    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
    finally:
        cursor.close()
            
def get_gender_stats(conn):
    """
    Displays statistics based on gender, showing how different genders shop.
    """
    while True:
        print_section_header("Gender Menu")
        cursor = conn.cursor()
        print("Welcome! You are analyzing gender statistics! ")
        print("\nChoose the type of gender analysis you want to perform:")
        print("  (a) - Get total purchases and avg purchase price for each gender")
        print("  (b) - Get gender statistics based on product category")
        print("  (c) - Return to menu page")
        print("  (d) - Quit")
        
        ans = input("Enter an option: ").lower()
        if ans == 'a':
            get_total_avg_per_gender(conn)
            transition(conn, "gender")
        elif ans == 'b':
            while True:
                product_categories = {"Clothing", "Groceries", "Health & Beauty", "Home & Kitchen", "Books", "Electronics"}
                print("\nProduct categories are: Clothing, Groceries, Health & Beauty, Home & Kitchen, Books, and Electronics")
                product_category = input("What product category are you interested in? ")
                if product_category not in product_categories:
                    print("Invalid product category. Please check your spelling and ensure it is a valid listed category. ")
                    continue
                get_more_gender_analysis(conn, product_category)
                transition(conn, "gender")
                break
        elif ans == 'c':
            show_client_options(conn)
        elif ans == 'd':
            quit_ui()
        else:
            print("Invalid option. Please try again. ")
        # input("\nPress Enter to return to the Client Menu...")

        
def get_many_stats_per_store(conn):
    cursor = conn.cursor()
    print_section_header("Store Analysis Page")
    print("Welcome! You are viewing retail statistics by store, including total transactions, total revenue, and average foot traffic.")
    query = """
            WITH purchase_summary AS (
                SELECT store_id,
                    store_location,
                    COUNT(*) AS total_transactions,
                    SUM(purchased_product_price_usd) AS total_revenue
                FROM purchase
                GROUP BY store_id, store_location
            ),
            -- 2) Average foot traffic per store.
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
        if results:
            headers = ["Store ID", "Store Location", "Total Purchases", "Total Revenue ($)", "Avg Foot Traffic"]
            print("\nRetail Statistics by Store:")
            print(tabulate(results, headers=headers, tablefmt="pretty"))  # Structured table format
        else:
            print("\nNo results found.\n")

    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
    finally:
        cursor.close()
                
def get_store_stats(conn):
    """
    Displays statistics based on stores, beneficial for store manager clients.
    """
    while True:
        print_section_header("Store Menu")
        cursor = conn.cursor()
        print("Welcome! You are analyzing store statisicts! ")
        print("\nChoose the type of store analysis you want to perform:")
        print("  (a) - Get the most popular payment method for each store")
        print("  (b) - General revenue statistics, including total transactions, total revenue, and average foot traffic. ")
        print("  (c) - Get store statistics based on store_id")
        print("  (d) - Return to menu page")
        print("  (e) - Quit")
      
        ans = input("Enter an option: ").lower()
        if ans == 'a':
            print("\nFetching the most popular payment method...\n")
            most_popular_payment_method(conn)
            transition(conn, "store")
        elif ans == 'b':
            get_many_stats_per_store(conn)
            transition(conn, "store")
        elif ans == 'c':
            while True: 
                print("Analyzing Store Statistics")
                print("Get store stats based on store id and location: ")
                store_id = input("What store id are you interested in? ")
                
                if not store_id.isdigit():
                    print("Invalid input. Store ID must be a number. Please try again. ")
                    continue
                
                store_id = int(store_id)

                if store_id < 1 or store_id > 999999: 
                    print("Invalid store ID. It must be between 1 and 999999. Please try again. ")
                    continue
                try:
                    cursor.execute("SELECT store_count(%s);", (store_id,))
                    store_count_result = cursor.fetchone()
                    num_open_stores = store_count_result[0] if store_count_result else 0
                    
                    if num_open_stores == 0:
                        print(f"Store ID: {store_id} is not in the database.")
                        continue
                except mysql.connector.Error as err:
                    sys.stderr.write(f"Error: {err}\n")
        
                get_specific_store_analysis(conn, store_id)
                transition(conn, "store")
                break
        elif ans == 'd':
            show_client_options(conn)
        elif ans == 'e':
            quit_ui()
        else:
            print("Invalid option. Please try again. ")

            
def get_more_gender_analysis(conn, product_category):
    """
    Counts the number of male, female, and non-binary customers who purchased Health and Beauty products.
    """
    cursor = conn.cursor()
    print_section_header("Gender Analysis Page")
    print(f"Welcome! You are viewing the total purchase count for each gender for the product category {product_category}. ")
    query = """
        SELECT c.gender, 
            COUNT(*) AS purchase_count
        FROM customer c
        JOIN purchase p 
            ON c.customer_id = p.customer_id
        JOIN product pr 
            ON p.product_id = pr.product_id
        WHERE pr.product_category = %s
        GROUP BY c.gender;
    """
    try:
        cursor.execute(query, (product_category,))
        results = cursor.fetchall()
        if not results:
            print(f"\nError: No purchases found for the product category '{product_category}'.")
            print("Please check the spelling or try a different category.")
            return

        headers = ["Gender", "Purchase Count"]
        print(f"\n{product_category} Product Purchases by Gender:")
        print(tabulate(results, headers=headers, tablefmt="pretty"))
    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
    finally:
        cursor.close()


def get_min_max_buyers_per_product(conn):
    cursor = conn.cursor()
    print_section_header("Age Analysis Page")
    print("Welcome! You are viewing the min and max buyer age group for each product category. ")
    query = """
            SELECT product_category, 
                   MIN(age_range) AS youngest_buyers,
                   MAX(age_range) AS oldest_buyers
            FROM sales_summary_by_age_group
            GROUP BY product_category;
            """
    try:
        cursor.execute(query)
        results = cursor.fetchall()

        if results:
            headers = ["Product Category", "Youngest Buyers", "Oldest Buyers"]
            print("\n" + tabulate(results, headers=headers, tablefmt="grid") + "\n")
        else:
            print("\nNo results found.\n")

        # ask if user wants to delve deeper into the data to derive specific insights.
        # data_science_questions(conn)

    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
    finally:
        cursor.close()


def get_wants_versus_needs_per_age_group(conn):
    cursor = conn.cursor()
    print_section_header("Age Analysis Page")
    print("Welcome! You are viewing the spending breakdown of necessities vs. non-necessities by age group.")
    query = """
            SELECT age_range, 
                    SUM(CASE WHEN product_category IN ('Groceries', 'Health & Beauty') 
                    THEN total_sales ELSE 0 END) 
                        AS necessities,
                    SUM(CASE WHEN product_category NOT IN ('Groceries', 'Health & Beauty') 
                    THEN total_sales ELSE 0 END) 
                        AS non_necessities
            FROM sales_summary_by_age_group
            GROUP BY age_range
            ORDER BY age_range;
            """
    try:
        cursor.execute(query)
        results = cursor.fetchall()

        if results:
            headers = ["Age Range", "Spent on Necessities", "Spent on Non Necessities"]
            print("\n" + tabulate(results, headers=headers, tablefmt="grid") + "\n")
        else:
            print("\nNo results found.\n")

        # ask if user wants to delve deeper into the data to derive specific insights.
        # data_science_questions(conn)

    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
    finally:
        cursor.close()


def get_most_popular_store_chains_per_age_group(conn):
    """
    Determines the most common store location visited by different age groups.
    """
    cursor = conn.cursor()
    print_section_header("Age Analysis Page")
    print("Welcome! You are viewing the most common store location visited by different age groups. ")
    # Specify age group categories up to 50 and then just classify as above 50 years. Assume customers
    # must be at least 18 (adult) to make a purchase.

    # get the rank of stores by most purchases
    query = """
        SELECT 
            age_group, 
            store_chain, 
            total_purchases
        FROM (
            SELECT 
                CASE 
                    WHEN c.age BETWEEN 18 AND 25 THEN '18-25'
                    WHEN c.age BETWEEN 26 AND 35 THEN '26-35'
                    WHEN c.age BETWEEN 36 AND 50 THEN '36-50'
                    WHEN c.age BETWEEN 40 AND 49 THEN '40-49'
                    WHEN c.age BETWEEN 50 AND 59 THEN '50-59'
                    WHEN c.age BETWEEN 60 AND 69 THEN '60-69'
                    WHEN c.age BETWEEN 70 AND 79 THEN '70-79'
                    WHEN c.age BETWEEN 80 AND 89 THEN '80-89'
                    ELSE '90+'
                END AS age_group,
                s.store_chain_name AS store_chain,
                COUNT(*) AS total_purchases
            FROM customer_visits cv
            JOIN customer c ON cv.customer_id = c.customer_id
            JOIN store s ON cv.store_id = s.store_id
            GROUP BY age_group, s.store_chain_name, s.store_id
        ) ranked_stores
        WHERE total_purchases = (
            SELECT MAX(total_purchases)
            FROM (
                SELECT 
                    CASE 
                        WHEN c.age BETWEEN 18 AND 25 THEN '18-25'
                        WHEN c.age BETWEEN 26 AND 35 THEN '26-35'
                        WHEN c.age BETWEEN 36 AND 50 THEN '36-50'
                        WHEN c.age BETWEEN 40 AND 49 THEN '40-49'
                        WHEN c.age BETWEEN 50 AND 59 THEN '50-59'
                        WHEN c.age BETWEEN 60 AND 69 THEN '60-69'
                        WHEN c.age BETWEEN 70 AND 79 THEN '70-79'
                        WHEN c.age BETWEEN 80 AND 89 THEN '80-89'
                        ELSE '90+'
                    END AS age_group,
                    s.store_chain_name,
                    COUNT(*) AS total_purchases
                FROM customer_visits cv
                JOIN customer c ON cv.customer_id = c.customer_id
                JOIN store s ON cv.store_id = s.store_id
                GROUP BY age_group, s.store_chain_name, s.store_id
            ) max_counts
            WHERE max_counts.age_group = ranked_stores.age_group
        )
        ORDER BY age_group;
    """
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        headers = ["Age Group", "Store Chain", "Visit Count"]
        if results:
            print("\n" + tabulate(results, headers=headers, tablefmt="grid") + "\n")
        else:
            print("\nNo results found.\n")
        # ask if user wants to delve deeper into the data to derive specific insights.
        # data_science_questions(conn)
    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
    finally:
        cursor.close()
        
# REMEMBER TO ADD CASES THAT CHECK IF THE TYPE IS CORRECT SO THAT WE DONT GET A SQL ERROR
def get_specific_store_analysis(conn, store_id):
    """
    Fetches the number of open stores for a store chain (store_count) 
    and calculates the store score (store_score) for a specific store
    """
    print_section_header("Store Analysis Page")
    print(f"Welcome! You are viewing the number of chains and store score for store with store_id {store_id}")
    print("\nStore score represents the success of the store in relation to foot traffic and transactions. ")

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT store_count(%s);", (store_id,))
        store_count_result = cursor.fetchone()
        num_open_stores = store_count_result[0] if store_count_result else 0

        cursor.execute("SELECT store_score(%s);", (store_id,))
        store_score_result = cursor.fetchone()
        store_score = store_score_result[0] if store_score_result else 0

        print(f"\nAnalysis for Store ID: {store_id}")
        print("------------------------------------------------------")
        print(f"Total Stores in Chain: {num_open_stores}")
        print(f"Store Score: {store_score:.2f}")
        print("------------------------------------------------------")

    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")

    finally:
        cursor.close()

# WORKING ON RN
def get_specific_inventory_analysis(conn):
    """
    Retrieves products with the highest price in inventory
    """
    print_section_header("Most Expensive Items")
    cursor = conn.cursor()
    print("Welcome! You are viewing the 10 most expensive products in inventory of each store. ")
    query = """
        SELECT 
            inventory.product_id, 
            store.store_chain_name,
            inventory.store_location, 
            inventory.product_price_usd
        FROM inventory JOIN store 
        ON inventory.store_id = store.store_id 
        AND inventory.store_location = store.store_location
        ORDER BY inventory.product_price_usd DESC
        LIMIT 10;
    """
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        print("\n Store Sale Statistics")
        headers = ["Product ID", "Store Chain", "Location", "Product Price"]
        table = []
        for row in results:
            table.append([row[0], row[1], row[2], row[3]])

        # Print the table using tabulate
        print(tabulate(table, headers=headers, tablefmt="pretty"))
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
    
def create_account_client(conn):
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
        is_store_manager = input("Are you a store manager? If Yes, type 1. Else, type 0: ")
        if is_store_manager != "0" and is_store_manager != "1":
            print("Invalid input. Please try again. ")
            continue
        phone_number = input("Enter phone number: ")
        query = """
            CALL sp_add_user(%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            cursor.execute(query, (username, password, 0, first_name, last_name, is_store_manager, phone_number, None))
            conn.commit()
            check_query = "SELECT username, is_admin FROM user_info WHERE username = %s"
            print(f"User '{result[0]}' created successfully. ")
            break

        except mysql.connector.Error as err:
            sys.stderr.write(f"Error: {err}\n")
        finally:
            cursor.close()

def get_contact_email(conn, username):
    """
    Given a username, retrieves the contact email of the person associated 
    with the username
    """
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT get_contact_email(%s);", (username,))
        result = cursor.fetchone()
        if result:
            print(f"Username: {username}, Contact Email: {result[0]}")
        else:
            print(f"No associated email with given username: {username}")
            print("Please check spelling or punctuation")
    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
    finally:
        cursor.close()

def get_store_chain(conn, store_id):
    """
    Given a store_id, retrieves the corresponding store chain name
    """
    print_section_header("Store Chain Info")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT store_id_to_store_chain(%s);", (store_id,))
        result = cursor.fetchone()
        if result:
            print(f"Store ID: {store_id}, Store Chain Name: {result[0]}")
        else:
            print(f"No associated store chain with given store_id: {store_id}")
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
        print_section_header("Login Page")
        cursor = conn.cursor()
        print("Welcome! Please log in as a client.")
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
            
            if result and result[0] == 1:
                print("Client login successful!")
                show_client_options(conn)
                # return 2  # Admin user
            elif result and result[0] == 2:
                print("You are registered as an admin. Please use the admin interface.")
                # return 1  # Regular user
            else:
                print("Invalid password. Please try again. ")
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

def show_client_options(conn):
    """
    Displays options users can choose in the application, such as
    viewing <x>, filtering results with a flag (e.g. -s to sort),
    sending a request to do <x>, etc.
    """
    # The user will have the option to view tables for broad categories such as age stats, gender stats, etc.
    # Once they see these tables, they are prompted to further ask specific data science related questions
    # like asking more about beauty products bought by 10-20 year olds. We can also use user defined functions for this.

    # Below are some examples of questions the user can ask. We plan on making C, D, and E more broad categories
    # to make it easier to conduct robust analysis of data using this interface.
    while True:
        print_section_header("Menu Page")
        print('What would you like to do to explore retail data? ')
        print('  (A) - Get Age Statistics')
        print('  (B) - Get Gender Statistics')
        print('  (C) - Get Store Statistics')
        print('  (D) - Get Overall Store Statistics. This outputs a view.')
        print('  (E) - Find Chain Store')
        print('  (F) - Get Products with the Highest Price in Inventory of a Store')
        print('  (q) - Quit')
        print()
        ans = input('Enter an option: ').lower()
        if ans == 'a':
            get_age_stats(conn)
        elif ans == 'b':
            get_gender_stats(conn) 
        elif ans == 'c':
            get_store_stats(conn)
        elif ans == 'd':
            view_materialized_store_sales(conn)
        elif ans == 'e':
            store_id = input("Please enter store id: ").strip()
            get_store_chain(conn, store_id)
        elif ans == 'f':
            get_specific_inventory_analysis(conn)
        elif ans == 'q':
            quit_ui()
        else:
            print("Invalid option. Please try again.")
        input("\nPress Enter to return to the Client Menu...")

  
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
        print_section_header("Client Page")
        print("Would you like to: ")
        print("1. Create an account")
        print("2. Login")
        print("3. Exit")
        
        print_lines()
        choice = input("Enter your choice (1/2/3): ").strip()
        
        if choice == '1':
            create_account_client(conn)
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
