import pandas as pd
import geopandas as gpd
from datetime import date
import json

data_file_covid_ecdc = './data/U99TR3NJ.csv'
data_file_geo_europe = './data/europe.geojson'

def load_data():
    geo_data, europe_iso_list = load_data_geo()
    covid_raw = load_data_ecdc()
    # filter for european data and date 2020
    covid_data = filter_data_ecdc(covid_raw, europe_iso_list)

    return covid_data, geo_data

def load_data_ecdc():
    df = pd.read_csv(data_file_covid_ecdc)
    df['date'] = df.apply(lambda row: date(year = row['year'], month = row['month'], day = row['day']), axis = 1)
    return df.drop(columns=['dateRep', 'day', 'month', 'year'])

def load_data_geo():
    gdf = gpd.read_file(data_file_geo_europe)
    gdf = gdf[gdf['ISO2'] != 'IL'] # remove Israel
    europe_iso_list = list(gdf.ISO3)
    return gdf.to_json(), europe_iso_list

def filter_data_ecdc(df, iso_list):
    df_filtered = df[df.countryterritoryCode.isin(iso_list)]

    frst_date = date.fromisoformat('2020-03-01')
    df_filtered = df_filtered[df_filtered.date >= frst_date]

    return df_filtered.copy().reset_index(drop = True)

# old unused functions from here on-->

# load without geopandas
def load_data_geo_old():
    data = None
    with open(data_file_geo_europe) as f:
        data = json.load(f)
    return json.dumps(data)

# transrorm the covid data into a dictionary by date
# it seems better to filter in the bokeh view
def transform_to_date_dict(df):
    data = {}

    dates = sorted(df.date.unique())
    for date in dates:
        data[date] = df[df.date == date].copy().reset_index(drop = True)
    return data

# instead of dates transform to days
# if dateobject has problem with visualization
def dates_to_days(df):
    dates = list(sorted(df.date.unique()))
    days = [i for i in range(1,len(dates) + 1)]
    change = dict(zip(dates, days))

    df['day'] = df.apply(lambda row: change[row['date']], axis = 1)
    return df.copy().reset_index(drop = True)

# sort dataframe by date
def sort_by_date(df):
    return df.sort_values(by=['date'])
