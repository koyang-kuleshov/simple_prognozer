import json
import os
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

REGION_POPULATION_PATH = os.path.abspath(os.path.dirname(__file__))
REGEX_INT_POP = r'^(?:(\d+(?:\,))+\d+|\d+$)'


def get_population(country):
    countries_pop_data_url = {
        "countries_without_subdivisions": single_countries_pop(),
        "US": us_pop(),
        "Italy": italy_pop(),
        "Brazil": table_data_parser('https://en.wikipedia.org/wiki/States_of_Brazil',
                                    'wikitable', 1, 1, 0, 4),
        "Russia": table_data_parser('https://en.wikipedia.org/wiki/List_of_federal_subjects_of_Russia_by_population',
                                    'wikitable', 1, 1, 1, 2),
        "Mexico": table_data_parser('https://en.wikipedia.org/wiki/List_of_Mexican_states_by_population',
                                    'wikitable', 1, 1, 1, 2),
        "Japan": table_data_parser('https://www.citypopulation.de/Japan-Cities.html',
                                   'data', 1, 1, 1, 12),
        "Canada": table_data_parser('https://en.wikipedia.org/wiki/Population_of_Canada_by_province_and_territory',
                                    'wikitable', 2, 1, 1, 9),
        "Colombia": table_data_parser('https://www.citypopulation.de/en/colombia/cities/',
                                      'data', 1, 1, 1, 10),
        "Peru": table_data_parser('https://www.citypopulation.de/en/peru/cities/',
                                  'data', 1, 1, 1, 10),
        "Spain": table_data_parser('https://www.citypopulation.de/en/spain/cities/',
                                   'data', 1, 1, 1, 10),
        "India": table_data_parser(
            'https://en.wikipedia.org/wiki/List_of_states_and_union_territories_of_India_by_population',
            'wikitable', 1, 1, 1, 2
        ),
        "United Kingdom": uk_pop(),
        "China": china_pop(),
        "Chile": chili_pop(),
        "Netherlands": netherlands_pop(),
        "Australia": table_data_parser('http://www.citypopulation.de/en/australia/cities/uc/',
                                       'data', 1, 1, 1, 10),
        "Pakistan": table_data_parser('https://en.wikipedia.org/wiki/Administrative_units_of_Pakistan',
                                      'wikitable', 1, 1, 0, 9),
        "Germany": table_data_parser('http://www.citypopulation.de/en/germany/cities/',
                                     'data', 1, 1, 1, 10),
        "Sweden": table_data_parser('http://www.citypopulation.de/en/sweden/cities/mun/',
                                    'data', 1, 1, 1, 9),
        "Ukraine": ukraine_pop(),
        "Denmark": denmark_pop(),
        "France": france_pop()

    }

    return countries_pop_data_url[country]


def get_soup(url):
    res = requests.get(url).text
    return BeautifulSoup(res, features="html.parser")


def table_data_parser(url, soup_class, start_slice, end_slice, num_country, num_pop):
    soup = get_soup(url)
    country_population = {}

    with open(os.path.join(REGION_POPULATION_PATH, 'countries_aliases.json'), encoding='utf-8') as json_file:
        countries_aliases = json.load(json_file)

    for items in soup.find('table', class_=soup_class).find_all('tr')[start_slice::end_slice]:
        data = items.find_all(['th', 'td'])

        try:
            country = data[num_country].a.text
            # Если название на странице отличается от csv, используем алиас
            # TODO take alias from mainapp_country (if table don't rewrite)
            if country in countries_aliases.keys():
                country = countries_aliases[country]
            population = int(re.search(REGEX_INT_POP, data[num_pop].text).group(0).replace(',', ''))
            country_population.update({country: population})
        except AttributeError:
            pass

    return country_population


def int_data_parser(url, soup_teg, soup_class):
    soup = get_soup(url)

    res = int(re.search(REGEX_INT_POP, soup.find(soup_teg, class_=soup_class).text).group(0).replace(',', ''))

    return res


def single_countries_pop():
    soup = get_soup("https://worldpopulationreview.com/countries")

    with open(os.path.join(REGION_POPULATION_PATH, 'countries_aliases.json'), encoding='utf-8') as json_file:
        countries_aliases = json.load(json_file)

    country_population = {}
    for items in soup.find('table', class_='table').find_all('tr')[1::1]:
        data = items.find_all(['th', 'td'])

        try:
            country = data[1].a.text
            # Если название на странице отличается от csv, используем алиас
            # TODO take alias from mainapp_country (if table don't rewrite)
            if country in countries_aliases.keys():
                country = countries_aliases[country]
            population = int(data[2].text.replace(',', ''))
            country_population.update({country: population})
        except AttributeError:
            break

    soup = get_soup("https://countrymeters.info/en/Kosovo")

    kosovo_pop = soup.find('div', id='cp1').text.replace(',', '')
    country_population.update({"Kosovo": kosovo_pop})

    return country_population


