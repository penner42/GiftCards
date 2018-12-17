from selenium.common.exceptions import NoSuchElementException
import re, json, time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

class Extractor:
    @staticmethod
    def complete_challenge(browser, email, phonenum):
        return None

    @staticmethod
    def subject():
        return ""

    @staticmethod
    def delay():
        pass

    @staticmethod
    def find_element(browser, list_of_options, default_value):
        return_value = default_value
        for l in list_of_options:
            locator = l.get('id')
            func = l.get('method', browser.find_element_by_xpath)
            postprocess = l.get('postprocess', lambda s: s.text.strip())
            exception = l.get('exception', NoSuchElementException)
            try:
                return_value = postprocess(func(locator))
                if return_value == '':
                    continue
                break
            except exception:
                pass
        return return_value

class StaplesExtractor(Extractor):
    @staticmethod
    def name():
        return "Staples"

    @staticmethod
    def email():
        return ['DoNotReply.Staples@blackhawk-net.com']

    @staticmethod
    def fetch_payload(msg):
        return msg.get_payload(1).get_payload(decode=True)

    @staticmethod
    def fetch_url(msg_parsed, browser, email):
        egc_link = msg_parsed.findAll("a", title=re.compile('View Gift'))
        urls = []
        if len(egc_link) > 0:
            for u in egc_link:
                urls.insert(0, u['href'])
            return urls

    @staticmethod
    def fetch_codes(browser):
        # Get the card amount
        try:
            card_amount = browser.find_element_by_xpath('//*[@id="main"]/div[1]/div[2]/h2').text.strip()
        except NoSuchElementException:
            card_amount = 'Unknown'

        # card store
        card_store = '{} {}'.format(card_amount, browser.find_element_by_id('productName').get_attribute('value'))

        # Get the card number
        card_code = browser.find_element_by_id('cardNumber').get_attribute('value')
        card_pin = browser.find_element_by_id('pinNumber').get_attribute('value')

        return {'card_store': card_store, 'card_amount': card_amount, 'card_code': card_code, 'card_pin': card_pin}

class NeweggExtractor(Extractor):
    @staticmethod
    def name():
        return "Newegg"

    @staticmethod
    def email():
        return ['info@newegg.com']

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

        # check if card is ready?
        try:
            browser.find_element_by_xpath('//*[contains(text(), "Your gift card number is currently being retrieved.")]')
            return None
        except NoSuchElementException:
            pass

        # Get the card amount
        try:
            card_amount = browser.find_element_by_xpath('//*[@id="lblCertAmount"]').text.strip()
        except NoSuchElementException:
            card_amount = browser.find_element_by_xpath('//*[@id="desktop"]/div[1]/div[2]/div[1]/div/div/div[1]/div[2]/div[1]').text.strip()

        # Get the card number
        try:
            card_code = browser.find_element_by_xpath('//*[@id="imgCertBarCode"]').get_attribute('src').split('CBID=')[1].split('&')[0]
        except NoSuchElementException:
            try:
                card_code = browser.find_element_by_xpath('//*[@id="desktop"]/div[1]/div[2]/div[1]/div/div/div[1]/div[2]/div[3]/div/div').text.strip()
            except NoSuchElementException:
                try:
                    datacert = json.loads(browser.find_element_by_id('ids-configuration').get_attribute('data-certificate'))
                    card_code = datacert['CardNumber']
                except (NoSuchElementException, TypeError, KeyError) as e:
                    card_code = ''

        try:
            card_pin = browser.find_element_by_xpath('//*[@id="lblPin"]').text.strip()
        except NoSuchElementException:
            try:
                datacert = json.loads(browser.find_element_by_id('ids-configuration').get_attribute('data-certificate'))
                card_pin = datacert['Pin']
            except (NoSuchElementException, TypeError, KeyError) as e:
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
        return ['gifts@paypal.com']

    @staticmethod
    def delay():
        time.sleep(5)

    @staticmethod
    def complete_challenge(browser, email, phonenum):
        try:
            browser.find_element_by_id('captcha-standalone')
            x = browser.get_window_position()['x']
            if x == -10000:
                browser.set_window_position(10,10)
            finished = False
            while not finished:
                try:
                    wait = WebDriverWait(browser, 10)
                    wait.until(EC.presence_of_element_located((By.ID, "react-engine-props")))
                    finished = True
                except TimeoutException:
                    pass

            if x == -10000:
                browser.set_window_position(-10000,0)
        except NoSuchElementException:
            return None


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
        script_json = json.loads(browser.find_element_by_id('react-engine-props').get_attribute('innerHTML'))
        card_store = script_json['cardDetails']['description']
        card_amount = script_json['cardDetails']['itemValue']
        card_code = script_json['cardDetails']['giftCard']['card_number']
        try:
            card_pin = script_json['cardDetails']['giftCard']['security_code']
        except KeyError:
            card_pin = ''

        return {'card_store': card_store, 'card_amount': card_amount, 'card_code': card_code, 'card_pin': card_pin}


