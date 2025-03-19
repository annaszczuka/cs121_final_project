# import pandas as pd
# from tabulate import tabulate

# df = pd.read_csv('data.csv')                                   
# revenues = {}
# for row in df.iterrows():
#     row = row[1]
#     rev = (row['product_price_usd']) - (row['product_cost_usd']) - ((row['product_price_usd']) * (row['discount_percent']) / 100)
#     temp = (row['store_id'], row['store_location'])
#     if temp in revenues:
#         revenues[temp] += rev
#     else:
#         revenues[temp] = rev
    
# table_data = [(store_id, store_location, revenue) for (store_id, store_location), revenue in revenues.items()]
# table_data.sort(key=lambda x: x[2], reverse=True)
# print("FIFTH QUERY: total revenues", tabulate(table_data, headers=["Store ID", "Store Location", "Revenue"], tablefmt="grid"))

import pandas as pd
from tabulate import tabulate

# Load data
df = pd.read_csv('data.csv')

# Filter to include only store_id 26
df = df[df['store_id'] == 26]

# Calculate profit per row
df['profit'] = (df['product_price_usd'] * (1 - df['discount_percent']) / 100) - df['product_cost_usd']

# Group by store ID and store location to get total profit
revenues = df.groupby(['store_id', 'store_location'])['profit'].sum().reset_index()

# Sort by total profit in descending order (though only one store is included)
revenues = revenues.sort_values(by='profit', ascending=False)

# Convert to table format and print
print("FIFTH QUERY: Total Profits (Only store_id = 26)")
print(tabulate(revenues, headers=["Store ID", "Store Location", "Total Profit"], tablefmt="grid"))
