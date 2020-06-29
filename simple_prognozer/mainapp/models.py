from django.db import models


class Country(models.Model):
    country_region = models.CharField(verbose_name='Country',
                                      max_length=128,
                                      primary_key=True
                                      )


class Subdivision(models.Model):
    country = models.ForeignKey(Country,
                                on_delete=models.CASCADE,
                                )
    subdivision = models.CharField(verbose_name='Province, Region or City',
                                   max_length=128,
                                   default=0
                                   )
    # FIPS только для US
    fips = models.PositiveIntegerField(verbose_name='FIPS US inner number',
                                       blank=True
                                       )
    # Admin2 только для US
    admin2 = models.CharField(verbose_name='Admin2 County name. US only',
                              max_length=128
                              )
    last_update = models.CharField(verbose_name='Last update',
                                   max_length=128
                                   )
    # Широта
    lat = models.DecimalField(verbose_name='Latitude',
                              max_digits=19,
                              decimal_places=16,
                              default=0.0
                              )
    # Долгота
    longitude = models.DecimalField(verbose_name='Longitude',
                                    max_digits=19,
                                    decimal_places=16,
                                    default=0.0
                                    )


class MainTable(models.Model):
    subdivision = models.ForeignKey(Subdivision,
                                    on_delete=models.CASCADE,
                                    related_name='maintable',
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
    # Заболеваемость
    incidence_rate = models.DecimalField(verbose_name='Incidence rate',
                                         max_digits=19,
                                         decimal_places=16,
                                         blank=True
                                         )
    # Соотношение Заболеваемости И Летальности в % на 100 000 человек
    case_fatality_ratio = models.\
        DecimalField(verbose_name='Case fatality ratio',
                     max_digits=19,
                     decimal_places=16,
                     default=0
                     )
    testing_rate = models.DecimalField(verbose_name='Testing rate',
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
    # 80% от region_population округляем в большую сторону
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
