# This script uses Python and BeautifulSoup to scrape financial data from the Web and build your own dataset for Options
# It is based loosely on the the tutorial given by Harry Sauers (https://www.freecodecamp.org/news/how-i-get-options-data-for-free-fba22d395cc8/)
# It uses the google cloud API through and OAuth 2.0 Client ID to access the google sheet. By using the standard google
# APIs included below, it allows this python script to access the contents of the google sheet cells. From that we can
# read wheat the users transactions are/have been and can pull the relevant price data from yahoo finance by using
# beautiful soup.

# Date: 6/10/2021
# Author: Kuan Chen
from bs4 import BeautifulSoup as bs
import requests
import datetime


def main():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
        "Upgrade-Insecure-Requests": "1", "DNT": "1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate"}  # allows yahoo finance to recognise how to display info
    data_url = 'https://finance.yahoo.com/quote/RKLB220414C00012500?p=RKLB220414C00012500'
    option_info = data_url[data_url.find('?p=') + 3:len(
        data_url)]  # cleans the url such that only the relevant information is present
    # option_info = 'SPY211008P00300000'

    if len(option_info) == 18:  # tickers can be 3 or 4 character so we need to account for two scenarios
        mod = 0
    elif len(option_info) == 19:
        mod = 1
    else:
        raise Exception("Something fucked up yo")
    ticker = option_info[0:3 + mod]  # otherwise the information is in a standardized and easy to access structure
    expiration = option_info[3 + mod:9 + mod]
    expiration_out = datetime.datetime(2000 + int(expiration[0:2]), int(expiration[2:4]), int(expiration[4:6]))
    type = option_info[9 + mod]
    if type == 'C':
        type_out = 'call'
    else:
        type_out = 'put'
    # print(expiration_out.strftime("%b %d %Y %H:%M:%S"))  # reformat date into more readable vers.

    data_html = requests.get(data_url, headers=headers).content  # pulls html data from the website listed
    content = bs(data_html, 'html.parser')  # parses html to usable format
    name_data = []
    price_data = []
    for tr in content.find_all('tr'):  # simple for loop which pulls data from table and places it in an array
        tds = tr.find_all('td')
        name_data.append(tds[0].text)
        price_data.append(tds[1].text)

    print(option_info)
    print(name_data)
    print(price_data)
    print(type_out)
    print(ticker)
    print(expiration_out)


if __name__ == '__main__':
    main()
