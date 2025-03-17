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
# ----------------------------------------------------------------------
def get_conn():
    """"
    Returns a connected MySQL connector instance, if connection is successful.
    If unsuccessful, exits.
    """
    try:
        conn = mysql.connector.connect(
          host='localhost',
          user='appadmin',
          # Find port in MAMP or MySQL Workbench GUI or with
          # SHOW VARIABLES WHERE variable_name LIKE 'port';
          port='3306',  # this may change!
          password='retailpwd', # adminpw
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


def count_gender_health_beauty():
    """
    Counts the number of male, female, and non-binary customers who purchased Health and Beauty products.
    """
    conn = get_conn()
    cursor = conn.cursor()
    query = """
        SELECT c.gender, COUNT(*) AS purchase_count
        FROM customer c
        JOIN purchase p ON c.customer_id = p.customer_id
        JOIN product pr ON p.product_id = pr.product_id
        WHERE pr.product_category = 'Health & Beauty'
        GROUP BY c.gender;
    """
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        print("Health & Beauty Product Purchases by Gender:")
        for row in results:
            print(f"Gender: {row[0]}, Purchase Count: {row[1]}")
    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
    finally:
        cursor.close()
        conn.close()


def most_popular_payment_method():
    """
    Finds the most commonly used payment method for each store.
    """
    conn = get_conn()
    cursor = conn.cursor()
    query = """
        SELECT p.store_id, p.payment_method, COUNT(*) AS usage_count
        FROM purchase p
        GROUP BY p.store_id, p.payment_method
        ORDER BY p.store_id, usage_count DESC;
    """
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        print("Most Popular Payment Methods Per Store:")
        for row in results:
            print(f"Store ID: {row[0]}, Payment Method: {row[1]}, Usage Count: {row[2]}")
    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
    finally:
        cursor.close()
        conn.close()


def most_common_store_location_per_age_group():
    """
    Determines the most common store location visited by different age groups.
    """
    conn = get_conn()
    cursor = conn.cursor()
    # Specify age group categories up to 50 and then just classify as above 50 years. Assume customers
    # must be at least 18 (adult) to make a purchase.
    query = """
        SELECT 
            CASE 
                WHEN c.age BETWEEN 18 AND 25 THEN '18-25'
                WHEN c.age BETWEEN 26 AND 35 THEN '26-35'
                WHEN c.age BETWEEN 36 AND 50 THEN '36-50'
                ELSE '50+' 
            END AS age_group,
            s.store_location,
            COUNT(*) AS visit_count
        FROM customer_visits cv
        JOIN customer c ON cv.customer_id = c.customer_id
        JOIN store s ON cv.store_id = s.store_id
        GROUP BY age_group, s.store_location
        ORDER BY age_group, visit_count DESC;
    """
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        print("Most Common Store Locations by Age Group:")
        for row in results:
            print(f"Age Group: {row[0]}, Store Location: {row[1]}, Visit Count: {row[2]}")
    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
    finally:
        cursor.close()
        conn.close()


def get_age_stats():
    """
    Displays a table of retail statistics grouped by age.
    After viewing the table, the user can ask further questions related to age or gender statistics.
    """
    conn = get_conn()
    cursor = conn.cursor()

    query = """
        SELECT 
            CASE 
                WHEN c.age BETWEEN 18 AND 25 THEN '18-25'
                WHEN c.age BETWEEN 26 AND 35 THEN '26-35'
                WHEN c.age BETWEEN 36 AND 50 THEN '36-50'
                ELSE '50+' 
            END AS age_group,
            COUNT(p.purchase_id) AS total_purchases,
            AVG(i.product_price_usd) AS avg_spent_per_purchase
        FROM customer c
        JOIN purchase p ON c.customer_id = p.customer_id
        JOIN inventory i ON p.product_id = i.product_id
        GROUP BY age_group
        ORDER BY age_group;
    """

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
        # ask if user wants to delve deeper into the data to derive specific insights.
        data_science_questions()
    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
    finally:
        cursor.close()
        conn.close()


def get_gender_stats():
    """
    Displays statistics based on gender, showing how different genders shop.
    """
    conn = get_conn()
    cursor = conn.cursor()

    query = """
        SELECT c.gender, 
               COUNT(p.purchase_id) AS total_purchases,
               AVG(i.product_price_usd) AS avg_spent_per_transaction
        FROM customer c
        JOIN purchase p ON c.customer_id = p.customer_id
        JOIN inventory i ON p.product_id = i.product_id
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
        data_science_questions()

    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
    finally:
        cursor.close()
        conn.close()


def get_more_age_analysis():
    """
    Allows deeper age-related analysis, such as finding the most common products purchased per age group.
    """
    conn = get_conn()
    cursor = conn.cursor()

    query = """
        Query to get the most common products purchased per age group.
    """

    try:
        cursor.execute(query)
        results = cursor.fetchall()
        print("\nMost Popular Product Categories by Age Group:")
        for row in results:
            print(row)
        data_science_questions()
    except mysql.connector.Error as err:
        sys.stderr.write(f"Error: {err}\n")
    finally:
        cursor.close()
        conn.close()


# ----------------------------------------------------------------------
# Admin Functionalities
# ----------------------------------------------------------------------


def add_new_transaction():
    """
    Allows an admin to add a new transaction manually into the database.
    """
    conn = get_conn()
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
        conn.close()


def update_customer_info():
    """
    Allows the admin to update a customer's information.
    """
    conn = get_conn()
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
        conn.close()


def delete_transaction_record():
    """
    Allows the admin to delete a transaction record.
    """
    conn = get_conn()
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
        conn.close()


def view_store_performance():
    """
    Displays store performance reports including revenue, total transactions,
    and average foot traffic per store.
    """
    conn = get_conn()
    cursor = conn.cursor()

    # Query to display the store performance reports including revenue, total transactions,
    # and average foot traffic per store.
    query = """
        SELECT s.store_id, s.store_location, 
               COUNT(p.purchase_id) AS total_transactions,
               SUM(i.product_price_usd) AS total_revenue,
               AVG(pop.foot_traffic) AS avg_foot_traffic
        FROM store s
        JOIN purchase p ON s.store_id = p.store_id
        JOIN inventory i ON p.product_id = i.product_id
        JOIN popularity pop ON s.store_id = pop.store_id
        GROUP BY s.store_id, s.store_location;
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
        conn.close()


# ----------------------------------------------------------------------
# Functions for Logging Users In
# ----------------------------------------------------------------------
# Note: There's a distinction between database users (admin and client)
# and application users (e.g. members registered to a store). You can
# choose how to implement these depending on whether you have app.py or
# app-client.py vs. app-admin.py (in which case you don't need to
# support any prompt functionality to conditionally login to the sql database)


# ----------------------------------------------------------------------
# Command-Line Functionality
# ----------------------------------------------------------------------

def show_options():
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
    print('What would you like to do to explore retail data? ')
    print('  (A) - Get Age Statistics')
    print('  (B) - Get Gender Statistics')
    print('  (C) - Count Health & Beauty Purchases by Gender')
    print('  (D) - Find Most Popular Payment Methods Per Store')
    print('  (E) - Determine Most Common Store Locations for Each Age Group') # location stats
    print('  (q) - quit')
    print()
    ans = input('Enter an option: ').lower()
    if ans == 'a':
        get_age_stats()
    elif ans == 'b':
        get_gender_stats()
    if ans == 'c':
        count_gender_health_beauty()
    elif ans == 'd':
        most_popular_payment_method()
    elif ans == 'e':
        most_common_store_location_per_age_group()
    elif ans == 'q':
        quit_ui()
    else:
        print("Invalid option. Please try again.")


def data_science_questions():
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
        print("\nWould you like to explore more?")
        print("  (1) - View Gender-Specific Statistics")
        print("  (2) - View More Age-Based Analysis")
        print("  (b) - Back to Main Menu")
        print("  (q) - Quit")

        ans = input("Enter an option: ").lower()

        if ans == '1':
            get_gender_stats()
        elif ans == '2':
            get_more_age_analysis()
        elif ans == 'b':
            show_options()
        elif ans == 'q':
            quit_ui()
        else:
            print("Invalid option. Please try again.")

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
    print('What would you like to do? ')
    print('  (1) - Add a New Transaction')
    print('  (2) - Update a Customer\'s Information')
    print('  (3) - Delete a Transaction Record')
    print('  (4) - View Store Performance Reports')
    print('  (q) - quit')
    print()
    ans = input('Enter an option: ').lower()
    if ans == '1':
        add_new_transaction()
    elif ans == '2':
        update_customer_info()
    elif ans == '3':
        delete_transaction_record()
    elif ans == '4':
        view_store_performance()
    elif ans == 'q':
        quit_ui()
    else:
        print("Invalid option. Please try again.")


def quit_ui():
    """
    Quits the program, printing a goodbye message to the user.
    """
    # We can also add some bullet points here to summarize some cool statistics from the data and leave the user off
    # with something interesting about retail data!
    print('Good bye!')
    exit()


def main():
    """
    Main function for starting things up.
    """
    show_options()


if __name__ == '__main__':
    # This conn is a global object that other functions can access.
    # You'll need to use cursor = conn.cursor() each time you are
    # about to execute a query with cursor.execute(<sqlquery>)
    conn = get_conn()
    main()



 SELECT product_id, product_category FROM staging_data WHERE product_id IN (SELECT product_id FROM staging_data GROUP BY product_id HAVING COUNT(DISTINCT product_category) > 1) ORDER BY product_id, product_category;