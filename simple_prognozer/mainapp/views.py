from django.shortcuts import render
from django.db.models import Sum, F
from django.shortcuts import get_object_or_404

from mainapp.models import Country, TimeSeries, MainTable


def total_active(*args):
    if args:
        return MainTable.objects.filter(country_id=args).aggregate(Sum('active')).get('active__sum')
    else:
        return MainTable.objects.aggregate(Sum('active')).get('active__sum')


def total_deaths(*args):
    if args:
        return MainTable.objects.filter(country_id=args).aggregate(Sum('deaths')).get('deaths__sum')
    else:
        return MainTable.objects.aggregate(Sum('deaths')).get('deaths__sum')


def total_recovered(*args):
    if args:
        return MainTable.objects.filter(country_id=args).aggregate(Sum('recovered')).get('recovered__sum')
    return MainTable.objects.aggregate(Sum('recovered')).get('recovered__sum')


def total_confirmed(*args):
    if args:
        return MainTable.objects.filter(country_id=args).aggregate(Sum('confirmed')).get('confirmed__sum')
    return MainTable.objects.aggregate(Sum('confirmed')).get('confirmed__sum')


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

        'active': total_active(),
        'deaths': total_deaths(),
        'recovered': total_recovered(),
        'confirmed': total_confirmed(),
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

        'active': total_active(pk),
        'deaths': total_deaths(pk),
        'recovered': total_recovered(pk),
        'confirmed': total_confirmed(pk),
    }

    return render(request, 'mainapp/country_page.html', context)
