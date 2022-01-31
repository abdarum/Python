import datetime
import locale
import logging
import os
import time

import json_logging  # logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

#############################
######  User Settings  ######
#############################
bossa_url = 'https://bossa.pl/analizy/dywidendy'
bossa_file_path = r'C:\Users\Kornel\Desktop\tmp\Dywidendy\20220104_230700_Dywidendy _ Dom Maklerski Banku Ochrony Środowiska.html'

#############################
##### GLOBAL Variables ######
#############################

file_datestamp_format = '%Y%m%d_%H%M%S'
__init_datestamp = datetime.datetime.now().strftime(file_datestamp_format)
gen_logs_dir_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "gen", "logs"))

# # logging gear
# json_logging.init_non_web(enable_json=True)
logger = logging.getLogger("duplicated_photos_remove-logger")
logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler(sys.stdout))

log_filename = "dividend_list_log_" + __init_datestamp + ".json"
log_file_path = os.path.abspath(os.path.join(gen_logs_dir_path, log_filename))
logger.addHandler(logging.FileHandler(log_file_path))

logger.info("Dividend listing init. Logging timestamp: {}".format(__init_datestamp))
print("Log stored at: {}".format(log_file_path))

#############################
######     Classes     ######
#############################
class ErrorDef:
    PARSE_STOOQ_OPERATION_TABLE_NOT_DIVIDEND_IN_ROW = 'Error parsing, row in the Stooq operation table. Operation different than dividend'

class DividendItem:
    def __init__(self, date=None, percent=None, nominal=None, rights_issue=None,
            share_price_date=None, share_price_nominal=None):
        self.date = date
        self.percent = percent
        self.nominal = nominal
        self.rights_issue = rights_issue
        self.share_price_date = share_price_date
        self.share_price_nominal = share_price_nominal

        logger.info("DividendItem created: {}".format(str(self)))

    def __str__(self):
        return str(self.__dict__)

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

        logger.info("DividendCompanyItem created: {}".format(str(self)))

    def __str__(self):
        return str(self.__dict__)

