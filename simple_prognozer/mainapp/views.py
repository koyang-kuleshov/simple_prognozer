from django.shortcuts import render
from django.db.models import Sum, F
from django.shortcuts import get_object_or_404

from mainapp.models import Country, TimeSeries


def index(request):
    labels = []
    data_confirmed = []
    data_deaths = []
    data_recovered = []

    queryset = TimeSeries.objects.all().values('last_update'). \
        annotate(Sum('confirmed'), Sum('deaths'), Sum('recovered'))

    for day in queryset:
        labels.append('{:%d/%m}'.format(day['last_update']))
        data_confirmed.append(day['confirmed__sum'] / 1000)
        data_deaths.append(day['deaths__sum'] / 1000)
        data_recovered.append(day['recovered__sum'] / 1000)

    countries = Country.objects.all()

    # {"confirmed": 555, "deaths": 17, "recovered": 28, "date": "2020-01-22"}
    covid_total_timeline = [
        {
            "confirmed": day['confirmed__sum'],
            "deaths": day['deaths__sum'],
            "recovered": day['recovered__sum'],
            "date": day['last_update'].strftime('%Y-%m-%d')
        }
        for day in queryset
    ]

    context = {
        'labels': labels,
        'data_confirmed': data_confirmed,
        'data_deaths': data_deaths,
        'data_recovered': data_recovered,
        'countries': countries,
        'covid_total_timeline': covid_total_timeline,
    }
    return render(request, 'mainapp/index.html', context)


def country_page(request, pk):
    country = get_object_or_404(Country, pk=pk)
    countries = Country.objects.all()

    queryset = TimeSeries.objects.filter(country_id=pk).values('last_update'). \
        annotate(Sum('confirmed'), Sum('deaths'), Sum('recovered'))

    chart_data = [
        {
            "date": day['last_update'].strftime('%m-%d'),
            "confirmed": day['confirmed__sum'],
            "recovered": day['recovered__sum'],
            "deaths": day['deaths__sum'],
        }
        for day in queryset
    ]

    context = {
        'country_name': country.country,
        'countries': countries,
        'chart_data': chart_data,
    }

    return render(request, 'mainapp/country_page.html', context)
