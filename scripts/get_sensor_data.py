import requests
import pandas as pd
import datetime
import argparse


base_url = "http://vm-01.cern.ch:8080/"

def get_sensor_name(sensor_id):
    url = f"{base_url}/sensor-name/{sensor_id}"
    response = requests.get(url)
    return response.json()


def get_df_for_day(sensor_id, day_str):
    url = f"{base_url}/day/{day_str}/{sensor_id}"
    response = requests.get(url)
    data = response.json()
    return pd.DataFrame.from_dict(data, orient='index', columns=['value'])


def main(args):
    sd = datetime.datetime.strptime(args.start, "%Y-%m-%d").date()
    ed = datetime.datetime.strptime(args.end, "%Y-%m-%d").date()

    sensor_name = get_sensor_name(args.elid)

    i = 0
    date = sd
    while date <= ed:
        df = get_df_for_day(args.elid, date)
        df.to_csv(f'data/{sensor_name}_{date}.csv', sep=' ', header=0)
        date += datetime.timedelta(days=1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=str, default="2022-06-01", help="start date as string")
    parser.add_argument("--end", type=str, default="2022-06-02", help="end date as string")
    parser.add_argument("--elid", type=int, default=48001913454874, help="id of sensor")
    args = parser.parse_args()
    main(args)
