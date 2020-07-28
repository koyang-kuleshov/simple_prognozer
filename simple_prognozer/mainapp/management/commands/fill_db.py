<<<<<<<<< Temporary merge branch 1
=========
from django.core.management.base import BaseCommand
from django.utils import timezone
from mainapp.models import TimeSeries, Country, Subdivision, MainTable, Continent

>>>>>>>>> Temporary merge branch 2
import csv
import re
import requests
import codecs

from datetime import datetime
from github.MainClass import Github
import pycountry_convert as pc
from contextlib import closing

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from mainapp.models import TimeSeries, Country, Subdivision, MainTable, Continent
from simple_prognozer.config import TOKEN


REPO_PATH = 'CSSEGISandData/COVID-19'
GIT = Github(TOKEN)
REPO = GIT.get_repo(REPO_PATH)
DR_REPO_FILE_LIST = 'csse_covid_19_data/csse_covid_19_daily_reports'
DR_REPO_TS_FILE_LIST = 'csse_covid_19_data/csse_covid_19_time_series'
DAILY_REPORTS_DIR_PATH = ('https://github.com/CSSEGISandData/COVID-19/raw/'
                          'master/csse_covid_19_data'
                          '/csse_covid_19_daily_reports/'
                          )

# так как набор столбцов различается, создадим словарь
# в котором привяжем таблицу к столбцам, так же укажем тип
# получаемых данных
TS_PARAMS = {
    'confirmed_US': [7, 4, 5, 6, 8, 9, 11, 'confirmed'],
    'deaths_US': [7, 4, 5, 6, 8, 9, 12, 'deaths'],
    'confirmed_global': [1, None, None, 0, 2, 3, 4, 'confirmed'],
    'deaths_global': [1, None, None, 0, 2, 3, 4, 'deaths'],
    'recovered_global': [1, None, None, 0, 2, 3, 4, 'recovered'],
}


def get_csv(file_name):
    print('Getting daily report csv...')

    daily_reports_file_list = REPO.get_contents(DR_REPO_FILE_LIST)

    if file_name == 'daily_reports':
        daily_reports_file_path = DAILY_REPORTS_DIR_PATH + \
                                  str(daily_reports_file_list[-2]).split('/')[
                                      -1].split(".")[
                                      0] + '.csv'
        req = requests.get(daily_reports_file_path)
        url_content = req.content
        csv_file = open('daily_report.csv', 'wb')
        csv_file.write(url_content)
        csv_file.close()


def get_or_none(model, *args, **kwargs):
    """метод возвращает None, если запись не найдена в таблице"""
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None


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
>>>>>>>>> Temporary merge branch 2


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

        # очистка таблицы
        TimeSeries.objects.all().delete()

        # получаем список временных рядов в репозитории
        time_series_file_list = REPO.get_contents(DR_REPO_TS_FILE_LIST)[3:]

        # зададим счетчик по которму разграничим создание таблиц
        # при обработке confirmed данных и
        # обновление при обработке deaths и recovered данных
        confirmed_table = 0

        # перебираем по одному
        for time_series_file in time_series_file_list:
            confirmed_table += 1
            # получаем данные с помощью запроса
            print('Getting TimeSeries')
            print(time_series_file.download_url)
            with closing(requests.get(time_series_file.download_url,
                                      stream=True)) as r:

                # загружаем при помощи reader, декодируя данные
                reader = csv.reader(codecs.iterdecode(r.iter_lines(), 'utf-8'))

                # получаем текущую зону для добавления к дате,
                # что бы иключить ошибку при записи в БД
                current_tz = timezone.get_current_timezone()

                # собираем заголовки в отдельный список
                headers = next(reader)

                # парсим нахвание файла в url что бы понять
                # к какому типу данных отностится таблица и
                # является глобальной или USA
                pattern = r".*time_series_covid19_(\w*_\w*).\w*"
                ts_type_data = re.search(pattern,
                                         time_series_file.download_url)

                # распаковываем индексы столбцов по переменным
                country_index, fips_index, admin2_index, subdivision_index, \
                lat_index, long_index, start_date_index, \
                type_data = TS_PARAMS[ts_type_data[1]]

                models_create_instances = []
                models_update_instances = []

                print('Filling TimeSeries...')
                # перебираем данные построчно
                for row in reader:
                    # получаем страну или None
                    country = get_or_none(Country, country=row[country_index])

                    # если есть fips, преобразуем его в int
                    # если нет то None
                    if fips_index and row[fips_index]:
                        fips = int(float(row[fips_index]))
                    else:
                        fips = None

                    # если есть admin2_index, берем значение
                    # если нет то None
                    if admin2_index:
                        admin2 = row[admin2_index]
                    else:
                        admin2 = None

                    # получаем subdivision или None
                    subdivision = get_or_none(
                        Subdivision,
                        country=country,
                        subdivision=row[subdivision_index],
                        fips=fips,
                        admin2=admin2,
                        # China Hebei с разными lat и longitude
                        # в разных таблицах
                        # lat=row[lat_index],
                        # longitude=row[long_index]
                    )

                    # если страна и subdivision не None
                    if country:
                        # берем только даты из заголовков
                        dates = headers[start_date_index:]
                        # перебираем строку
                        for num, record in enumerate(row[start_date_index:]):
                            # преобразуем запись из таблицы в datetime
                            # и добавляем зону для корректной записи в БД
                            last_update = current_tz.localize(
                                datetime.strptime(dates[num], '%m/%d/%y')
                            )

                            # создадим словарь с ключем в зависимости
                            # от типа таблицы (confirmed, deaths, recovered)
                            # и значением показателя за этот день
                            values = dict.fromkeys([type_data], record)
                            # если мы обрабатываем первые 2 таблицы confirmed
                            if confirmed_table < 3:
                                # создаем экземпляр и добавляем в список
                                models_create_instances.append(
                                    TimeSeries(
                                        country=country,
                                        subdivision=subdivision,
                                        last_update=last_update,
                                        **values
                                    )
                                )
                            # иначе мы обрабатываем deaths или recovered
                            else:
                                # получаем из бд запись
                                try:
                                    event = TimeSeries.objects.get(
                                        country=country,
                                        subdivision=subdivision,
                                        last_update=last_update,
                                    )
                                    # обновляем значение deaths или recovered
                                    setattr(event, type_data, record)
                                    # добавляем в список
                                    models_update_instances.append(event)
                                except MultipleObjectsReturned:
                                    break
                                except ObjectDoesNotExist:
                                    models_create_instances.append(
                                        TimeSeries(
                                            country=country,
                                            subdivision=subdivision,
                                            last_update=last_update,
                                            **values
                                        )
                                    )

                # если мы обрабатываем первые 2 таблицы confirmed
                if confirmed_table < 3:
                    # создаем записи в таблице
                    TimeSeries.objects.bulk_create(models_create_instances)
                    print(f'Fill {ts_type_data[1]} done!')
                # иначе мы обрабатываем deaths или recovered
                else:
                    TimeSeries.objects.bulk_create(models_create_instances)
                    # обновляем данные deaths или recovered
                    TimeSeries.objects.bulk_update(models_update_instances,
                                                   [type_data])
                    print(f'Fill {ts_type_data[1]} done!')

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
