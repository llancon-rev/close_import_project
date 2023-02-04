# close_import_project

Python Version: 3.8.5

The script has 3 main components. From lines 17 to 94 the logic needed to be extracted into some helper methods to make the import code more readable and probably also easier to mainain for future use. The helper methods ensure that the Leads are created without being duplicated and with the custom fields data.

From lines 96 to 156, is the main part of the code that imports leads and contacts. However before each row is imported, the email and phone number are validated to ensure the data is cleanly imported into Close. This follows the same pattern that was observed when testing the CSV file with the Close import CSV feature, as it will not import specific rows that have either an invalid email or phone number. At the moment, this script will raise an error if there was a API failure to debug further. A further optimization could be to generate a CSV that includes the rows of data that were not imported which would probably be useful to troubleshoot bad data. 

Finally, in Part 2 of the project it was to generate a CSV that is a Report of the Revenue per State. From lines 158 to 189 the report is generate by grouping all leads by US State and then creating the output CSV 'State Revenue Report.csv'. In order to calculate the median revenue, the statistics module was used. 

Need to validate email addresses and phone numbers. Seems best to skip rows with either invalid email addresses or phone numbers.
Decided to use 'validate_email 1.3' and 'phonenumbers 8.13.5' to validate contact data before it is imported. 