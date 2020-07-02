# https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_daily_reports/06-26-2020.csv

"""
SD - c s
1 - c simgle:
  list
  fill wiki - pop
  print tail
    contry +alias

2 - c multi:
final_dict = {key: t[key] for key in t if key not in [key1, key2]}

"""

import json
import os

import requests
import pandas as pd
from bs4 import BeautifulSoup

REGION_POPULATION_PATH = os.path.abspath(os.path.dirname(__file__))


def get_population(countries_without_subdivisions_list, countries_list):
    countries_with_subdivisions_list = [country for country in countries_list
                                        if country['country__country'] not in countries_without_subdivisions_list]
    countries_without_subdivisions_list = [country for country in countries_list
                                           if country['country__country'] in countries_without_subdivisions_list]
    single_countries_population = single_countries_parser()
    region_population_us_cities = region_population_us_cities_parser()

    res = {}
    get_population_error = {}
    # {'id': 1, 'subdivision': 'South Carolina', 'country__country': 'US', 'fips': 45001}
    # {'id': 3787, 'subdivision': None, 'country__country': 'Yemen', 'fips': None}
    for country in countries_without_subdivisions_list:
        if country['country__country'] in single_countries_population.keys():
            res.update({country['id']: single_countries_population[country['country__country']]})
        else:
            get_population_error.update({country['country__country']: "not found in wiki"})

    for country in countries_with_subdivisions_list:

        if country['fips']:

            if country['fips'] in region_population_us_cities.keys():
                res.update({country['id']: region_population_us_cities[country['fips']]})
            else:
                get_population_error.update({
                    country['country__country']: {
                        "status": "not found in region_population_us_cities.csv",
                        "subdivision": country['subdivision'],
                        "fips": country['fips']
                    }
                })

        else:
            get_population_error.update({
                country['country__country']: {
                    "status": "not found",
                    "subdivision": country['subdivision'],
                    "fips": country['fips']
                }
            })

    with open(os.path.join(REGION_POPULATION_PATH, 'get_population_error.json'),
              'w', encoding='utf-8') as f:
        json.dump(get_population_error, f, ensure_ascii=False, indent=4)

    return res


def region_population_us_cities_parser():
    csv_file = os.path.join(REGION_POPULATION_PATH, 'region_population_us_cities.csv')
    df = pd.read_csv(csv_file)

    fips = df['county_fips']
    population = df['population']

    country_population = {}
    for i in range(len(fips)):
        if fips[i] in country_population.keys():
            country_population.update({fips[i]: country_population[fips[i]] + population[i]})
        else:
            country_population.update({fips[i]: population[i]})

    return country_population


def single_countries_parser():
    url = "https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population"

    res = requests.get(url).text
    soup = BeautifulSoup(res, features="html.parser")

    country_population = {}
    for items in soup.find('table', class_='wikitable').find_all('tr')[1::1]:
        data = items.find_all(['th', 'td'])
        try:
            country = data[1].a.text
            population = int(data[2].text.replace(',', ''))
            country_population.update({country: population})
        except AttributeError:
            break

    return country_population


if __name__ == '__main__':
    # single_countries_parser()
    # regions_json_updater()
    region_population_us_cities_parser()
