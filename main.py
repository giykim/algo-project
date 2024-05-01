import pandas as pd

from dash_app import App
from feature_vector_creator import calc_price_change, feature_vector
from model import get_predictions
from orders import create_blotter, get_orders


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
    pred, pred_stats = get_predictions(feature_df, target_df, feature_col, interval_length, True, True)

    # Get buy and sell orders based on predictions
    daily_df = pd.read_csv("data/refinitiv_palantir_daily.csv")
    daily_df["Date"] = pd.to_datetime(daily_df["Date"])
    first_idx = daily_df[daily_df["Date"] == first_date].index[0]
    daily_df = daily_df.iloc[first_idx:]
    daily_df.reset_index(drop=True, inplace=True)
    buy_orders, sell_orders = get_orders(daily_df, pred, perc_change)

    # Get and analyze blotter
    blotter_df, blotter_stats = create_blotter(buy_orders, sell_orders, first_date, True)

    # TODO: Get rid of bad trades
    badTradesDf = blotter_df.copy()
    badTradesDf['badTrade'] = (badTradesDf['DailyReturn'] <= -0.01).astype(int)

    
    # Visualization
    app = App(daily_df, blotter_df, blotter_stats)
    app.run_app()


if __name__ == "__main__":
    main()

