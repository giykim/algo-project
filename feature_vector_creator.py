import pandas as pd

# Load the datasets
stock_Data = pd.read_csv("refinitivOHLC_2Weeks_3Years.csv")
acled_Data = pd.read_csv("events_over_time.csv")

# Ensure the 'Date' columns in both dataframes are in the same format
stock_Data['Date'] = pd.to_datetime(stock_Data['Date'])
acled_Data['Date'] = pd.to_datetime(acled_Data['Date'])

# Merge the dataframes on the 'Date' column
# This will add the feature value from acled_Data to stock_Data based on matching dates
merged_Data = pd.merge(stock_Data, acled_Data, on='Date', how='left')

# 'how='left'' ensures that all rows from stock_Data are kept in the merged dataframe,
# even if there's no matching date in acled_Data (the feature value for these rows will be NaN)

# You might want to fill NaN values if any, depending on your needs, for example:
# merged_Data.fillna({'feature_column_name': 0}, inplace=True)

# Save the merged dataframe to a new CSV file if needed
merged_Data.to_csv("merged_Stock_and_Acled_Data.csv", index=False)

print(merged_Data)