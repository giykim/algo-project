import numpy as np
import pandas as pd

from orders import create_blotter, get_orders
from dash_app import dash_app
from feature_vector_creator import calc_price_change, feature_vector
from model import get_predictions


def main():
    # Get Data
    df = feature_vector()
    feature_df = df.dropna()
    perc_change = 0.05
    target_df = calc_price_change(feature_df, perc_change)

    # Predict whether to long
    interval_length = 13
    first_date = feature_df.iloc[interval_length + 1]["Date"]
    print(f"Starting at {first_date}")
    feature_col = ["Open Price", "war", "conflict", "united states", "Count", "FEDFUNDS"]
    predictions = get_predictions(feature_df, target_df, feature_col, interval_length, True)

    # Get buy and sell orders based on predictions
    daily_df = pd.read_csv("data/refinitiv_palantir_daily.csv")
    daily_df["Date"] = pd.to_datetime(daily_df["Date"])
    first_idx = daily_df[daily_df["Date"] == first_date].index[0]
    daily_df = daily_df.iloc[first_idx:]
    daily_df.reset_index(drop=True, inplace=True)
    buy_orders, sell_orders = get_orders(daily_df, predictions, perc_change)

    # TODO: Create blotter
    blotter_df = create_blotter(buy_orders, sell_orders, first_date, True)

    # TODO: Analyze blotter

    # TODO: Get rid of bad trades

    # Visualization
    # dash_app(daily_df, buy_orders, sell_orders)


if __name__ == "__main__":
    main()

