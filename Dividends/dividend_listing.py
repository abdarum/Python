import datetime
import json
import locale
import logging
import os
import pickle
import time

import json_logging  # logging
from bs4 import BeautifulSoup
from pandas_datareader import data as pdr
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
json_logging.init_non_web(enable_json=True)
logger = logging.getLogger("duplicated_photos_remove-logger")
logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler(sys.stdout))

log_filename = "dividend_list_log_" + __init_datestamp + ".json"
log_file_path = os.path.abspath(os.path.join(gen_logs_dir_path, log_filename))
logger.addHandler(logging.FileHandler(log_file_path))

logger.info("Dividend listing init. Logging timestamp: {}".format(__init_datestamp))
print("Log stored at: {}".format(log_file_path))

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, DividendItem):
        return obj.__dict__
    raise TypeError ("Type %s not serializable" % type(obj))

#############################
######     Classes     ######
#############################
class ErrorDef:
    PARSE_STOOQ_OPERATION_TABLE_NOT_DIVIDEND_IN_ROW = 'Error parsing, row in the Stooq operation table. Operation different than dividend'
    PARSE_DATE_FAILED = 'Error parsing, Parse date failed'

class ForceDef:
    FORCE_DISABLED = 'Force disabled'
    COMPANY_ADD_OVERWRITE_EXISTING_COMPANY = 'Company add - overwrite existing company'
    FETCH_BOSSA_COMPANIES_LIST = 'Fetch bossa companies list'

    @staticmethod
    def is_force_active(cur_permission, goal_permission):
        if isinstance(cur_permission, (str)):
            cur_permission = [cur_permission]
        if isinstance(goal_permission, (str)):
            goal_permission = [goal_permission]
        
        if ForceDef.FORCE_DISABLED in goal_permission or ForceDef.FORCE_DISABLED in cur_permission:
            return False

        for cur in cur_permission:
            if cur in goal_permission:
                return True

        return False


class BaseWebdriver:
    HTTP_TIMEOUT_SECONDS = 5

    def __init__(self):
        # init web driver
        self.script_parent_dir_path = os.path.dirname(os.path.abspath(__file__))
        self.download_dir_path = os.path.abspath(os.path.join(self.script_parent_dir_path, os.pardir, 'gen', 'downloads'))
        firefox_profile = webdriver.FirefoxProfile()

        firefox_profile.set_preference("browser.download.folderList",2)
        firefox_profile.set_preference("browser.download.manager.showWhenStarting", False)
        firefox_profile.set_preference("browser.download.dir", self.download_dir_path)
        firefox_profile.set_preference("browser.helperApps.neverAsk.saveToDisk","text/csv")

        self.driver = webdriver.Firefox(firefox_profile=firefox_profile)
        logger.info("Firefox selenium webdriver init")

    def get_soup_from_url(self, url):
        logger.info("Get soup from url website {}".format(url))
        self.driver.get(url)
        self.base_webdriver.sleep()
        html_str = self.driver.page_source
        
        soup = BeautifulSoup(html_str, 'html.parser')
        return soup

    def get_soup_from_file(self, file_path):
        with open(file_path, 'r') as file:
            html_str = file.read()
        
        soup = BeautifulSoup(html_str, 'html.parser')
        return soup
    
    def get(self, url):
        self.driver.get(url)

    def sleep(self, seconds=None):
        time.sleep(self.HTTP_TIMEOUT_SECONDS)

    def refresh(self):
        self.driver.refresh()

    def find_element(self, find_by, find_content):
        return self.driver.find_element(find_by, find_content)

    def find_elements(self, find_by, find_content):
        return self.driver.find_elements(find_by, find_content)
    

