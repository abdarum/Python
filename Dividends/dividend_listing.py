import copy
import datetime
import json
import locale
import logging
import math
import os
import pickle
import time

import json_logging  # logging
import stringcase
import tqdm
from bs4 import BeautifulSoup
from pandas_datareader import data as pdr
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from statsmodels.stats.weightstats import DescrStatsW

#############################
######  User Settings  ######
#############################
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
    if isinstance(obj, (
            DividendItem, 
            DividendCompanyItemStatistics, 
            DividendCompanyItemStatistics.DividendsOccurrence,
        )):
        return obj.__dict__
    raise TypeError ("Type %s not serializable" % type(obj))

#############################
######     Classes     ######
#############################
class ErrorDef:
    PARSE_STOOQ_OPERATION_TABLE_NOT_DIVIDEND_IN_ROW = 'Error parsing, row in the Stooq operation table. Operation different than dividend'
    PARSE_DATE_FAILED = 'Error parsing, Parse date failed'

class SupportLevelDef:
    ALL = 'all'
    MANDATORY = 'mandatory'
    OPTIONAL = 'optional'

class ForceDef:
    FORCE_DISABLED = 'Force disabled'
    COMPANY_ADD_OVERWRITE_EXISTING_COMPANY = 'Company add - overwrite existing company'
    FETCH_BOSSA_COMPANIES_LIST = 'Fetch bossa companies list'
    DELETE_COMPANY_ITEM_FROM_COMPANIES_LIST = 'Delete company item from companies list'

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
    HTTP_TIMEOUT_SECONDS = 20

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
        self.sleep()
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
        try:
            return self.driver.find_element(find_by, find_content)
        except NoSuchElementException:
            logger.error('Element has not been found')
            return ''

    def get_html_of_element(self, find_by, find_content):
        try:
            return self.find_element(find_by, find_content).get_attribute('innerHTML')
        except AttributeError:
            logger.error('Object has no property innerHTML')
            return ''

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
                    logger.error('Parsing error, dividend_item skipped. Dividend item: {}. Error {}'.format(dividend_item, err_row))
                else:
                    dividends_list.append(dividend_item)

        return dividends_list

    def parse_operations_website(self, short_name=None):
        if short_name is None:
            # page can not be parsed
            return {}

        dividend_url = self.URL_INSTRUMENT.format(short_name)
        logger.info("Parse stooq operations website {}".format(dividend_url))
        self.base_webdriver.get(dividend_url)
        self.base_webdriver.sleep()
        self.agree_cookies_stooq()
        self.skip_daily_limit_occured_stooq()

        # Dividend list table - fth1
        dividend_table_html = self.base_webdriver.get_html_of_element(By.ID, 'fth1')

        dividends_list = self.parse_operation_table(dividend_table_html)

        ret_dict = {}
        ret_dict['dividends_list'] = dividends_list
                
        return ret_dict

    @staticmethod
    def get_close_share_price_nominal(name_short, date):
        # query_date_str should be in format '2002-07-02'
        query_date_str = date.strftime(StooqWebdriver.SHARE_PRICE_VALUE_TIME_FORMAT)
        query_name_short = name_short
        if not query_name_short.endswith(StooqWebdriver.SHARE_PRICE_VALUE_COUNTRY_SUFFIX):
            query_name_short += StooqWebdriver.SHARE_PRICE_VALUE_COUNTRY_SUFFIX
        df = pdr.DataReader(query_name_short, "stooq", query_date_str, query_date_str)
        val = None
        try:
            val = df.iloc[0]['Close']
        except:
            return None
        return val

    @staticmethod
    def get_stooq_instrument_url(name_short):
        key_label = 'stooq_instrument'
        link_url = StooqWebdriver.URL_INSTRUMENT.format(name_short)
        return key_label, link_url

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
        if long_name is None:
            # page can not be parsed
            return {}
        url = self.BIZNESRADAR_INSTRUMENTS_URL.format(long_name)
        logger.info("Parse sector from BiznesRadar website {}".format(url))
        self.base_webdriver.get(url)
        self.base_webdriver.sleep()

        # # <table class="profileSummary">
        table_html = self.base_webdriver.get_html_of_element(By.CLASS_NAME, 'profileSummary')
        ret_val_dict = self.parse_profile_summary_table(table_html)

        return ret_val_dict

    def update_fields_supported(self, support_level=None):
        if support_level is None:
            support_level = SupportLevelDef.MANDATORY
        update_fields_supported = []
        mandatory = ['sector_gpw', 'sector_name', 'isin_tag', ]
        optional = ['ipo_date', ]
        if support_level in [SupportLevelDef.ALL, SupportLevelDef.MANDATORY]:
            update_fields_supported.extend(mandatory)
        if support_level in [SupportLevelDef.ALL, SupportLevelDef.OPTIONAL]:
            update_fields_supported.extend(optional)
        return update_fields_supported

    @staticmethod
    def get_biznesradar_instrument_url(name_long):
        key_label = 'biznesradar_instrument'
        link_url = BiznesradarWebdriver.BIZNESRADAR_INSTRUMENTS_URL.format(name_long)
        return key_label, link_url

