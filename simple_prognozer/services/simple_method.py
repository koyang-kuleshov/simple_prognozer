""" Метод прогнозирования заражения 80% населения в заданном регионе
country_id = 1
subdivision_id = 27
"""


import datetime
import os
import math
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "simple_prognozer.settings")
django.setup()

from mainapp.models import MainTable

INFECTION_LIMIT = 0.8


def date_convert(combine_datetime):
    year, month, day = map(lambda i: int(i),
                           combine_datetime.split(' ')[0].split('-'))
    return year, month, day


def simple_method(reg):
    country, sub = reg
    if len(country) > 2:
        country = country.title().replace('-', ' ')
    else:
        country = 'US'
    sub = sub.title().replace('-', ' ')
    region = MainTable.objects.filter(country_id__country=country,
                                      subdivision_id__subdivision=sub)
    region_population = region[0].region_population
    infections_limit = math.ceil(INFECTION_LIMIT * region_population)

    # TODO: Fetch from TimeSeries
    first_update = datetime.date(*date_convert('2020-03-02 04:33:46')).\
        toordinal()
    last_update = region[0].last_update.toordinal()
    observation_period = last_update - first_update

    confirmed = region[0].confirmed
    confirmed_per_day = confirmed / observation_period
    now_date = datetime.datetime.today().toordinal()
    end_date = now_date + (infections_limit - confirmed) / confirmed_per_day
    end_date = datetime.datetime.fromordinal(int(end_date))
    return end_date


if __name__ == "__main__":
    print(simple_method(('us', 'new-york')))
