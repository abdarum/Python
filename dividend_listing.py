import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

#############################
##### GLOBAL CONSTANTS ######
#############################

#############################
######  User Settings  ######
#############################
bossa_url = 'https://bossa.pl/analizy/dywidendy'
bossa_file_path = r'C:\Users\Kornel\Desktop\tmp\Dywidendy\20220104_230700_Dywidendy _ Dom Maklerski Banku Ochrony Środowiska.html'


#############################
######     Classes     ######
#############################
class ErrorDef:
    PARSE_STOOQ_OPERATION_TABLE_NOT_DIVIDEND_IN_ROW = 'Error parsing, row in the Stooq operation table. Operation different than dividend'

class DividendItem:
    def __init__(self, date=None, percent=None, nominal=None, rights_issue=None):
        self.date = date
        self.percent = percent
        self.nominal = nominal
        self.rights_issue = rights_issue

class DividendCompanyItem:
    def __init__(self,
            bossa_instrument_url=None,
            name_short=None,
            name_long=None,
            sector_gpw=None,
            sector_name=None,
            dividends_list=None):
        self.bossa_instrument_url = bossa_instrument_url
        self.name_short = name_short
        self.name_long = name_long
        self.sector_gpw = sector_gpw
        self.sector_name = sector_name
        self.dividends_list = []
        if dividends_list != None:
            assert isinstance(dividends_list, list)
            self.dividends_list.extend(dividends_list)


    def __str__(self):
        return str(self.__dict__)

class DividendCompaniesContainer:
    items_list = []

    #############################
    ###### Class constants ######
    #############################
    BOSSA_INSTRUMENTS_URL = 'https://bossa.pl/notowania/instrumenty/'
    BIZNESRADAR_INSTRUMENTS_URL = 'https://www.biznesradar.pl/operacje/' # next long name of instrument e.g. ATLANTAPL
    STOOQ_INSTRUMENTS_URL = 'https://stooq.pl/q/m/?s=' # next short name of instrument e.g. zwc
    HTTP_TIMEOUT_SECONDS = 5

    #############################
    ######  Class methods  ######
    #############################
    def __init__(self):
        # init web driver
        binary = FirefoxBinary(r'C:\Program Files\Mozilla Firefox\firefox.exe')
        self.driver = webdriver.Firefox(firefox_binary=binary)

    def append(self, item):
        self.items_list.append(item)

    def __get_soup_from_file(self, file_path):
        with open(file_path, 'r') as file:
            html_str = file.read()
        
        soup = BeautifulSoup(html_str, 'html.parser')
        return soup

    def __get_soup_from_url(self, url, timeout=None):
        http_timeout = self.HTTP_TIMEOUT_SECONDS
        time.sleep(http_timeout)
        r = requests.get( url )
        if timeout:
            http_timeout = timeout
        data = r.json()

        html_str = r.text
        # html_str = requests.get(url, timeout=(3.05, 3000), headers=self.headers).text
        
        soup = BeautifulSoup(html_str, 'html.parser')
        return soup

    def __webdriver_agree_cookies_stood(self):
        buttons = self.driver.find_elements_by_xpath("//*[contains(text(), 'Zgadzam się')]")

        for btn in buttons:
            btn.click()
            time.sleep(self.HTTP_TIMEOUT_SECONDS)

    def parse_stooq_operation_table(self, table_html=None):
        err_method = None
        html_str = table_html

        table = BeautifulSoup(html_str, 'html.parser')
        columns_names = {}

        dividends_list = []        
        for row_idx, row in enumerate(table.find_all('tr')):
            err_row = None
            columns = row.find_all('td')
            if len(columns) == 0:
                columns = row.find_all('th')
                columns = [elem.text for elem in columns]
                for col_idx, col_val in enumerate(columns):
                    columns_names[col_idx] = col_val
            else:
                columns = [elem.text for elem in columns]
                row_dict = {}

                for col_idx, col_val in enumerate(columns):
                    row_dict[columns_names[col_idx]] = col_val
                
                # parse values - adjust to the schema
                for key in row_dict.keys():
                    if key == 'Data':
                        row_dict[key] = row_dict.get(key)
                    elif key == 'Zdarzenie':
                        if row_dict.get(key).startswith('Dywidenda '):
                            val_str = row_dict.get(key).replace('Dywidenda ', '').replace('%', '')
                            try:
                                row_dict[key] = float(val_str)
                            except:
                                pass
                        else:
                            err_row = ErrorDef.PARSE_STOOQ_OPERATION_TABLE_NOT_DIVIDEND_IN_ROW

                    elif key == 'Nominalnie':
                        try:
                            row_dict[key] = float(row_dict.get(key))
                        except:
                            pass
                        
                    elif key == 'Dzielnik':
                        try:
                            row_dict[key] = float(row_dict.get(key))
                        except:
                            pass

                dividend_item = DividendItem(
                    date=row_dict.get('Data'), 
                    percent=row_dict.get('Zdarzenie'),
                    nominal=row_dict.get('Nominalnie'),
                    rights_issue=row_dict.get('Dzielnik')
                    )
                
                if err_row:
                    print('Parsing error, dividend_item skipped. Dividend item: {}. Error {}'.format(dividend_item, err_row))
                else:
                    dividends_list.append(dividend_item)

        return dividends_list


    def parse_stooq_operations_website(self, short_name=None):
        url = self.STOOQ_INSTRUMENTS_URL + short_name
        self.driver.get(url)
        time.sleep(self.HTTP_TIMEOUT_SECONDS)
        self.__webdriver_agree_cookies_stood()

        # fth1
        table_item = self.driver.find_element_by_id('fth1')
        # table

        table_html = table_item.get_attribute('innerHTML')
        dividends_list = self.parse_stooq_operation_table(table_html)

        ret_dict = {}
        ret_dict['dividends_list'] = dividends_list

        return ret_dict

    def parse_bossa_dividend_html(self, bossa_file_path=None, bossa_url=None):
        assert bossa_file_path or bossa_url, 'Source wasn\'t set correctly'

        soup = None
        if bossa_file_path:
            soup = self.__get_soup_from_file(bossa_file_path)
        elif bossa_url:
            soup = self.__get_soup_from_url(bossa_url)

        for link in soup.find_all('a'):
            link_url = link.get('href')
            if( not link_url is None and link_url.startswith(self.BOSSA_INSTRUMENTS_URL) ):
                instrument_short = link_url.replace(self.BOSSA_INSTRUMENTS_URL, '')
                instrument_long = link.text
                stooq_content = self.parse_stooq_operations_website(instrument_short)
                dividends_list = stooq_content.get('dividends_list')

                dividend_company_item = DividendCompanyItem(
                    bossa_instrument_url = link_url,
                    name_short = instrument_short,
                    name_long = instrument_long)


                self.append(dividend_company_item)
                print('test')

#############################
###### BUSINESS LOGIC  ######
#############################
dividends_list = DividendCompaniesContainer()
dividends_list.parse_bossa_dividend_html(bossa_file_path=bossa_file_path)
print('done')
# https://www.bankier.pl/wiadomosc/Inwestowanie-dywidendowe-Poradnik-dla-poczatkujacych-7601780.html