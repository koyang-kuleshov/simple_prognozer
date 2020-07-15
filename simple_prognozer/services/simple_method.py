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

from mainapp.models import MainTable, TimeSeries

INFECTION_LIMIT = 0.8


def simple_method(reg):
    if len(reg["country"]) > 2:
        country = reg["country"].title().replace('-', ' ')
    else:
        country = 'US'
    region = MainTable.objects.filter(country_id__country=country)
    if not region:
        return 'Country not found'
    if reg["subdivision"]:
        sub = reg["subdivision"].title().replace('-', ' ')
        region = MainTable.objects.filter(country_id__country=country,
                                          subdivision_id__subdivision=sub)
    if reg["admin2"]:
        admin2 = reg["admin2"].title().replace('-', ' ')
        region = MainTable.objects.filter(country_id__country=country,
                                          subdivision_id__subdivision=sub,
                                          subdivision_id__admin2=admin2)

    try:
        region_population = region[0].region_population
    except IndexError as err:
        return f'Population not found: {err}'
    infections_limit = math.ceil(INFECTION_LIMIT * region_population)

    first_update = TimeSeries.objects.filter(country_id__country=country,
                                             subdivision_id__subdivision=sub).\
        order_by('last_update')[0].last_update.toordinal()
    last_update = region[0].last_update.toordinal()
    observation_period = last_update - first_update

    confirmed = region[0].confirmed
    confirmed_per_day = confirmed / observation_period
    now_date = datetime.datetime.today().toordinal()
    end_date = now_date + (infections_limit - confirmed) / confirmed_per_day
    end_date = datetime.datetime.fromordinal(int(end_date))
    return end_date
