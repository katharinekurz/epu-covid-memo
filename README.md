# epu-covid-memo

> A script to automate the aggregation of state and county level COVID-19 statistics.

<!-- tmpl start -->

## Dataset (last updated Tue Jun 29 12:11:36 2021)

Click [here](https://covid-artifacts.s3.amazonaws.com/records/2021-6-29-121136-covid_artifact.xls) to download.

<!-- tmpl end -->

## Usage

```
curl -s -L https://raw.githubusercontent.com/katharinekurz/epu-covid-memo/master/scripts/run.sh | bash
```

This will generate and open an excel spreadsheet with county and state level statistics, state metadata, and 7 day deltas.