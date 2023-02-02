# importing csv module
import csv

# Load environment variables
from dotenv import load_dotenv
import os
load_dotenv('vault.env')

# Set API Key
api_key = os.getenv("CLOSE_API_KEY")

# Source CSV file name
source_file = "aapl.csv"

# initializing the titles and rows list
fields = []
rows = []

# reading csv file
with open(source_file, 'r') as csvfile:
	# creating a csv reader object
	csvreader = csv.reader(csvfile)
	
	# extracting field names through first row
	fields = next(csvreader)

	# extracting each data row one by one
	for row in csvreader:
		rows.append(row)


print(f"test: {api_key}!!")