Our data comes from the public kaggle dataset linked below: 
https://www.kaggle.com/datasets/abdurraziq01/retail-data/data

We made significant changes to the csv file by using ChatGPT and python functions to generate columns such as year_opened, purchase_id, visit_date, 
customer name, store chain name, is_favorite, purchased_product_price_usd. 
We also diversified the gender column by including x.

We also removed some unnecessary columns, including but not limited to marketing expenditure, discount applied, profit, and more. 
We removed this columns as these columns can be derived from other columns

First clone the repo: $ git clone https://github.com/annaszczuka/cs121_final_project.git

To install the requirements needed to run the files, run 
$ conda create --name new_env python=3.10.16 
$ conda activate new_env 
$ cd cs121_final_project 
$ pip install -r requirements.txt (This step might take 2-5 minutes)

To get into mysql run: mysql --local-infile=1 -u root -p

To create the database, run 
mysql> CREATE DATABASE retaildb; 
mysql> USE retaildb;

To setup and load data, run 
mysql> source setup.sql; 
mysql> source load-data.sql; 
mysql> source setup-passwords.sql; 
mysql> source setup-routines.sql; 
mysql> source grant-permissions.sql; 
mysql> source queries.sql; -- this is good to confirm no syntax errors mysql> quit;

To run the application as a client, run $ python3 app-client.py

To run the application as an admin, run $ python3 app-admin.py

Upon running these Python files, one will be prompted to create an account or log in. 
Afterward, the output in the command line terminal will contain instructions on what retail statistics to explore. 
Users will be prompted to enter digits or letter choices to navigate retail store statistics.

One feature that remains unfinished within the scope of this project is the admin having the ability to insert a purchase at a new store 
and for a new customer who has not yet purchased anything previously. This functionality would have included additional triggers to ensure 
tables update correctly, which have not yet been implemented.
