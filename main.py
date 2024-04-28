from datetime import datetime, timedelta

import pandas as pd

from dash_app import dash_app
from feature_vector_creator import calc_price_change, feature_vector
from model import get_predictions


def main():
    df = feature_vector()
    feature_df = df.dropna()
    target_df = calc_price_change(feature_df)

    interval_length = 13
    feature_col = ["Open Price", "war", "conflict", "united states", "Count", "FEDFUNDS"]
    predictions = get_predictions(feature_df, target_df, feature_col, interval_length)

    daily_df = pd.read_csv("data/refinitiv_palantir_daily.csv")
    daily_df["Date"] = pd.to_datetime(daily_df["Date"])

    buy_orders = []
    sell_orders = []
    balance = 0

    for date, value in predictions.items():
        if value[1]:
            for i in range(14): # in case market was closed
                cur_date = date + timedelta(days=i)
                if cur_date in daily_df["Date"].values:
                    open_price = daily_df[daily_df["Date"] == cur_date].iloc[0]["Open Price"]
                    buy_orders.append((cur_date, open_price))
                    balance -= open_price
                    break
    print(buy_orders)

    count = 0
    for order_date, _ in buy_orders:
        count += 1
        idx = daily_df[daily_df["Date"] == order_date].index
        start_price = daily_df.iloc[idx].iloc[0]["Open Price"]
        last_date = None
        for i in range(14):
            cur_date = order_date + timedelta(days=i)
            if cur_date in daily_df["Date"].values:
                last_date = cur_date
                high_price = daily_df[daily_df["Date"] == cur_date].iloc[0]["High Price"]
                if (high_price - start_price) / start_price > 0.03:
                    sell_orders.append((cur_date, 1.03 * start_price))
                    break
        if len(sell_orders) < count:
            close_price = daily_df[daily_df["Date"] == last_date].iloc[0]["Close Price"]
            sell_orders.append((last_date, close_price))

    # TODO: Visualization
    dash_app(daily_df, buy_orders, sell_orders)

    # TODO: Get rid of bad trades


if __name__ == "__main__":
    main()

