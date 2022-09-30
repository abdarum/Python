# Output format
# 24 LIP - SZTOKHOLM-SKAVSTA(NYO) -> WROCŁAW(WRO) - 17:10 -> 18:45 - 1h 35m - W61872 - 318 kr(142,78zł)
# 22 LIP - Wrocław(WRO) -> Stockholm Arlanda(ARN) - 13:00 -> 14:55 - 1h 55m - FR7606 - 178,00 zł

dst_file_path = r"C:\Kornel\GitHub\Python\Trip_Management\dest_html.html"


class Flight:
    class Airport:
        def __init__(self):
            self.name = None
            self.iata_code = None

        def __init__(self, name, iata_code):
            self.__init__()
            self.name = name
            self.iata_code = iata_code

        def __str__(self):
            ret_str = ""
            if self.iata_code and self.name:
                ret_str = "{}({})".format(self.name, self.iata_code)
            elif self.name:
                ret_str = "{}".format(self.name)
            elif self.iata_code:
                ret_str = "{}".format(self.iata_code)
            return ret_str
        
    def __init__(self):
        self.dep_timestamp = None
        self.dep_airport = None
        self.arr_timestamp = None
        self.arr_airport = None
        self.flight_duration = None
        self.flight_number = None
        self.flight_price = None

class SkyLinesParser:
    def __init__(self):
        self.input_html_path = None
        self.parsed_flight = None

    def set_input_html(self, path):
        self.input_html_path = path

    def parse_html(self):
        pass

    def print_flight(self):
        print_str = ""
        print_str = "TEST print"
        print(print_str)
        pass


dest_parser = SkyLinesParser()
dest_parser.set_input_html(dst_file_path)
dest_parser.parse_html()
dest_parser.print_flight()