class CashstarExtractor(Extractor):
    @staticmethod
    def name():
        return "Cashstar"

    @staticmethod
    def email():
        return ['cashstar.com']

    @staticmethod
    def fetch_payload(msg):
        return msg.get_payload(1).get_payload(decode=True)

    @staticmethod
    def fetch_url(msg_parsed, browser, email):
        egc_link = msg_parsed.find("a", href=re.compile(".cashstar.com/gift-card/view/"))
        if egc_link is not None:
            return egc_link['href']

    @staticmethod
    def complete_challenge(browser, email, phonenum):
        try:
            browser.find_element_by_id("error-page")
            return None
        except NoSuchElementException:
            pass

        emailaddr = browser.find_element_by_id("id_value")
        emailaddr.send_keys(email)
        wait = WebDriverWait(browser, 3)
        while emailaddr.get_attribute("value") != email:
            try:
                wait.until(EC.text_to_be_present_in_element_value((By.ID, "id_value"), email))
            except TimeoutException:
                emailaddr.clear()
                emailaddr.send_keys(email)

        emailaddr.submit()
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#skip, #redeem")))
        try:
            skip = browser.find_element_by_id("skip")
        except NoSuchElementException:
            skip = browser.find_element_by_id('redeem')

        browser.get(skip.get_attribute('href'))

    @staticmethod
    def fetch_codes(browser):
        try:
            browser.find_element_by_id("error-page")
            return None
        except NoSuchElementException:
            pass

        try:
            browser.find_element_by_class_name("promotion")
            card_code = "{}{}{}{}".format(
                browser.find_element_by_xpath(
                    '//*[@id="container"]/div[1]/div[2]/div[2]/div[1]/div/div[1]/div/div/p[1]/span[1]').text,
                browser.find_element_by_xpath(
                    '//*[@id="container"]/div[1]/div[2]/div[2]/div[1]/div/div[1]/div/div/p[1]/span[2]').text,
                browser.find_element_by_xpath(
                    '//*[@id="container"]/div[1]/div[2]/div[2]/div[1]/div/div[1]/div/div/p[1]/span[3]').text,
                browser.find_element_by_xpath(
                    '//*[@id="container"]/div[1]/div[2]/div[2]/div[1]/div/div[1]/div/div/p[1]/span[4]').text
            )
            card_pin = browser.find_element_by_xpath(
                '//*[@id="container"]/div[1]/div[2]/div[2]/div[1]/div/div[1]/div/div/p[2]').text[5:]
            card_amount = browser.find_element_by_xpath(
                '//*[@id="container"]/div[1]/div[2]/div[2]/div[1]/div/div[1]/div/div/p[3]').text[8:-4]
            card_store = browser.find_element_by_class_name("header").find_element_by_css_selector('a').get_attribute('href')
        except NoSuchElementException:
            card_code = "{}{}{}{}".format(
                browser.find_element_by_xpath('//*[@id="container"]/div[1]/div[2]/div[3]/div[2]/p[1]/span[1]').text,
                browser.find_element_by_xpath('//*[@id="container"]/div[1]/div[2]/div[3]/div[2]/p[1]/span[2]').text,
                browser.find_element_by_xpath('//*[@id="container"]/div[1]/div[2]/div[3]/div[2]/p[1]/span[3]').text,
                browser.find_element_by_xpath('//*[@id="container"]/div[1]/div[2]/div[3]/div[2]/p[1]/span[4]').text,
            )
            card_pin = browser.find_element_by_xpath('//*[@id="container"]/div[1]/div[2]/div[3]/div[2]/p[2]').text[5:]
            card_amount = ''
            card_store = browser.find_element_by_class_name("header").find_element_by_css_selector('a').get_attribute('href')

        return {'card_store': card_store, 'card_amount': card_amount, 'card_code': card_code, 'card_pin': card_pin}


