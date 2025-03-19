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

def most_popular_payment_method(conn):
    """
    Finds the most commonly used payment method for each store.
    """
    cursor = conn.cursor()
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
        print("Most Popular Payment Methods Per Store:")
        for row in results:
            print(f"Store ID: {row[0]}, Store Location: {row[1]}, Payment Method: {row[2]}, Usage Count: {row[3]}")
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
        cursor = conn.cursor()
        
        print("\nChoose the type of age analysis you want to perform:")
        print("1. Analyze basic statistics.")
        print("2. More in depth analysis.")
        print("3. Quit")
        choice = input("Enter your choice (1 or 2 or 3): ")

        if choice == "1":
            query = """
                SELECT 
                    
            """


            # """
            #     SELECT
            #         CASE
            #             WHEN c.age BETWEEN 18 AND 25 THEN '18-25'
            #             WHEN c.age BETWEEN 26 AND 35 THEN '26-35'
            #             WHEN c.age BETWEEN 36 AND 50 THEN '36-50'
            #             ELSE '50+'
            #         END AS age_group,
            #         COUNT(p.purchase_id) AS total_purchases,
            #         AVG(p.purchased_product_price_usd) AS avg_spent_per_purchase
            #     FROM customer c
            #     JOIN purchase p
            #         ON c.customer_id = p.customer_id
            #     GROUP BY age_group
            #     ORDER BY age_group;
            # """

            try:
                cursor.execute(query)
                results = cursor.fetchall()
                print("\nRetail Statistics by Age Group:")
                print("------------------------------------------------")
                print("Age Group | Total Purchases | Avg Spent Per Purchase ($)")
                print("------------------------------------------------")
                for row in results:
                    print(f"{row[0]} | {row[1]} | {row[2]:.2f}")
                print("------------------------------------------------")
            except mysql.connector.Error as err:
                sys.stderr.write(f"Error: {err}\n")
            finally:
                cursor.close()
        elif choice == "2":
            # ask if user wants to delve deeper into the data to derive specific insights.
            data_science_questions(conn)
        elif choice == "3":
            quit_ui()
        else:
            print("Invalid option. Please try again.")
            input("\nPress Enter to return to the Client Menu...")
            


def get_gender_stats(conn):
    """
    Displays statistics based on gender, showing how different genders shop.
    """
    while True:
        cursor = conn.cursor()
        
        print("\nChoose the type of gender analysis you want to perform:")
        print("1. Analyze basic statistics.")
        print("2. More in depth analysis")
        print("3. Quit")
        choice = input("Enter your choice (1 or 2 or 3): ")
        if choice == "1":
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
                print("------------------------------------------------")
                print("Gender | Total Purchases | Avg Spent Per Transaction ($)")
                print("------------------------------------------------")
                for row in results:
                    print(f"{row[0]} | {row[1]} | {row[2]:.2f}")
                print("------------------------------------------------")

            except mysql.connector.Error as err:
                sys.stderr.write(f"Error: {err}\n")
            finally:
                cursor.close()
        elif choice == "2":
            data_science_questions(conn)
        elif choice == "3":
            quit_ui()
        else:
            print("Invalid option. Please try again.")
            input("\nPress Enter to return to the Client Menu...")
        
def get_store_stats(conn):
    """
    Displays statistics based on stores, beneficial for store manager clients.
    """
    while True:
        cursor = conn.cursor()
        print("\nChoose the type of store analysis you want to perform:")
        print("1. Analyze the most popular payment method.")
        print("2. Analyze general revenue statistics.")
        print("3. More in depth analysis")
        print("4. Quit")
        choice = input("Enter your choice (1 or 2): ")
        
        
        if choice == "1":
            print("\nFetching the most popular payment method...\n")
            most_popular_payment_method(conn)
            return  # Exit function after running the chosen query
        elif choice == "2":
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
                print("\nRetail Statistics by Store:")
                print("------------------------------------------------")
                print("Store ID | Store Location | Total Purchases | Total Revenue | Avg Foot Traffic ($)")
                print("------------------------------------------------")
                for row in results:
                    print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]:.2f} | {row[4]:.2f}")
                print("------------------------------------------------")

            except mysql.connector.Error as err:
                sys.stderr.write(f"Error: {err}\n")
            finally:
                cursor.close()
        elif choice == "3":
            data_science_questions(conn)
        elif choice == '4':
            quit_ui()
        else:
            print("Invalid option. Please try again.")
            input("\nPress Enter to return to the Client Menu...")
            
def get_more_gender_analysis(conn, product_category):
    """
    Counts the number of male, female, and non-binary customers who purchased Health and Beauty products.
    """
    cursor = conn.cursor()
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
        print("Health & Beauty Product Purchases by Gender:")
        for row in results:
            print(f"Gender: {row[0]}, Purchase Count: {row[1]}")
    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
    finally:
        cursor.close()

            
def get_more_age_analysis(conn):
    """
    Determines the most common store location visited by different age groups.
    """
    cursor = conn.cursor()
    # Specify age group categories up to 50 and then just classify as above 50 years. Assume customers
    # must be at least 18 (adult) to make a purchase.
    query = """
        SELECT 
            sa.age_range AS age_group,
            s.store_id,
            s.store_location,
            COUNT(*) AS visit_count
        FROM sales_summary_by_age_group sa
        JOIN store s 
        ON sa.product_category = s.store_id -- Assuming product_category represents stores in some way
        GROUP BY sa.age_range, s.store_id, s.store_location
        ORDER BY sa.age_range, visit_count DESC;
    """
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        print("Most Common Store Locations by Age Group:")
        for row in results:
            print(f"Age Group: {row[0]}, Store Location: {row[1]}, Visit Count: {row[2]}")
        print("------------------------------------------------")
        # ask if user wants to delve deeper into the data to derive specific insights.
        data_science_questions(conn)
    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
    finally:
        cursor.close()
        