class BossaWebdriver:
    URL_INSTRUMENTS_SUFFIX = '/notowania/instrumenty/'
    URL_INSTRUMENTS_PREFIX = 'https://bossa.pl'
    URL_ANALYSE_DIVIDS = 'https://bossa.pl/analizy/dywidendy'

    
    def __init__(self, base_webdriver):
        self.base_webdriver = base_webdriver


    def parse_dividend_companies_list(self, bossa_file_path=None):
        bossa_url = '{}'.format(self.URL_ANALYSE_DIVIDS)
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
                if not bossa_file_path is None:
                    link_url = "{}{}".format(self.URL_INSTRUMENTS_PREFIX, link_url)
                dividend_company_item = DividendCompanyItem(
                    bossa_instrument_url = link_url,
                    name_short = instrument_short,
                    name_long = instrument_long)
                dividend_ret_list.append(dividend_company_item)

        return dividend_ret_list

    @staticmethod
    def get_bossa_instrument_url(name_short):
        key_label = 'bossa_instrument'
        link_url = "{}{}{}".format(BossaWebdriver.URL_INSTRUMENTS_PREFIX, BossaWebdriver.URL_INSTRUMENTS_SUFFIX, name_short)
        return key_label, link_url

class NotowaniaPulsBiznesuWebdriver:
    URL_INSTRUMENT_DETAILS = 'https://notowania.pb.pl/instrument/{}/informacje-spolka'

    def __init__(self, base_webdriver):
        self.base_webdriver = base_webdriver

    def parse_operations_website(self, isin_tag=None):
        if isin_tag is None:
            # page can not be parsed
            return {}

        url = self.URL_INSTRUMENT_DETAILS.format(isin_tag)
        logger.info("Parse sector from NotowaniaPulsBiznesu website {}".format(url))
        self.base_webdriver.get(url)
        self.base_webdriver.sleep()

        basic_data_table_html = self.base_webdriver.get_html_of_element(By.ID, 'boxBasicData')

        ret_val_dict = self.parse_basic_data_table(basic_data_table_html)

        description_of_activity_html = self.base_webdriver.get_html_of_element(By.ID, 'boxDesc')
        ret_val_dict.update(self.parse_description_table(description_of_activity_html))

        return ret_val_dict

    def parse_basic_data_table(self, table_html=None):
        html_str = table_html

        table = BeautifulSoup(html_str, 'html.parser').find(class_="boxContent boxTable")

        ret_val_dict = {'eur_class_of_activity': None}
        for row_idx, row in enumerate(table.find_all('tr')):
            desc = row.find_all('td')[0].text
            val = row.find_all('td')[1].text
            if desc == 'EKD:' and ret_val_dict.get('eur_class_of_activity') is None:
                ret_val_dict['eur_class_of_activity'] = val

        for key in ret_val_dict.keys():
            if isinstance(ret_val_dict.get(key), str):
                ret_val_dict[key] = ret_val_dict.get(key).replace('\n', '')

        return ret_val_dict


    def parse_description_table(self, html_str=None):
        soup = BeautifulSoup(html_str, 'html.parser')

        ret_val_dict = {'description_of_activity': None}

        content = soup.find(class_="boxContent")
        val = content.text

        ret_val_dict['description_of_activity'] = val

        for key in ret_val_dict.keys():
            if isinstance(ret_val_dict.get(key), str):
                ret_val_dict[key] = ret_val_dict.get(key).replace('\n', '')

        return ret_val_dict

    def update_fields_supported(self, support_level=None):
        if support_level is None:
            support_level = SupportLevelDef.MANDATORY
        update_fields_supported = []
        mandatory = ['eur_class_of_activity', 'description_of_activity']
        optional = [ ]
        if support_level in [SupportLevelDef.ALL, SupportLevelDef.MANDATORY]:
            update_fields_supported.extend(mandatory)
        if support_level in [SupportLevelDef.ALL, SupportLevelDef.OPTIONAL]:
            update_fields_supported.extend(optional)
        return update_fields_supported

    @staticmethod
    def get_notowaniapb_instrument_url(isin_tag):
        key_label = 'notowaniapb_instrument'
        link_url = NotowaniaPulsBiznesuWebdriver.URL_INSTRUMENT_DETAILS.format(isin_tag)
        return key_label, link_url

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