class SamsungPayExtractor(Extractor):
    @staticmethod
    def name():
        return "Samsung Pay"

    @staticmethod
    def email():
        return ['no-reply@samsungpay.com']

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
        if "gyft" in browser.current_url:
            # card store
            try:
                card_store = browser.find_element_by_xpath('/html/body/main/aside/table/tbody/tr/td[2]/h6[2]').text
            except NoSuchElementException:
                card_store = 'unknown'

            # card amount
            try:
                card_amount = browser.find_element_by_xpath('/html/body/main/aside/table/tbody/tr/td[2]/h6[1]').text
            except NoSuchElementException:
                card_amount = 'unknown'

            # card number
            try:
                card_code = browser.find_element_by_xpath('/html/body/main/aside/div[5]/div/div[2]/div[2]').text
            except NoSuchElementException:
                card_code = 'unknown'

            # card pin
            try:
                card_pin = browser.find_element_by_xpath('/html/body/main/aside/div[5]/div/div[4]/div[2]').text
            except NoSuchElementException:
                card_pin = ''

        else:
            # card store
            card_store = Extractor.find_element(browser,
                [
                    {'id': 'retailerName', 'method': browser.find_element_by_name,
                     'postprocess': lambda s: s.get_attribute('value')},
                    {'id': '//*[@id="main"]/div[1]/div[1]/img',
                     'postprocess': lambda s: s.get_attribute('alt')},
                    {'id': '/html/head/title',
                     'postprocess': lambda s: s.get_attribute('innerHTML')},
                ],
                'Unknown Brand'
            )

            # Get the card amount
            card_amount = Extractor.find_element(browser,
                [
                    {'id': '//*[@id="amount"]'},
                    {'id': '//*[@id="card-details"]/b[2]'},
                    {'id': '//*[@id="main"]/div[2]/div[1]/h1/span',
                     'postprocess': lambda s: re.search('\$\d+', s.text.strip()).group(0)},
                    {'id': '//*[@id="main"]/div[1]/div[2]/h2'},
                    {'id': '//*[@id="egc-amount"]'},
                    {'id': '//*[@id="main"]/div[1]/div[1]/h1',
                     'postprocess': lambda s: re.search('\$\d+', s.text.strip()).group(0)},
                ],
                'Unknown Value')

            # Get the card number
            card_code = Extractor.find_element(browser,
                [
                    {'id': 'cardNumber', 'method': browser.find_element_by_name,
                     'postprocess': lambda s: s.get_attribute('value')},
                    {'id': '//*[@id="cardNumber2"]'},
                    {'id': '//*[@id="main"]/div[2]/div/p/span'},
                    {'id': '//*[@id="cardNumber3"]'}
                 ],
                'Unknown Card Number')

            # Get the card PIN. Leave blank if we can't find it, as some cards don't have PINs
            card_pin = Extractor.find_element(browser,
                [
                    {'id': 'pinNumber', 'method': browser.find_element_by_name,
                     'postprocess': lambda s: s.get_attribute('value')},
                    {'id': '//*[@id="main"]/div[2]/div[2]/p[2]/span'},
                    {'id': '//*[@id="Span2"]'}
                ],
                '')

        return {'card_store': card_store, 'card_amount': card_amount, 'card_code': card_code, 'card_pin': card_pin}

