import sys 
import mysql.connector
import mysql.connector.errorcode as errorcode
from tabulate import tabulate
import re

def check_user_or_pass(conn, word, type, is_login):
    cursor = conn.cursor()
    if word == "":
        print(f"You did not enter a {type}. Please try again. ")
        return 0 
    
    if " " in word:
        print(f"There cannot be spaces in a {type}. Please try again. ")
        return 0
    
    if not re.match(r"^[a-zA-Z0-9_]+$", word):
        print(f"The {type} can only contain letters, numbers, and underscores. "
              "Please try again.")
        return 0
    
    # checks to make sure username is in the database
    if type == "username":
        check_query = f"SELECT username FROM user_info WHERE username = %s"
        cursor.execute(check_query, (word,))
        result = cursor.fetchone()
        if is_login and not result:
            print("Username does not exist. Please try again. ")
            return 0
        if not is_login and result:
            print("Username is already taken. Please try again. ")
            return 0
    return 1

def print_lines():
    print("\n")
    
def print_divider():
    print("\n" + "-" * 60 + "\n")

def print_section_header(title):
    print("\n" + "=" * 60)
    print(f" {title} ".center(60, " "))
    print("=" * 60 + "\n")
    
