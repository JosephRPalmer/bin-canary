from datetime import datetime

class CouncilAdaptor:

    def __init__(self, name, location, country, colour_map):
        self.name = name
        self.location = location
        self.country = country
        self.colour_map = colour_map

    def extract_bin_dates(self, door_number, postcode):
        #override this and return a map of waste type and collection date
        pass

    def format_date(self, date):

        # Assuming the input date is a string in the format "Monday, 24 March 2025"
        date_obj = datetime.strptime(date, "%A, %d %B %Y")
        date = date_obj.strftime("%d/%m/%Y")
        return date

    def clean_string(self, string):
        return string.strip().replace("\n", " ").replace("\r", " ").replace("\t", " ").replace("(", "").replace(")", "")

    def assign_colour(self, waste_type):
        # Assign a colour to the waste type
        return self.colour_map.get(waste_type)