# REMEMBER TO ADD CASES THAT CHECK IF THE TYPE IS CORRECT SO THAT WE DONT GET A SQL ERROR
def get_specific_store_analysis(conn, store_id, store_location):
    """
    Fetches the number of open stores for a store chain (store_count) 
    and calculates the store score (store_score) for a specific store
    """
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT store_count(%s);", (store_id,))
        store_count_result = cursor.fetchone()
        num_open_stores = store_count_result[0] if store_count_result else 0
        
        if num_open_stores == 0:
            print(f"Store ID: {store_id} at Location: {store_location} is not in the database.")
            return

        cursor.execute("SELECT store_score(%s);", (store_id,))
        store_score_result = cursor.fetchone()
        store_score = store_score_result[0] if store_score_result else 0

        print(f"\nAnalysis for Store ID: {store_id}, Location: {store_location}")
        print("------------------------------------------------------")
        print(f"Total Stores in Chain: {num_open_stores}")
        print(f"Store Score: {store_score:.2f}")
        print("------------------------------------------------------")

    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")

    finally:
        cursor.close()


def create_account_client(conn):
    cursor = conn.cursor()
    username = input("Enter username: ")
    password = input("Enter password: ")
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    try:
        cursor.execute("SELECT get_contact_email(%s)", (username,))  # Assuming not an admin (0)
        email = cursor.fetchone()[0]  # Fetch the email from the query result
    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")

    is_store_manager = input("Are you a store manager? If Yes, type 1. Else, 0: ")
    phone_number = input("Enter phone number: ")
    query = """
        CALL sp_add_user(%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    try:
        cursor.execute(query, (username, password, 0, first_name, last_name, email, is_store_manager, phone_number, None))
        conn.commit()
        check_query = "SELECT username, is_admin FROM user_info WHERE username = %s"
        cursor.execute(check_query, (username,))
        result = cursor.fetchone()

        if result:
            print(f"User '{result[0]}' created successfully with client status: {result[1]}")
        else:
            print("Failed to create the client account.")

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
        print("Welcome! Please log in as a client.")
        username = input("Enter username: ")
        password = input("Enter password: ")
        
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
                print("Invalid username or password.")
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
        print('What would you like to do to explore retail data? ')
        print('  (A) - Get Age Statistics')
        print('  (B) - Get Gender Statistics')
        print('  (C) - Get Store Statistics')
        print('  (q) - quit')
        print()
        ans = input('Enter an option: ').lower()
        if ans == 'a':
            get_age_stats(conn)
        elif ans == 'b':
            get_gender_stats(conn) 
        elif ans == 'c':
            get_store_stats(conn)
        elif ans == 'q':
            quit_ui()
        else:
            print("Invalid option. Please try again.")
        input("\nPress Enter to return to the Client Menu...")


def data_science_questions(conn):
    """
    After viewing age statistics, allows users to explore further statistics related to gender or age.
    """
    # Here are examples of specific statistics the user can ask for upon choosing and broad category such as
    # age or gender first. They also have the option to return back to the main menu to continue analysis using a
    # different category.

    # For example, if the user chooses to explore gender_stats, one piece of information they can get is executing a
    # query that shows how different genders shop by calculating the average product prices, total profit,
    # and total number of purchases.

    # Another example is if the user chooses to explore age stats, they can get a list of the most common products
    # purchased per age group.

    # We also plan to add user defined functions in SQL to allow the users of this application to get more diverse
    # answers, such as customer profitability score based on spending behavior and store profitability.
    # Another idea we have is to categorize a particular customer based on their spending score in relation to other
    # customers.
    # Another useful UDF would be to compare competitor price with a store's product for pricing strategy analysis.

    # Additionally, we would like to display graphs to further help researchers analyze retail data.
    # For example, a scatterplot could help display relationships of each attribute with profit.
    # We can also output a plot of the average spending score by age group to allow a visual display of whether there is
    # a difference in the average spending between different age groups.
    # We can also display a plot of the total profit made by each product category to allow users to analyze whether
    # there is a particular category that makes significantly more profit.
    # We can also display a correlation plot to analyze what attributes have the highest correlation and lowest.
    # For example, one might wonder whether Profit and Product Price are correlated, and this plot will make it really
    # easy to check that.
    while True:
        print("\nWhat would you like to explore more?")
        print("  (1) - View Gender-Specific Statistics")
        print("  (2) - View More Age-Based Analysis")
        print("  (3) - View Specific Store Analysis")
        print("  (b) - Back to Main Menu")
        print("  (q) - Quit")

        ans = input("Enter an option: ").lower()

        if ans == '1':
            print("Analyzing Gender Statistics")
            print("Get gender stats based on product category: ")
            product_category = input("What product category are you interested in? ")
            get_more_gender_analysis(conn, product_category)
        elif ans == '2':
            print("Analyzing Age Statistics")
            print("Get most common store location based on age group: ")
            get_more_age_analysis(conn)
        elif ans == '3':
            print("Analyzing Store Statistics")
            print("Get store stats based on store id and location: ")
            store_id = input("What store id are you interested in? ")
            store_location = input("Are you interested in a specific location? ")
            print()
            get_specific_store_analysis(conn, store_id, store_location)
        elif ans == 'b':
            show_client_options(conn)
        elif ans == 'q':
            quit_ui()
        else:
            print("Invalid option. Please try again.")
        print("\nPress enter to return to the menu")

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
        print("\n=== Client Page ===")
        print("Would you like to: ")
        print("1. Create an account")
        print("2. Login")
        print("3. Exit")
        
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
