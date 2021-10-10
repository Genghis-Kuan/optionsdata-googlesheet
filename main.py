from __future__ import print_function
from bs4 import BeautifulSoup as bs
import requests
import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
# This script uses Python and BeautifulSoup to scrape financial data from the Web and build your own dataset for Options
# It is based loosely on the the tutorial given by Harry Sauers (https://www.freecodecamp.org/news/how-i-get-options-data-for-free-fba22d395cc8/)
# It uses the google cloud API through and OAuth 2.0 Client ID to access the google sheet. By using the standard google
# APIs included below, it allows this python script to access the contents of the google sheet cells. From that we can
# read wheat the users transactions are/have been and can pull the relevant price data from yahoo finance by using
# beautiful soup.

# Date: 6/10/2021
# Author: Kuan Chen



# https://developers.google.com/sheets/api/quickstart/python
# https://developers.google.com/workspace/guides/create-credentials
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '12-XSq38g7wJ9Jz1wmEJSEhaWSgvOQ5wv3Qs2tGVw_Jk'
SAMPLE_RANGE_NAME = 'Derivatives Transactions!C3:N'


def main():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
        "Upgrade-Insecure-Requests": "1", "DNT": "1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate"}  # allows yahoo finance to recognise how to display info
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        for i in range(len(values)):  # everything will happen within this loop
            ticker = values[i][0]
            strike = values[i][4]
            dir_type = values[i][5]
            exp_date = values[i][6]
            # print(ticker, strike, dir_type, exp_date)

            # Reformat variables above into yahoo finance (yf) format
            yf_ticker = ticker  # ticker needs no format
            yf_strike = '000' + str(int(float(strike) * 1000))  # strike format
            yf_dir_type = 'C' if  dir_type == 'Call' else 'P'  # direction format

            yf_exp_temp = exp_date.partition('/')
            yf_exp_day = yf_exp_temp[0]  # day format
            if len(str(yf_exp_day)) == 1:  # accounts for one digit days
                yf_exp_day = '0' + yf_exp_day
            yf_exp_temp = yf_exp_temp[2].partition('/')
            yf_exp_month = yf_exp_temp[0]  # month format
            if len(str(yf_exp_month)) == 1:  # accounts for one digit months
                yf_exp_month = '0' + yf_exp_month
            yf_exp_year = yf_exp_temp[2]  # year format
            yf_exp_year = str(int(yf_exp_year) - 2000)
            yf_exp_date = yf_exp_year + yf_exp_day + yf_exp_month
            # print(yf_exp_date)

            # Compile the pulled ticked from the gsheet into a data using yf format

            yf_data = yf_ticker + yf_exp_date + yf_dir_type + yf_strike
            data_url = 'https://finance.yahoo.com/quote/' + yf_data + '?p=' + yf_data
            print(data_url)
            # option_info = data_url[data_url.find('?p=') + 3:len(
            #     data_url)]  # cleans the url such that only the relevant information is present
            # option_info = 'SPY211008P00300000'

            # if len(option_info) == 18:  # tickers can be 3 or 4 character so we need to account for two scenarios
            #     mod = 0
            # elif len(option_info) == 19:
            #     mod = 1
            # else:
            #     raise Exception("Something fucked up yo")
            # ticker = option_info[0:3 + mod]  # otherwise the information is in a standardized and easy to access structure
            # expiration = option_info[3 + mod:9 + mod]
            # expiration_out = datetime.datetime(2000 + int(expiration[0:2]), int(expiration[2:4]), int(expiration[4:6]))
            # type = option_info[9 + mod]
            # if type == 'C':
            #     type_out = 'call'
            # else:
            #     type_out = 'put'
            # # print(expiration_out.strftime("%b %d %Y %H:%M:%S"))  # reformat date into more readable vers.
            #
            # data_html = requests.get(data_url, headers=headers).content  # pulls html data from the website listed
            # content = bs(data_html, 'html.parser')  # parses html to usable format
            # name_data = []
            # price_data = []
            # for tr in content.find_all('tr'):  # simple for loop which pulls data from table and places it in an array
            #     tds = tr.find_all('td')
            #     name_data.append(tds[0].text)
            #     price_data.append(tds[1].text)
            #
            # print(option_info)
            # print(name_data)
            # print(price_data)
            # print(type_out)
            # print(ticker)
            # print(expiration_out)


if __name__ == '__main__':
    main()
