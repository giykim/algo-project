from datetime import datetime, timedelta

import numpy as np
import pandas as pd


def get_orders(df: pd.DataFrame, predictions: dict, perc_change: float):
    buy_orders = []
    sell_orders = []

    for date, value in predictions.items():
        if value[1]:
            for i in range(14): # in case market was closed
                cur_date = date + timedelta(days=i)
                if cur_date in df["Date"].values:
                    open_price = df[df["Date"] == cur_date].iloc[0]["Open Price"]
                    buy_orders.append((cur_date, open_price))
                    break

    count = 0
    for order_date, _ in buy_orders:
        count += 1
        idx = df[df["Date"] == order_date].index
        start_price = df.iloc[idx].iloc[0]["Open Price"]
        last_date = None
        for i in range(14):
            cur_date = order_date + timedelta(days=i)
            if cur_date in df["Date"].values:
                last_date = cur_date
                high_price = df[df["Date"] == cur_date].iloc[0]["High Price"]
                if (high_price - start_price) / start_price > perc_change:
                    sell_orders.append((cur_date, (1+perc_change) * start_price))
                    break
        if len(sell_orders) < count:
            close_price = df[df["Date"] == last_date].iloc[0]["Close Price"]
            sell_orders.append((last_date, close_price))

    return buy_orders, sell_orders
