import pandas as pd
from datetime import date

# TODO: maby change to not transform data to day by day data
# but use a view instead in bokeh which filteres for specific data
def load_data():
    df = load_data_ecdc()
    data = {}

    dates = sorted(df.date.unique())
    for date in dates:
        data[date] = df[df.date == date].copy().reset_index()
    return data


def load_data_ecdc():
    df = pd.read_csv('./data/U99TR3NJ.csv')
    df['date'] = df.apply(lambda row: date(year = row['year'], month = row['month'], day = row['day']), axis = 1)
    return df.drop(columns=['dateRep', 'day', 'month', 'year'])
