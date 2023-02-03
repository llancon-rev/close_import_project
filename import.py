import csv
import statistics
from closeio_api import Client

# Load environment variables
from dotenv import load_dotenv
import os
load_dotenv('vault.env')

# Importing modules to validate email and phone numbers
import validate_email
import phonenumbers

lead_count = 0
contact_count = 0

## Defining helper methods ##

def find_lead_id(lead):
	for lead in leads:
		if row["Company"] == lead["name"]:
			lead_id = lead["lead_id"]
			return lead_id

def lead_exists(leads, company_name):
    for lead in leads:
        if lead.get('name') == company_name:
            return True
    return False

def create_or_update_lead(row, leads):
	# Importing unique Leads
	if not lead_exists(leads, row['Company']):
		lead = {
				"name": row["Company"]
				}
		try:
			post_lead = api.post('lead', data=lead)
			new_lead = {
				"name": row["Company"],
				"lead_id": post_lead["id"],
				"custom.cf_QunpCuMvHJxiV5QjYrusGG9D8Uzi08CsS5jGTbxHfm4": "",
				"custom.cf_CVsgcfWqI7sz5KjvSckz34AtB6lEoKnctkA5C610TZb": "",
				"custom.cf_lS1kT2uuH2KChn2UjzK0NRLhceKWudOWzhySB53GR5w": ""
				}
			leads.append(new_lead)
			global lead_count
			lead_count += 1
		# print(post_lead)
		except Exception as e:
			print(f"{lead['name']}: Lead could not be posted because {str(e)}")
		# To ensure custom fields are import if there on the first try
		
	# Lead exists but does it have all the custom fields?
	for lead in leads:
		if lead.get(row["Company"]) == row["Company"] and (lead.get(row["custom.Company Founded"]) != "" or lead.get(row["custom.Company Revenue"]) != "" or lead.get(row["Company US State"]) != "") :
			# If all custom fields exist for lead then return the current lead object.
			return
		else:
			update_company(lead,row["custom.Company Founded"], row["custom.Company Revenue"], row["Company US State"])

			
def update_company(lead, company_founded, company_revenue, company_us_state):
	if company_founded == company_revenue == company_us_state == "":
		return
	else:
		lead_id = find_lead_id(lead)
		# Update the Company Founded if it's not empty in the current row
		print(lead)
		if lead["custom.cf_QunpCuMvHJxiV5QjYrusGG9D8Uzi08CsS5jGTbxHfm4"] == "" and row["custom.Company Founded"] != "":
			update_custom_field(lead, lead_id,'company founded', row["custom.Company Founded"])
			lead.update({"custom.cf_QunpCuMvHJxiV5QjYrusGG9D8Uzi08CsS5jGTbxHfm4": row["custom.Company Founded"]})
		if lead["custom.cf_CVsgcfWqI7sz5KjvSckz34AtB6lEoKnctkA5C610TZb"] == "" and row["custom.Company Revenue"] != "":
			update_custom_field(lead, lead_id,'company revenue', row["custom.Company Revenue"] )
			lead.update({"custom.cf_CVsgcfWqI7sz5KjvSckz34AtB6lEoKnctkA5C610TZb": row["custom.Company Revenue"]})
		if lead["custom.cf_lS1kT2uuH2KChn2UjzK0NRLhceKWudOWzhySB53GR5w"] == "" and row["Company US State"] != "":
			update_custom_field(lead, lead_id,'company us state',row["Company US State"])
			lead.update({"custom.cf_lS1kT2uuH2KChn2UjzK0NRLhceKWudOWzhySB53GR5w": row["Company US State"]})


def update_custom_field(lead, lead_id,field, field_val):
  if field == 'company founded':
    custom_field_k, custom_field_v  = "custom.cf_QunpCuMvHJxiV5QjYrusGG9D8Uzi08CsS5jGTbxHfm4", field_val
  if field == 'company revenue':
    custom_field_k, custom_field_v  = "custom.cf_CVsgcfWqI7sz5KjvSckz34AtB6lEoKnctkA5C610TZb", field_val
  if field == 'company us state':
    custom_field_k, custom_field_v = "cf_lS1kT2uuH2KChn2UjzK0NRLhceKWudOWzhySB53GR5w", field_val
  else:
    "no updates"
  updated_lead = {
	custom_field_k : custom_field_v
	}
  try:
    updated_lead = api.put(f'lead/{lead_id}', data=updated_lead)
    # print(f"Successfully updated Lead: {updated_lead}")
  except Exception as e:
    print(f"{updated_lead}: Lead could not be posted because {str(e)}")

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
	# Processing each data row
	for row in csvreader:
		try:
			parsed_number = phonenumbers.parse(row["Contact Phones"], None)
		except Exception as e:
			print(f"Could not parse phone number because: {str(e)}")
			# If the phone number can't be parsed it moves on to next row
			continue

		# Email and phone data is valid the row is saved
		if validate_email.validate_email(row["Contact Emails"]) and phonenumbers.is_valid_number(parsed_number):
		
##### importing Leads #########	
			create_or_update_lead(row, leads)

##### importing Contacts #########
			## Finding lead_id for Contact that will be imported next
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
			}
			try:
				post_contact = api.post('contact', data=contact)
				contacts.append(contact)
				contact_count += 1
			except Exception as e:
				print(f"{contact}: Contact could not be posted because: {str(e)}")

print(f"Leads imported: {lead_count} and Contacts imported: {contact_count}")
# print(leads)

### Generating CVS with State Revenue report

# Group the Leads by US State
state_data = {}
for lead in leads:
    state = lead['custom.cf_lS1kT2uuH2KChn2UjzK0NRLhceKWudOWzhySB53GR5w']
    if state not in state_data:
        state_data[state] = {
            'companies': [],
            'revenues': []
        }
	
    if lead_exists(leads, lead['name']):
        state_data[state]['companies'].append(lead['name'])
        try:
            state_data[state]['revenues'].append(float(lead['custom.cf_CVsgcfWqI7sz5KjvSckz34AtB6lEoKnctkA5C610TZb'][1:].replace(',', '')))
        except Exception as e:
            print(f"{lead}: Revenue could not be converted to float because {str(e)}")
	    
# Write the output CSV data
with open('State Revenue Report.csv', 'w', newline='') as output_file:
    fieldnames = ['Company US State', 'Total Companies', 'Total Revenue', 'Median Revenue']
    writer = csv.DictWriter(output_file, fieldnames=fieldnames)
    writer.writeheader()
    for state, data in state_data.items():
        writer.writerow({
            'Company US State': state,
            'Total Companies': len(data['companies']),
            'Total Revenue': sum(data['revenues']),
            'Median Revenue': statistics.median(data['revenues'])
        })
	
print("Job Done!!")
