import json
import os
import re

import requests
import pandas as pd

from bs4 import BeautifulSoup

REGION_POPULATION_PATH = os.path.abspath(os.path.dirname(__file__))

SINGLE_COUNTRIES_POP_DATA_URL = "https://worldpopulationreview.com/countries"
KOSOVO_POPULATION_POP_DATA_URL = "https://countrymeters.info/en/Kosovo"
US_CITIES_POP_DATA_URL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/' \
                     'csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv'
ITALY_POPULATION_POP_DATA_URL = 'https://en.wikipedia.org/wiki/Regions_of_Italy'
TRENTO_BOLZANO_POP_DATA_URL = 'http://www.citypopulation.de/en/italy/admin/04__trentino_alto_adige/'
BRAZIL_POP_DATA_URL = 'https://en.wikipedia.org/wiki/States_of_Brazil'
RU_POP_DATA_URL = 'https://en.wikipedia.org/wiki/List_of_federal_subjects_of_Russia_by_population'
MX_POP_DATA_URL = 'https://en.wikipedia.org/wiki/List_of_Mexican_states_by_population'
JP_POP_DATA_URL = 'https://www.citypopulation.de/Japan-Cities.html'
CA_POP_DATA_URL = 'https://en.wikipedia.org/wiki/Population_of_Canada_by_province_and_territory'
CO_POP_DATA_URL = 'https://www.citypopulation.de/en/colombia/cities/'
PE_POP_DATA_URL = 'https://www.citypopulation.de/en/peru/cities/'
ES_POP_DATA_URL = 'https://www.citypopulation.de/en/spain/cities/'
IN_POP_DATA_URL = 'https://en.wikipedia.org/wiki/List_of_states_and_union_territories_of_India_by_population'
CN_POP_DATA_URL = 'http://www.citypopulation.de/en/china/cities/'
CL_POP_DATA_URL = 'https://www.citypopulation.de/en/chile/cities/'


def get_population(countries_without_subdivisions_list, countries_list):
    countries_with_subdivisions_list = [country for country in countries_list
                                        if country['country__country'] not in countries_without_subdivisions_list]
    countries_without_subdivisions_list = [country for country in countries_list
                                           if country['country__country'] in countries_without_subdivisions_list]
    single_countries_population = single_countries_parser()
    region_population_us_cities = region_population_us_cities_parser()
    region_population = region_population_parser()

    res = {}
    get_population_error = {}
    # {'id': 1, 'subdivision': 'South Carolina', 'country__country': 'US', 'fips': 45001}
    # {'id': 3787, 'subdivision': None, 'country__country': 'Yemen', 'fips': None}
    for country in countries_without_subdivisions_list:
        if country['country__country'] in single_countries_population.keys():
            res.update({country['id']: single_countries_population[country['country__country']]})
        else:
            get_population_error.update({country['country__country']: "not found in single_countries_parser"})

    for country in countries_with_subdivisions_list:

        if country['fips']:

            if country['fips'] in region_population_us_cities.keys():
                res.update({country['id']: region_population_us_cities[country['fips']]})
            else:
                get_population_error.update({
                    country['country__country']: {
                        "status": "not found in time_series_covid19_deaths_US.csv",
                        "subdivision": country['subdivision'],
                        "fips": country['fips']
                    }
                })
        # Hong Kong, Macau
        elif country['subdivision'] in single_countries_population.keys():
            res.update({country['id']: single_countries_population[country['country__country']]})

        else:

            if country['subdivision'] in region_population.keys():
                res.update({country['id']: region_population[country['subdivision']]})
            else:

                if country['country__country'] in get_population_error.keys():
                    get_population_error[country['country__country']]['subdivisions']\
                        .update({country['subdivision']: country['subdivision']})
                else:
                    get_population_error.update({
                        country['country__country']: {
                            "status": "not found",
                            "subdivisions": {country['subdivision']: country['subdivision']},
                            "fips": country['fips']
                        }
                    })

    with open(os.path.join(REGION_POPULATION_PATH, 'get_population_error.json'),
              'w', encoding='utf-8') as f:
        json.dump(get_population_error, f, ensure_ascii=False, indent=4)

    return res


def region_population_us_cities_parser():
    url = US_CITIES_POP_DATA_URL
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


