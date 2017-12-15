from selenium.common.exceptions import NoSuchElementException
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

class Extractor:
    @staticmethod
    def complete_challenge(browser, email):
        return None

class NeweggExtractor(Extractor):
    @staticmethod
    def name():
        return "Newegg"

    @staticmethod
    def email():
        return "info@newegg.com"

    @staticmethod
    def fetch_payload(msg):
        return msg.get_payload(decode=True)

    @staticmethod
    def fetch_url(msg_parsed, browser, email):
        egc_link = msg_parsed.findAll("a", text=re.compile('View and Print the card'))
        urls = []
        if len(egc_link) > 0:
            for u in egc_link:
                urls.insert(0, u['href'])
            return urls

    @staticmethod
    def fetch_codes(browser):
        # card store
        card_store = browser.title.strip()

        # Get the card amount
        try:
            card_amount = browser.find_element_by_xpath('//*[@id="lblCertAmount"]').text.strip()
        except NoSuchElementException:
            card_amount = browser.find_element_by_xpath('//*[@id="desktop"]/div[1]/div[2]/div[1]/div/div/div[1]/div[2]/div[1]').text.strip()

        # Get the card number
        try:
            card_code = browser.find_element_by_xpath('//*[@id="imgCertBarCode"]').get_attribute('src').split('CBID=')[1].split('&')[0]
        except NoSuchElementException:
            card_code = browser.find_element_by_xpath('//*[@id="desktop"]/div[1]/div[2]/div[1]/div/div/div[1]/div[2]/div[3]/div/div').text.strip()
        try:
            card_pin = browser.find_element_by_xpath('//*[@id="lblPin"]').text.strip()
        except NoSuchElementException:
            try:
                card_pin = browser.find_element_by_xpath('//*[@id="desktop"]/div[1]/div[2]/div[1]/div/div/div[1]/div[2]/div[4]').text.split('PIN:')[1].strip()
            except NoSuchElementException:
                card_pin = ''

        return {'card_store': card_store, 'card_amount': card_amount, 'card_code': card_code, 'card_pin': card_pin}

class PPDGExtractor(Extractor):
    @staticmethod
    def name():
        return "PayPal Digital Gifts"

    @staticmethod
    def email():
        return "gifts@paypal.com"

    @staticmethod
    def fetch_payload(msg):
        return msg.get_payload(decode=True)

    @staticmethod
    def fetch_url(msg_parsed, browser, email):
        egc_link = msg_parsed.find("a", text="View My Code")
        if egc_link is not None:
            # Open the link in the browser
            return egc_link['href']

    @staticmethod
    def fetch_codes(browser):
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

        return {'card_store': card_store, 'card_amount': card_amount, 'card_code': card_code, 'card_pin': card_pin}


class CashstarExtractor(Extractor):
    @staticmethod
    def name():
        return "Cashstar"

    @staticmethod
    def email():
        return "cashstar.com"

    @staticmethod
    def fetch_payload(msg):
        return msg.get_payload(1).get_payload(decode=True)

    @staticmethod
    def fetch_url(msg_parsed, browser, email):
        egc_link = msg_parsed.find("a", href=re.compile(".cashstar.com/gift-card/view/"))
        if egc_link is not None:
            return egc_link['href']

    @staticmethod
    def complete_challenge(browser, email):
        try:
            browser.find_element_by_id("error-page")
            return None
        except NoSuchElementException:
            pass

        emailaddr = browser.find_element_by_id("id_value")
        emailaddr.send_keys(email)
        wait = WebDriverWait(browser, 15)
        while emailaddr.get_attribute("value") != email:
            try:
                wait.until(EC.text_to_be_present_in_element_value((By.ID, "id_value"), email))
            except TimeoutException:
                emailaddr.send_keys(email)

        emailaddr.submit()
        wait.until(EC.presence_of_element_located((By.ID, "skip")))
        skip = browser.find_element_by_id("skip")
        browser.get(skip.get_attribute('href'))

    @staticmethod
    def fetch_codes(browser):
        try:
            browser.find_element_by_id("error-page")
            return None
        except NoSuchElementException:
            pass

        # card store
        card_store = browser.find_element_by_id("sub-hdr").find_element_by_class_name("print-focus").text

        # Get the card amount
        card_amount = browser.find_element_by_class_name("egc-title-highlight").text

        # Get the card number
        card_number = browser.find_element_by_id("barcode-num").text.split()[1].split(":")[1]
        card_pin = browser.find_element_by_id("barcode-num").text.split()[3]

        return {'card_store': card_store, 'card_amount': card_amount, 'card_code': card_code, 'card_pin': card_pin}


class SamsungPayExtractor(Extractor):
    @staticmethod
    def name():
        return "Samsung Pay"

    @staticmethod
    def email():
        return "no-reply@samsungpay.com"

    @staticmethod
    def fetch_payload(msg):
        return msg.get_payload(1).get_payload(decode=True)

    @staticmethod
    def fetch_url(msg_parsed, browser, email):
        egc_link = msg_parsed.find('img', src='http://giftcard-art.prod.looppay.com/redeem-button.png')
        if egc_link is not None:
            return egc_link.parent['href']

    @staticmethod
    def fetch_codes(browser):
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

        return {'card_store': card_store, 'card_amount': card_amount, 'card_code': card_code, 'card_pin': card_pin}

class AmazonExtractor(Extractor):
    @staticmethod
    def name():
        return "Amazon"

    @staticmethod
    def email():
        return "gc-orders@gc.email.amazon.com"

    @staticmethod
    def fetch_payload(msg):
        return msg.get_payload(1).get_payload(decode=True)

    @staticmethod
    def fetch_url(msg_parsed, browser, email):
        egc_link = msg_parsed.find('img', alt='Get Gift Card')
        if egc_link is not None:
            return egc_link.parent['href']

    @staticmethod
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

        return {'card_store': card_store, 'card_amount': card_amount, 'card_code': card_code, 'card_pin': card_pin}


extractors_list = [AmazonExtractor, CashstarExtractor, SamsungPayExtractor, PPDGExtractor, NeweggExtractor]
