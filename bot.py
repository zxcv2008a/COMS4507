import os
import requests
import time

# Constants
INITIAL_BALANCE = 1000000  # $1 million
INTERVALS = 60  # seconds
STOP_LOSS_PERCENTAGE = 0.05  # 5%


# Functions
def get_price():
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {"X-CMC_PRO_API_KEY": os.getenv("COINMARKETKEY")}
    params = {"symbol": "BTC"}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return data["data"]["BTC"]["quote"]["USD"]["price"]
    else:
        return None


def take_decision(price, balance, buy_order, sell_order):
    if buy_order is None:
        # Check if we have enough balance to place a new buy order
        if balance > 0:
            # Calculate the amount of BTC we can buy with our balance
            amount = balance / price
            # Place the buy order (replace this with your own code for getting buy orders)
            buy_order = {"amount": amount, "price": price}
            print("New buy order placed:", buy_order)
        else:
            print("Insufficient balance to place a new buy order")
    elif sell_order is None:
        # Check if the price has gone up enough to place a new sell order
        if price >= buy_order["price"] * 1.05:  # 5% profit
            # Calculate the amount of BTC we can sell for a 5% profit
            amount = buy_order["amount"]
            sell_price = price
            # Place the sell order (replace this with your own code for getting sell orders)
            sell_order = {"amount": amount, "price": sell_price}
            print("New sell order placed:", sell_order)
        elif price <= buy_order["price"] * (1 - STOP_LOSS_PERCENTAGE):
            # If the price falls below our stop loss threshold, sell at a loss
            amount = buy_order["amount"]
            sell_price = price
            sell_order = {"amount": amount, "price": sell_price}
            print("Stop loss triggered:", sell_order)
        else:
            print("Waiting for price to reach sell threshold")
    else:
        # Check if the sell order has been filled
        if price >= sell_order["price"]:
            # Calculate the profit/loss from the trade
            profit = (sell_order["price"] - buy_order["price"]) * sell_order["amount"]
            balance += profit
            print("Trade completed. Profit:", profit, "New balance:", balance)
            # Reset the buy and sell orders
            buy_order = None
            sell_order = None
        else:
            print("Waiting for sell order to be filled")
    return buy_order, sell_order, balance


# Main program
balance = INITIAL_BALANCE
buy_order = None
sell_order = None

while True:
    price = get_price()
    if price is not None:
        print("Current price of BTC: $", price)
        buy_order, sell_order, balance = take_decision(
            price, balance, buy_order, sell_order
        )
    else:
        print("Error getting price from CoinMarketCap API")

    time.sleep(INTERVALS)
