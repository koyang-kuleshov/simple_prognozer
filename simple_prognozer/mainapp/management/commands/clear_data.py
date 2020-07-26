from django.core.management.base import BaseCommand

from mainapp.models import TimeSeries, Country, Subdivision, MainTable


class Command(BaseCommand):
    def handle(self, *args, **options):
        TimeSeries.objects.all().delete()
        MainTable.objects.all().delete()
        Subdivision.objects.all().delete()
        Country.objects.all().delete()
