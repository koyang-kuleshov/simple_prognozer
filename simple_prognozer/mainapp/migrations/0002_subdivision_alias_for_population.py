# Generated by Django 3.0.7 on 2020-07-16 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subdivision',
            name='alias_for_population',
            field=models.CharField(max_length=128, null=True, verbose_name='Alias'),
        ),
    ]