class DividendCompaniesContainer:
    items_list = []

    #############################
    ###### Class constants ######
    #############################
    BOSSA_INSTRUMENTS_URL = '/notowania/instrumenty/'
    BIZNESRADAR_INSTRUMENTS_URL = 'https://www.biznesradar.pl/operacje/{}' # next long name of instrument e.g. ATLANTAPL
    STOOQ_INSTRUMENTS_URL = 'https://stooq.pl/q/m/?s={}' # next short name of instrument e.g. zwc
    STOOQ_INSTRUMENT_DATA_POINTS_URL = 'https://stooq.pl/q/a2/?s={}&i=w&t=c&a=ln&z=3000&l=0&d=1&ch=0&f=0&lt=58&r=0&o=1' # csv with data
    HTTP_TIMEOUT_SECONDS = 5

    #############################
    ######  Class methods  ######
    #############################
    def __init__(self):
        logger.info("DividendCompaniesContainer init")
        locale.setlocale(locale.LC_ALL, "pl_PL.utf8")
        logger.info("Set locale to {}".format(locale.getlocale()))
        # pl_datetime_now = datetime.datetime.now().strftime("%d %B %Y godz: %H:%M:%S")
        self._init_webdriver()

    def _init_webdriver(self):
        # init web driver
        self.script_parent_dir_path = os.path.dirname(os.path.abspath(__file__))
        self.download_dir_path = os.path.join(self.script_parent_dir_path, os.pardir, 'gen', 'downloads')
        firefox_profile = webdriver.FirefoxProfile()

        firefox_profile.set_preference("browser.download.folderList",2)
        firefox_profile.set_preference("browser.download.manager.showWhenStarting", False)
        firefox_profile.set_preference("browser.download.dir", self.download_dir_path)
        firefox_profile.set_preference("browser.helperApps.neverAsk.saveToDisk","text/csv")

        self.driver = webdriver.Firefox(firefox_profile=firefox_profile)
        logger.info("Firefox selenium webdriver init")


    def append(self, item):
        self.items_list.append(item)
        logger.info("Add Dividend Company {} to items_list".format(item))

    def __get_soup_from_file(self, file_path):
        with open(file_path, 'r') as file:
            html_str = file.read()
        
        soup = BeautifulSoup(html_str, 'html.parser')
        return soup

    def __get_soup_from_url(self, url):
        logger.info("Get soup from url website {}".format(url))
        self.driver.get(url)
        time.sleep(self.HTTP_TIMEOUT_SECONDS)
        html_str = self.driver.page_source
        
        soup = BeautifulSoup(html_str, 'html.parser')
        return soup

    def __webdriver_agree_cookies_stooq(self):
        buttons = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Zgadzam się')]")

        for btn in buttons:
            btn.click()
            time.sleep(self.HTTP_TIMEOUT_SECONDS)
            logger.info("Using cookies agreed at stooq website")
            self.driver.refresh()
            time.sleep(self.HTTP_TIMEOUT_SECONDS)

    
    def __webdriver_daily_limit_occured_stooq(self):
        buttons = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Odblokuj dostęp...')]")

        for btn in buttons:
            btn.click()
            # TODO
            logger.info("Script came across daily limit of fetched data from website")
            logger.error("WARNING: automatic parsing should be added !!!")
            print("WARNING: automatic parsing should be added !!!")
            time.sleep(self.HTTP_TIMEOUT_SECONDS)
            self.driver.refresh()
            time.sleep(self.HTTP_TIMEOUT_SECONDS)


    def _parse_stooq_operation_table(self, table_html=None, data_points=None):
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
                        try:
                            date_str = row_dict.get(key).split(', ')[1]
                            date_obj = datetime.datetime.strptime(date_str, '%d %b %Y')
                            
                            row_dict[key] = date_obj
                        except:
                            pass
                        
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

        # TODO
        # get val from data_points
        # self.share_price_date = share_price_date
        # self.share_price_nominal = share_price_nominal
        # https://stackoverflow.com/questions/66165563/given-a-specific-date-find-the-next-date-in-the-list-using-python

        return dividends_list


    def parse_stooq_data_points_website(self, short_name=None):
        data_points_page_url = self.STOOQ_INSTRUMENT_DATA_POINTS_URL.format(short_name)
        logger.info("Download and parse data points collected form {}".format(data_points_page_url))
        self.driver.get(data_points_page_url)
        time.sleep(self.HTTP_TIMEOUT_SECONDS)
        data_points_item = self.driver.find_element(By.ID, 'csv_')
        data_points_item.click()
        # TODO  parse csv saved in self.download_dir_path - ATP_w.csv = '{}_w.csv'.format(short_name)

        return None

    def parse_stooq_operations_website(self, short_name=None):
        dividend_url = self.STOOQ_INSTRUMENTS_URL.format(short_name)
        logger.info("Parse stooq operations website {}".format(dividend_url))
        self.driver.get(dividend_url)
        time.sleep(self.HTTP_TIMEOUT_SECONDS)
        self.__webdriver_agree_cookies_stooq()
        self.__webdriver_daily_limit_occured_stooq()

        # Dividend list table - fth1
        table_item = self.driver.find_element(By.ID, 'fth1')
        dividend_table_html = table_item.get_attribute('innerHTML')

        data_points = self.parse_stooq_data_points_website(short_name)

        dividends_list = self._parse_stooq_operation_table(dividend_table_html, data_points)

        ret_dict = {}
        ret_dict['dividends_list'] = dividends_list

        return ret_dict


    def _parse_biznesradar_profile_summary_table(self, table_html=None):
        html_str = table_html

        table = BeautifulSoup(html_str, 'html.parser')

        ret_val_dict = {'sector_gpw': None, 'sector_name': None}
        for row_idx, row in enumerate(table.find_all('tr')):
            desc = row.find_all('th')
            val = row.find_all('td')
            if len(desc) > 0:
                desc = desc[0]
            if len(val) > 0:
                val = val[0]
            if desc.text == 'Sektor:':
                ret_val_dict['sector_gpw'] = val.text
            if desc.text == 'Branża:':
                ret_val_dict['sector_name'] = val.text

        for key in ret_val_dict.keys():
            ret_val_dict[key] = ret_val_dict.get(key).replace('\n', '')

        return ret_val_dict

    def parse_biznesradar_operations_website(self, long_name=None):
        url = self.BIZNESRADAR_INSTRUMENTS_URL.format(long_name)
        logger.info("Parse sector from BiznesRadar website {}".format(url))
        self.driver.get(url)
        time.sleep(self.HTTP_TIMEOUT_SECONDS)

        # # <table class="profileSummary">
        table_item = self.driver.find_element(By.CLASS_NAME, 'profileSummary')

        table_html = table_item.get_attribute('innerHTML')
        ret_val_dict = self._parse_biznesradar_profile_summary_table(table_html)

        return ret_val_dict


    def parse_bossa_dividend_html(self, bossa_file_path=None, bossa_url=None):
        assert bossa_file_path or bossa_url, 'Source wasn\'t set correctly'

        soup = None
        if bossa_file_path:
            soup = self.__get_soup_from_file(bossa_file_path)
        elif bossa_url:
            soup = self.__get_soup_from_url(bossa_url)

        for link in soup.find_all('a'):
            link_url = link.get('href')
            if( not link_url is None and self.BOSSA_INSTRUMENTS_URL in link_url ):
                instrument_short = link_url.split(self.BOSSA_INSTRUMENTS_URL)[-1]
                instrument_long = link.text
                dividend_company_item = "https://bossa.pl{}".format(link_url)
                dividend_company_item = DividendCompanyItem(
                    bossa_instrument_url = dividend_company_item,
                    name_short = instrument_short,
                    name_long = instrument_long)
                self.append(dividend_company_item)

        print('test')

    def update_companies_list(self):
        for item in self.items_list:
            # dividends_list
            if len(item.dividends_list) == 0:
                stooq_content = self.parse_stooq_operations_website(item.name_short)
                dividends_list = stooq_content.get('dividends_list')
                item.dividends_list.extend(dividends_list)
            
            # biznesradar
            if None in [item.sector_gpw, item.sector_name]:
                biznesradar_content = self.parse_biznesradar_operations_website(item.name_long)
                sector_gpw = biznesradar_content.get('sector_gpw')
                sector_name = biznesradar_content.get('sector_name')
                if item.sector_gpw is None:
                    item.sector_gpw=sector_gpw
                if item.sector_name is None:
                    item.sector_name=sector_name


            print('test')


#############################
###### BUSINESS LOGIC  ######
#############################
dividends_list = DividendCompaniesContainer()
dividends_list.parse_bossa_dividend_html(bossa_url=bossa_url)
# dividends_list.parse_bossa_dividend_html(bossa_file_path=bossa_file_path)
dividends_list.update_companies_list()
print('done')
# https://www.bankier.pl/wiadomosc/Inwestowanie-dywidendowe-Poradnik-dla-poczatkujacych-7601780.html

