# Generated by Django 3.0.7 on 2020-07-28 16:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0002_subdivision_alias_for_population'),
    ]

    operations = [
        migrations.CreateModel(
            name='Continent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('continent', models.CharField(max_length=32, unique=True, verbose_name='Continent')),
            ],
        ),
        migrations.AddField(
            model_name='country',
            name='continent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='mainapp.Continent'),
        ),
    ]
