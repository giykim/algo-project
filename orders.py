from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def create_blotter(buy_orders: list,
                   sell_orders: list,
                   first_date: datetime.timestamp,
                   print_stats: bool = False):
    blotter_df = pd.DataFrame(columns=["Identifier",
                                       "EntryTimestamp",
                                       "ExitTimestamp",
                                       "TradeQuantity",
                                       "Price",
                                       "EntryPrice",
                                       "ExitPrice",
                                       ])
    stats = {}

    for i in range(len(buy_orders)):
        row = {"Identifier": "PLTR.K",
               "EntryTimestamp": buy_orders[i][0],
               "ExitTimestamp": sell_orders[i][0],
               "Quantity": 1,
               "EntryPrice": buy_orders[i][1],
               "ExitPrice": sell_orders[i][1],
               }
        blotter_df = pd.concat([blotter_df, pd.DataFrame([row])], ignore_index=True)

    blotter_df["EntryTimestamp"] = blotter_df["EntryTimestamp"].dt.date
    blotter_df["ExitTimestamp"] = blotter_df["ExitTimestamp"].dt.date

    # Extra Stats
    blotter_df["Days"] = np.maximum(1, (blotter_df["ExitTimestamp"] - blotter_df["EntryTimestamp"]).dt.days)
    blotter_df["Return"] = np.log(blotter_df["ExitPrice"] / blotter_df["EntryPrice"]) * np.sign(blotter_df["Quantity"])
    blotter_df["DailyReturn"] = blotter_df["Return"] / blotter_df["Days"]
    blotter_df["Value"] = abs(blotter_df["Quantity"] * blotter_df["EntryPrice"])
    matched_df = blotter_df[pd.notna(blotter_df["ExitTimestamp"])]
    portfolio_value = np.sum(matched_df["Value"])
    grouped_df = matched_df.groupby("Identifier")

    # Strategy Expected Returns
    expected_returns = {}
    weights = {}
    for name, group in grouped_df:
        identifier = matched_df[matched_df["Identifier"] == name]
        expected_returns[name] = np.prod(1 + identifier["DailyReturn"]) ** (1 / len(identifier)) - 1
        weights[name] = np.sum(identifier["Value"]) / portfolio_value
    expected_portfolio_returns = np.sum([x * y for x, y in zip(weights.values(), expected_returns.values())])
    stats["ExpectedReturns"] = expected_portfolio_returns
    if print_stats:
        print(f"Strategy's Expected Returns: {round(100 * expected_portfolio_returns, 4)}%")

    # Volatility
    portfolio_volatility = np.std(matched_df["DailyReturn"])
    stats["Volatility"] = portfolio_volatility
    if print_stats:
        print(f"Strategy's Volatility: {round(portfolio_volatility, 4)}")

    # Risk Free Rate
    # https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=2023
    risk_free_rate = 0.09 / 30 / 100
    if print_stats:
        print(f"Daily Risk Free Rate: {round(100 * risk_free_rate, 4)}%")
        print(f"\t(based on {first_date.date()})")

    # Sharpe Ratio
    sharpe = (expected_portfolio_returns - risk_free_rate) / portfolio_volatility
    stats["Sharpe"] = sharpe
    if print_stats:
        print(f"Strategy's Sharpe Ratio: {round(sharpe, 4)}")

    spx = pd.read_csv("data/spx_daily.csv")
    spx = pd.DataFrame(spx.drop_duplicates(subset=["Date"]))
    spx["Date"] = pd.to_datetime(spx["Date"])

    spx["SPXReturn"] = np.log(spx["Price Close"] / spx["Price Close"].shift(1))
    spx["SPXDays"] = spx["Date"].diff().dt.days
    spx.drop(spx.index[0], inplace=True)
    spx = spx.reset_index(drop=True)
    spx["SPXDailyReturn"] = spx["SPXReturn"] / spx["SPXDays"]

    date_range = pd.date_range(start=spx["Date"].min(), end=spx["Date"].max(), freq="D")
    spx = spx.set_index("Date").reindex(date_range).reset_index()
    spx.rename(columns={"index": "Date"}, inplace=True)
    spx = spx.fillna(method="bfill")
    spx["Date"] = spx["Date"].dt.date

    blotter_df = pd.merge(blotter_df, spx, left_on="ExitTimestamp", right_on="Date", how="left")
    num_days = (blotter_df.iloc[-1]["Date"] - blotter_df.iloc[0]["Date"]).days

    lin_reg = LinearRegression()
    matched_df = blotter_df[pd.notna(blotter_df["DailyReturn"])]
    X = matched_df["SPXDailyReturn"].values.reshape(-1, 1)
    y = matched_df["DailyReturn"]

    lin_reg.fit(X, y)
    alpha = lin_reg.intercept_
    beta = lin_reg.coef_[0]
    stats["Alpha"] = alpha
    stats["Beta"] = beta
    print(f"Alpha: {round(alpha, 4)}")
    print(f"Beta: {round(beta, 4)}")

    # Expected Return
    expected_market_return = np.prod(1 + blotter_df["SPXDailyReturn"]) ** (1 / num_days) - 1
    expected_sml_return = risk_free_rate + beta * (expected_market_return - risk_free_rate)

    distance = abs(expected_portfolio_returns - expected_sml_return)
    stats["DistanceSML"] = distance
    print(f"Distance Between Strategy and Security Market Line: {round(distance, 4)}")

    blotter_df.drop(["Date",
                     "Instrument",
                     "TradeQuantity",
                     "Price",
                     "Price Close",
                     "SPXReturn",
                     "SPXDays",
                     "SPXDailyReturn",
                     ],
                    axis=1, inplace=True)

    return blotter_df, stats

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
