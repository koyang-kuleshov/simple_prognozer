import json
import os

from django.db.models import Count
from django.shortcuts import render
import csv


from services import parse
from services.region_population import get_population, REGION_POPULATION_PATH

from django.shortcuts import render
from django.db.models import Sum

from mainapp.models import MainTable, Country, Subdivision, TimeSeries


def index(request):
    labels = []
    data_confirmed = []
    data_deaths = []
    data_recovered = []
    # daily_reports_to_maintable()  # Запись Daily_Reports в таблицу MainTable
    population_to_maintable()

    queryset = TimeSeries.objects.all().values('last_update').annotate(Sum('confirmed'), Sum('deaths'), Sum('recovered'))

    for day in queryset:
        labels.append('{:%d/%m}'.format(day['last_update']))
        data_confirmed.append(day['confirmed__sum'] / 1000)
        data_deaths.append(day['deaths__sum'] / 1000)
        data_recovered.append(day['recovered__sum'] / 1000)

    context = {
        'labels': labels,
        'data_confirmed': data_confirmed,
        'data_deaths': data_deaths,
        'data_recovered': data_recovered,
    }
    return render(request, 'mainapp/index.html', context)


def daily_reports_to_maintable():
    """ Запись Daily_Reports в таблицу MainTable """

    parse.get_csv('daily_reports')
    with open('daily_report.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if Country.objects.filter(country=row[3]).count():
                country = Country.objects.get(country=row[3])
            else:
                country = Country(country=row[3])
                country.save()

            subdivision = Subdivision(country=country, subdivision=row[2] or None, fips=row[0] or None,
                                      admin2=row[1] or None,
                                      lat=row[5] or None, longitude=row[6] or None)
            subdivision.save()
            main = MainTable(country=country, subdivision=subdivision, confirmed=row[7], deaths=row[8],
                             recovered=row[9],
                             active=row[10] or 0, last_update=row[4], incidence_rate=row[12] or None,
                             case_fatality_ratio=row[13] or None)
            main.save()


def population_to_maintable():
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
            for sub in list(Subdivision.objects.filter(country_id=country['country']).values('id', 'subdivision'))
        }
        for country in countries_with_subdivisions_exclude_us
    }

    all_countries_dict = {**countries_without_subdivisions, **us_subdivisions, **countries_with_subdivisions_dict}

    for countries_segment in list(all_countries_dict):
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