class AmazonExtractor(Extractor):
    @staticmethod
    def name():
        return "Amazon"

    @staticmethod
    def email():
        return ['gc-orders@gc.email.amazon.com']

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
        card_store = Extractor.find_element(browser,
                                            [
                                                {'id': '//*[@id="main"]/div[1]/div[1]/img',
                                                 'postprocess': lambda s: s.get_attribute('alt')},
                                                {'id': '//*[@id="main"]/h1/strong'},
                                                {'id': '/html/head/title',
                                                 'postprocess': lambda s: s.get_attribute('innerHTML')}
                                            ],
                                            'Unknown Store')
        #
        # card_store = browser.find_element_by_xpath('//*[@id="main"]/div[1]/div[1]/img').get_attribute("alt")
        # if card_store == "":
        #     card_store = browser.find_element_by_xpath('//*[@id="main"]/h1/strong').text.strip()

        # Get the card amount
        card_amount = Extractor.find_element(browser,
                                             [
                                                 {'id': '//*[@id="main"]/div[1]/div[2]/h2'},
                                                 {'method': browser.find_element_by_id,
                                                  'id': 'amount'},
                                                 {'id': '//*[@id="main"]/div[2]/div/p[2]',
                                                  'postprocess': lambda s: re.search('.*?(\$\d*).*',
                                                                                     s.text.strip()).group(1)},

                                             ],
                                             'Unknown Amount')
        # try:
        #     card_amount = browser.find_element_by_xpath('//*[@id="main"]/div[1]/div[2]/h2').text.strip()
        # except NoSuchElementException:
        #     card_amount = browser.find_element_by_id("amount").text.strip()

        # Get the card number
        card_code = Extractor.find_element(browser,
                                           [
                                               {'id': '//*[@id="cardNumber2"]'},
                                               {'id': '//*[@id="redeem"]'}
                                           ],'Unknown Code')
        #
        # card_code = browser.find_element_by_xpath('//*[@id="cardNumber2"]').text.strip()
        card_pin = Extractor.find_element(browser, [{'id': '//*[@id="main"]/div[2]/div[2]/p[2]/span'}], '')
        if card_pin == card_code:
            card_pin = Extractor.find_element(browser, [{'id': '//*[@id="claimCode"]'}], '')
        # try:
        #     card_pin = browser.find_element_by_xpath('//*[@id="main"]/div[2]/div[2]/p[2]/span').text.strip()
        # except NoSuchElementException:
        #     card_pin = ''

        # if card_pin == card_code:
        #     try:
        #         card_pin = browser.find_element_by_xpath('//*[@id="claimCode"]').text.strip()
        #     except NoSuchElementException:
        #         pass

        return {'card_store': card_store, 'card_amount': card_amount, 'card_code': card_code, 'card_pin': card_pin}

class GiftCardMallExtractor(Extractor):
    @staticmethod
    def name():
        return "Gift Card Mall"

    @staticmethod
    def email():
       return ['gcm-support@giftcardmall.com', 'customerservice@giftcardmall.com', 'gcm-cust-serv@giftcardmall.com']

    @staticmethod
    def fetch_payload(msg):
        return msg.get_payload(decode=True)

    @staticmethod
    def fetch_url(msg_parsed, browser, email):
        egc_link = msg_parsed.findAll("a", {"class": "email-btn-link"})
        if len(egc_link) == 0:
#            egc_link = msg_parsed.findAll("a", text=re.compile("Click to View"))
            egc_link = msg_parsed.findAll("a", text=re.compile("Click to Access"))
            if len(egc_link) == 0:
                egc_link = msg_parsed.findAll('a', {'class': 'activation-spot-url'})

        urls = []
        if len(egc_link) > 0:
            for u in egc_link:
                urls.insert(0, u['href'])
            return urls

    @staticmethod
    def fetch_codes(browser):
        # card store
        card_store = browser.find_element_by_id('productName').get_attribute('value')
        card_amount = Extractor.find_element(browser,
                                             [
                                                 {'id': '//*[@id="main"]/div[1]/div[1]/h1',
                                                  'postprocess': lambda s: re.search('.*?(\$\d*).*', s).group(1)},
                                                 {'id': '//*[@id="main"]/div[1]/div[2]/h2'}
                                             ],
                                             'Unknown Amount')

        card_code = Extractor.find_element(browser,
                                          [
                                              {'method': browser.find_element_by_id,
                                               'id': 'cardNumber',
                                               'postprocess': lambda s: s.get_attribute('value')}
                                          ],
                                          'Unknown Code')
        card_pin = browser.find_element_by_id('pinNumber').get_attribute('value')

        return {'card_store': card_store, 'card_amount': card_amount, 'card_code': card_code, 'card_pin': card_pin}

