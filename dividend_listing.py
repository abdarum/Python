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
class DividendItem:
    def __init__(self):
        self.percent = None
        self.nominal = None

class DividendCompanyItem:
    def __init__(self,
            bossa_instrument_url=None,
            name_short=None,
            name_long=None,
            sector_gpw=None,
            sector_name=None):
        self.bossa_instrument_url = bossa_instrument_url
        self.name_short = name_short
        self.name_long = name_long
        self.sector_gpw = sector_gpw
        self.sector_name = sector_name

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

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': 'FCCDCF=[null,null,null,["CPS4aoPPS4aoPEsABBPLB-CoAP_AAH_AAB5YHQpD7T7FbSFCyP55fLsAMAhXRkCEAqQAAASABmABQAKQIAQCkkAQFASgBAACAAAgICZBAQAMCAgACUABQABAAAEEAAAABAAIIAAAgAEAAAAIAAACAIAAAAAIAAAAEAAAmwgAAIIACAAABAAAAAAAAAAAAAAAAgdCgPsLsVtIUJI_Gk8uwAgCFdGQIQCoAAAAIAGYAAAApAgBAKQQBAABKAAAAIAACAgJgEBAAgACAABQAFAAEAAAAAAAAAAAAggAACAAQAAAAgAAAIAgAAAAAgAAAAAAACBCAAAggAIAAAAAAAAAAAAAAAAAAACAAA.f-gAAAAAAAA","1~2072.66.70.89.93.108.122.149.2202.162.167.196.2253.241.2299.259.2357.311.317.323.2373.338.358.415.440.449.2506.2526.482.486.494.495.2568.2571.2575.540.574.2677.817.864.981.1051.1095.1097.1127.1201.1205.1211.1276.1301.1365.1415.1449.1451.1570.1577.1651.1716.1765.1870.1878.1889","E04CC7CA-B4E7-4DB1-B094-7988B95FF5E3"],null,null,[]]; FCNEC=[["AKsRol-ZW-cUg7_Jfj3sVnDUsNiZM4BhtDLM6iUdyRrgGOJ3WAU8xrY10EctRdI68cuuChzvhd2EENRxttugLMWUzh2PZdjHKEBiYVZ9-hj6FOxdzZK7d7LplfqUo-qj1YnG8P2GxR6eNOCe93kO6E8saaYVg3zqjw=="],null,[]]; privacy=1642290642; PHPSESSID=g33e2uc55nhuf6tkojiialhto2; uid=plbnvv7f37jaqv90e7lf0dcxx8; _ga=GA1.2.60653019.1642290643; cookie_uu=220119000; _gid=GA1.2.1761052878.1642605637; cookie_user=?0001dllg000011800d1300e3|zwc+aca+nvt+atp+sfg+sev+krc+kgh',
        'DNT': '1',
        'Host': 'stooq.pl',
        # 'If-Modified-Since': 'Wed, 19 Jan 2022 16:59:51 GMT',
        'Referer': 'https://stooq.pl/pomoc/?q=9&s=zwc',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform:': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'xxx': 'xxx',
        'xxx': 'xxx',
        'xxx': 'xxx',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
    }

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


    def test_web_browser(self, url=None):
        print('test')
        self.driver.get(url)
        time.sleep(self.HTTP_TIMEOUT_SECONDS)
        self.__webdriver_agree_cookies_stood()

        # fth1
        id_box = self.driver.find_element_by_id('fth1')

        print('test')

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

                dividend_company_item = DividendCompanyItem(
                    bossa_instrument_url = link_url,
                    name_short = instrument_short,
                    name_long = instrument_long)

                soup = self.test_web_browser(self.STOOQ_INSTRUMENTS_URL+instrument_short)

                self.append(dividend_company_item)

#############################
###### BUSINESS LOGIC  ######
#############################
dividends_list = DividendCompaniesContainer()
dividends_list.parse_bossa_dividend_html(bossa_file_path=bossa_file_path)
print('done')
# https://www.bankier.pl/wiadomosc/Inwestowanie-dywidendowe-Poradnik-dla-poczatkujacych-7601780.html