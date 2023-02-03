import csv
from closeio_api import Client

# Load environment variables
from dotenv import load_dotenv
import os
load_dotenv('vault.env')

# Importing modules to validate email and phone numbers
import validate_email
import phonenumbers

# Set API Key
api_key = os.getenv("CLOSE_API_KEY")
api = Client(api_key)

# Source CSV file name
source_file = "Close Sample Import File.csv"

# reading csv file
with open(source_file, 'r') as csvfile:

	# creating a csv reader object
	csvreader = csv.DictReader(csvfile)
	leads = []
	contacts=[]
	# extracting each data row one by one
	for row in csvreader:
		#  Email still not validated
		email = row["Contact Emails"]

		try:
			parsed_number = phonenumbers.parse(row["Contact Phones"], None)
		except Exception:
			# If the phone number can't be parsed it moves on to next row
			continue

		# Email and phone data is valid the row is saved
		if validate_email.validate_email(email) and phonenumbers.is_valid_number(parsed_number):
			# Empty Company Found case
			if row["custom.Company Founded"] in ['']:
				row["custom.Company Founded"] = "01.01.2023"
			# Empty Company Revenue case
			if row["custom.Company Revenue"] in ['']:
				row["custom.Company Revenue"] = "$0.00"
			if row["Company US State"] == "":
				row["Company US State"] = "None"

			# Importing unique Leads
			if row["Company"] not in leads:
				lead = {
					"name": row["Company"],
					"custom.cf_QunpCuMvHJxiV5QjYrusGG9D8Uzi08CsS5jGTbxHfm4": row["custom.Company Founded"],
					"custom.cf_CVsgcfWqI7sz5KjvSckz34AtB6lEoKnctkA5C610TZb": row["custom.Company Revenue"],
					"custom.cf_lS1kT2uuH2KChn2UjzK0NRLhceKWudOWzhySB53GR5w": row["Company US State"]
				}
				# {"Company Founded": "cf_QunpCuMvHJxiV5QjYrusGG9D8Uzi08CsS5jGTbxHfm4"}
				# {"Company Revenue": "cf_CVsgcfWqI7sz5KjvSckz34AtB6lEoKnctkA5C610TZb"}
				# {"Company US State" "cf_lS1kT2uuH2KChn2UjzK0NRLhceKWudOWzhySB53GR5w"}
				try:
					post_lead = api.post('lead', data=lead)
					new_lead = {
						"name": row["Company"],
						"lead_id": post_lead["id"]
					}
					leads.append(new_lead)
					# print(post_lead)
				except Exception as e:
					print(f"{lead['id']}: Lead could not be posted because {str(e)}")
					continue

			# Finding lead_id  for Contact that will be imported next
			for lead in leads:
				if row["Company"] == lead["name"]:
					lead_id = lead["lead_id"]
			# Handle contact name empty cases
			if row["Contact Name"] in ['', None]:
					if row["Contact Emails"] not in ['', None]:
						row["Contact Name"] = row["Contact Emails"]
					else:
						row["Contact Name"] = row["Contact Phones"]
			
			contact = {
				"lead_id": lead_id,
				"name": row["Contact Name"],
				"emails":  [
					{"email": row["Contact Emails"],"type":"office"}
				],
				"phones":[
					{"phones": row["Contact Phones"], "type":"office"}
				]
				# "custom.Company Found": row["custom.Company Founded"],
				# "custom.Company Revenue": row["custom.Company Revenue"],
				# "Company US State": row["Company US State"]
			}
			try:
				post_contact = api.post('contact', data=contact)
				contacts.append(contact)

			except Exception as e:
				print(f"{contact}: Contact could not be posted because {str(e)}")

# print(leads)

print(contacts)

# params = { PARAMS HERE }

# resp = api.get('custom_field/lead')
# print(resp)

		