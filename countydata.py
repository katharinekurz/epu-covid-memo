import requests
import csv
import xlwt
import datetime
import statedata

COUNTIES = {
    "Alabama": ["Jefferson", "Montgomery"],
    "Arkansas": ["Benton" , "Washington"],
    "Florida": ["Miami-Dade"],
    "Georgia": ["Muscogee"],
    "Kentucky": ["Perry" , "Jefferson" , "Pike" , "Letcher"],
    "Louisiana": ["East Carroll" ,  "Orleans" , "Madison"],
    "Mississippi": ["Bolivar" , "Sunflower" , "Washington" , "Hinds" , ],
    "North Carolina": ["Mecklenburg"],
    "South Carolina": ["Charleston"],
    "Tennessee": ["Knox"],
    "Texas": ["Harris"],
    "Virginia": ["Richmond city"],
    "West Virginia": ["Kanawha" , "Boone" , "Mingo"]
}

DEFAULT_RECORD = {
    "cases": 0,
    "deaths": 0,
}

# fetch the latest covid records per state and county
result = requests.get("https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv")

# write the covid cases to a temporary file
with open("data" , "w") as file:
    file.write(result.text)

def get_data(file_path):
    """
    Reads the historical records from given CSV file.

    :param file_path: The path to the CSV file.
    """
    data = {}
    with open("data" , "r") as file:
        csvreader = csv.DictReader(file)

        # loop through every record
        for row in csvreader:
            # get the state, county and date for the current record.
            state = row["state"]
            county = row["county"]
            date = row["date"]

            if state not in data :
                data[state] = {}

            if county not in data [state]:
                data[state][county] = {}

            # accumulate the county-level data to the data object, indexed by
            # state, then county.
            data[state][county][date] = row
    return data 

def get_state_data(state, data):
    """
    Gets the cases and deaths, per date, for a given state.

    :param state: The name of the state to query data for.
    :param data: The data parsed from the CSV file.

    outputs data in the given format:
    {
        "2020-03-30": {
            "cases": 20,
            "deaths": 5
        },
        "2020-03-31": {
            "cases": 45,
            "deaths": 2
        }
    }
    """
    per_day = {}

    # get the data for the state
    state_data = data[state]

    # loop over all the county data for the state.
    for county in state_data:
        # loop through all the dates in the county records.
        for date in state_data[county]:
            # get the data for the current date, in the given county.
            row = data[state][county][date]

            if date not in per_day :
                per_day [date] = {"cases": 0, "deaths": 0}
            
            # accumulate the county level cases and deaths to the overall
            # state cases and deaths count, for the current date.
            per_day[date]["cases"] += int(row["cases"])
            per_day[date]["deaths"] += int(row["deaths"])

    # return the state data, organized per day.
    return per_day


def get_county_data(county, state, data):
    """
    Gets the cases and deaths, per date, for a given county.

    :param county: The name of the county to query data for.
    :param state: The name of the county to query data for.
    :param data: The data parsed from the CSV file.

    outputs data in the given format:
    {
        "2020-03-30": {
            "cases": 20,
            "deaths": 5
        },
        "2020-03-31": {
            "cases": 45,
            "deaths": 2
        }
    }
    """
    per_day = {}

    # get the records for the given state
    state_data = data[state]

    # get the records for the given county
    county_data = state_data[county]

    for date in county_data:
        per_day[date] = {}
        per_day[date]["cases"] = county_data[date]["cases"]
        per_day[date]["deaths"] = county_data[date]["deaths"]
    
    return per_day

data = get_data("data")


# Tuesday is the 2nd day of the week, starting from 0, so
# it's represented as 1.
TUESDAY = 1

def get_tuesday_range():
    """
    Returns a date pointing to the most recent Tuesday, and another date
    pointing to the wednesday before it.
    """
    today = datetime.date.today()

    # this is the number of days from Tuesday
    day_delta = today.weekday() - TUESDAY

    week_delta = 0

    if day_delta < 0:
        # if day_delta is negitive, we need to look at last week.
        week_delta = 1

    most_recent_tuesday = today - datetime.timedelta(days=day_delta, weeks=week_delta)
    previous_tuesday = today - datetime.timedelta(days=day_delta, weeks=week_delta + 1)

    return previous_tuesday, most_recent_tuesday


def get_next_day(date):
    """
    Returns the next day's date, relative to the given date.
    """
    return date + datetime.timedelta(days=1)