class DividendCompanyItemStatistics:
    def __init__(self, ipo_date=None, dividends_list=None):
        self.erase_data()
        self.update_dividends_list(dividends_list)
        self.update_ipo_date(ipo_date)

    def erase_data(self):
        self.dividends_list = []
        self.computed_at = None
        self.occurrence_module = DividendCompanyItemStatistics.DividendsOccurrence()
        self.summary_benchmark_score = None
        self.days_since_last_dividend = None
        self.number_of_dividends_paid = None

    def update_dividends_list(self, dividends_list=None):
        if dividends_list != None:
            assert isinstance(dividends_list, list)
            self.dividends_list.extend(dividends_list)
            self.dividends_list.sort(key=lambda x: x.date, reverse=True)
            if len(self.dividends_list) > 0:
                self.days_since_last_dividend = datetime.datetime.now() - self.dividends_list[0].date
                self.days_since_last_dividend = self.days_since_last_dividend.days
                self.number_of_dividends_paid = len(self.dividends_list)

    def update_ipo_date(self, ipo_date=None):
        self.ipo_date = ipo_date

    def benchmark_score(self):
        try:
            summary_score = None
            dividend_gaps_mean = self.occurrence_module.dividend_gaps_in_days_mean
            dividend_gaps_std = self.occurrence_module.dividend_gaps_in_days_std
            days_since_last_dividend = self.days_since_last_dividend
            number_of_dividends_paid = self.number_of_dividends_paid
            
            #############
            # recalculate - prepare for compute single coefficient
            #############
            param_dividend_gaps_mean = (365.0/dividend_gaps_mean)
            param_dividend_gaps_std = (90.0/dividend_gaps_std)
            number_of_dividends_paid = (7.0/number_of_dividends_paid)

            # ignore all cases up to 450 days
            param_days_since_last_dividend = self.days_since_last_dividend - 450
            if param_days_since_last_dividend > 0:
                param_days_since_last_dividend = 1/float(param_days_since_last_dividend)
            else:
                param_days_since_last_dividend = 1

            benchmark_formula = [
                {'weight': 30, 'val': param_dividend_gaps_mean},
                {'weight': 40, 'val': param_dividend_gaps_std},
                {'weight': 10, 'val': number_of_dividends_paid},
                {'weight': 20, 'val': param_days_since_last_dividend},
            ]
            statsmodel = DescrStatsW(
                data=[item.get('val') for item in benchmark_formula],
                weights=[item.get('weight') for item in benchmark_formula],
                ddof=1)

            summary_score = statsmodel.sum / statsmodel.sum_weights
            self.summary_benchmark_score = summary_score
        except TypeError:
            # skip if data are None
            self.summary_benchmark_score = 0

    def compute(self):
        self.occurrence_module.compute(self.dividends_list)
        self.computed_at = datetime.datetime.now()
        self.benchmark_score()



    class DividendsOccurrence:
        def __init__(self):
            self.dividend_gaps_in_days_list = []
            self.dividend_gaps_in_days_mean = None
            self.dividend_gaps_in_days_std = None

        def compute(self, dividends_list=None):
            self.prepare_dividend_gaps_in_days(dividends_list)
            self.compute_statistics()

        def prepare_dividend_gaps_in_days(self, dividends_list):
            dividend_gaps_in_days_list = []
            dividend_date_list = [item.date for item in dividends_list]
            if len(dividend_date_list) > 1:
                dividend_gaps_in_days_list = [dividend_date_list[idx-1] - dividend_date_list[idx] for idx in range(1, len(dividend_date_list))]
                dividend_gaps_in_days_list = [item.days for item in dividend_gaps_in_days_list]

            self.dividend_gaps_in_days_list = dividend_gaps_in_days_list

        def compute_statistics(self):
            dividend_gaps_in_days_list = self.dividend_gaps_in_days_list

            if len(dividend_gaps_in_days_list) > 1:
                weights = list(range(len(dividend_gaps_in_days_list), 0, -1))
                weights_sum = sum(weights)
                weights = [0.25*math.pow(val, 2) for val in weights]
                statsmodel = DescrStatsW(dividend_gaps_in_days_list, weights=weights, ddof=1)
                self.dividend_gaps_in_days_mean = statsmodel.mean
                self.dividend_gaps_in_days_std = statsmodel.std


