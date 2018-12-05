import re
from datetime import datetime

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

from bot.time_util import sleep
from bot.users import Users
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
        self.answered = []
        self.selenium_local_session = selenium_local_session

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

    def set_selenium_remote_session(self, selenium_url=''):
        """Starts remote session for a selenium server.
         Useful for docker setup."""
        self.browser = webdriver.Remote(
            command_executor=selenium_url,
            desired_capabilities=DesiredCapabilities.CHROME)

        message = "Session started!"
        print(self.username, message, "initialization", "info")
        print('')

        return self

    def act(self, answer_file, url=None):
        driver = self.browser
        answers = Answers(answer_file)
        u = url or answers.url()
        print("url: %s" % u)
        driver.get(u)
        self.login(driver)
        sleep()
        try:
            self.start_test(driver)
        except selenium.common.exceptions.TimeoutException as te:
            self.save_assessment(answer_file, '<code>Unable to start_test(<a href="%s">%s</a>)</code>' % (u, u))
            return

        sleep()

        try:
            while True:
                self.answering(driver, answers)
                sleep()
        except selenium.common.exceptions.TimeoutException:
            text = driver.find_element_by_id("Assessment").get_attribute('innerHTML')
            self.save_assessment(answer_file, text)

            print("done Answering")

    def save_assessment(self, answer_file, text):
        if self.username in Users.users:
            Users.users[self.username][answer_file] = text
        else:
            Users.users[self.username] = {answer_file: text}

    def start_test(self, driver):
        wait = WebDriverWait(driver, 20)
        iframe1 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#course-player-container iframe')))
        driver.switch_to.frame(iframe1)
        iframe2 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#contentFrame')))
        driver.switch_to.frame(iframe2)

        try:
            button_ok = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#IntroBeginButton')))
            sleep()
            button_ok.click()
        except selenium.common.exceptions.TimeoutException:
            print("no button_ok")
        print("started Test")

    def answering(self, driver, answers):
        wait = WebDriverWait(driver, 20)
        button_next = wait.until(EC.element_to_be_clickable((By.ID, 'AssessmentNextButton')))
        self.answer_question(answers, wait)
        sleep()
        button_next.click()

    def answer_question(self, answers, wait):
        question = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#QuestionViewPrompt > table > tbody > tr > td:nth-child(2)')))
        print(question.text)
        answers_parent = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#QuestionViewChoices')))
        test_answers = answers_parent.find_elements_by_css_selector("tr > td:nth-child(2)")
        options = []
        for test_answer in test_answers:
            options += [test_answer.text]
        a = list(map(lambda e: str(e).replace(" ", ""), answers.get(question=question.text, options=options)))
        if str(question.text) not in self.answered:
            for test_answer in test_answers:
                if str(test_answer.text).replace(" ", "") in a:
                    sleep()
                    test_answer.click()
                    if str(question.text) not in self.answered:
                        self.answered += [str(question.text)]
            print("answered")
        else:
            print("skipped")

    def login(self, driver):
        try:
            wait = WebDriverWait(driver, 20)
            element = wait.until(EC.element_to_be_clickable((By.ID, 'i0116')))
            (ActionChains(driver)
             .move_to_element(element)
             .click().send_keys(self.username).perform())
            sleep(5)
            driver.find_element_by_id("idSIButton9").click()
            sleep(5)
            element = wait.until(EC.element_to_be_clickable((By.ID, 'i0118')))
            (ActionChains(driver)
             .move_to_element(element)
             .click().send_keys(self.password).perform())
            driver.find_element_by_id("idSIButton9").click()
        except Exception as e:
            print("Exception in login(): %s" % type(e))

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