class StooqWebdriver:
    URL_INSTRUMENT = 'https://stooq.pl/q/m/?s={}' # next short name of instrument e.g. zwc
    SHARE_PRICE_VALUE_COUNTRY_SUFFIX = '.PL'
    SHARE_PRICE_VALUE_TIME_FORMAT = '%Y-%m-%d'
    DIVIDEND_PAID_DATE_FORMAT = '%d %b %Y'

    def __init__(self, base_webdriver):
        self.base_webdriver = base_webdriver

    def agree_cookies_stooq(self):
        buttons = self.base_webdriver.find_elements(By.XPATH, "//*[contains(text(), 'Zgadzam się')]")

        for btn in buttons:
            btn.click()
            self.base_webdriver.sleep()
            logger.info("Using cookies agreed at stooq website")
            self.base_webdriver.refresh()
            self.base_webdriver.sleep()

    
    def skip_daily_limit_occured_stooq(self):
        buttons = self.base_webdriver.find_elements(By.XPATH, "//*[contains(text(), 'Odblokuj dostęp...')]")

        for btn in buttons:
            btn.click()
            # TODO
            logger.info("Script came across daily limit of fetched data from website")
            logger.error("WARNING: automatic parsing should be added !!!")
            print("WARNING: automatic parsing should be added !!!")
            self.base_webdriver.sleep()
            self.base_webdriver.refresh()
            self.base_webdriver.sleep()


    def parse_operation_table(self, table_html=None):
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
                            date_obj = datetime.datetime.strptime(date_str, self.DIVIDEND_PAID_DATE_FORMAT)
                            row_dict[key] = date_obj
                        except:
                            err_row = ErrorDef.PARSE_DATE_FAILED
                        
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

    def parse_operations_website(self, short_name=None):
        dividend_url = self.URL_INSTRUMENT.format(short_name)
        logger.info("Parse stooq operations website {}".format(dividend_url))
        self.base_webdriver.get(dividend_url)
        self.base_webdriver.sleep()
        self.agree_cookies_stooq()
        self.skip_daily_limit_occured_stooq()

        # Dividend list table - fth1
        table_item = self.base_webdriver.find_element(By.ID, 'fth1')
        dividend_table_html = table_item.get_attribute('innerHTML')

        dividends_list = self.parse_operation_table(dividend_table_html)
        for divid_val_item in dividends_list:
            divid_val_item.close_share_price_nominal = self.get_close_share_price_nominal(short_name, divid_val_item.date)

        ret_dict = {}
        ret_dict['dividends_list'] = dividends_list
                
        return ret_dict


    def get_close_share_price_nominal(self, name_short, date):
        # query_date_str should be in format '2002-07-02'
        query_date_str = date.strftime(self.SHARE_PRICE_VALUE_TIME_FORMAT)
        query_name_short = name_short
        if not query_name_short.endswith(self.SHARE_PRICE_VALUE_COUNTRY_SUFFIX):
            query_name_short += self.SHARE_PRICE_VALUE_COUNTRY_SUFFIX
        df = pdr.DataReader(query_name_short, "stooq", query_date_str, query_date_str)
        val = None
        try:
            val = df.iloc[0]['Close']
        except:
            return None
        return val

class BiznesradarWebdriver:
    BIZNESRADAR_INSTRUMENTS_URL = 'https://www.biznesradar.pl/operacje/{}' # next long name of instrument e.g. ATLANTAPL
    IPO_DATE_FORMAT = '%d.%m.%Y'
    
    def __init__(self, base_webdriver):
        self.base_webdriver = base_webdriver

    def parse_profile_summary_table(self, table_html=None):
        html_str = table_html

        table = BeautifulSoup(html_str, 'html.parser')

        ret_val_dict = {'sector_gpw': None, 'sector_name': None, 
                        'isin_tag': None, 'ipo_date': None,}
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
            if desc.text == 'ISIN:':
                ret_val_dict['isin_tag'] = val.text
            if desc.text == 'Data debiutu:':
                try:
                    date_str = val.text
                    date_obj = datetime.datetime.strptime(date_str, self.IPO_DATE_FORMAT)
                    ret_val_dict['ipo_date'] = date_obj
                except:
                    err_row = ErrorDef.PARSE_DATE_FAILED

        for key in ret_val_dict.keys():
            if isinstance(ret_val_dict.get(key), str):
                ret_val_dict[key] = ret_val_dict.get(key).replace('\n', '')

        return ret_val_dict

    def parse_operations_website(self, long_name=None):
        url = self.BIZNESRADAR_INSTRUMENTS_URL.format(long_name)
        logger.info("Parse sector from BiznesRadar website {}".format(url))
        self.base_webdriver.get(url)
        self.base_webdriver.sleep()

        # # <table class="profileSummary">
        table_item = self.base_webdriver.find_element(By.CLASS_NAME, 'profileSummary')

        table_html = table_item.get_attribute('innerHTML')
        ret_val_dict = self.parse_profile_summary_table(table_html)

        return ret_val_dict

class BossaWebdriver:
    URL_INSTRUMENTS_SUFFIX = '/notowania/instrumenty/'
    URL_INSTRUMENTS_PREFIX = 'https://bossa.pl'
    
    def __init__(self, base_webdriver):
        self.base_webdriver = base_webdriver


    def parse_dividend_companies_list(self, bossa_file_path=None):
        bossa_url = '{}{}'.format(self.URL_INSTRUMENTS_PREFIX, self.URL_INSTRUMENTS_SUFFIX)
        assert bossa_file_path or bossa_url, 'Source wasn\'t set correctly'

        soup = None
        if bossa_file_path:
            soup = self.base_webdriver.get_soup_from_file(bossa_file_path)
        elif bossa_url:
            soup = self.base_webdriver.get_soup_from_url(bossa_url)

        dividend_ret_list = []
        for link in soup.find_all('a'):
            link_url = link.get('href')
            if( not link_url is None and self.URL_INSTRUMENTS_SUFFIX in link_url ):
                instrument_short = link_url.split(self.URL_INSTRUMENTS_SUFFIX)[-1]
                instrument_long = link.text
                dividend_company_item = "{}{}".format(self.URL_INSTRUMENTS_PREFIX, link_url)
                dividend_company_item = DividendCompanyItem(
                    bossa_instrument_url = dividend_company_item,
                    name_short = instrument_short,
                    name_long = instrument_long)
                dividend_ret_list.append(dividend_company_item)

        return dividend_ret_list

