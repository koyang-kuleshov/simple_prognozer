""" Метод прогнозирования заражения 80% населения в заданном регионе
country_id = 1
subdivision_id = 27
"""


import datetime
import os
import math

from mainapp.models import MainTable

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "simple_prognozer.settings")
django.setup()


def simple_method(reg):
    country, sub = reg
    country = country.title().replace('-', ' ')
    sub = sub.title().replace('-', ' ')
    region = MainTable.objects.filter(country_id__country=country,
                                      subdivision_id__subdivision=sub)
    region_population = region[0].region_population
    infections_limit = math.ceil(0.8 * region_population)
    print(infections_limit)
    end_date = ''
    return end_date


if __name__ == "__main__":
    simple_method(('us', 'new-york'))
