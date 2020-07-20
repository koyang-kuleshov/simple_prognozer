from mainapp.models import MainTable, Subdivision
from django.core.management.base import BaseCommand

from django.db.models import Count
from services.region_population import get_population, REGION_POPULATION_PATH

import json
import os


class Command(BaseCommand):
    help = 'Fill population'

    def handle(self, *args, **kwargs):
        print('Filling population...')

        countries_without_subdivisions = {"countries_without_subdivisions": {
            country[list(country)[1]]: country[list(country)[0]]
            for country in
            (Subdivision.objects.select_related()
             .values('country', 'country__country')
             .annotate(Count('country_id'))
             .order_by('country_id')
             .filter(country_id__count=1))
        }}

        us_subdivisions = {
            "US": {
                sub[list(sub)[0]]: sub[list(sub)[1]]
                for sub in Subdivision.objects.values('fips', 'id').order_by('fips').filter(country_id=1)
            }
        }

        countries_with_subdivisions_exclude_us = Subdivision.objects.select_related() \
            .values('country', 'country__country') \
            .annotate(Count('country_id')) \
            .order_by('country_id') \
            .filter(country_id__count__gt=1) \
            .exclude(country_id=1)

        countries_with_subdivisions_dict = {
            country['country__country']: {
                sub[list(sub)[1]]: sub[list(sub)[0]]
                for sub in
                list(Subdivision.objects.filter(country_id=country['country']).values('id', 'subdivision'))
            }
            for country in countries_with_subdivisions_exclude_us
        }

        all_countries_dict = {**countries_without_subdivisions, **us_subdivisions,
                              **countries_with_subdivisions_dict}

        for countries_segment in list(all_countries_dict):
            print(countries_segment)
            population = get_population(countries_segment)

            for res in list(population):  # sub/country
                if res == 'null':
                    MainTable.objects.filter(subdivision_id=all_countries_dict[countries_segment].pop(None)) \
                        .update(region_population=population[res])
                elif res in all_countries_dict[countries_segment]:
                    MainTable.objects.filter(subdivision_id=all_countries_dict[countries_segment].pop(res)) \
                        .update(region_population=population[res])

        with open(os.path.join(REGION_POPULATION_PATH, 'get_population_error.json'),
                  'w', encoding='utf-8') as f:
            json.dump(all_countries_dict, f, ensure_ascii=False, indent=4)

        print('Population fill done.')
