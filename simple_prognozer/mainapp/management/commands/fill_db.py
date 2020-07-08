import os
import csv

from django.core.management.base import BaseCommand

from mainapp.models import MainTable, Subdivision, Country
from django.conf import settings
from services import parse
from services.region_population import get_population


class Command(BaseCommand):
    help = 'Fill db'

    def handle(self, *args, **kwargs):
        """ Запись Daily_Reports в таблицу MainTable """

        print('Filling MainTable...')

        parse.get_csv('daily_reports')
        with open('daily_report.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                print(row)
                if Country.objects.filter(country=row[3]).exists():
                    country = Country.objects.get(country=row[3])
                else:
                    country = Country(country=row[3])
                    country.save()

                subdivision, _ = Subdivision.objects.update_or_create(country=country,
                                                                      subdivision=row[2] or None,
                                                                      fips=row[0] or None,
                                                                      admin2=row[1] or None,
                                                                      lat=row[5] or None,
                                                                      longitude=row[6] or None)

                main, _ = MainTable.objects.update_or_create(country=country, subdivision=subdivision,
                                                             confirmed=row[7],
                                                             deaths=row[8],
                                                             recovered=row[9],
                                                             active=row[10] or None, last_update=row[4],
                                                             incidence_rate=row[12] or None,
                                                             case_fatality_ratio=row[13] or None)

            print('Filling population...')

            countries_without_subdivisions_list = [
                Country.objects.values_list('country', flat=True).get(pk=obj.country_id)
                for obj in Subdivision.objects.order_by('country_id')
                if Subdivision.objects.filter(country_id=obj.country_id).count() == 1
            ]

            countries_list = list(Subdivision.objects.values('id', 'subdivision', 'country__country', 'fips')
                                  .order_by('country_id'))

            res = get_population(countries_without_subdivisions_list, countries_list)
            for res_id in res.keys():
                population_from_maintable_qs = MainTable.objects.filter(subdivision_id=res_id).values(
                    'region_population')

                if population_from_maintable_qs[0]['region_population'] != res[res_id]:
                    population_from_maintable_qs.update(region_population=res[res_id])

        print('MainTable and population fill done!')
