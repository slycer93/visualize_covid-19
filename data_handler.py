import pandas as pd
import geopandas as gpd
from datetime import date
import json

geo_europe = './data/europe.geojson'
ecdc_data = './data/U99TR3NJ.csv'

class DataHandler():
    def __init__(self):
        self.date_range = [date.fromisoformat('2020-03-01')]
        self.iso_list = []
        self.geo_data = None
        self.data = {}
        self.fields = []
        self._load()

    def initial_view(self):
        df_initial = self.data[self.date_range[0]]
        df_initial = df_initial.rename(columns={self.fields[0]: 'line_1', self.fields[1]: 'line_2'})
        return self.europe_view(df_initial)

    def europe_view(self, df):
        return df.groupby(['date']).sum().reset_index()

    def update_view(self, date, field_1, field_2, iso = 'EUR'):
        df_date = self.data[date]
        df = df_date.loc[:,['date', 'ISO3', field_1]].rename(columns={field_1: 'line_1'})
        df = pd.concat([df, df_date.loc[:,field_2]], axis = 1)
        df = df.rename(columns={field_2: 'line_2'})
        if iso == 'EUR':
            return self.europe_view(df)
        else:
            return df[df['ISO3'] == iso]

    def _load(self):
        self._load_data_geo()

        # load first dataset
        data_ecdc, fields_ecdc = self._load_data_ecdc()
        # TODO: add more data
        data_all = data_ecdc
        self.fields += fields_ecdc

        self._transform_to_date_dict(data_all)

    def _load_data_geo(self):
        gdf = gpd.read_file(geo_europe)
        gdf = gdf[gdf['ISO2'] != 'IL'] # remove Israel
        self.iso_list = list(gdf.ISO3)
        self.geo_data = gdf

    def _filter_europe(self, df):
        return df[df.ISO3.isin(self.iso_list)]

    def _filter_date(self, df):
        return df[df.date >= self.date_range[0]]

    def _transform_to_date_dict(self, df):
        dates = list(sorted(df.date.unique()))
        for date in dates:
            self.data[date] = df[df.date <= date].copy().reset_index(drop = True)
        self.date_range.append(dates[-1])

    def _load_data_ecdc(self):
        df = pd.read_csv(ecdc_data)
        df = df.rename(columns={'countryterritoryCode': 'ISO3', 'popData2018': 'population'})
        # create datetime objs
        df['date'] = df.apply(lambda row: date(year = row['year'], month = row['month'], day = row['day']), axis = 1)
        # drop unneeded columns
        df = df.drop(columns=['dateRep', 'day', 'month', 'year', 'geoId', 'continentExp'])
        # filters
        df = self._filter_europe(df)
        df = self._filter_date(df)
        return df, ['cases', 'deaths']
