run environment:
1. pipenv install
2. pipenv shell

run notebook:
* pipenv run jupyter notebook

example repository "play button":
* https://github.com/bokeh/bokeh/blob/master/examples/app/gapminder/main.py

examples:
* https://ourworldindata.org/epi-curve-covid-19

data sources:
* https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide
* https://www.acaps.org/covid19-government-measures-dataset

required:
pip install nbserverproxy && jupyter serverextension enable --py nbserverproxy
pip install xlrd
