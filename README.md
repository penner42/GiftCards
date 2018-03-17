# eGift Card Extractor, Swiper, Barcode reader

This script will attempt to extract the card type, amount, number, and PIN
given the claim emails sent by a variety of gift card providers and format it as a CSV.
The script will also optionally take a screenshot of each card.

## Installation
Requires Python 3.

Download or clone this repo and install 
[ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/).
Install the dependencies with `pip install -r requirements.txt`. Choose chromedriver location 
and fill in email address information in Settings tab.

Note: Kivy 1.10.0 clipboard is broken, and this currently requires Kivy 1.10.1-dev0. 
Installation is not completely straightforward. A bug in pip requires Cython to be 
installed separately prior to installing Kivy (```pip3 install Cython=0.25.2```). See Kivy installation instructions for building from
source. ```pip3 install git+https://github.com/kivy/kivy.git@master``` should work if all 
prerequisites are installed properly. Tested on Windows and Linux. Mac TBD.