def get_week_interval():
    """
    Returns a list of date strings for the last 8 days, from the most recent tuesday,
    in ascending order.
    """
    start_day, end_day = get_tuesday_range()
    current_day = start_day
    date_strings = []

    while current_day.ctime() != get_next_day(end_day).ctime():
        date_string = current_day.strftime('%Y-%m-%d')
        date_strings.append(date_string)
        current_day = get_next_day(current_day)

    return date_strings

def write_header(sheet, columns):
    for index, column in enumerate(columns):
        sheet.write(0, index + 1, column)
    
wb = xlwt.Workbook(encoding="utf-8")


def export_county_data_to_excel(wb, county, state, data):
    sheet_name = "{}-{}".format(county, state)
    sheet = wb.add_sheet(sheet_name)
    write_header(sheet, ["County Cases", "County Deaths", "State Cases", "State Deaths"])

    state_data = get_state_data(state, data)
    county_data = get_county_data(county, state, data)

    for row, date in enumerate(state_data):
        state_records = state_data.get(date)
        county_records = county_data.get(date, DEFAULT_RECORD)

        sheet.write(row+1, 0, date)
        sheet.write(row+1, 1, county_records["cases"])
        sheet.write(row+1, 2, county_records["deaths"])
        sheet.write(row+1, 3, state_records["cases"])
        sheet.write(row+1, 4, state_records["deaths"])

state_metadata = statedata.get_data()

def export_state_metadata_to_excel(wb, state, data):
    sheet_name = "{} metadata".format(state)
    sheet = wb.add_sheet(sheet_name)

    columns = [
        "hospitalized_currently",
        "hospitalized_cumulative",
        "cases_total",
        "cases_white",
        "cases_black",
        "cases_latinx",
        "cases_asian",
        "cases_aian",
        "cases_nhpi",
        "cases_multiracial",
        "cases_other",
        "cases_unknown",
        "cases_ethnicity_hispanic",
        "cases_ethnicity_nonhispanic",
        "cases_ethnicity_unknown",
        "deaths_total",
        "deaths_white",
        "deaths_black",
        "deaths_latinx",
        "deaths_asian",
        "deaths_aian",
        "deaths_nhpi",
        "deaths_multiracial",
        "deaths_other",
        "deaths_unknown",
        "deaths_ethnicity_hispanic",
        "deaths_ethnicity_nonhispanic",
        "deaths_ethnicity_unknown"
    ]

    write_header(sheet, columns)
    state_data = state_metadata[state]

    dates = list(reversed(list(state_data.keys())))
    for row, date in enumerate(dates):
        state_records = state_data.get(date)
        sheet.write(row+1, 0, date)
        for index, column in enumerate(columns):
            sheet.write(row+1, index+1, state_records.get(column))


def export_county_increases_to_excel(wb, county, state, data):
    sheet_name = "{}-{}-i".format(county, state)
    sheet = wb.add_sheet(sheet_name)
    write_header(sheet, ["County Case Increases", "County Death Increases", "State Case Increases", "State Death Increases"])
    
    state_data = get_state_data(state, data)
    county_data = get_county_data(county, state, data)

    date_strings = get_week_interval()

    start_date = date_strings[0]
    last_state_cases = int(state_data.get(start_date).get("cases"))
    last_state_deaths = int(state_data.get(start_date).get("deaths"))
    last_county_cases = int(county_data.get(start_date).get("cases"))
    last_county_deaths = int(county_data.get(start_date).get("deaths"))


    for row, date in enumerate(date_strings[1:]):
        state_records = state_data.get(date, DEFAULT_RECORD)
        county_records = county_data.get(date, DEFAULT_RECORD)

        sheet.write(row+1, 0, date)
        sheet.write(row+1, 1, max([int(county_records["cases"])-last_county_cases, 0]))
        sheet.write(row+1, 2, max([int(county_records["deaths"])-last_county_deaths, 0]))
        sheet.write(row+1, 3, max([int(state_records["cases"])-last_state_cases, 0]))
        sheet.write(row+1, 4, max([int(state_records["deaths"])-last_state_deaths, 0]))

        last_county_cases = int(county_records["cases"])
        last_county_deaths = int(county_records["deaths"])
        last_state_cases = int(state_records["cases"])
        last_state_deaths = int(state_records["deaths"])

        
        
        
    

for state in COUNTIES: 
    for county in COUNTIES[state]:
        export_county_data_to_excel(wb, county, state, data)
        export_county_increases_to_excel(wb, county, state, data)

for state in statedata.STATES:
    export_state_metadata_to_excel(wb, state, state_metadata)


wb.save("headfile.xls")
