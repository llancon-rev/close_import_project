import unittest
from closeio_api import Client
import sys
import io
sys.path.append('.')
from lead import Lead

class TestLead(unittest.TestCase):
    def setUp(self):
        self.lead  = Lead("Close test", {
            Lead.FIELDS["company_founded"] : "01.01.2011",
            Lead.FIELDS["company_revenue"] : "$1,000,000,000.01",
            Lead.FIELDS["company_us_state"] : "California"
        })
        self.leads = [Lead("Close test", {
            Lead.FIELDS["company_founded"] : "01.01.2011",
            Lead.FIELDS["company_revenue"] : "$1,000,000,000.01",
            Lead.FIELDS["company_us_state"] : "California"
            }),
            Lead("Close test2", {
            Lead.FIELDS["company_founded"] : "01.01.2011",
            Lead.FIELDS["company_revenue"] : "$1,000,000,000.01",
            Lead.FIELDS["company_us_state"] : "California"
            })]

    def test_lead_name(self):
        self.assertEqual(self.lead.name, "Close test")

    def test_leads_count(self):
        self.assertEqual(len(self.leads), 2)

    def test_leads_post_no_api_key_error(self):
        api_key = None
        close_api = Client(api_key)
        captured_output = io.StringIO()
        # save stdout to a variable
        sys.stdout = captured_output

        Lead.post_leads(self.leads, close_api, errors=[])

        # restore stdout to ensure each test is isolated
        sys.stdout = sys.__stdout__
        
        expected_output = f"{self.lead.name} Lead could not be posted because: Must specify api_key."
        self.assertIn(expected_output, captured_output.getvalue())

    def test_leads_post_tracks_errors(self):
        errors=[]
        api_key = None
        close_api = Client(api_key)
        Lead.post_leads(self.leads, close_api, errors)
        self.assertEqual(len(self.leads), 0)
        self.assertEqual(len(errors), 2)        

if __name__ == '__main__':
    unittest.main()
