import pandas as pd
import geopandas as gpd
from datetime import date
import json
from sklearn.preprocessing import minmax_scale

geo_europe = './data/europe.geojson'
ecdc_data = './data/U99TR3NJ.csv'
restrictions = './data/acaps_covid19_government_measures_dataset.xlsx'

class DataHandler():
    def __init__(self):
        self.date_range = [date.fromisoformat('2020-03-01')] # first date
        self.dates = []
        self.iso_list = []
        self.country_iso = {}
        self.geo_data = None
        self.restriction_data=None
        self.data = {}
        self.data_all_dates = []
        self.fields = []
        self.color_fields = ['Cases by population', 'Deaths by population', 'Deaths by cases']
        self.y_range_end = {}
        self._load()

    def initial_view(self):
        df_initial = self.data[self.date_range[0]]
        df_initial = df_initial.rename(columns={self.fields[0]: 'line', self.fields[1]: 'restr','Cumulated Restrictions':'line_3'})
        return self.europe_view(df_initial)

    def europe_view(self, df):
        return df.groupby(['date']).sum().reset_index()

    def update_view(self, date, field, category='Public health measures', iso = 'EUR'):
        df_date = self.data[date]
        df = df_date.loc[:,['date', 'ISO3', field]].rename(columns={field: 'line'})
        df = pd.concat([df, df_date[df_date['CATEGORY']==category]['Cumulated Restrictions']], axis = 1).fillna(method='bfill')
        df = df.rename(columns={'Cumulated Restrictions': 'restr'})
        if iso == 'EUR':
            return self.europe_view(df)
        else:
            return df[df['ISO3'] == iso].copy()

    def _load(self):
        self._load_data_geo()
        self._preprocess_data_geo()
        # create iso list of european countrys
        self.iso_list = list(self.geo_data.ISO3)

        # load first dataset
        data_ecdc, fields_ecdc = self._load_data_ecdc()
        df_restriction,categories=self._load_data_restrictions()
        # TODO: add more data
        data_all=pd.merge(data_ecdc, df_restriction,  how='left', left_on=['ISO3','date'], right_on = ['ISO3','DATE_IMPLEMENTED']).fillna(method='bfill')

        #data_all = data_ecdc
        self.fields += fields_ecdc
        self.fields += ['Cumulated Restrictions Overall']

        self._transform_to_date_dict(data_all)
        # dataframe for all dates is contained in the data of the last date
        self.data_all_dates = self.data[self.date_range[1]]
        # create iso_country dict
        self.country_iso = self.data_all_dates.loc[:, ['ISO3', 'countriesAndTerritories']].drop_duplicates().set_index('countriesAndTerritories').T.to_dict('records')[0]
        self.country_iso['Europe'] = 'EUR'
        # find max y ranges from data
        self._find_y_range_end()
        # add fields to the geo_dataframe
        self._add_fields_to_geo_data()

    def _load_data_restrictions(self):
        df_raw=pd.read_excel(restrictions, sheet_name='Database')
        df_raw['DATE_IMPLEMENTED']=df_raw['DATE_IMPLEMENTED'].apply(pd.to_datetime).dt.date
        df_raw['No. Restrictions']=1
        df_raw = df_raw.rename(columns={'ISO': 'ISO3'})
        df=df_raw.filter(["ISO3","CATEGORY","DATE_IMPLEMENTED","No. Restrictions"]).groupby(['ISO3','CATEGORY', 'DATE_IMPLEMENTED']).count().reset_index()
        df['Cumulated Restrictions']=df.groupby(['ISO3','CATEGORY']).cumsum()
        df['Cumulated Restrictions Overall']=df.groupby(['ISO3']).cumsum()['No. Restrictions']
        return df, df.CATEGORY.unique()

    def _load_data_geo(self):
        self.geo_data = gpd.read_file(geo_europe)

    def _preprocess_data_geo(self):
        # remove Israel
        self.geo_data = self.geo_data[self.geo_data['ISO2'] != 'IL']
        # rename needed columns
        self.geo_data = self.geo_data.rename(columns={'NAME': 'country'})
        # keep only needed columns
        self.geo_data = self.geo_data.loc[:,['ISO3', 'country', 'geometry']].copy()

    def _filter_europe(self, df):
        return df[df.ISO3.isin(self.iso_list)]

    def _filter_date(self, df):
        return df[df.date >= self.date_range[0]]

    def _transform_to_date_dict(self, df):
        dates = list(sorted(df.date.unique()))
        for date in dates:
            self.data[date] = df[df.date <= date].copy().reset_index(drop = True)

        # set dates to obj variables
        self.dates = dates
        self.date_range.append(dates[-1])

    def _find_y_range_end(self):
        df = self.data_all_dates
        self.y_range_end['EUR'] = self._get_max_value(self.europe_view(df), self.fields)
        for iso in self.iso_list:
            df_iso = df[df['ISO3'] == iso]
            self.y_range_end[iso] = self._get_max_value(df_iso, self.fields)

    def _get_max_value(self, df, columns):
        max_values = {}
        for column in columns:
            max = df[column].max()
            if max < 10:
                max = 10
            max_values[column] = max
        return max_values

    def _add_fields_to_geo_data(self):
        fields = [*self.fields, 'ISO3']
        data_europe = self.data_all_dates.groupby(['ISO3']).sum().reset_index().loc[:,fields]
        self.geo_data = self.geo_data.join(data_europe.set_index('ISO3'), on='ISO3')
        population = self.data_all_dates.loc[:,['ISO3', 'population']].drop_duplicates()
        self.geo_data = self.geo_data.join(population.set_index('ISO3'), on='ISO3')
        for color_field in self.color_fields:
            cf = color_field.lower().split(' ')
            self.geo_data[color_field] = self.geo_data.apply(lambda row: row[cf[0]] / row[cf[-1]], axis = 1)
            self.geo_data[color_field] = minmax_scale(self.geo_data[color_field], feature_range=(0, 100))
        self.color_fields.append('Cumulated Restrictions Overall')

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
