import re
from datetime import datetime
from time import sleep

import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy, ProxyType

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.action_chains import ActionChains

from .settings import Settings


class Bot:

    def __init__(self,
                 username=None,
                 password=None,
                 selenium_local_session=True,
                 page_delay=25,
                 headless_browser=False,
                 proxy_address=None,
                 proxy_chrome_extension=None,
                 proxy_port=0,
                 ):
        self.password = password
        self.username = username
        self.browser = None
        self.headless_browser = headless_browser
        self.proxy_address = proxy_address
        self.proxy_port = proxy_port
        self.proxy_chrome_extension = proxy_chrome_extension
        self.page_delay = page_delay

        if selenium_local_session:
            self.set_selenium_local_session()

    def set_selenium_local_session(self):
        """Starts local session for a selenium server.
        Default case scenario."""
        chromedriver_location = Settings.chromedriver_location
        chrome_options = Options()
        chrome_options.add_argument('--dns-prefetch-disable')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--lang=en-US')
        chrome_options.add_argument('--disable-setuid-sandbox')

        # this option implements Chrome Headless, a new (late 2017)
        # GUI-less browser. chromedriver 2.9 and above required
        if self.headless_browser:
            chrome_options.add_argument('--headless')
            # Replaces browser User Agent from "HeadlessChrome".
            user_agent = "Chrome"
            chrome_options.add_argument('user-agent={user_agent}'
                                        .format(user_agent=user_agent))
        capabilities = DesiredCapabilities.CHROME
        # Proxy for chrome
        if self.proxy_address and self.proxy_port > 0:
            prox = Proxy()
            proxy = ":".join([self.proxy_address, self.proxy_port])
            prox.proxy_type = ProxyType.MANUAL
            prox.http_proxy = proxy
            prox.socks_proxy = proxy
            prox.ssl_proxy = proxy
            prox.add_to_capabilities(capabilities)

        # add proxy extension
        if self.proxy_chrome_extension and not self.headless_browser:
            chrome_options.add_extension(self.proxy_chrome_extension)

        chrome_prefs = {
            'intl.accept_languages': 'en-US'
        }
        chrome_options.add_experimental_option('prefs', chrome_prefs)
        try:
            self.browser = webdriver.Chrome(chromedriver_location,
                                            desired_capabilities=capabilities,
                                            chrome_options=chrome_options)
        except selenium.common.exceptions.WebDriverException as exc:
            print(exc)
            raise Exception('ensure chromedriver is installed at {}'.format(
                Settings.chromedriver_location))

        # prevent: Message: unknown error: call function result missing 'value'
        matches = re.match(r'^(\d+\.\d+)',
                           self.browser.capabilities['chrome']['chromedriverVersion'])
        if float(matches.groups()[0]) < Settings.chromedriver_min_version:
            raise Exception('chromedriver {} is not supported, expects {}+'.format(
                float(matches.groups()[0]), Settings.chromedriver_min_version))

        self.browser.implicitly_wait(self.page_delay)
        print('Session started - %s'
              % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        return self

    def act(self, url):
        driver = self.browser
        driver.get(url)
        self.login()


    def login(self):
        driver = self.browser
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.element_to_be_clickable((By.ID, 'i0116')))
        (ActionChains(driver)
         .move_to_element(element)
         .click().send_keys(self.username).perform())
        driver.find_element_by_id("idSIButton9").click()
        element = wait.until(EC.element_to_be_clickable((By.ID, 'i0118')))
        (ActionChains(driver)
         .move_to_element(element)
         .click().send_keys(self.password).perform())
        driver.find_element_by_id("idSIButton9").click()
        sleep(1)
        try:
            driver.find_element_by_id("idSIButton9").click()
        except NoSuchElementException:
            print("Yes not Found")

    def end(self):
        """Closes the current session"""
        try:
            self.browser.delete_all_cookies()
            self.browser.quit()
        except WebDriverException as exc:
            print('Could not locate Chrome: {}'.format(exc))

        print('Session ended - {}'.format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        print('-' * 20 + '\n\n')
