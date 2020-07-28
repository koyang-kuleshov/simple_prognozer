from django.core.management.base import BaseCommand
from django.utils import timezone
from mainapp.models import TimeSeries, Country, Subdivision, MainTable, Continent

import csv
import requests

from github.MainClass import Github
import pandas as pd
import pycountry_convert as pc

from simple_prognozer.config import TOKEN


REPO_PATH = 'CSSEGISandData/COVID-19'
GIT = Github(TOKEN)
REPO = GIT.get_repo(REPO_PATH)
DR_REPO_FILE_LIST = 'csse_covid_19_data/csse_covid_19_daily_reports'
DAILY_REPORTS_DIR_PATH = ('https://github.com/CSSEGISandData/COVID-19/raw/'
                          'master/csse_covid_19_data'
                          '/csse_covid_19_daily_reports/'
                          )


def get_csv(file_name):
    print('Getting daily report csv...')

    daily_reports_file_list = REPO.get_contents(DR_REPO_FILE_LIST)

    if file_name == 'daily_reports':
        daily_reports_file_path = DAILY_REPORTS_DIR_PATH +\
            str(daily_reports_file_list[-2]).split('/')[-1].split(".")[
                0] + '.csv'
        req = requests.get(daily_reports_file_path)
        url_content = req.content
        csv_file = open('daily_report.csv', 'wb')
        csv_file.write(url_content)
        csv_file.close()


def get_continent(country_name):
    continents = {'AF': 'Africa',
                  'AS': 'Asia',
                  'EU': 'Europe',
                  'NA': 'North America',
                  'OC': 'Australia and Oceania',
                  'SA': 'South America'}

    if country_name == 'US':
        return continents['NA']
    elif country_name == 'Burma':
        return continents['AS']
    elif country_name[:5] == 'Congo':
        return continents['AF']
    elif country_name == "Cote d'Ivoire":
        return continents['AF']
    elif country_name == 'Diamond Princess':
        return continents['NA']
    elif country_name == 'MS Zaandam':
        return continents['NA']
    elif country_name == 'Holy See':
        return continents['EU']
    elif country_name == 'Korea, South':
        return continents['AS']
    elif country_name == 'Kosovo':
        return continents['EU']
    elif country_name == 'Taiwan*':
        return continents['AS']
    elif country_name == 'West Bank and Gaza':
        return continents['AS']
    elif country_name == 'Western Sahara':
        return continents['AF']
    elif country_name == 'Timor-Leste':
        return continents['OC']
    else:
        return continents[(pc.country_alpha2_to_continent_code(pc.country_name_to_country_alpha2(country_name)))]


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
                continent, _ = Continent.objects.get_or_create(continent=get_continent(row[3]))

                country, _ = Country.objects.get_or_create(country=row[3], continent=continent)

                subdivision, _ = Subdivision.objects.\
                    get_or_create(country=country,
                                  subdivision=row[2] or None,
                                  fips=row[0] or None,
                                  admin2=row[1] or None,
                                  defaults={
                                    'lat': row[5] or None,
                                    'longitude': row[6] or None
                                  }
                                  )

                main, _ = MainTable.\
                    objects.update_or_create(
                        country=country,
                        subdivision=subdivision,
                        defaults={'confirmed': row[7],
                                  'deaths': row[8],
                                  'recovered': row[9],
                                  'active': row[10] or None,
                                  'last_update': row[4],
                                  'incidence_rate': row[12] or None,
                                  'case_fatality_ratio': row[13] or None
                                  }
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
        df_result.loc[df_result['Country_Region'] ==
                      'Mainland China', 'Country_Region'] = 'China'
        df_result.loc[df_result['Country_Region'] ==
                      ' Azerbaijan', 'Country_Region'] = 'Azerbaijan'
        df_result.loc[df_result['Country_Region'] ==
                      'Gambia, The', 'Country_Region'] = 'Gambia'
        df_result.loc[df_result['Country_Region'] ==
                      'Hong Kong SAR', 'Country_Region'] = 'China'
        df_result.loc[df_result['Country_Region'] ==
                      'Hong Kong', 'Country_Region'] = 'China'
        df_result.loc[df_result['Country_Region'] ==
                      'Iran (Islamic Republic of)', 'Country_Region'] = 'Iran'
        df_result.loc[df_result['Country_Region'] ==
                      'South Korea', 'Country_Region'] = 'Korea, South'
        df_result.loc[df_result['Country_Region'] ==
                      'Republic of Korea', 'Country_Region'] = 'Korea, South'
        df_result.loc[df_result['Country_Region'] ==
                      'Russian Federation', 'Country_Region'] = 'Russia'
        df_result.loc[df_result['Country_Region'] ==
                      'UK', 'Country_Region'] = 'United Kingdom'
        df_result.loc[df_result['Country_Region'] ==
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

        print('Filling Countries ISO 2 codes...')
        all_contries = (Country.objects.all().values('country'))
        for country in all_contries:
            try:
                Country.objects.filter(country=country['country']) \
                    .update(iso_alpha_2=pycountry.countries.get(name=country['country']).alpha_2)
            except:
                pass

        Country.objects.filter(country='US').update(iso_alpha_2='US')
        Country.objects.filter(country='Russia').update(iso_alpha_2='RU')
        Country.objects.filter(country='Bolivia').update(iso_alpha_2='BO')
        Country.objects.filter(country='Brunei').update(iso_alpha_2='BN')
        Country.objects.filter(country='Burma').update(iso_alpha_2='MM')
        Country.objects.filter(country='Congo (Kinshasa)').update(iso_alpha_2='CD')
        Country.objects.filter(country='Congo (Brazzaville)').update(iso_alpha_2='CG')
        Country.objects.filter(country="Cote d'Ivoire").update(iso_alpha_2='CI')
        Country.objects.filter(country='Holy See').update(iso_alpha_2='VA')
        Country.objects.filter(country='Iran').update(iso_alpha_2='IR')
        Country.objects.filter(country='Korea, South').update(iso_alpha_2='KR')
        Country.objects.filter(country='Kosovo').update(iso_alpha_2='XK')
        Country.objects.filter(country='Laos').update(iso_alpha_2='LA')
        Country.objects.filter(country='Moldova').update(iso_alpha_2='MD')
        Country.objects.filter(country='Syria').update(iso_alpha_2='SY')
        Country.objects.filter(country='Taiwan*').update(iso_alpha_2='TW')
        Country.objects.filter(country='Tanzania').update(iso_alpha_2='TZ')
        Country.objects.filter(country='Venezuela').update(iso_alpha_2='VE')
        Country.objects.filter(country='Vietnam').update(iso_alpha_2='VN')
        Country.objects.filter(country='West Bank and Gaza').update(iso_alpha_2='PS')
        print('Fill Countries ISO 2 codes done!')
