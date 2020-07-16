import csv

from django.views.generic import ListView

from services import parse

from django.shortcuts import render
from django.db.models import Sum

from mainapp.models import MainTable, Country, Subdivision, TimeSeries


def index(request):
    labels = []
    data_confirmed = []
    data_deaths = []
    data_recovered = []

    queryset = TimeSeries.objects.all().values('last_update').\
        annotate(Sum('confirmed'), Sum('deaths'), Sum('recovered'))

    for day in queryset:
        labels.append('{:%d/%m}'.format(day['last_update']))
        data_confirmed.append(day['confirmed__sum'] / 1000)
        data_deaths.append(day['deaths__sum'] / 1000)
        data_recovered.append(day['recovered__sum'] / 1000)

    countries = Country.objects.all()

    context = {
        'labels': labels,
        'data_confirmed': data_confirmed,
        'data_deaths': data_deaths,
        'data_recovered': data_recovered,
        'countries': countries,
    }
    return render(request, 'mainapp/index.html', context)