def data_parser(url, soup_class, start_slice, num_country, num_pop, country_population):
    url = url
    res = requests.get(url).text
    soup = BeautifulSoup(res, features="html.parser")
    regex = r'^(?:(\d+(?:\,))+\d+|\d+$)'

    with open(os.path.join(REGION_POPULATION_PATH, 'countries_aliases.json'), encoding='utf-8') as json_file:
        countries_aliases = json.load(json_file)

    for items in soup.find('table', class_=soup_class).find_all('tr')[start_slice::1]:
        data = items.find_all(['th', 'td'])

        try:
            country = data[num_country].a.text
            # Если название на странице отличается от csv, используем алиас
            # TODO take alias from mainapp_country (if table don't rewrite)
            if country in countries_aliases.keys():
                country = countries_aliases[country]
            population = int(re.search(regex, data[num_pop].text).group(0).replace(',', ''))
            country_population.update({country: population})
        except AttributeError:
            pass

    return country_population


def region_population_parser():
    url = ITALY_POPULATION_POP_DATA_URL
    res = requests.get(url).text
    soup = BeautifulSoup(res, features="html.parser")

    with open(os.path.join(REGION_POPULATION_PATH, 'countries_aliases.json')) as json_file:
        countries_aliases = json.load(json_file)

    country_population = {}
    for items in soup.find('table', class_='wikitable').find_all('tr')[2::1]:
        data = items.find_all(['th', 'td'])

        try:
            country = data[1].a.text
            # Если название на странице отличается от csv, используем алиас
            # TODO take alias from mainapp_country (if table don't rewrite)
            if country in countries_aliases.keys():
                country = countries_aliases[country]
            population = int(data[3].text.replace(',', ''))
            country_population.update({country: population})
        except AttributeError:
            pass

    country_population = data_parser(TRENTO_BOLZANO_POP_DATA_URL, 'data', 2, 0, 2, country_population)

    country_population = data_parser(BRAZIL_POP_DATA_URL, 'wikitable', 1, 0, 4,  country_population)

    country_population = data_parser(RU_POP_DATA_URL, 'wikitable', 1, 1, 2, country_population)

    country_population = data_parser(MX_POP_DATA_URL, 'wikitable', 1, 1, 2, country_population)

    country_population = data_parser(JP_POP_DATA_URL, 'data', 1, 1, 12, country_population)

    country_population = data_parser(CA_POP_DATA_URL, 'wikitable', 2, 1, 9, country_population)

    country_population = data_parser(CO_POP_DATA_URL, 'data', 1, 1, 10, country_population)

    country_population = data_parser(PE_POP_DATA_URL, 'data', 1, 1, 10, country_population)

    country_population = data_parser(ES_POP_DATA_URL, 'data', 1, 1, 10, country_population)

    country_population = data_parser(IN_POP_DATA_URL, 'wikitable', 1, 1, 2, country_population)

    country_population = data_parser(CN_POP_DATA_URL, 'data', 1, 1, 11, country_population)

    country_population = data_parser(CL_POP_DATA_URL, 'data', 1, 1, 9, country_population)

    # region Nuble for Chile
    if 'Nuble' not in country_population.keys():
        url = 'https://www.citypopulation.de/en/chile/admin/'
        res = requests.get(url).text
        soup = BeautifulSoup(res, features="html.parser")

        for items in soup.find('table', class_='data').find_all('tr')[1::1]:
            data = items.find_all(['th', 'td'])
            country = data[0].a.text
            if country == 'Ñuble':
                population = int(data[6].text.replace(',', ''))
                country_population.update({"Nuble": population})
                break

        country_population['Biobio'] -= country_population['Nuble']

    # Netherlands
    print(single_countries_parser()['Netherlands'])
    country_population.update({"Netherlands": population})


    return country_population


def single_countries_parser():
    url = SINGLE_COUNTRIES_POP_DATA_URL
    res = requests.get(url).text
    soup = BeautifulSoup(res, features="html.parser")

    with open(os.path.join(REGION_POPULATION_PATH, 'countries_aliases.json')) as json_file:
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

    url = KOSOVO_POPULATION_POP_DATA_URL
    res = requests.get(url).text
    soup = BeautifulSoup(res, features="html.parser")

    kosovo_pop = soup.find('div', id='cp1').text.replace(',', '')
    country_population.update({"Kosovo": kosovo_pop})

    return country_population


if __name__ == '__main__':
    # single_countries_parser()
    # regions_json_updater()
    region_population_us_cities_parser()
