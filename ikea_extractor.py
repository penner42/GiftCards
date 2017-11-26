import os
import email
import re
import csv
from datetime import datetime
from imaplib import IMAP4, IMAP4_SSL
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import config

# Fetch codes from DOM
def fetch_codes(browser):
    # card store
    card_store = browser.find_element_by_id("sub-hdr").find_element_by_class_name("print-focus").text

    # Get the card amount
    card_amount = browser.find_element_by_class_name("egc-title-highlight").text

    # Get the card number
    card_number = browser.find_element_by_id("barcode-num").text.split()[1].split(":")[1]
    card_pin = browser.find_element_by_id("barcode-num").text.split()[3]

    return card_store, card_amount, card_number, card_pin


# Connect to the server
if config.IMAP_SSL:
    mailbox = IMAP4_SSL(host=config.IMAP_HOST, port=config.IMAP_PORT)
else:
    mailbox = IMAP4(host=config.IMAP_HOST, port=config.IMAP_PORT)

# Log in and select the configured folder
mailbox.login(config.IMAP_USERNAME, config.IMAP_PASSWORD)
mailbox.select(config.FOLDER)

# Search for matching emails
status, messages = mailbox.search(None, '(FROM {})'.format(config.FROM_EMAIL))
if status == "OK":
    # Convert the result list to an array of message IDs
    messages = messages[0].split()

    if len(messages) < 1:
        # No matching messages, stop
        print("No matching messages found, nothing to do.")
        exit()

    # Open the CSV for writing
    with open('cards_' + datetime.now().strftime('%m-%d-%Y_%H%M%S') + '.csv', 'w', newline='') as csv_file:
        # Start the browser and the CSV writer
        browser = webdriver.Chrome(config.CHROMEDRIVER_PATH)
        csv_writer = csv.writer(csv_file)

        # Create a directory for screenshots if it doesn't already exist
        screenshots_dir = os.path.join(os.getcwd(), 'screenshots')
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)

        # For each matching email...
        for msg_id in messages:
            print("---> Processing message id {}...".format(msg_id.decode('UTF-8')))

            # Fetch it from the server
            status, data = mailbox.fetch(msg_id, '(RFC822)')
            if status == "OK":
                # Convert it to an Email object
                msg = email.message_from_bytes(data[0][1])

                # Get the HTML body payload
                msg_html = msg.get_payload(1).get_payload(decode=True)

                # Save the email timestamp
                datetime_received = datetime.fromtimestamp(
                    email.utils.mktime_tz(email.utils.parsedate_tz(msg.get('date'))))

                # Parse the message
                msg_parsed = BeautifulSoup(msg_html, 'html.parser')

                # Find the "View Gift" link
                # for link in msg_parsed.find_all('a'):
                #     print(link)
                #     pass

                egc_link = msg_parsed.find("a", text=re.compile("https://ikea-usa.cashstar.com/gift-card/view/"))
                if egc_link is not None:
                    # Open the link in the browser
                    browser.get(egc_link['href'])
                    emailaddr = browser.find_element_by_id("id_value")
                    emailaddr.send_keys(config.IMAP_USERNAME)
                    emailaddr.submit()
                    wait = WebDriverWait(browser, 10)
                    wait.until(EC.presence_of_element_located((By.ID, "skip")))
                    skip = browser.find_element_by_id("skip")
                    browser.get(skip.get_attribute("href"))

                    card_store, card_amount, card_number, card_pin = fetch_codes(browser)

                    # while card_number != barcode_number:
                    #     print("WARNING: Erroneous code found. Retrying.")
                    #     print("card_number: {}; barcode_number: {}".format(card_number, barcode_number))
                    #     browser.get(egc_link['href'])
                    #     card_type, card_amount, card_number, barcode_number = fetch_codes(browser)

                    # # Get the card PIN if it exists, otherwise set to N/A
                    # elem = browser.find_elements_by_xpath('//*[@id="main"]/div[2]/div[2]/p[2]/span')
                    # if len(elem) > 0:
                    #     card_pin = re.sub(r"\s+", '', browser.find_element_by_xpath('//*[@id="main"]/div[2]/div[2]/p[2]/span').text)
                    # else:
                    #     card_pin = 'N/A'

                    # Save a screenshot
                    browser.save_screenshot(os.path.join(screenshots_dir, card_number + '.png'))

                    # Write the details to the CSV
                    csv_writer.writerow([card_amount, card_number, card_pin, card_store, datetime_received, egc_link['href']])

                    # Print out the details to the console
                    print("{}: {} {}, {}, {}".format(card_amount, card_number, card_pin, card_store, datetime_received))
                else:
                    print("ERROR: Unable to find eGC link in message {}, skipping.".format(msg_id.decode('UTF-8')))
            else:
                print("ERROR: Unable to fetch message {}, skipping.".format(msg_id.decode('UTF-8')))

        # Close the browser
        browser.close()
else:
    print("FATAL ERROR: Unable to fetch list of messages from server.")
    exit(1)
