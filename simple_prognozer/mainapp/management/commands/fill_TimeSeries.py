import pandas as pd
from github.MainClass import Github

from django.utils import timezone
from django.core.management.base import BaseCommand

from mainapp.models import TimeSeries, Country, Subdivision


class Command(BaseCommand):
    def handle(self, *args, **options):
        # настройки для подключения к github
        token = '2c67b8917aa76671447a6782d81e29e5c94fe0a5'
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

        # удаляем дубликаты для US
        df_result = df_result.drop_duplicates(subset=['FIPS',
                                                      'Admin2',
                                                      'Country_Region',
                                                      'Province_State',
                                                      'Last_Update'],
                                              keep=False)

        # групируем фрейм, оставляя только страны и регионы
        df_by_country = df_result.groupby(
            ['Last_Update', 'Country_Region', 'Province_State', 'Admin2', 'FIPS', 'Lat', 'Long_'],
            as_index=False)[['Confirmed', 'Deaths', 'Recovered']].sum()

        # получаем текущую зону для добавления к дате, что бы иключить ошибку
        current_tz = timezone.get_current_timezone()

        # переводим датафрейм в словарь
        df_records = df_by_country.to_dict('records')

        # создаем список объектов для записи в бд

        print('Filling TimeSeries...')

        for record in df_records:
            if Country.objects.filter(country=record['Country_Region']).exists():
                country = Country.objects.get(country=record['Country_Region'])
            else:
                country = Country(country=record['Country_Region'])
                country.save()

            subdivision, _ = Subdivision.objects.update_or_create(country=country,
                                                                  subdivision=record['Province_State'],
                                                                  admin2=record['Admin2'] or None,
                                                                  fips=int(record['FIPS']) or None,
                                                                  )

            time_series, _ = TimeSeries.objects.update_or_create(country=country,
                                                                 subdivision=subdivision,
                                                                 last_update=record['Last_Update'],
                                                                 confirmed=record['Confirmed'],
                                                                 deaths=record['Deaths'],
                                                                 recovered=record['Recovered'])

        print('TimeSeries fill done!')

        # записываем данные в таблицу
