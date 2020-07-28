from django.db import models


class Continent(models.Model):
    continent = models.CharField(verbose_name='Continent',
                                 max_length=32,
                                 unique=True)


class Country(models.Model):
    country = models.CharField(verbose_name='Country',
                               max_length=128,
                               unique=True)

    continent = models.ForeignKey(Continent,
                                  on_delete=models.DO_NOTHING,
                                  null=True)


class Subdivision(models.Model):
    country = models.ForeignKey(Country,
                                on_delete=models.DO_NOTHING,
                                )

    subdivision = models.CharField(verbose_name='Province, Region or City',
                                   max_length=128,
                                   null=True
                                   )

    # Альтернативное название страны/региона для поиска кол-ва населения
    alias_for_population = models.CharField(verbose_name='Alias',
                                            max_length=128,
                                            null=True
                                            )

    # FIPS только для US
    fips = models.IntegerField(verbose_name='FIPS US inner number',
                               null=True
                               )

    # Admin2 только для US
    admin2 = models.CharField(verbose_name='Admin2 County name. US only',
                              max_length=128,
                              null=True,
                              )

    # Широта
    lat = models.DecimalField(verbose_name='Latitude',
                              max_digits=19,
                              decimal_places=16,
                              null=True
                              )

    # Долгота
    longitude = models.DecimalField(verbose_name='Longitude',
                                    max_digits=19,
                                    decimal_places=16,
                                    null=True
                                    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['admin2', 'country', 'fips'],
                                    name='uq_subdivison')
        ]


class MainTable(models.Model):
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING)
    subdivision = models.ForeignKey(Subdivision,
                                    on_delete=models.DO_NOTHING,
                                    null=True
                                    )
    # Заболевшие
    confirmed = models.PositiveIntegerField(verbose_name='Confirmed',
)
    # Смерти
    deaths = models.PositiveIntegerField(verbose_name='Deaths',
                                         )
    # Выздоровления
    recovered = models.PositiveIntegerField(verbose_name='Recovered',
                                            )
    # Активные больные
    active = models.IntegerField(verbose_name='Active',
                                 null=True,
                                 )

    last_update = models.DateTimeField(verbose_name='Last update',
                                       )

    # Заболеваемость
    incidence_rate = models.DecimalField(verbose_name='Incidence rate',
                                         max_digits=25,
                                         decimal_places=16,
                                         blank=True,
                                         null=True,
                                         )
    # Соотношение Заболеваемости И Летальности в % на 100 000 человек
    case_fatality_ratio = models. \
        DecimalField(verbose_name='Case fatality ratio',
                     max_digits=25,
                     decimal_places=16,
                     default=0,
                     null=True
                     )

    region_population = models. \
        PositiveIntegerField(verbose_name='Region population',
                             default=0
                             )


class TimeSeries(models.Model):
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING)
    subdivision = models.ForeignKey(Subdivision, on_delete=models.DO_NOTHING,
                                    null=True)
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
