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
    dict_val = {}
    
    DIVIDEND_COMPANY_DICT_KEY_BOSSA_INSTRUMENT_URL, \
    DIVIDEND_COMPANY_DICT_KEY_NAME_SHORT, \
    DIVIDEND_COMPANY_DICT_KEY_NAME_LONG, \
    DIVIDEND_COMPANY_DICT_KEY_PERCENT, \
    DIVIDEND_COMPANY_DICT_KEY_NOMINAL, \
    DIVIDEND_COMPANY_DICT_KEY_SECTOR_GPW, \
    DIVIDEND_COMPANY_DICT_KEY_SECTOR_NAME, \
    DIVIDEND_COMPANY_DICT_KEY___COUNTER \
    = range(8)

    __DICT_KEY = {
        DIVIDEND_COMPANY_DICT_KEY_BOSSA_INSTRUMENT_URL: 'bossa_instrument_url',
        DIVIDEND_COMPANY_DICT_KEY_NAME_SHORT: 'name_short',
        DIVIDEND_COMPANY_DICT_KEY_NAME_LONG: 'name_long',
        DIVIDEND_COMPANY_DICT_KEY_PERCENT: 'percent',
        DIVIDEND_COMPANY_DICT_KEY_NOMINAL: 'nominal',
        DIVIDEND_COMPANY_DICT_KEY_SECTOR_GPW: 'sector_GPW',
        DIVIDEND_COMPANY_DICT_KEY_SECTOR_NAME: 'sector_name',
        }

    __DICT_NAME = {
        DIVIDEND_COMPANY_DICT_KEY_BOSSA_INSTRUMENT_URL: 'Bossa instrument url',
        DIVIDEND_COMPANY_DICT_KEY_NAME_SHORT: 'Name short',
        DIVIDEND_COMPANY_DICT_KEY_NAME_LONG: 'Name long',
        DIVIDEND_COMPANY_DICT_KEY_PERCENT: 'Percent value',
        DIVIDEND_COMPANY_DICT_KEY_NOMINAL: 'Nominal value',
        DIVIDEND_COMPANY_DICT_KEY_SECTOR_GPW: 'Sector GPW',
        DIVIDEND_COMPANY_DICT_KEY_SECTOR_NAME: 'Sector name',
        }

    @staticmethod
    def type_to_key(status: int):
        return DividendCompanyItem.__DICT_KEY[status]

    @staticmethod
    def type_to_name(status: int):
        return DividendCompanyItem.__DICT_NAME[status]

    def dict_raw(self):
        return self.dict_val

    def dict_key(self):
        ret_dict = {} 
        for i in self.dict_val.keys():
            ret_dict[self.type_to_key(i)] = self.dict_val[i]
        return ret_dict

    def dict_name(self):
        ret_dict = {} 
        for i in self.dict_val.keys():
            ret_dict[self.type_to_name(i)] = self.dict_val[i]
        return ret_dict

    def __str__(self):
        return str(self.dict_key())

    def get_val(self, key):
        return self.dict_val.get(key)

    def set_val(self, key, val=None):
        if val is not None:
            self.dict_val[key] = val

    def bossa_instrument_url(self, val=None):
        cur_key = self.DIVIDEND_COMPANY_DICT_KEY_BOSSA_INSTRUMENT_URL
        self.set_val(cur_key, val)
        return self.get_val(cur_key)

    def name_short(self, val=None):
        cur_key = self.DIVIDEND_COMPANY_DICT_KEY_NAME_SHORT
        self.set_val(cur_key, val)
        return self.get_val(cur_key)
 
    def name_long(self, val=None):
        cur_key = self.DIVIDEND_COMPANY_DICT_KEY_NAME_LONG
        self.set_val(cur_key, val)
        return self.get_val(cur_key)

    def percent(self, val=None):
        cur_key = self.DIVIDEND_COMPANY_DICT_KEY_PERCENT
        self.set_val(cur_key, val)
        return self.get_val(cur_key)

    def nominal(self, val=None):
        cur_key = self.DIVIDEND_COMPANY_DICT_KEY_NOMINAL
        self.set_val(cur_key, val)
        return self.get_val(cur_key)

    def sector_gpw(self, val=None):
        cur_key = self.DIVIDEND_COMPANY_DICT_KEY_SECTOR_GPW
        self.set_val(cur_key, val)
        return self.get_val(cur_key)

    def sector_name(self, val=None):
        cur_key = self.DIVIDEND_COMPANY_DICT_KEY_SECTOR_NAME
        self.set_val(cur_key, val)
        return self.get_val(cur_key)

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
                dividend_company_item.bossa_instrument_url(link_url)
                dividend_company_item.name_short(instrument_short)
                dividend_company_item.name_long(instrument_long)

                self.append(dividend_company_item)

#############################
###### BUSINESS LOGIC  ######
#############################
dividends_list = DividendCompaniesContainer()
dividends_list.parse_bossa_dividend_html(bossa_file_path=bossa_file_path)
print('done')
