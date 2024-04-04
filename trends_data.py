from datetime import datetime, timedelta
import json
import os

import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from serpapi import GoogleSearch


def get_trends(topics, override=False):
    if os.path.isfile("interest_over_time.json"):
        if not override:
            print("File already exists")
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

    with open("interest_over_time.json", "w") as outfile:
        json.dump(interest_over_time, outfile, indent=4)


def load_trends_data(topics):
    try:
        with open("interest_over_time.json") as infile:
            json_data = json.load(infile)
    except FileNotFoundError:
        print("File not found")
    except json.JSONDecodeError as e:
        print("JSON decoding error:", e)

    trends_list = []
    # cur_year = -1
    for data in json_data["timeline_data"]:
        row = []

        data_info = data["date"].split("\u2009–\u2009")

        # by start date
        # if cur_year == -1:
        #     cur_year = data_info[-1][-4:]
        # if "," in data_info[0]:
        #     row.append(data_info[0])
        # else:
        #     row.append(f"{data_info[0]}, {cur_year}")
        # cur_year = data_info[-1][-4:]

        # by end date
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
    trends_df.iloc[:, 0] = pd.to_datetime(trends_df.iloc[:, 0])
    trends_df.iloc[:, 0] += timedelta(days=2)

    col = ["Date"]
    for topic in topics.split(","):
        col.append(topic)
    trends_df.columns = col

    trends_df.to_csv("trends_data.csv", index=False)

    return json_data

topics = "war,conflict,united states"
get_trends(topics)
load_trends_data(topics)