class DividendItem:
    def __init__(self, date=None, percent=None, nominal=None, rights_issue=None,
            close_share_price_nominal=None):
        self.date = date
        self.percent = percent
        self.nominal = nominal
        self.rights_issue = rights_issue
        self.close_share_price_nominal = close_share_price_nominal

        logger.info("DividendItem created: {}".format(str(self)))

    def __str__(self):
        return str(self.__dict__)

    def json(self):
        return json.dumps(self.__dict__, default=json_serial)

class DividendCompanyItem:
    def __init__(self,
            bossa_instrument_url=None,
            name_short=None,
            name_long=None,
            isin_tag=None,
            ipo_date=None,
            sector_gpw=None,
            sector_name=None,
            dividends_list=None):
        self.bossa_instrument_url = bossa_instrument_url
        self.name_short = name_short
        self.name_long = name_long
        self.isin_tag = isin_tag
        self.ipo_date = ipo_date 
        self.sector_gpw = sector_gpw
        self.sector_name = sector_name
        self.dividends_list = []
        self.update_dividends_list(dividends_list)

        logger.info("DividendCompanyItem created: {}".format(str(self)))

    def update(self, update_dict):
        bossa_instrument_url = update_dict.get('bossa_instrument_url')
        name_short = update_dict.get('name_short')
        name_long = update_dict.get('name_long')
        isin_tag = update_dict.get('isin_tag')
        ipo_date  = update_dict.get('ipo_date')
        sector_gpw = update_dict.get('sector_gpw')
        sector_name = update_dict.get('sector_name')
        dividends_list = update_dict.get('dividends_list')


        if bossa_instrument_url != None:        
            self.bossa_instrument_url = bossa_instrument_url
        if name_short != None:        
            self.name_short = name_short
        if name_long != None:        
            self.name_long = name_long
        if isin_tag != None:        
            self.isin_tag = isin_tag
        if ipo_date != None:        
            self.ipo_date = ipo_date 
        if sector_gpw != None:        
            self.sector_gpw = sector_gpw
        if sector_name != None:        
            self.sector_name = sector_name

        if dividends_list != None:
            self.update_dividends_list(dividends_list)



    def update_dividends_list(self, dividends_list=None):
        if dividends_list != None:
            assert isinstance(dividends_list, list)
            self.dividends_list.extend(dividends_list)

    def __str__(self):
        return str(self.__dict__)

    def json(self):
        return json.dumps(self.__dict__, default=json_serial)

    def dividends_list_needs_update(self):
        return len(self.dividends_list) == 0