class BestBuyExtractor(Extractor):
    @staticmethod
    def name():
        return "Best Buy"

    @staticmethod
    def complete_challenge(browser, email, phonenum):
        try:
            browser.find_element_by_id('phoneNumberChallenge')
        except NoSuchElementException:
            return None

        phone = browser.find_element_by_name('phone')
        phone_dashed = phonenum[0:3]+"-"+phonenum[3:6]+"-"+phonenum[6:10]
        phone.send_keys(phonenum)
        wait = WebDriverWait(browser, 15)
        while phone.get_attribute("value") != phone_dashed:
            try:
                wait.until(EC.text_to_be_present_in_element_value((By.NAME, "phone"), phone_dashed))
            except TimeoutException:
                phone.send_keys(phonenum)
        phone.submit()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "gift-card-container")))

    @staticmethod
    def email():
        return ['BestBuyInfo@emailinfo.bestbuy.com', 'bestbuygiftcards@cashstar.com']

#    @staticmethod
#     def subject():
#        return "E-Gift Card"
#         return ""
    @staticmethod
    def fetch_payload(msg):
        return msg.get_payload(decode=True)

    @staticmethod
    def fetch_url(msg_parsed, browser, email):
        egc_link = msg_parsed.findAll('a', text=re.compile('Claim my e-gift card'))
        if len(egc_link) == 0:
            egc_link = msg_parsed.findAll("a", text=re.compile("Click to View"))

        urls = []
        if len(egc_link) > 0:
            for u in egc_link:
                urls.insert(0, u['href'])
            return urls

    @staticmethod
    def fetch_codes(browser):
        # card store
        card_store = 'Best Buy'
        card_code = browser.find_element_by_xpath('//*[@id="app"]/div/div/div[4]/div[2]/div[1]/p').text.strip()
        card_pin = browser.find_element_by_xpath('//*[@id="app"]/div/div/div[4]/div[2]/div[2]/p').text.strip()
        card_amount = browser.find_element_by_xpath('//*[@id="app"]/div/div/div[4]/div[2]/div[3]/div').text.split(" ")[0].strip()

        return {'card_store': card_store, 'card_amount': card_amount, 'card_code': card_code, 'card_pin': card_pin}

class MyGiftCardsPlusExtractor(Extractor):
    @staticmethod
    def name():
        return "MyGiftCardsPlus"

    @staticmethod
    def complete_challenge(browser, email, phonenum):
        try:
            browser.find_element_by_partial_link_text('Login')
        except NoSuchElementException:
            return None

        wait = WebDriverWait(browser, 15)
        while browser.title != "Gift Card":
            try:
                wait.until(EC.title_contains("Gift Card"))
            except TimeoutException:
                pass

    @staticmethod
    def email():
        return ['ClientCareMGC@mygiftcardsplus.com']

    @staticmethod
    def fetch_payload(msg):
        return msg.get_payload(1).get_payload(decode=True)

    @staticmethod
    def fetch_url(msg_parsed, browser, email):
        egc_link = msg_parsed.findAll('a', text=re.compile('https://www.mygiftcardsplus.com/card'))
        urls = []
        if len(egc_link) > 0:
            for u in egc_link:
                urls.insert(0, u['href'])
            return urls

    @staticmethod
    def fetch_codes(browser):
        # card store
        store_json = json.loads(browser.find_element_by_id('ids-configuration').get_attribute('data-configuration'))
        card_store = store_json[0]['settings']['brandName']

        script_json = json.loads(browser.find_element_by_id('ids-configuration').get_attribute('data-certificate'))
        card_amount = script_json['InitialBalance']
        card_code = script_json['CardNumber']
        try:
            card_pin = script_json['Pin']
        except KeyError:
            card_pin = ''

        return {'card_store': card_store, 'card_amount': card_amount, 'card_code': card_code, 'card_pin': card_pin}


extractors_list = [AmazonExtractor, BestBuyExtractor, CashstarExtractor, SamsungPayExtractor, PPDGExtractor,
                   NeweggExtractor, StaplesExtractor, GiftCardMallExtractor, MyGiftCardsPlusExtractor]
