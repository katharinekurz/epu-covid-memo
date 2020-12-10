import json
import requests
import csv
import io

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
stateraceresults = requests.get("https://docs.google.com/spreadsheets/d/e/2PACX-1vS8SzaERcKJOD_EzrtCDK1dX1zkoMochlA9iHoHg_RSw3V8bkpfk1mpw4pfL5RdtSOyx_oScsUtyXyk/pub?gid=43720681&single=true&output=csv")

def get_date_string(date):
    return "{}-{}-{}".format(date[:4], date[4:6], date[6:8])

def get_data():
    data = {}
    racedata = get_racedata()

    for row in json.loads(stateresults.text):
        date = str(row.get("date"))
        normalized_date = get_date_string(date)
        state = row.get("state")

        # only track specified states
        if state not in STATES:
            continue

        if state not in data:
            data[state] = {}
        record = racedata[state].get(normalized_date, {})
        record["Date"] = normalized_date
        record["hospitalized_currently"] = row["hospitalizedCurrently"]
        record["hospitalized_cumulative"] = row["hospitalizedCumulative"]
        data[state][normalized_date] = record
    return data

def get_racedata(): 
    reader = csv.DictReader(io.StringIO(stateraceresults.text))
    data = {}

    for row in reader:
        date = str(row.get("Date"))
        normalized_date = get_date_string(date)
        state = row.get("State")

        record = {}
        for attribute in list(row.keys()):
            if attribute in ["Date", "State"]:
                continue
            name = attribute.lower()
            record[name] = row[attribute]

        if state not in data:
            data[state] = {}
        
        data[state][normalized_date] = record
    return data