def us_pop():
    url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/' \
          'csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv'
    df = pd.read_csv(url, error_bad_lines=False)

    fips = df['FIPS']
    population = df['Population']

    country_population = {}
    for i in range(len(fips)):
        if fips[i] in country_population.keys():
            country_population.update({(fips[i]): country_population[fips[i]] + population[i]})
            break
        else:
            country_population.update({fips[i]: population[i]})

    return country_population


def italy_pop():
    country_population = table_data_parser('https://en.wikipedia.org/wiki/Regions_of_Italy', 'wikitable', 2, 1, 1, 3)
    country_population_trento_bolzano = table_data_parser(
        'http://www.citypopulation.de/en/italy/admin/04__trentino_alto_adige/'
        , 'data', 2, 1, 0, 2
    )
    country_population.update(country_population_trento_bolzano)

    return country_population


def uk_pop():
    soup = get_soup('https://countrymeters.info/en/Channel_Islands')

    country_population = table_data_parser(
        'https://en.wikipedia.org/wiki/Countries_of_the_United_Kingdom_by_population',
        'wikitable', 1, 1, 1, 2
    )
    country_population.update(
        table_data_parser(
            'https://en.wikipedia.org/wiki/Regions_of_England',
            'wikitable', 1, 1, 0, 1
        )
    )
    country_population.update({
        "Anguilla": single_countries_pop()['Anguilla'],
        "Bermuda": single_countries_pop()['Bermuda'],
        "British Virgin Islands": single_countries_pop()['British Virgin Islands'],
        "Cayman Islands": single_countries_pop()['Cayman Islands'],
        "Channel Islands": int(re.search(REGEX_INT_POP, soup.find('td', class_='counter').find_all('div')[0].text)
                               .group(0).replace(',', '')),
        "Falkland Islands (Malvinas)": single_countries_pop()['Falkland Islands (Malvinas)'],
        "Gibraltar": single_countries_pop()['Gibraltar'],
        "Isle of Man": single_countries_pop()['Isle of Man'],
        "Montserrat": single_countries_pop()['Montserrat'],
        "Turks and Caicos Islands": single_countries_pop()['Turks and Caicos Islands']
    })

    return country_population


def china_pop():
    country_population = table_data_parser('http://www.citypopulation.de/en/china/cities/', 'data', 1, 1, 1, 11)
    country_population.update({
        "Hong Kong": single_countries_pop()['Hong Kong'],
        "Macau": single_countries_pop()['Macau']
    })

    return country_population


def chili_pop():
    country_population = table_data_parser('https://www.citypopulation.de/en/chile/cities/', 'data', 1, 1, 1, 9)

    # region Nuble for Chile
    if 'Nuble' not in country_population.keys():
        soup = get_soup('https://www.citypopulation.de/en/chile/admin/')

        for items in soup.find('table', class_='data').find_all('tr')[1::1]:
            data = items.find_all(['th', 'td'])
            country = data[0].a.text
            if country == 'Ñuble':
                population = int(data[6].text.replace(',', ''))
                country_population.update({"Nuble": population})
                break

        country_population['Biobio'] -= country_population['Nuble']

    return country_population


def netherlands_pop():
    country_population = {
        "Aruba": single_countries_pop()['Aruba'],
        "Bonaire, Sint Eustatius and Saba": sum(
            table_data_parser(
                'http://www.citypopulation.de/en/caribbeannetherlands/',
                'data', 1, 1, 1, 10).values()

        ),
        "Curacao": single_countries_pop()['Curacao'],
        "Sint Maarten": single_countries_pop()['Sint Maarten'],
        "null": single_countries_pop()['Netherlands']

    }

    return country_population


def ukraine_pop():
    country_population = table_data_parser(
        'https://en.wikipedia.org/wiki/List_of_Ukrainian_oblasts_and_territories_by_population',
        'wikitable', 1, 1, 1, 2)
    country_population.update({
        "Sevastopol*": int_data_parser('https://populationstat.com/ukraine/sevastopol', 'div', 'main-clock')
    })

    return country_population


def denmark_pop():
    country_population = {
        "Faroe Islands": single_countries_pop()['Faroe Islands'],
        "Greenland": single_countries_pop()['Greenland'],
        "null": single_countries_pop()['Denmark']
    }

    return country_population


def france_pop():
    country_population = table_data_parser(
        'https://en.wikipedia.org/wiki/Ranked_list_of_French_regions',
        'wikitable', 1, 1, 1, 2)

    country_population.update({
        "French Polynesia": single_countries_pop()['French Polynesia'],
        "New Caledonia": single_countries_pop()['New Caledonia'],
        "Reunion": single_countries_pop()['Reunion'],
        "Saint Barthelemy": single_countries_pop()['Saint Barthelemy'],
        "Saint Pierre and Miquelon": single_countries_pop()['Saint Pierre and Miquelon'],
        "St Martin": single_countries_pop()['St Martin'],
        "null": single_countries_pop()['France']
    })

    return country_population


if __name__ == '__main__':
    # single_countries_pop()
    # regions_json_updater()
    # print(single_countries_pop())
    for i in single_countries_pop():
        print(i)
