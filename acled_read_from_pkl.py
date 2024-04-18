import requests
import numpy as np
from datetime import datetime, timedelta
import csv
import pickle


def get_events_data(pages=500):
    with open('raw_data.pkl', 'rb') as f:
        all_data = pickle.load(f)
    return all_data

def process_data(data_list):
    # Convert to a list of tuples (date, event_count)
    processed_data = [(datetime.strptime(line.split(",")[1], '%Y-%m-%d'), 1) for line in data_list]

    with open('processed_data.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Date', 'Event Count'])
        writer.writerows(processed_data)

    return processed_data

def aggregate_events(data):
    # Ensure data is sorted by date
    data.sort(key=lambda x: x[0])
    start_date = data[0][0]
    end_date = data[-1][0]

    # Generate a complete date range from start to end
    date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

    event_counts = []

    # Indices to maintain the sliding window's range within the data
    window_start = 0
    window_end = 0
    print(len(date_range))
    i = 0
    for current_date in date_range:
        # Move the window's start to exclude events older than 14 days from the current date
        while window_start < len(data) and data[window_start][0] < current_date - timedelta(days=14):
            window_start += 1
        
        # Adjust the window's end to include all events up to and including the current date
        while window_end < len(data) and data[window_end][0] <= current_date:
            window_end += 1
        
        # The number of events within the window is the difference between end and start indices
        count = window_end - window_start
        event_counts.append([current_date.strftime('%Y-%m-%d'), count])
        print(i)
        i += 1
    return np.array(event_counts)

def main():
    raw_data = get_events_data()
    
    processed_data = process_data(raw_data)
    events_over_time = aggregate_events(processed_data)
    np.savetxt("events_over_time500.csv", events_over_time, delimiter=",", fmt='%s', header="Date Event Count", comments='')


if __name__ == "__main__":
    main()