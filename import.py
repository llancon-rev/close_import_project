import csv
from closeio_api import Client
import argparse
from datetime import datetime
from lead import Lead
from contact import Contact
import statistics

# Load environment variables
from dotenv import load_dotenv
import os
load_dotenv('vault.env')

### Setting up date range args to import data within specified range. Date Range is required to run the script. ### 
parser = argparse.ArgumentParser()
# Example of specifying date range when running script: python import.py --start_date 01.01.1950 --end_date 31.01.2023
parser.add_argument("--start_date", help="start date in format DD.MM.YYYY", required=True)
parser.add_argument("--end_date", help="end date in format DD.MM.YYYY", required=True)

args = parser.parse_args()

start_date = datetime.strptime(args.start_date, "%d.%m.%Y")
end_date = datetime.strptime(args.end_date, "%d.%m.%Y")

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
        # First check if Company founded date falls within date range that was specified and skip CSV row if its out of range or blank.
        if row["custom.Company Founded"] in [None, ''] or (datetime.strptime(row["custom.Company Founded"], "%d.%m.%Y") < start_date or datetime.strptime(row["custom.Company Founded"], "%d.%m.%Y") > end_date):
            # print(f"{row['Company']} and founded on {row['custom.Company Founded']}")
            continue
        # Creating leads and contacts before importing data is validated and grouped together.
        lead = Lead(row["Company"], {
            Lead.FIELDS["company_founded"] : row["custom.Company Founded"],
            Lead.FIELDS["company_revenue"] : row["custom.Company Revenue"],
            Lead.FIELDS["company_us_state"] : row["Company US State"]
        })
        contact = Contact(row["Contact Name"], row["Contact Emails"], row["Contact Phones"], row)
        
        # Groups Leads and associated Contacts together if contact data is valid.
        if contact.validate_contact_data() == True:
            lead.add_or_update_lead(row, leads)
            lead.add_contact(contact, leads, row)
        else:
        # If contact data is invalid it is tracked in the 'errors' list 
            if not lead.lead_exists(errors, row["Company"]):
                errors.append(lead)
            print(f"invalid contact! {contact.to_dict()}")

####  Removing Leads grouped with Contacts that have invalid data. ### 
for error in errors:
    for lead in leads:
        if lead.name == error.name:
            leads.remove(lead)

###  Importing Leads grouped with Contacts provided the associated contact in a group didn't have errors. ### 
# Set API Key
api_key = os.getenv("CLOSE_API_KEY")
api = Client(api_key)

for lead in leads:
    try:
        response = api.post('lead', data=lead.to_dict())
        print(response)
    except Exception as e:
        print(f"{lead}: Lead could not be posted because {str(e)}")

### Generating CSV with State Revenue report ### 
# Group the Leads by US State
state_data = Lead.group_leads_by_state(leads)

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


for lead in leads:
    print(lead.to_dict())
count = len(leads)
print(f"Job Done!! total leads imported: {count}")
