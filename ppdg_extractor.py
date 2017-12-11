import os
import email
import re
import csv
import sys
from datetime import datetime, timedelta, date
from imaplib import IMAP4, IMAP4_SSL
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

import config

# Fetch codes from DOM
def fetch_codes(browser):
    # card store
    subdiv = 3
    try:
        browser.find_element_by_id("DM_categories")
        subdiv = 4
    except NoSuchElementException:
        pass

    card_store = browser.find_element_by_xpath("//*[@id=\"main-content\"]/div[3]/div/div["+str(subdiv)+"]/section/div/div[1]/div/div/img").get_attribute("alt")

    # Get the card amount
    try:
        browser.find_element_by_class_name("barcode")
        card_amount = browser.find_element_by_xpath("//*[@id=\"main-content\"]/div[3]/div/div["+str(subdiv)+"]/section/div/div[1]/div/div/div[2]/dl[1]/dd").text.strip()
        # Get the card number
        card_code = browser.find_element_by_xpath("//*[@id=\"main-content\"]/div[3]/div/div["+str(subdiv)+"]/section/div/div[1]/div/div/div[2]/dl[2]/dd").text.strip()
        try:
            card_pin = browser.find_element_by_xpath("//*[@id=\"main-content\"]/div[3]/div/div["+str(subdiv)+"]/section/div/div[1]/div/div/div[2]/dl[3]/dd").text.strip()
        except NoSuchElementException:
            card_pin = ''
            
    except NoSuchElementException:
        card_amount = browser.find_element_by_xpath("//*[@id=\"main-content\"]/div[3]/div/div["+str(subdiv)+"]/section/div/div[1]/div/div/div[1]/dl[1]/dd").text.strip()
        # Get the card number
        card_code = browser.find_element_by_xpath("//*[@id=\"main-content\"]/div[3]/div/div["+str(subdiv)+"]/section/div/div[1]/div/div/div[1]/dl[2]/dd").text.strip()
        try:
            card_pin = browser.find_element_by_xpath("//*[@id=\"main-content\"]/div[3]/div/div["+str(subdiv)+"]/section/div/div[1]/div/div/div/dl[3]/dd").text.strip()
        except NoSuchElementException:
            card_pin = ''

    return card_store, card_amount, card_code, card_pin


# Connect to the server
if config.IMAP_SSL:
    mailbox = IMAP4_SSL(host=config.IMAP_HOST, port=config.IMAP_PORT)
else:
    mailbox = IMAP4(host=config.IMAP_HOST, port=config.IMAP_PORT)

# Log in and select the configured folder
mailbox.login(config.IMAP_USERNAME, config.IMAP_PASSWORD)
mailbox.select(config.FOLDER)

# Search for matching emails
days = 0
if len(sys.argv) > 1:
    days = int(sys.argv[1])

# Search for matching emails
if  days> 0:
    since = (date.today() - timedelta(days-1)).strftime("%d-%b-%Y")
    status, messages = mailbox.search(None, '(FROM {})'.format("gifts@paypal.com") + ' SINCE ' + since)
else:
    status, messages = mailbox.search(None, '(FROM {})'.format("gifts@paypal.com"))

if status == "OK":
    # Convert the result list to an array of message IDs
    messages = messages[0].split()

    if len(messages) < 1:
        # No matching messages, stop
        print("No matching messages found, nothing to do.")
        exit()

    # Open the CSV for writing
    with open('ppdg_' + datetime.now().strftime('%m-%d-%Y_%H%M%S') + '.csv', 'w', newline='') as csv_file:
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
                msg_html = msg.get_payload(decode=True)

                # Save the email timestamp
                datetime_received = datetime.fromtimestamp(
                    email.utils.mktime_tz(email.utils.parsedate_tz(msg.get('date'))))

                # Parse the message
                msg_parsed = BeautifulSoup(msg_html, 'html.parser')

                # Find the "View Gift" link

                egc_link = msg_parsed.find("a", text="View My Code")
                if egc_link is not None:
                    # Open the link in the browser
                    browser.get(egc_link['href'])

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
                    csv_writer.writerow([card_number, card_pin, card_amount, card_store, datetime_received, egc_link['href']])

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
