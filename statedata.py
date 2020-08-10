import json
import requests

STATES = [
    "AL",
    "AK",
    "FL",
    "GA",
    "KY",
    "LA",
    "MS",
    "NC",
    "SC",
    "TN",
    "TX",
    "VA",
    "WV"
]

stateresults = requests.get("https://covidtracking.com/api/v1/states/daily.json")
stateraceresults = requests.get("https://docs.google.com/spreadsheets/d/e/2PACX-1vR_xmYt4ACPDZCDJcY12kCiMiH0ODyx3E1ZvgOHB8ae1tRcjXbs_yWBOA4j4uoCEADVfC1PS2jYO68B/pub?gid=43720681&single=true&output=csv")

def get_data():
    data = {}
    for row in json.loads(stateresults.text):
        date = str(row.get("date"))
        normalized_date = "{}-{}-{}".format(date[:4], date[4:6], date[6:8])
        state = row.get("state")
        if state not in data:
            data[state] = {}
        
        record = {}
        record["date"] = normalized_date
        record["hospitalized_currently"] = row["hospitalizedCurrently"]
        record["hospitalized_cumulative"] = row["hospitalizedCumulative"]
        data[state][normalized_date] = record

    
    return data

