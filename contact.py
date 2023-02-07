# Importing modules to validate email and phone numbers
import validate_email
import phonenumbers

class Contact:
    def __init__(self, name, emails, phones, row):
        self.name = name
        self.emails = [{"email": emails, "type": "office"}]
        self.phones = [{"phone": phones, "type": "office"}]
        self.handle_empty_contact_name(row)

    def to_dict(self):
        result = {"name": self.name}
        # Excludes empty attributes from dictionary as this will be called when the API call is executed.
        if self.emails[0]["email"] not in [None, '']:
            result["emails"] = self.emails
        if self.phones[0]["phone"] not in [None, '']:
            result["phones"] = self.phones
        return result
                
    def handle_empty_contact_name(self, row):
        if row["Contact Name"] in ['', None]:
            if row["Contact Emails"] not in ['', None]:
                self.name = row["Contact Emails"]
            else:
                self.name = row["Contact Phones"]
        else:
            self.name = row["Contact Name"]

    def parse_phone_number(self, phone):
        try:
            parsed_number = phonenumbers.parse(phone, None)
            return parsed_number
        except Exception as e:
            print(f"Could not parse phone number because: {str(e)} {phone}")

    def validate_phone(self, phone):
        try:
            phonenumbers.is_valid_number(phone)
        except Exception:
            return False
        return True

    def validate_contact_data(contact):
        parsed_number = contact.parse_phone_number(contact.phones[0]["phone"])
        phone = contact.phones[0]["phone"]
        email = contact.emails[0]["email"]

        if email == "" and phone == "":
            return True
        elif email == "" and contact.validate_phone(parsed_number):
            return True
        elif phone == "" and validate_email.validate_email(email):
            return True
        elif validate_email.validate_email(email) and contact.validate_phone(parsed_number):
            return True
        return False