class DividendCompanyItem:
    def __init__(self,
            bossa_instrument_url=None,
            name_short=None,
            name_long=None,
            isin_tag=None,
            ipo_date=None,
            sector_gpw=None,
            sector_name=None,
            eur_class_of_activity=None,
            description_of_activity=None,
            dividends_list=None):
        self.bossa_instrument_url = bossa_instrument_url
        self.name_short = name_short
        self.name_long = name_long
        self.isin_tag = isin_tag
        self.ipo_date = ipo_date 
        self.sector_gpw = sector_gpw
        self.sector_name = sector_name
        self.eur_class_of_activity = eur_class_of_activity
        self.description_of_activity = description_of_activity
        self.dividends_list = []
        self.update_dividends_list(dividends_list)

        logger.info("DividendCompanyItem created: {}".format(str(self)))

    def update(self, update_dict):
        name_short = update_dict.get('name_short')
        name_long = update_dict.get('name_long')
        isin_tag = update_dict.get('isin_tag')
        ipo_date  = update_dict.get('ipo_date')
        sector_gpw = update_dict.get('sector_gpw')
        sector_name = update_dict.get('sector_name')
        dividends_list = update_dict.get('dividends_list')
        eur_class_of_activity = update_dict.get('eur_class_of_activity')
        description_of_activity = update_dict.get('description_of_activity')


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
        if eur_class_of_activity != None:        
            self.eur_class_of_activity = eur_class_of_activity
        if description_of_activity != None:        
            self.description_of_activity = description_of_activity

        if dividends_list != None:
            self.update_dividends_list(dividends_list)

        self.force_update_urls()

    def update_dividends_list(self, dividends_list=None):
        if dividends_list != None:
            assert isinstance(dividends_list, list)
            self.dividends_list.extend(dividends_list)

        for divid_val_item in self.dividends_list:
            divid_val_item.close_share_price_nominal = StooqWebdriver.get_close_share_price_nominal(self.name_short, divid_val_item.date)

    def force_update_urls(self):
            try:
                del self.bossa_instrument_url
            except AttributeError:
                logger.debug('bossa_instrument_url variable doesn\'t exist. It was deleted before')

            self.url_dict = {}
            if not self.name_long is None:
                key_label, link_url = BiznesradarWebdriver.get_biznesradar_instrument_url(self.name_long)
                self.url_dict[key_label] = link_url
            if not self.name_short is None:
                key_label, link_url = StooqWebdriver.get_stooq_instrument_url(self.name_short)
                self.url_dict[key_label] = link_url
                key_label, link_url = BossaWebdriver.get_bossa_instrument_url(self.name_short)
                self.url_dict[key_label] = link_url
            if not self.isin_tag is None:
                key_label, link_url = NotowaniaPulsBiznesuWebdriver.get_notowaniapb_instrument_url(self.isin_tag)
                self.url_dict[key_label] = link_url
            
    def __str__(self):
        return str(self.__dict__)

    def json(self):
        return json.dumps(self.__dict__, default=json_serial)

    def json_str(self):
        return json.dumps(self.__dict__, default=json_serial, indent=4, ensure_ascii=False)

    def json_str_without_duplicates(self):
        ret_dict = copy.deepcopy(self.__dict__)
        try:
            del ret_dict['statistics_module'].dividends_list
        except AttributeError: 
            logger.debug('dividends_list from statistics_module variable doesn\'t exist. It was deleted before')

        try:
            del ret_dict['statistics_module'].ipo_date
        except AttributeError: 
            logger.debug('ipo_date from statistics_module variable doesn\'t exist. It was deleted before')


        return json.dumps(ret_dict, default=json_serial, indent=4, ensure_ascii=False, sort_keys=True)

    def dividends_list_needs_update(self):
        return len(self.dividends_list) == 0

    def fields_needs_update(self, keys_list):
        assert isinstance(keys_list, list)

        values_list = []
        for key in keys_list:
            values_list.append(self.__dict__.get(key))

        return None in values_list

    def compute_statistics(self):
        # calculated_statistics
        try: 
            # check if calculated_statistics exist 
            self.statistics_module
        except AttributeError: 
            self.statistics_module = None

        
        self.statistics_module = DividendCompanyItemStatistics(
            dividends_list=self.dividends_list,
            ipo_date=self.ipo_date)
        self.statistics_module.compute()


