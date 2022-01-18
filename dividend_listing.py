import requests
from bs4 import BeautifulSoup


#############################
######    CONSTANTS    ######
#############################
BOSSA_INSTRUMENTS_URL = 'https://bossa.pl/notowania/instrumenty/'

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
}


#############################
######  User Settings  ######
#############################
bossa_url = 'https://bossa.pl/analizy/dywidendy'
bossa_file_path = r'C:\Users\Kornel\Desktop\tmp\Dywidendy\20220104_230700_Dywidendy _ Dom Maklerski Banku Ochrony Środowiska.html'


#############################
######     Classes     ######
#############################

class DividendCompanyItem:
    def __init__(self):
        self.bossa_instrument_url = None
        self.name_short = None
        self.name_long = None
        self.percent = None
        self.nominal = None
        self.sector_gpw = None
        self.sector_name = None

    def __str__(self):
        return str(self.__dict__)

class DividendCompaniesContainer:
    items_list = []

    def append(self, item):
        self.items_list.append(item)

    def __get_soup_from_file(self, file_path):
        with open(file_path, 'r') as file:
            html_str = file.read()
        
        soup = BeautifulSoup(html_str, 'html.parser')
        return soup

    def __get_soup_from_url(self, url):
        html_str = requests.get(url, headers=headers).text
        
        soup = BeautifulSoup(html_str, 'html.parser')
        return soup

    def parse_bossa_dividend_html(self, bossa_file_path=None, bossa_url=None):
        assert bossa_file_path or bossa_url, 'Source wasn\'t set correctly'

        soup = None
        if bossa_file_path:
            soup = self.__get_soup_from_file(bossa_file_path)
        elif bossa_url:
            soup = self.__get_soup_from_url(bossa_url)

        for link in soup.find_all('a'):
            link_url = link.get('href')
            if( not link_url is None and link_url.startswith(BOSSA_INSTRUMENTS_URL) ):
                instrument_short = link_url.replace(BOSSA_INSTRUMENTS_URL, '')
                instrument_long = link.text

                dividend_company_item = DividendCompanyItem()
                dividend_company_item.bossa_instrument_url = link_url
                dividend_company_item.name_short = instrument_short
                dividend_company_item.name_long = instrument_long

                self.append(dividend_company_item)

#############################
###### BUSINESS LOGIC  ######
#############################
dividends_list = DividendCompaniesContainer()
dividends_list.parse_bossa_dividend_html(bossa_file_path=bossa_file_path)
print('done')
