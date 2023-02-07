from closeio_api import Client

class Lead:
    def __init__(self, name, custom_fields):
        self.name = name
        self.custom_fields = custom_fields
        self.contacts = []

    FIELDS = {
            "company_founded" : "custom.cf_QunpCuMvHJxiV5QjYrusGG9D8Uzi08CsS5jGTbxHfm4",
            "company_revenue" : "custom.cf_CVsgcfWqI7sz5KjvSckz34AtB6lEoKnctkA5C610TZb",
            "company_us_state" : "custom.cf_lS1kT2uuH2KChn2UjzK0NRLhceKWudOWzhySB53GR5w"
        }
    
    def to_dict(self):
        result = {"name": self.name,
                  "contacts": [contact.to_dict() for contact in self.contacts]
                  }
        # Excludes empty custom fields when to_dict is called as it is called when executing the post request to Close API
        if self.custom_fields[Lead.FIELDS["company_founded"]] not in [None, '']:
            result[Lead.FIELDS["company_founded"]] = self.custom_fields[Lead.FIELDS["company_founded"]]
        if self.custom_fields[Lead.FIELDS["company_revenue"]] not in [None, '']:
            result[Lead.FIELDS["company_revenue"]] = self.custom_fields[Lead.FIELDS["company_revenue"]]
        if self.custom_fields[Lead.FIELDS["company_us_state"]] not in [None, '']:
            result[Lead.FIELDS["company_us_state"]] = self.custom_fields[Lead.FIELDS["company_us_state"]]
        return result

    def __str__(self):
        return f"Company: {self.name}, Custom Fields: {self.custom_fields}, Contacts: {self.contacts}"

    def lead_exists(self, leads, name):
        for lead in leads:
            if lead.name == name:
                return True
        return False
            
    def update_fields(self, row):
        if self.custom_fields[Lead.FIELDS["company_founded"]] == "" and row['custom.Company Founded'] != '':
            self.custom_fields[Lead.FIELDS["company_founded"]] = row['custom.Company Founded']
        
        if self.custom_fields[Lead.FIELDS["company_revenue"]] == "" and row['custom.Company Revenue'] != '':
            self.custom_fields[Lead.FIELDS["company_revenue"]] = row['custom.Company Revenue']
        
        if self.custom_fields[Lead.FIELDS["company_us_state"]] == "" and row['Company US State'] != '':
            self.custom_fields[Lead.FIELDS["company_us_state"]] = row['Company US State']

    def add_or_update_lead(self, row, leads):
        if not self.lead_exists(leads, row["Company"]):
            leads.append(self)
        else:
            for lead in leads:
                if lead.name == row["Company"]:
                    lead.update_fields(row)
                    break

    def add_contact(self, contact, leads, row):
        for lead in leads:
            if lead.name == row["Company"]:
                lead.contacts.append(contact)

    def missing_state(lead):
        return lead.custom_fields[Lead.FIELDS["company_us_state"]] in [None,'']
    
    def missing_revenue(lead):
        return lead.custom_fields[Lead.FIELDS["company_revenue"]] in [None, '']
    
    def missing_state_or_revenue(lead):
        if lead.missing_state() or lead.missing_revenue():
            return True
        else:
            return False

    def group_leads_by_state(leads):
        state_data = {}
        for lead in leads:
            state = lead.custom_fields[Lead.FIELDS["company_us_state"]]
            if state not in state_data and not lead.missing_state_or_revenue():
                state_data[state] = {
                'companies': [],
                'revenues': []
            }
        # Skip over leads that have missing State or Revenue
            if not lead.missing_state_or_revenue():
                state_data[state]['companies'].append(lead.name)
                try:
                    state_data[state]['revenues'].append(float(lead.custom_fields[Lead.FIELDS["company_revenue"]][1:].replace(',', '')))
                except Exception as e:
                    print(f"{lead}: Revenue could not be converted to float because {str(e)}")
        return state_data