class DividendCompaniesContainer:
    companies_items_dict = {}

    #############################
    ###### Class constants ######
    #############################
    # store files constants
    STORE_CURRENT_SETTINGS_FILENAME = 'curr_settings_dividend_listing'
    STORE_FILE_EXTENSION = '.pickle'
    FILENAME_OF_DATA_LOG_FILE = '__data_preview.log'

    #############################
    ######  Class methods  ######
    #############################
    def __init__(self):
        self.force_permissions = [ForceDef.FETCH_BOSSA_COMPANIES_LIST]
        # self.force_permissions.append(ForceDef.DELETE_COMPANY_ITEM_FROM_COMPANIES_LIST)
        self.base_webdriver = BaseWebdriver()
        self.stooq_webdriver = StooqWebdriver(self.base_webdriver)
        self.biznesradar_webdriver = BiznesradarWebdriver(self.base_webdriver)
        self.bossa_webdriver = BossaWebdriver(self.base_webdriver)
        self.notowania_pb_webdriver = NotowaniaPulsBiznesuWebdriver(self.base_webdriver)

        logger.info("DividendCompaniesContainer init")
        locale.setlocale(locale.LC_ALL, "pl_PL.utf8")
        logger.info("Set locale to {}".format(locale.getlocale()))
        # pl_datetime_now = datetime.datetime.now().strftime("%d %B %Y godz: %H:%M:%S")
        self.dumps_dir_path = os.path.abspath(os.path.join(self.base_webdriver.download_dir_path, os.pardir, 'dumps'))
        self.path_to_data_log_file = os.path.join(gen_logs_dir_path, self.FILENAME_OF_DATA_LOG_FILE)
        self.data_content_log_del()
        self.dump_restore_configs()

    def json(self):
        return json.dumps(self.__dict__)

    def data_content_log_del(self):
        try:
            os.remove(self.path_to_data_log_file)
        except OSError:
            pass
            
    def data_content_log_append(self, str_val):
        with open(self.path_to_data_log_file, "a", encoding='utf-8') as data_file:
            print(str_val, file=data_file)

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
            

    def _dump_get_summary_dump_name_filename(self, additional_desc=None, extension=None):
        now = datetime.datetime.now()
        time_format = "%Y%m%d_%H%M%S_"
        time_str = now.strftime(time_format)
        if not isinstance(additional_desc, str):
            additional_desc = ''
        else:
            additional_desc = '_{}_'.format(stringcase.snakecase(additional_desc))
        if extension is None:
            extension = self.STORE_FILE_EXTENSION
        filename = "{}{}{}{}".format(time_str, additional_desc, self.STORE_CURRENT_SETTINGS_FILENAME, extension)
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

    def dump_store_configs(self, additional_desc=None):
        filename_of_pickle_file = self._dump_get_summary_dump_name_filename(additional_desc)
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
            logger.error('Selected key {} exist in dataset. Item skipped'.format(key))
    
    def company_del(self, item_key):
        force_active = ForceDef.is_force_active(self.force_permissions, ForceDef.DELETE_COMPANY_ITEM_FROM_COMPANIES_LIST)
        if force_active:
            item = self.companies_items_dict.pop(item_key, None)
            logger.info("Deleted Dividend Company {} from items_list".format(item))
    

    def get_companies_keys(self):
        return self.companies_items_dict.keys()

    def count_companies(self):
        return len(self.companies_items_dict.keys())

    def dividend_list_prepared(self):
        return self.count_companies() > 0

    def update_companies_list_web_scraping(self):
        skip_items_up_to = None
        support_level = None # SupportLevelDef.MANDATORY

        items_len = len(self.companies_items_dict.keys())
        with tqdm.tqdm(total=items_len, desc='Update companies list') as pbar:
            for item_idx, item_key in enumerate(self.companies_items_dict.keys()):
                if isinstance(skip_items_up_to, int) and item_idx < skip_items_up_to:
                    time.sleep(0.01)
                    pbar.update(1)
                    continue

                item = self.companies_items_dict[item_key]
                # Stooq dividends list
                if item.dividends_list_needs_update():
                    stooq_content = self.stooq_webdriver.parse_operations_website(item.name_short)
                    item.update(stooq_content)
                
                # Biznes Radar
                if item.fields_needs_update(self.biznesradar_webdriver.update_fields_supported(support_level)):
                    biznesradar_content = self.biznesradar_webdriver.parse_operations_website(item.name_long)
                    item.update(biznesradar_content)

                # Notowania Puls Biznesu
                if item.fields_needs_update(self.notowania_pb_webdriver.update_fields_supported(support_level)):
                    notowania_pb_content = self.notowania_pb_webdriver.parse_operations_website(item.isin_tag)
                    item.update(notowania_pb_content)

                logger.info("Update company item {} with id {}".format(item, item_idx))
                pbar.update(1)
                self.dump_store_configs_curr()
        logger.info('Update companies list - web scraping done')

    def fetch_dividends_companies_list(self):
        force_active = ForceDef.is_force_active(self.force_permissions, ForceDef.FETCH_BOSSA_COMPANIES_LIST)
        if (not self.dividend_list_prepared()) or  force_active:
            # dividend_list = self.bossa_webdriver.parse_dividend_companies_list(bossa_file_path=bossa_file_path)
            dividend_list = self.bossa_webdriver.parse_dividend_companies_list()

            # add companies
            for item in dividend_list:
                self.company_add(item)

            # del companies
            dividend_list_keys = [item.name_short for item in dividend_list]
            not_exists_in_web_db = list(set(self.get_companies_keys()) - set(dividend_list_keys))
            for item_key in not_exists_in_web_db:
                print('Item {} not exist in the web database. Do you want to delete?'.format(item_key))
                self.company_del(item_key=item_key)
                # raise ValueError('Item not contains in web db')

            # save results
            self.dump_store_configs_curr()
            self.dump_store_configs('raw_dataset')
        logger.info('Fetch dividends companies list done')

    def update_companies_list_calculate_statistics(self):
        skip_items_up_to = None

        items_len = len(self.companies_items_dict.keys())
        with tqdm.tqdm(total=items_len, desc='Update companies list') as pbar:
            for item_idx, item_key in enumerate(self.companies_items_dict.keys()):
                if isinstance(skip_items_up_to, int) and item_idx < skip_items_up_to:
                    time.sleep(0.01)
                    pbar.update(1)
                    continue

                item = self.companies_items_dict[item_key]
                item.compute_statistics()

                pbar.update(1)

        self.dump_store_configs_curr()
        self.dump_store_configs('statistics_calculated')
        logger.info('Update companies list - calculate statistics done')

    def sort_by_benchmark_coefficient_companies_list(self):
        items_len = len(self.companies_items_dict.keys())
        try:
            sorted_companies_items_dict = dict(sorted(self.companies_items_dict.items(), key=lambda item: item[1].statistics_module.summary_benchmark_score, reverse=True))
            for item_idx, item_key in enumerate(sorted_companies_items_dict.keys()):
                item = self.companies_items_dict[item_key]
                item.statistics_module.idx_on_list = item_idx
                self.companies_items_dict = sorted_companies_items_dict
        except:
            logger.error('Parse failed')

        logger.info('Sort by benchmark coefficient companies list done')

    
    #############################
    ######      Tools      ######
    #############################

    def tool_manual_update_of_companies_items_dict(self):
        skip_items_up_to = None
        
        items_len = len(self.companies_items_dict.keys())
        with tqdm.tqdm(total=items_len, desc='Update companies list') as pbar:
            for item_idx, item_key in enumerate(self.companies_items_dict.keys()):
                if isinstance(skip_items_up_to, int) and item_idx < skip_items_up_to:
                    time.sleep(0.01)
                    pbar.update(1)
                    continue

                item = self.companies_items_dict[item_key]

                ####################
                # Manual update here

                item.force_update_urls()

                # Manual update here
                ####################
                pbar.update(1)
        # save results
        # self.dump_store_configs_curr()
        # self.dump_store_configs('manual_update_dataset')

        logger.info('Tool manual update of companies items dict done')

    def tool_preview_of_companies_list(self):
        skip_items_up_to = None
        items_separator_str = '\n------------------------------\n\t\tIdx {}\n------------------------------\n'
        
        items_len = len(self.companies_items_dict.keys())
        with tqdm.tqdm(total=items_len, desc='Update companies list') as pbar:
            for item_idx, item_key in enumerate(self.companies_items_dict.keys()):
                if isinstance(skip_items_up_to, int) and item_idx < skip_items_up_to:
                    time.sleep(0.01)
                    pbar.update(1)
                    continue

                item = self.companies_items_dict[item_key]
                str_val = items_separator_str.format(item.statistics_module.idx_on_list)
                self.data_content_log_append(str_val)

                str_val = item.json_str_short()
                self.data_content_log_append(str_val)

                pbar.update(1)

        logger.info('Preview of companies list done')

#############################
###### BUSINESS LOGIC  ######
#############################
if __name__=='__main__':
    dividends_list = DividendCompaniesContainer()
    dividends_list.fetch_dividends_companies_list()
    dividends_list.update_companies_list_web_scraping()
    dividends_list.update_companies_list_calculate_statistics()
    dividends_list.sort_by_benchmark_coefficient_companies_list()
    dividends_list.tool_preview_of_companies_list()
    dividends_list.dump_store_configs()
    print('done')
# https://www.bankier.pl/wiadomosc/Inwestowanie-dywidendowe-Poradnik-dla-poczatkujacych-7601780.html

