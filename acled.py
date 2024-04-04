import requests
import numpy as np
from datetime import datetime, timedelta

def fetch_data(page):
    base_url = "https://api.acleddata.com/acled/read.csv/"
    params = {
        "key": "tHgpcI60XvD8v014T1DP",
        "email": "hth8@duke.edu",
        "page": page,
        "fields": "event_id_cnty|event_date"
    }
    response = requests.get(base_url, params=params)
    return response.text

def get_events_data(pages=500):
    all_data = []
    for page in range(1, pages + 1):
        print(page)
        data = fetch_data(page)
        all_data.extend(data.split("\n")[1:-1])  # Skip header and last empty line
    return all_data

def process_data(data_list):
    # Convert to a list of tuples (date, event_count)
    processed_data = [(datetime.strptime(line.split(",")[1], '%Y-%m-%d'), 1) for line in data_list]
    return processed_data

def aggregate_events(data):
    # Sort by date
    data.sort(key=lambda x: x[0])
    start_date = data[0][0]
    end_date = data[-1][0]

    # Create a date range
    date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

    # Count events for each date in the range
    event_counts = []
    for current_date in date_range:
        count = sum(1 for date, _ in data if current_date - timedelta(days=14) < date <= current_date)
        event_counts.append([current_date.strftime('%Y-%m-%d'), count])
    
    return np.array(event_counts)

def main():
    raw_data = get_events_data()
    processed_data = process_data(raw_data)
    events_over_time = aggregate_events(processed_data)
    np.savetxt("events_over_time500.csv", events_over_time, delimiter=",", fmt='%s', header="Date Event Count", comments='')


if __name__ == "__main__":
    main()