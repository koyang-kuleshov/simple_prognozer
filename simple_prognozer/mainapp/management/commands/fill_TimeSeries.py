import pandas as pd
from github.MainClass import Github

from django.core.management.base import BaseCommand
from mainapp.models import TimeSeries, Country, Subdivision


class Command(BaseCommand):
    def handle(self, *args, **options):
        # настройки для подклбчения к github
        token = '952d6b2c5667ad09b38d798a3f98bf27289de9f6'
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
            # загружаем отчет в дата фрейм
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

        # df_result = pd.read_csv('converted.csv')
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

        # удаляем дубликаты для US
        df_result = df_result.drop_duplicates(subset=['FIPS',
                                                      'Admin2',
                                                      'Country_Region',
                                                      'Province_State',
                                                      'Last_Update'],
                                              keep=False)

        # групируем фрейм, оставляя только страны и регионы
        df_by_country = df_result.groupby(
            ['Last_Update', 'Country_Region', 'Province_State'],
            as_index=False)[['Confirmed', 'Deaths', 'Recovered']].sum()

        for index, row in df_by_country.iterrows():
            country = Country.objects.get_or_create(country=row['Country_Region'])
            subdivision = Subdivision.objects.get_or_create(
                country=country,
                subdivision=row['Country_Region'])
            seria = TimeSeries(country=country,
                               subdivision=subdivision,
                               last_update=row['Last_Update'],
                               confirmed=row['Confirmed'],
                               deaths=row['Deaths'],
                               recovered=row['Recovered']
                               )
            seria.save()


