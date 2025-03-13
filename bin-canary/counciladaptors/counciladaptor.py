class CouncilAdaptor:

    def __init__(self, name, location, country):
        self.name = name
        self.location = location
        self.country = country

    def extract_bin_dates(self, door_number, postcode):
        #override this
        pass
