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
from .answers import Answers


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
        chrome_options.add_argument('--lang=de-DE')
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
            'intl.accept_languages': 'de-DE'
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

    def act(self, url, answer_file):
        driver = self.browser
        driver.get(url)
        self.login(driver)
        answers = Answers(answer_file)
        self.start_test(driver)

        try:
            while True:
                self.answering(driver, answers)
        except selenium.common.exceptions.TimeoutException:
            print("done Answering")


    def start_test(self, driver):
        wait = WebDriverWait(driver, 10)
        iframe1 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#course-player-container iframe')))
        driver.switch_to.frame(iframe1)
        iframe2 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#contentFrame')))
        driver.switch_to.frame(iframe2)

        try:
            button_ok = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#IntroBeginButton')))
            button_ok.click()
        except selenium.common.exceptions.TimeoutException:
            print("no button_ok")
        print("started Test")

    def answering(self, driver, answers):
        wait = WebDriverWait(driver, 10)
        question = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#QuestionViewPrompt > table > tbody > tr > td:nth-child(2)')))
        print(question.text)
        answers_parent = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#QuestionViewChoices')))
        test_answers = answers_parent.find_elements_by_css_selector("tr > td:nth-child(2)")

        options = []
        for test_answer in test_answers:
            options = options + [test_answer.text]

        a = answers.get(question=question.text, options=options)

        for test_answer in test_answers:
            if test_answer.text in a:
                test_answer.click()

        button_next = wait.until(EC.element_to_be_clickable((By.ID, 'AssessmentNextButton')))
        button_next.click()
        print("answered")

    def login(self, driver):
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
        print("logged in")

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
