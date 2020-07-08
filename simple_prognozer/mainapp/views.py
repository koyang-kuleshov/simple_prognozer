from django.shortcuts import render
import csv
from services import parse

from mainapp.models import MainTable, Country, Subdivision


# Create your views here.


def index(request):
    daily_reports_to_maintable()  # Запись Daily_Reports в таблицу MainTable
    population_to_maintable()

    context = {

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
                             active=row[10], last_update=row[4], incidence_rate=row[12] or None,
                             case_fatality_ratio=row[13] or None)
            main.save()


def population_to_maintable():
    from services.region_population import get_population

    countries_without_subdivisions_list = [
        Country.objects.values_list('country', flat=True).get(pk=obj.country_id)
        for obj in Subdivision.objects.order_by('country_id')
        if Subdivision.objects.filter(country_id=obj.country_id).count() == 1
    ]

    countries_list = list(Subdivision.objects.values('id', 'subdivision', 'country__country', 'fips')
                          .order_by('country_id'))

    res = get_population(countries_without_subdivisions_list, countries_list)
    for res_id in res.keys():
        population_from_maintable_qs = MainTable.objects.filter(subdivision_id=res_id).values('region_population')

        if population_from_maintable_qs[0]['region_population'] != res[res_id]:
            population_from_maintable_qs.update(region_population=res[res_id])
