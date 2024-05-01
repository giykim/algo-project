import pandas as pd


def calc_price_change(df: pd.DataFrame, perc_change: float) -> pd.DataFrame:
    target_df = pd.DataFrame()
    target_df["Date"] = df["Date"]
    target_df["Long"] = (df["High Price"] - df["Open Price"]) / df["Open Price"] > perc_change
    target_df["Short"] = (df["Low Price"] - df["Open Price"]) / df["Open Price"] < -perc_change
    target_df["badTrade"] = (df["Low Price"] - df["Open Price"]) / df["Open Price"] < -.12
    return target_df


def feature_vector():
    # Load the datasets
    stock_data = pd.read_csv("data/refinitiv_palantir_biweekly.csv")
    acled_data = pd.read_csv("data/events_over_time500.csv")
    trends_data = pd.read_csv("data/trends_data.csv")
    fed_data = pd.read_csv("data/fed_funds_complete.csv")

    stock_data["Date"] = pd.to_datetime(stock_data["Date"])
    acled_data["Date"] = pd.to_datetime(acled_data["Date"])
    trends_data["Date"] = pd.to_datetime(trends_data["Date"])
    fed_data["Date"] = pd.to_datetime(fed_data["Date"])


    # Merge the dataframes on the "Date" column
    merged_data = pd.merge(stock_data, acled_data, on="Date", how="left")
    merged_data = pd.merge(merged_data, trends_data, on="Date", how="left")
    merged_data = pd.merge(merged_data, fed_data, on="Date", how="left")

    # Save the merged dataframe to a new CSV file if needed
    merged_data.to_csv("data/merged_data.csv", index=False)
    return merged_data