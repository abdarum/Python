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

class DividendItem:
    dict_val = {}
    DIVIDEND_DICT_KEY_BOSSA_INSTRUMENT_URL, \
    DIVIDEND_DICT_KEY_NAME_SHORT, \
    DIVIDEND_DICT_KEY_NAME_LONG, \
    DIVIDEND_DICT_KEY_PERCENT, \
    DIVIDEND_DICT_KEY_NOMINAL, \
    DIVIDEND_DICT_KEY_SECTOR_GPW, \
    DIVIDEND_DICT_KEY_SECTOR_NAME, \
    DIVIDEND_DICT_KEY___COUNTER \
    = range(8)

    __DICT_KEY = {
        DIVIDEND_DICT_KEY_BOSSA_INSTRUMENT_URL: 'bossa_instrument_url',
        DIVIDEND_DICT_KEY_NAME_SHORT: 'name_short',
        DIVIDEND_DICT_KEY_NAME_LONG: 'name_long',
        DIVIDEND_DICT_KEY_PERCENT: 'percent',
        DIVIDEND_DICT_KEY_NOMINAL: 'nominal',
        DIVIDEND_DICT_KEY_SECTOR_GPW: 'sector_GPW',
        DIVIDEND_DICT_KEY_SECTOR_NAME: 'sector_name',
        }

    __DICT_NAME = {
        DIVIDEND_DICT_KEY_BOSSA_INSTRUMENT_URL: 'Bossa instrument url',
        DIVIDEND_DICT_KEY_NAME_SHORT: 'Name short',
        DIVIDEND_DICT_KEY_NAME_LONG: 'Name long',
        DIVIDEND_DICT_KEY_PERCENT: 'Percent value',
        DIVIDEND_DICT_KEY_NOMINAL: 'Nominal value',
        DIVIDEND_DICT_KEY_SECTOR_GPW: 'Sector GPW',
        DIVIDEND_DICT_KEY_SECTOR_NAME: 'Sector name',
        }

    @staticmethod
    def type_to_key(status: int):
        return DividendItem.__DICT_KEY[status]

    @staticmethod
    def type_to_name(status: int):
        return DividendItem.__DICT_NAME[status]

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

    def bossa_instrument_url(self, val=None):
        cur_key = self.DIVIDEND_DICT_KEY_BOSSA_INSTRUMENT_URL
        if val is None:
            return self.dict_val[cur_key]
        self.dict_val[cur_key] = val

    def name_short(self, val=None):
        cur_key = self.DIVIDEND_DICT_KEY_NAME_SHORT
        if val is None:
            return self.dict_val[cur_key]
        self.dict_val[cur_key] = val
 
    def name_long(self, val=None):
        cur_key = self.DIVIDEND_DICT_KEY_NAME_LONG
        if val is None:
            return self.dict_val[cur_key]
        self.dict_val[cur_key] = val

    def percent(self, val=None):
        cur_key = self.DIVIDEND_DICT_KEY_PERCENT
        if val is None:
            return self.dict_val[cur_key]
        self.dict_val[cur_key] = val

    def nominal(self, val=None):
        cur_key = self.DIVIDEND_DICT_KEY_NOMINAL
        if val is None:
            return self.dict_val[cur_key]
        self.dict_val[cur_key] = val

    def sector_gpw(self, val=None):
        cur_key = self.DIVIDEND_DICT_KEY_SECTOR_GPW
        if val is None:
            return self.dict_val[cur_key]
        self.dict_val[cur_key] = val

    def sector_name(self, val=None):
        cur_key = self.DIVIDEND_DICT_KEY_SECTOR_NAME
        if val is None:
            return self.dict_val[cur_key]
        self.dict_val[cur_key] = val

class DividendsContainer:
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

                dividend_item = DividendItem()
                dividend_item.bossa_instrument_url(link_url)
                dividend_item.name_short(instrument_short)
                dividend_item.name_long(instrument_long)

                self.append(dividend_item)
                print(link.get('href'))

#############################
###### BUSINESS LOGIC  ######
#############################
dividends_list = DividendsContainer()
dividends_list.parse_bossa_dividend_html(bossa_file_path=bossa_file_path)
