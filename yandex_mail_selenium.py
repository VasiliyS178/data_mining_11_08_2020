import os
from pathlib import Path
import pymongo
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# mongo_server = '127.0.0.1'
# mongo_port = '27017'


class YandexMail:
    def __init__(self, *args, **kwargs):
        self.__login = kwargs['login']
        self.__password = kwargs['password']
        self.driver = webdriver.Firefox()
        self.driver.get('https://mail.yandex.ru/lite')
        # self.mongo_uri = f'mongodb://{kwargs["mongo_login"]}:{kwargs["mongo_password"]}@{mongo_server}:{mongo_port}'
        self.mongo_uri = 'mongodb://localhost:27017'
        self.mongo_db = 'yandex_mail'
        self.mongo_collection = type(self).__name__
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    __xpath_login = {
        'login': '//div[contains(@class, "Field_view_floating-label")]//input[@id="passp-field-login"]',
        'login_btn': '//div[contains(@class, "passp-button passp-sign-in-button")]',
        'password': '//span[contains(@class, "extinput_view_floating-label")]/input[@id="passp-field-passwd"]'

    }
    __xpath_mail = {
        'pagination_next': '//div[@class="b-pager"]/span[@class="b-pager__links"]/span[@class="b-pager__active"]',
        'messages': '//div[@class="b-messages"]/div[contains(@class, "b-messages__message")]',
        'subject': '//div[@class="b-message-head__subject"]/span[@class="b-message-head__subject-text"]',
        'date': '//div[@class="b-message-head__top"]/span[contains(@class, "b-message-head__field_date")]/span',
        'from': '//div[@class="b-message-head"]/div[@class="b-message-head__field"][2]'
                '/span[@class="b-message-head__field-value"]/a',
        'content_table': '//div[@class="b-message-body__content"]//table',
        'content_text': '//div[@class="b-message-body__content"]'
    }

    def start(self):
        self.wait_get_element(self.__xpath_login['login']).send_keys(self.__login + Keys.ENTER)
        self.wait_get_element(self.__xpath_login['password']).send_keys(self.__password + Keys.ENTER)

        while True:
            messages_length = len(self.wait_get_element(self.__xpath_mail['messages'], multiple=True))

            for index in range(0, messages_length):
                messages = self.wait_get_element(self.__xpath_mail['messages'], multiple=True)
                message = messages[index]
                message.click()
                result = {
                    'subject': self.driver.find_element_by_xpath(self.__xpath_mail['subject']).text,
                    'date': self.driver.find_element_by_xpath(self.__xpath_mail['date']).text,
                    'from': self.driver.find_element_by_xpath(self.__xpath_mail['from']).text,
                }
                try:
                    message_body = self.driver.find_element_by_xpath(self.__xpath_mail['content_table']).text
                    result['content'] = message_body
                except NoSuchElementException as e:
                    message_body = self.driver.find_element_by_xpath(self.__xpath_mail['content_text']).text
                    result['content'] = message_body

                self.write_to_mongo(result)
                self.driver.execute_script('window.history.go(-1)')

            try:
                next_page = self.wait_get_element(self.__xpath_mail['pagination_next'])
                next_page.click()
            except Exception as e:
                print('No more pages to scrap')
                self.driver.quit()
                break

    def write_to_mongo(self, item):
        self.db[self.mongo_collection].insert_one(item)

    def wait_get_element(self, xpath, multiple=False, timeout=10):
        try:
            element_present = EC.presence_of_element_located((By.XPATH, xpath))
            WebDriverWait(self.driver, timeout).until(element_present)
            if multiple:
                return self.driver.find_elements_by_xpath(xpath)
            return self.driver.find_element_by_xpath(xpath)
        except TimeoutException:
            print("Timed out, shutting down")
            self.driver.quit()


if __name__ == '__main__':
    load_dotenv(dotenv_path=Path('.env').absolute())
    mail_crawler = YandexMail(
        login=os.getenv('YANDEXMAIL'),
        password=os.getenv('YANDEXPASSWORD'),
        # mongo_login=os.getenv('MONGOLOGIN'),
        # mongo_password=os.getenv('MONGOPASSWORD')
    )
    mail_crawler.start()
