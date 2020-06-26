from django.db import models


class MainTable(models.Model):
    # FIPS только для US
    fips = models.PositiveIntegerField(verbose_name='FIPS',
                                       blank=True
                                       )
    # Admin2 только для US
    admin2 = models.CharField(verbose_name='Admin2',
                              max_length=128
                              )
    province_state = models.CharField(verbose_name='Province',
                                      max_length=128
                                      )
    country_region = models.CharField(verbose_name='Country_region',
                                      max_length=128
                                      )
    last_update = models.CharField(verbose_name='Last_update',
                                   max_length=128
                                   )
    # Широта
    lat = models.DecimalField(verbose_name='Latitude',
                              max_digits=19,
                              decimal_places=16,
                              default=0
                              )
    # Долгота
    longitude = models.DecimalField(verbose_name='Longitude',
                                    max_digits=19,
                                    decimal_places=16,
                                    default=0
                                    )
    # Заболевшие
    confirmed = models.PositiveIntegerField(verbose_name='Confirmed',
                                            default=0
                                            )
    # Смерти
    deaths = models.PositiveIntegerField(verbose_name='Deaths',
                                         default=0
                                         )
    # Выздоровления
    recovered = models.PositiveIntegerField(verbose_name='Recovered',
                                            default=0
                                            )
    # Активные больные
    active = models.PositiveIntegerField(verbose_name='Active',
                                         default=0
                                         )
    # Формат Khakassia, Republic Russia
    combined_key = models.CharField(verbose_name='Combined_key',
                                    max_length=128,
                                    default='Russia',
                                    unique=True
                                    )
    # Заболеваемость
    incidence_rate = models.DecimalField(verbose_name='Incidence_rate',
                                         max_digits=19,
                                         decimal_places=16,
                                         blank=True
                                         )
    # Соотношение Заболеваемости И Летальности в % на 100 000 человек
    case_fatality_ratio = models.\
        DecimalField(verbose_name='Case_fatality_ratio',
                     max_digits=19,
                     decimal_places=16,
                     default=0
                     )
    testing_rate = models.DecimalField(verbose_name='Testin_rate',
                                       max_digits=19,
                                       decimal_places=16,
                                       default=0
                                       )
    hospitalization_rate = models.\
        DecimalField(verbose_name='Hospitalization_rate',
                     max_digits=19,
                     decimal_places=16,
                     default=0
                     )
    region_population = models.\
        PositiveIntegerField(verbose_name='Region population',
                             default=0
                             )
    # Округляем в большую сторону
    region_limit = models.PositiveIntegerField(verbose_name='Region limit',
                                               default=0
                                               )


class TimeSeries(models.Model):
    region = models.ForeignKey(MainTable, on_delete=models.CASCADE)
    last_update = models.DateTimeField()
    # Заболевшие
    confirmed = models.PositiveIntegerField(verbose_name='Confirmed',
                                            default=0
                                            )
    # Смерти
    deaths = models.PositiveIntegerField(verbose_name='Deaths',
                                         default=0
                                         )
    # Выздоровления
    recovered = models.PositiveIntegerField(verbose_name='Recovered',
                                            default=0
                                            )