class DividendCompaniesContainer:
    companies_items_dict = {}

    #############################
    ###### Class constants ######
    #############################
    # store files constants
    STORE_CURRENT_SETTINGS_FILENAME = 'curr_settings_dividend_listing'
    STORE_FILE_EXTENSION = '.pickle'

    #############################
    ######  Class methods  ######
    #############################
    def __init__(self):
        self.force_permissions = ForceDef.FORCE_DISABLED
        self.base_webdriver = BaseWebdriver()
        self.stooq_webdriver = StooqWebdriver(self.base_webdriver)
        self.biznesradar_webdriver = BiznesradarWebdriver(self.base_webdriver)
        self.bossa_webdriver = BossaWebdriver(self.base_webdriver)
        logger.info("DividendCompaniesContainer init")
        locale.setlocale(locale.LC_ALL, "pl_PL.utf8")
        logger.info("Set locale to {}".format(locale.getlocale()))
        # pl_datetime_now = datetime.datetime.now().strftime("%d %B %Y godz: %H:%M:%S")
        self.dumps_dir_path = os.path.abspath(os.path.join(self.base_webdriver.download_dir_path, os.pardir, 'dumps'))
        self.dump_restore_configs()

    def json(self):
        return json.dumps(self.__dict__)

    # Store settings 
    def _dump_prepare_dict_to_store(self):
        dict_to_return = dict()
        dict_to_return["companies_items_dict"] = self.companies_items_dict
        return dict_to_return

    def _dump_restore_from_dict(self, received_dict):
        try:
            self.companies_items_dict.update(received_dict.get("companies_items_dict"))
        except:
            logger.error("Dump restore failed")
            

    def _dump_get_summary_dump_name_filename(self):
        now = datetime.datetime.now()
        time_format = "%Y%m%d_%H%M%S_"
        time_str = now.strftime(time_format)
        filename = "{}{}{}".format(time_str, self.STORE_CURRENT_SETTINGS_FILENAME, self.STORE_FILE_EXTENSION)
        return filename

    def _dump_get_filename_to_store(self):
        filename = "{}{}".format(self.STORE_CURRENT_SETTINGS_FILENAME, self.STORE_FILE_EXTENSION)
        return filename

    def _dump_get_filename_to_restore(self):
        return self._dump_get_filename_to_store()

    def _dump_store_configs_settings(self, filename_of_pickle_file):
        dict_to_pickle = self._dump_prepare_dict_to_store()
        path_to_pickle_file = os.path.join(self.dumps_dir_path, filename_of_pickle_file)
        logger.info("Store objects: {} to current working file {}".format(dict_to_pickle.keys(), path_to_pickle_file))

        path_to_pickle_dir = os.path.dirname(path_to_pickle_file)
        os.makedirs(path_to_pickle_dir, exist_ok=True)
        db_file = open(path_to_pickle_file, 'wb')
        pickle.dump(dict_to_pickle, db_file)
        db_file.close()

    def _dump_restore_configs_settings(self, filename_of_pickle_file):
        path_to_pickle_file = os.path.join(self.dumps_dir_path, filename_of_pickle_file)
        if os.path.isfile(path_to_pickle_file):
            db_file = open(path_to_pickle_file, 'rb')
            dict_from_pickle = pickle.load(db_file)
            logger.info("Restore objects: {} from current working file {}".format(dict_from_pickle.keys(), path_to_pickle_file))
            self._dump_restore_from_dict(dict_from_pickle)
            db_file.close()

    def dump_store_configs_curr(self):
        filename_of_pickle_file = self._dump_get_filename_to_store()
        self._dump_store_configs_settings(filename_of_pickle_file)

    def dump_store_configs(self):
        filename_of_pickle_file = self._dump_get_summary_dump_name_filename()
        self._dump_store_configs_settings(filename_of_pickle_file)

    def dump_restore_configs(self):
        filename_of_pickle_file = self._dump_get_filename_to_restore()
        self._dump_restore_configs_settings(filename_of_pickle_file)

    def company_add(self, item):
        key = item.name_short
        curr_val_for_key = self.companies_items_dict.get(key)
        force_active = ForceDef.is_force_active(self.force_permissions, ForceDef.COMPANY_ADD_OVERWRITE_EXISTING_COMPANY)
        if (curr_val_for_key is None) or force_active:
            self.companies_items_dict[key] = item
            logger.info("Add Dividend Company {} to items_list".format(item))
            self.dump_store_configs_curr()
        else:
            raise ValueError('Selected key {} exist in dataset'.format(key))

    def count_companies(self):
        return len(self.companies_items_dict.keys())

    def dividend_list_prepared(self):
        return self.count_companies() > 0

    def update_companies_list(self):
        for item_idx, item_key in enumerate(self.companies_items_dict.keys()):
            item = self.companies_items_dict[item_key]
            # dividends_list
            if item.dividends_list_needs_update():
                stooq_content = self.stooq_webdriver.parse_operations_website(item.name_short)
                item.update(stooq_content)
            
            # biznesradar
            if None in [item.sector_gpw, item.sector_name]:
                biznesradar_content = self.biznesradar_webdriver.parse_operations_website(item.name_long)
                item.update(biznesradar_content)

            logger.info("Update company item {} with id {}".format(item, item_idx))
            self.dump_store_configs_curr()
            print('test')

    def fetch_dividends_companies_list(self):
        force_active = ForceDef.is_force_active(self.force_permissions, ForceDef.FETCH_BOSSA_COMPANIES_LIST)
        if (not self.dividend_list_prepared()) or  force_active:
            dividend_list = self.bossa_webdriver.parse_dividend_companies_list(bossa_file_path=bossa_file_path)
            # dividend_list = self.bossa_webdriver.parse_bossa_dividend_html(bossa_url=bossa_url)
            for item in dividend_list:
                self.company_add(item)
            self.dump_store_configs()

#############################
###### BUSINESS LOGIC  ######
#############################
if __name__=='__main__':
    dividends_list = DividendCompaniesContainer()
    dividends_list.fetch_dividends_companies_list()
    dividends_list.update_companies_list()
    dividends_list.dump_store_configs()
    print('done')
# https://www.bankier.pl/wiadomosc/Inwestowanie-dywidendowe-Poradnik-dla-poczatkujacych-7601780.html

