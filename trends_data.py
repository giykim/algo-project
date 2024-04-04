from datetime import datetime, timedelta
import json
import os

import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from serpapi import GoogleSearch


json_path = "interest_over_time.json"

def query_google_trends(topics, override=False):
    if os.path.isfile("interest_over_time.json"):
        if not override:
            print("Google trends JSON already exists")
            return

    print("Querying Google Trends")

    today = datetime.today()

    most_recent_monday = today - timedelta(days=today.weekday())

    start_date = most_recent_monday - timedelta(weeks=5 * 52)

    end_date = today + timedelta(days=(today.weekday() - 7))

    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    params = {
        "engine": "google_trends",
        "q": topics,
        "date": f"{start_date_str} {end_date_str}",
        "data_type": "TIMESERIES",
        "api_key": "" # insert personal key
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    interest_over_time = results["interest_over_time"]

    with open(json_path, "w") as outfile:
        json.dump(interest_over_time, outfile, indent=4)

    print(f"Saved Google trends query to {json_path}")


def process_trends_json(topics):
    try:
        with open(json_path) as infile:
            print(f"Reading interest data JSON")
            json_data = json.load(infile)
    except FileNotFoundError:
        print("Interest data JSON not found")
    except json.JSONDecodeError as e:
        print("JSON decoding error:", e)

    trends_list = []
    for data in json_data["timeline_data"]:
        row = []

        data_info = data["date"].split("\u2009–\u2009")

        if data_info[1][0].isdigit():
            row.append(f"{data_info[0].split(" ")[0]} {data_info[1]}")
        else:
            row.append(f"{data_info[1]}")

        for tmp in data["values"]:
            row.append(tmp["extracted_value"])

        trends_list.append(row)

    trends_df = pd.DataFrame(trends_list)

    scaler = MinMaxScaler()
    dates = trends_df.iloc[:, 0]
    values = pd.DataFrame(scaler.fit_transform(trends_df.iloc[:, 1:]), columns=trends_df.columns[1:])
    trends_df = pd.concat([dates, values], axis=1)
    trends_df.iloc[:, 0] = pd.to_datetime(trends_df.iloc[:, 0]).dt.date
    trends_df.iloc[:, 0] += timedelta(days=2)

    col = ["Date"]
    for topic in topics.split(","):
        col.append(topic)
    trends_df.columns = col

    csv_path = "trends_data.csv"
    trends_df.to_csv(csv_path, index=False)

    print(f"Saved Google trends JSON to {json_path}")


def google_trends_data(topics):
    query_google_trends(topics)
    process_trends_json(topics)


topics = "war,conflict,united states"
google_trends_data(topics)