from django.shortcuts import render
import csv
from services import parse

from mainapp.models import MainTable, Country, Subdivision


# Create your views here.


def index(request):
    daily_reports_to_maintable()  # Запись Daily_Reports в таблицу MainTable

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
