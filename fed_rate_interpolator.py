import pandas as pd

def fill_missing_dates_with_latest_value(csv_file_path):
    # Load the CSV file
    fed_funds_data = pd.read_csv(csv_file_path)
    
    # Convert 'DATE' to datetime
    fed_funds_data['DATE'] = pd.to_datetime(fed_funds_data['DATE'])
    
    # Generate a complete range of dates with daily frequency
    daily_date_range = pd.date_range(start=fed_funds_data['DATE'].min(), end=fed_funds_data['DATE'].max(), freq='D')
    
    # Reindex the dataframe to include all dates in the daily range, filling forward the 'FEDFUNDS' values
    daily_fed_funds_complete = fed_funds_data.set_index('DATE').reindex(daily_date_range, method='ffill').reset_index()
    
    # Rename the 'index' column back to 'DATE'
    daily_fed_funds_complete.rename(columns={'index': 'DATE'}, inplace=True)
    
    # Convert 'DATE' back to the standard date format for consistency with original data
    daily_fed_funds_complete['DATE'] = daily_fed_funds_complete['DATE'].dt.strftime('20%y-%m-%d')
    
    return daily_fed_funds_complete

# Path to the CSV file
data_path = 'data/FEDFUNDS.csv'

# Process the CSV to fill in missing dates
updated_data = fill_missing_dates_with_latest_value(data_path)

# Optionally, save the updated data to a new CSV file
updated_data.to_csv('data/fed_funds_complete.csv', index=False)

print("Updated CSV has been saved.")