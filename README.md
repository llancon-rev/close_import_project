# A Script for Close API to import from CSV file written in Python 
Python Version: 3.8.5

## Set up:
1. It assumes the source CSV file is called "Close Sample Import File.csv"
2. Store the API Key in a file called ".vault" and place API Key in this format:
```
CLOSE_API_KEY=API key goes here
```

## Modules needed: 
```
closeio_api 2.0
argparse 1.1
datetime 
statistics 1.0.3.5
dotenv 0.21.1
validate_email 1.3
phonenumbers 8.13.5

```

## Running the script:

Example:

```bash
python import.py --start_date 01.01.1950 --end_date 31.01.2023

```
# How this script works:
The script has 3 main components: a import, lead and contact component. The main part is the import file that contains the logic to import data from the source CSV file and also generate a US State revenue report in a CSV.

The lead and contact components contain the logic to eliminate invalid data. Each lead becomes invalid when it contains an associated contact that has bad contact data. For example an invalid phone number or email would invalidate a Lead even if it as other Contacts with good data. This follows the same pattern that was observed when testing Closes CSV import feature.

Once leads are verified to have good data the next stage is to ensure leads that have errors are removed from the import process. This is handled by tracking leads in a seperate 'errors' list. If the lead is in the 'errors' list, it will not be imported.

Once the leads are completely cleaned, only leads that have valid contact data, then the leads are imported to Close via a Post request to the Close API. 

The final stage is to create a US State revenue report. This is done by grouping the leads by state via the group_leads_by_state() function. This function returnts a dictionary of the states grouped with the company revenue data that will be used to generate the output CSV file. Finally once the lead State data is grouped together the script enters the final step, which iterates over the state data dictionary and writes the end result calculations to the output CSV. 

At the end script, the total number of leads added to Close is displayed in the terminal. 

It became necessary to create a Lead and Contact Class to organize the logic that each object would entail. The lead.py file contains logic that would involve processing leads at different stages of the import process. While the contact.py file has a similar functionality, in the sense of organizing logic that would process contacts, as well. Grouping logic into seperate classes will make the code easier to read and understand.

