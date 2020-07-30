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

    covid_total_timeline = [
        {
            "confirmed": day['confirmed__sum'],
            "deaths": day['deaths__sum'],
            "recovered": day['recovered__sum'],
            "date": day['last_update'].strftime('%Y-%m-%d')
        }
        for day in queryset
    ]

    covid_world_timeline = [
        {
            "date": day['last_update'].strftime('%Y-%m-%d'),
            "list": [
                {
                    "confirmed": data['confirmed__sum'],
                    "deaths": data['deaths__sum'],
                    "recovered": data['recovered__sum'],
                    "id": data['country__iso_alpha_2']
                }
                for data in
                TimeSeries.objects.filter(last_update=day['last_update']).values('country__iso_alpha_2').
                    annotate(Sum('confirmed'), Sum('deaths'), Sum('recovered'))
                if data['country__iso_alpha_2']
            ]
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
        'covid_world_timeline': covid_world_timeline,
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
    print(chart_data)

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
