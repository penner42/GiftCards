from selenium.common.exceptions import NoSuchElementException
import email
from bs4 import BeautifulSoup
from datetime import datetime

class Extractor:
    def extract(self):
        pass

class PPDGExtractor(Extractor):
    @staticmethod
    def name():
        return "PayPal Digital Gifts"

    def email(self):
        return "gifts@paypal.com"

    def fetch_urls(self, mailbox, messages):
        urls = []
        for msg_id in messages:
            print("---> Processing message id {}...".format(msg_id.decode('UTF-8')))
            # Fetch it from the server
            status, data = mailbox.fetch(msg_id, '(RFC822)')
            if status == "OK":
                # Convert it to an Email object
                msg = email.message_from_bytes(data[0][1])
                # Get the HTML body payload
                msg_html = msg.get_payload(decode=True)
                # Save the email timestamp
                datetime_received = datetime.fromtimestamp(email.utils.mktime_tz(email.utils.parsedate_tz(msg.get('date'))))
                # Parse the message
                msg_parsed = BeautifulSoup(msg_html, 'html.parser')
                # Find the "View My Code" link
                egc_link = msg_parsed.find("a", text="View My Code")
                if egc_link is not None:
                    urls.insert(0, [msg_id, datetime_received, egc_link])

        return urls

    def fetch_codes(self, browser):
        # card store
        subdiv = 3
        try:
            browser.find_element_by_id("DM_categories")
            subdiv = 4
        except NoSuchElementException:
            pass

        card_store = browser.find_element_by_xpath("//*[@id=\"main-content\"]/div[3]/div/div[" + str(
            subdiv) + "]/section/div/div[1]/div/div/img").get_attribute("alt")

        # Get the card amount
        try:
            browser.find_element_by_class_name("barcode")
            card_amount = browser.find_element_by_xpath("//*[@id=\"main-content\"]/div[3]/div/div[" + str(
                subdiv) + "]/section/div/div[1]/div/div/div[2]/dl[1]/dd").text.strip()
            # Get the card number
            card_code = browser.find_element_by_xpath("//*[@id=\"main-content\"]/div[3]/div/div[" + str(
                subdiv) + "]/section/div/div[1]/div/div/div[2]/dl[2]/dd").text.strip()
            try:
                card_pin = browser.find_element_by_xpath("//*[@id=\"main-content\"]/div[3]/div/div[" + str(
                    subdiv) + "]/section/div/div[1]/div/div/div[2]/dl[3]/dd").text.strip()
            except NoSuchElementException:
                card_pin = 0

        except NoSuchElementException:
            card_amount = browser.find_element_by_xpath("//*[@id=\"main-content\"]/div[3]/div/div[" + str(
                subdiv) + "]/section/div/div[1]/div/div/div[1]/dl[1]/dd").text.strip()
            # Get the card number
            card_code = browser.find_element_by_xpath("//*[@id=\"main-content\"]/div[3]/div/div[" + str(
                subdiv) + "]/section/div/div[1]/div/div/div[1]/dl[2]/dd").text.strip()
            try:
                card_pin = browser.find_element_by_xpath("//*[@id=\"main-content\"]/div[3]/div/div[" + str(
                    subdiv) + "]/section/div/div[1]/div/div/div/dl[3]/dd").text.strip()
            except NoSuchElementException:
                card_pin = 0

        return card_store, card_amount, card_code, card_pin


class CashstarExtractor(Extractor):
    @staticmethod
    def name():
        return "Cashstar"

    def email(self):
        return "cashstar.com"

    def fetch_codes(self, browser):
        def fetch_codes(browser):
            # card store
            card_store = browser.find_element_by_id("sub-hdr").find_element_by_class_name("print-focus").text

            # Get the card amount
            card_amount = browser.find_element_by_class_name("egc-title-highlight").text

            # Get the card number
            card_number = browser.find_element_by_id("barcode-num").text.split()[1].split(":")[1]
            card_pin = browser.find_element_by_id("barcode-num").text.split()[3]

            return card_store, card_amount, card_number, card_pin

class SamsungPayExtractor(Extractor):
    @staticmethod
    def name():
        return "Samsung Pay"

    def email(self):
        return "no-reply@samsungpay.com"

    def fetch_codes(self, browser):
        # card store
        card_store = browser.find_element_by_xpath('//*[@id="main"]/div[1]/div[1]/img').get_attribute("alt")

        # Get the card amount
        try:
            card_amount = browser.find_element_by_xpath('//*[@id="main"]/div[1]/div[2]/h2').text.strip()
        except NoSuchElementException:
            card_amount = browser.find_element_by_xpath('//*[@id="amount"]').text.strip()

        # Get the card number
        try:
            card_code = browser.find_element_by_xpath('//*[@id="cardNumber2"]').text.strip()
        except NoSuchElementException:
            card_code = browser.find_element_by_xpath('//*[@id="main"]/div[2]/div/p/span').text.strip()

        try:
            card_pin = browser.find_element_by_xpath('//*[@id="main"]/div[2]/div[2]/p[2]/span').text.strip()
        except NoSuchElementException:
            card_pin = ''

        return card_store, card_amount, card_code, card_pin

class AmazonExtractor(Extractor):
    @staticmethod
    def name():
        return "Amazon"

    def email(self):
        return "gc-orders@gc.email.amazon.com"

    def fetch_codes(self, browser):
        def fetch_codes(browser):
            # card store
            card_store = browser.find_element_by_xpath('//*[@id="main"]/div[1]/div[1]/img').get_attribute("alt")
            if card_store == "":
                card_store = browser.find_element_by_xpath('//*[@id="main"]/h1/strong').text.strip()

            # Get the card amount
            try:
                card_amount = browser.find_element_by_xpath('//*[@id="main"]/div[1]/div[2]/h2').text.strip()
            except NoSuchElementException:
                card_amount = browser.find_element_by_id("amount").text.strip()

            # Get the card number
            card_code = browser.find_element_by_xpath('//*[@id="cardNumber2"]').text.strip()
            try:
                card_pin = browser.find_element_by_xpath('//*[@id="main"]/div[2]/div[2]/p[2]/span').text.strip()
            except NoSuchElementException:
                card_pin = 0

            if card_pin == card_code:
                try:
                    card_pin = browser.find_element_by_xpath('//*[@id="claimCode"]').text.strip()
                except NoSuchElementException:
                    pass

            return card_store, card_amount, card_code, card_pin


extractors_list = [AmazonExtractor, CashstarExtractor, SamsungPayExtractor, PPDGExtractor]
