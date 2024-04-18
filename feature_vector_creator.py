import pandas as pd


def feature_vector():
    # Load the datasets
    stock_data = pd.read_csv("data/refinitivOHLC_2Weeks_3Years.csv")
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