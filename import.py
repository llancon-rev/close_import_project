import csv

# Load environment variables
from dotenv import load_dotenv
import os
load_dotenv('vault.env')

# Importing modules to validate email and phone numbers
import validate_email
import phonenumbers

# Set API Key
api_key = os.getenv("CLOSE_API_KEY")

# Source CSV file name
source_file = "Close Sample Import File.csv"

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
		email = row[2]
		
		try:
			parsed_number = phonenumbers.parse(row[3], None)
		except Exception:
			print("Unacceptable phone number!!")
			continue

		if validate_email.validate_email(email) and phonenumbers.is_valid_number(parsed_number):
			rows.append(row)


# printing the field names
print('Field names are: ' + ', '.join(field for field in fields))