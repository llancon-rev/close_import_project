import csv
import statistics
from closeio_api import Client
from lead import Lead
from contact import Contact

# Load environment variables
from dotenv import load_dotenv
import os
load_dotenv('vault.env')

#### Start to process source CSV file ####
# Source CSV file name
source_file = "Close Sample Import File.csv"

# Reading csv file
with open(source_file, 'r') as csvfile:
    # creating a csv reader object
    csvreader = csv.DictReader(csvfile)
    leads = []
    contacts=[]
    errors = []

    for row in csvreader:
        # Initializing leads and contacts before importing data is validated and grouped together.
        lead = Lead(row["Company"], {
            Lead.FIELDS["company_founded"] : row["custom.Company Founded"],
            Lead.FIELDS["company_revenue"] : row["custom.Company Revenue"],
            Lead.FIELDS["company_us_state"] : row["Company US State"]
        })
        contact = Contact(row["Contact Name"], row["Contact Emails"], row["Contact Phones"], row)
        
        # Groups Leads and Contacts together if contact data is valid.
        if contact.validate_contact_data() == True:
            lead.add_or_update_lead(row, leads)
            lead.add_contact(contact, leads, row)
        else:
            if not lead.lead_exists(errors, row["Company"]):
                errors.append(lead)
            print(f"invalid contact! {contact.to_dict()}")

# Removing Leads grouped with Contacts that have invalid data.
for error in errors:
    for lead in leads:
        if lead.name == error.name:
            leads.remove(lead)


# Importing Leads grouped with Contacts provided the associated contact in a group didn't have errors.
# Set API Key
api_key = os.getenv("CLOSE_API_KEY")
api = Client(api_key)

for lead in leads:
    print("")
    try:
        response = api.post('lead', data=lead.to_dict())
        print(response)
    except Exception as e:
        print(f"{lead}: Lead could not be posted because {str(e)}")

### Generating CVS with State Revenue report
# Group the Leads by US State
state_data = {}
for lead in leads:
    state = lead.custom_fields[Lead.FIELDS["company_us_state"]]
    if state not in state_data and lead.missing_state():
        state_data[state] = {
            'companies': [],
            'revenues': []
        }
	
    # Skip over leads that have missing State
    if lead.missing_state():
        state_data[state]['companies'].append(lead.name)
        try:
            state_data[state]['revenues'].append(float(lead.custom_fields[Lead.FIELDS["company_revenue"]][1:].replace(',', '')))
        except Exception as e:
            print(f"{lead}: Revenue could not be converted to float because {str(e)}")

def max_revenue(data):
    max_revenue = max(data['revenues'])
    max_index = data['revenues'].index(max_revenue)
    max_company = data['companies'][max_index]
    return max_company

# Write the output CSV data
with open('State Revenue Report.csv', 'w', newline='') as output_file:
    fieldnames = ['Company US State', 'Total Companies', 'Total Revenue', 'Median Revenue', 'Company with Most Revenue']
    writer = csv.DictWriter(output_file, fieldnames=fieldnames)
    writer.writeheader()
    for state, data in state_data.items():
        max_company = max_revenue(data)
        writer.writerow({
            'Company US State': state,
            'Total Companies': len(data['companies']),
            'Total Revenue': round(sum(data['revenues']), 2),
            'Median Revenue': round(statistics.median(data['revenues']),2),
	    	'Company with Most Revenue': max_company
        })

count = len(leads)
print(f"Job Done!! total leads: {count}")
