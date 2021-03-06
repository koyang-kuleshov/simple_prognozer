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

    context = {
        'labels': labels,
        'data_confirmed': data_confirmed,
        'data_deaths': data_deaths,
        'data_recovered': data_recovered,
        'countries': countries,
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
