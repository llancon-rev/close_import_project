# close_import_project

Python Version: 3.8.5
Dependencies needed: 
```closeio_api
argparse
datetime
statistics
```

# How run the script:
```python
python import.py --start_date 01.01.1950 --end_date 31.01.2023

```

The script has 3 main components: a import, lead and contact component. The main part is the import file that contains the logic to import data from the source CSV file and also generate a US State revenue report in a CSV.

The lead and contact components contain the logic to eliminate invalid data. Each lead becomes invalid when it contains an associated contact that has bad contact data. For example an invalid phone number or email would invalidate a Lead even if it as other Contacts with good data. This follows the same pattern that was observed when testing Closes CSV import feature.

Once leads are verified to have good data the next stage is to ensure leads that have errors are removed from the import process. This is handled by tracking leads in a seperate 'errors' list. If the lead is in the 'errors' list, it will not be imported.

Once the leads are completely cleaned, only leads that have valid contact data, then the leads are imported to Close via a Post request to the Close API. 

The final stage is to create a US State revenue report. This is done by grouping the leads by state via the group_leads_by_state() function. This function returnts a dictionary of the states grouped with the company revenue data that will be used to generate the output CSV file. Finally once the lead State data is grouped together the script enters the final step, which iterates over the state data dictionary and writes the end result calculations to the output CSV. 

At the end script, the total number of leads added to Close is displayed in the terminal. 



It became necessary to create a Lead and Contact Class to organize the logic that each object would entail. The lead.py file contains logic that would involve processing leads at different stages of the import process. While the contact.py file has a similar functionality, in the sense of organizing logic that would process contacts, as well. Grouping logic into seperate classes will make the code easier to read and understand.

From lines 17 to 94 the logic needed to be extracted into some helper methods to make the import code more readable and probably also easier to mainain for future use. The helper methods ensure that the Leads are created without being duplicated and with the custom fields data.

From lines 96 to 156, is the main part of the code that imports leads and contacts. However before each row is imported, the email and phone number are validated to ensure the data is cleanly imported into Close. This follows the same pattern that was observed when testing the CSV file with the Close import CSV feature, as it will not import specific rows that have either an invalid email or phone number. At the moment, this script will raise an error if there was a API failure to debug further. A further optimization could be to generate a CSV that includes the rows of data that were not imported which would probably be useful to troubleshoot bad data. 

Finally, in Part 2 of the project it was to generate a CSV that is a Report of the Revenue per State. From lines 158 to 189 the report is generate by grouping all leads by US State and then creating the output CSV 'State Revenue Report.csv'. In order to calculate the median revenue, the statistics module was used. 

Need to validate email addresses and phone numbers. Seems best to skip rows with either invalid email addresses or phone numbers.
Decided to use 'validate_email 1.3' and 'phonenumbers 8.13.5' to validate contact data before it is imported. 