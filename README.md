# Visualization of Covid-19 in Europe

This project visualizes restrictions, cases and deaths for the Covid-19 pandemie in Europe. The visualization uses a automated slider to inspect data by day and selectors to change the visualized data and country. It also drows a chloropleth for the data at the last date.

## Run Notebook with Bokeh server:

1. pipenv install
2. pipenv run jupyter serverextension enable --py nbserverproxy
3. pipenv run jupyter notebook

## Data Sources:

### Cases and Deaths by day:

* https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide

### Restrictions:

* https://www.acaps.org/covid19-government-measures-dataset

## Visualization Example:

![Alt text](Example_image.png?raw=true "Dashboard")
