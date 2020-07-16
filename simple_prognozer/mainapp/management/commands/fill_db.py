from django.core.management.base import BaseCommand
from django.utils import timezone
from mainapp.models import TimeSeries, Country, Subdivision, MainTable

import csv
import requests

from github.MainClass import Github
import pandas as pd

TOKEN = 'a6c034b6c7677dbe8693ae0ad5bce62ebcfaee18'  # GitHub token

REPO_PATH = 'CSSEGISandData/COVID-19'
GIT = Github(TOKEN)
REPO = GIT.get_repo(REPO_PATH)
DR_REPO_FILE_LIST = 'csse_covid_19_data/csse_covid_19_daily_reports'
DAILY_REPORTS_DIR_PATH = 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data' \
                         '/csse_covid_19_daily_reports/'


def get_csv(file_name):
    print('Getting daily report csv...')

    daily_reports_file_list = REPO.get_contents(DR_REPO_FILE_LIST)

    if file_name == 'daily_reports':
        daily_reports_file_path = DAILY_REPORTS_DIR_PATH + str(daily_reports_file_list[-2]).split('/')[-1].split(".")[
            0] + '.csv'
        req = requests.get(daily_reports_file_path)
        url_content = req.content
        csv_file = open('daily_report.csv', 'wb')
        csv_file.write(url_content)
        csv_file.close()


class Command(BaseCommand):
    help = 'Fill db'

    def handle(self, *args, **kwargs):
        """ Запись Daily_Reports в таблицу MainTable """

        print('Filling MainTable...')

        get_csv('daily_reports')
        with open('daily_report.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if Country.objects.filter(country=row[3]).exists():
                    country = Country.objects.get(country=row[3])
                else:
                    country = Country(country=row[3])
                    country.save()

                subdivision, _ = Subdivision.objects.get_or_create(country=country,
                                                                   subdivision=row[2] or None,
                                                                   fips=row[0] or None,
                                                                   admin2=row[1] or None,
                                                                   defaults={
                                                                       'lat': row[5] or None,
                                                                       'longitude': row[6] or None})

                main, _ = MainTable.objects.update_or_create(country=country, subdivision=subdivision,
                                                             defaults={'confirmed': row[7],
                                                                       'deaths': row[8],
                                                                       'recovered': row[9],
                                                                       'active': row[10] or None,
                                                                       'last_update': row[4],
                                                                       'incidence_rate': row[12] or None,
                                                                       'case_fatality_ratio': row[13] or None}
                                                             )
        print('MainTable fill done!')

        print('Getting TimeSeries data frame')
        # получаем список только отчетов
        daily_reports_file_list = REPO.get_contents(DR_REPO_FILE_LIST)[1:-1]

        # создаем пустой фрейм для наполнения
        df_result = pd.DataFrame(columns=['Last_Update',
                                          'FIPS',
                                          'Admin2',
                                          'Province_State',
                                          'Country_Region',
                                          'Lat',
                                          'Long_',
                                          'Confirmed',
                                          'Deaths',
                                          'Recovered',
                                          ])

        # перебираем отчеты по одному
        for report in daily_reports_file_list:
            # загружаем отчет в датафрейм
            df = pd.read_csv(report.download_url)

            # исправляем разночтения в названиях столбцов
            if {'Last Update'}.issubset(df.columns):
                df.rename(
                    columns={'Latitude': 'Lat', 'Longitude': 'Long_',
                             'Province/State': 'Province_State',
                             'Country/Region': 'Country_Region',
                             'Last Update': 'Last_Update'},
                    inplace=True)

            # вставляем отчет в общий дата фрейм
            df_result = pd.concat([df_result, df])

        # исправляем разные названия одной страны
        df_result.loc[df_result['Country_Region'] == \
                      'Mainland China', 'Country_Region'] = 'China'
        df_result.loc[df_result['Country_Region'] == \
                      ' Azerbaijan', 'Country_Region'] = 'Azerbaijan'
        df_result.loc[df_result['Country_Region'] == \
                      'Gambia, The', 'Country_Region'] = 'Gambia'
        df_result.loc[df_result['Country_Region'] == \
                      'Hong Kong SAR', 'Country_Region'] = 'China'
        df_result.loc[df_result['Country_Region'] == \
                      'Hong Kong', 'Country_Region'] = 'China'
        df_result.loc[df_result['Country_Region'] == \
                      'Iran (Islamic Republic of)', 'Country_Region'] = 'Iran'
        df_result.loc[df_result['Country_Region'] == \
                      'South Korea', 'Country_Region'] = 'Korea, South'
        df_result.loc[df_result['Country_Region'] == \
                      'Republic of Korea', 'Country_Region'] = 'Korea, South'
        df_result.loc[df_result['Country_Region'] == \
                      'Russian Federation', 'Country_Region'] = 'Russia'
        df_result.loc[df_result['Country_Region'] == \
                      'UK', 'Country_Region'] = 'United Kingdom'
        df_result.loc[df_result['Country_Region'] == \
                      'Taiwan', 'Country_Region'] = 'Taiwan*'

        # исправляем разные форматы дат
        df_result['Last_Update'] = pd.to_datetime(df_result['Last_Update'])
        df_result['Last_Update'] = df_result['Last_Update'].apply(
            lambda x: x.date())
        df_result['Last_Update'] = pd.to_datetime(df_result['Last_Update'])

        # заменяем nan на нули, т.к. в бд должны придти числа
        df_result.fillna(
            {
                'Confirmed': 0,
                'Deaths': 0,
                'Recovered': 0
            },
            inplace=True)

        # заменяем оставшиеся nan на None для корректной записи в БД
        df_result = df_result.where(df_result.notnull(), None)

        # получаем текущую зону для добавления к дате, что бы иключить ошибку
        current_tz = timezone.get_current_timezone()

        # переводим датафрейм в словарь
        df_records = df_result.to_dict('records')

        print('Filling TimeSeries...')

        # создаем список объектов для записи в бд
        model_instances = [TimeSeries(
            country=Country.objects.get_or_create(
                country=record['Country_Region'])[0],
            subdivision=Subdivision.objects.get_or_create(
                country=Country.objects.get(
                    country=record['Country_Region']),
                subdivision=record['Province_State'],
                fips=record['FIPS'],
                admin2=record['Admin2']
            )[0],
            last_update=current_tz.localize(record['Last_Update']),
            confirmed=record['Confirmed'],
            deaths=record['Deaths'],
            recovered=record['Recovered'],
        ) for record in df_records]

        # записываем данные в таблицу
        TimeSeries.objects.bulk_create(model_instances)

        print('Fill database done!')
