import os

import requests
from datetime import datetime, timedelta
from twilio.rest import Client
from bs4 import BeautifulSoup
import lxml
from smtplib import SMTP

My_email = os.environ["my_email"]
My_pass = ""
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
stock_api_key = os.environ["stock_api_key"]
news_api_key = os.environ["news_api_key"]
account_sid = "AC40115e87d53567139128a718375635c2"
auth_token = os.environ["auth_token"]
msgList= ["Subject:Stock Alerts 📈\n\n"]


stocks = {
    "TSLA": "Tesla Inc",
    "NVDA": "NVIDIA Corporation",
    "AAPL": "Apple Inc",
    "MSFT": "Microsoft Corporation",
    "AMZN": "Amazon.com, Inc.",
}
yesterday = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
dayBefYest = datetime.strftime(datetime.now() - timedelta(2), '%Y-%m-%d')
for stock in stocks:
    parameters = {
        "function": "TIME_SERIES_DAILY",
        "symbol": stock,
        "apikey": stock_api_key

    }
    news_parameters = {
        "qInTitle": stocks[stock],
        "apiKey": news_api_key
    }

    response = requests.get(url=STOCK_ENDPOINT, params=parameters)
    response.raise_for_status()
    time_series = response.json()["Time Series (Daily)"]
    yestClose = float(time_series[yesterday]['4. close'])
    dayBefClose = float(time_series[dayBefYest]['4. close'])
    delta = yestClose - dayBefClose
    print(stocks[stock])
    print(delta)

    emoji = ""
    if delta > 0:
        emoji = "🔺"
    else:
        emoji = "🔻"
    percentChange = (abs(delta) / yestClose) * 100
    print(percentChange)
    if percentChange > 2:
        response = requests.get(url=NEWS_ENDPOINT, params=news_parameters)
        articles = response.json()['articles'][slice(0, 2)]
        print(articles)
        compressed_list = [
            f"_{stocks[stock]}, {stock}  {emoji}{percentChange}, {round(abs(delta), 2)}_\n\n*Headline:*\n{article['title']}. \n\n*Brief:*\n{BeautifulSoup(article['description'], 'lxml').text}\n\n*Link:*\n{article['url']}\n"
            for article in articles]
        print(compressed_list)
        client = Client(account_sid, auth_token)
        for article in compressed_list:
            print(article)
            message = client.messages.create(
                body=article,
                from_='whatsapp:+14155238886',
                to='whatsapp:+917032422043')
            msgList.append(article)

with SMTP("smtp.gmail.com") as connection:
    connection.starttls()
    connection.login(My_email, My_pass)
    connection.sendmail(from_addr=My_email, to_addrs=My_email, msg= "".join(msgList).encode('utf-8'))
