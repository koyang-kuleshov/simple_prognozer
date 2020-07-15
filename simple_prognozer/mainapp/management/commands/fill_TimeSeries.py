import pandas as pd
from github.MainClass import Github

from django.utils import timezone
from django.core.management.base import BaseCommand

from mainapp.models import TimeSeries, Country, Subdivision


class Command(BaseCommand):
    def handle(self, *args, **options):
        # настройки для подключения к github
        token = ''
        repo_path = 'CSSEGISandData/COVID-19'
        dr_repo_file_list = 'csse_covid_19_data/csse_covid_19_daily_reports'

        # подключаемся
        git = Github(token)
        repo = git.get_repo(repo_path)

        # получаем список только отчетов
        daily_reports_file_list = repo.get_contents(dr_repo_file_list)[1:-1]

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

        print('TimeSeries fill done!')

