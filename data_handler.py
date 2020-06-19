import pandas as pd
import geopandas as gpd
from datetime import date
import json

data_file_covid_ecdc = './data/U99TR3NJ.csv'
data_file_geo_europe = './data/europe.geojson'

def load_data():
    # load geo data
    geo_data, europe_iso_list = load_data_geo()

    # load first dataset
    data_ecdc = load_data_ecdc()
    # filter for european data and date 2020
    covid_data = filter_by_iso(data_ecdc, europe_iso_list)
    # transform to dictionary by date
    covid_data, dates = transform_to_date_dict(covid_data)

    return covid_data, geo_data, dates

def europe_view(df):
    return df.groupby(['date']).sum().reset_index()

def load_data_ecdc():
    df = pd.read_csv(data_file_covid_ecdc)
    df = df.rename(columns={'countryterritoryCode': 'ISO3', 'popData2018': 'population'})
    df['date'] = df.apply(lambda row: date(year = row['year'], month = row['month'], day = row['day']), axis = 1)
    return df.drop(columns=['dateRep', 'day', 'month', 'year', 'geoId', 'continentExp'])

def load_data_geo():
    gdf = gpd.read_file(data_file_geo_europe)
    gdf = gdf[gdf['ISO2'] != 'IL'] # remove Israel
    europe_iso_list = list(gdf.ISO3)
    return gdf, europe_iso_list

def filter_by_iso(df, iso_list):
    df_filtered = df[df.ISO3.isin(iso_list)]

    frst_date = date.fromisoformat('2020-03-01')
    df_filtered = df_filtered[df_filtered.date >= frst_date]

    return df_filtered.copy().reset_index(drop = True)

# function to color chloropleth by
def geo_data_colors(gdf, df):
    color_by = ['cases', 'deaths']

# transrorm the covid data into a dictionary by date
def transform_to_date_dict(df):
    data = {}

    dates = list(sorted(df.date.unique()))
    for date in dates:
        data[date] = df[df.date <= date].copy().reset_index(drop = True)
    return data, dates

# old unused functions from here on-->

# load without geopandas
def load_data_geo_old():
    data = None
    with open(data_file_geo_europe) as f:
        data = json.load(f)
    return json.dumps(data)

def create_dates_list(df):
    dates = list(sorted(df.date.unique()))
    days = [i for i in range(0,len(dates))]
    dates = dict(zip(days, dates))
    return dates

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
