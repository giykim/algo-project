from datetime import datetime, timedelta

from dash_app import dash_app
import pandas as pd

from feature_vector_creator import calc_price_change, feature_vector
from model import get_predictions


def main():
    feature_df = feature_vector()
    feature_df = feature_df.dropna()
    target_df = calc_price_change(feature_df)

    interval_length = 52
    feature_col = ["Open Price", "war", "conflict", "united states", "FEDFUNDS"]
    predictions = get_predictions(feature_df, target_df, feature_col, interval_length)

    # sell_orders = [date + timedelta(days=14) for date in buy_orders]

    # TODO: Visualization
    dash_app(feature_df)

    # TODO: Get rid of bad trades


if __name__ == "__main__":
    main()

