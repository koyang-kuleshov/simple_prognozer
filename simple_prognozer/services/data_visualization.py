import os
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

from django_pandas.io import read_frame

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "simple_prognozer.settings")
django.setup()

from mainapp.models import TimeSeries


def graph_confirm(df_by_date, path):
    fig, ax = plt.subplots()
    ax.plot(df_by_date["last_update"],
             df_by_date["confirmed"]/1000)

    plt.xlabel('Дата')
    plt.ylabel('Число подтвержденных случаев, тыс. чел.')
    plt.savefig(os.path.join(path, 'confirmed'))


def graph_death_recovered(df_by_date, labels, path):
    fig, ax = plt.subplots()

    for label in labels:
        ax.plot(df_by_date["last_update"],
                 df_by_date[label]/1000,
                 label=labels[label])

    plt.ylabel('Число случаев, тыс. чел.')
    plt.xlabel('Дата')
    plt.legend()
    plt.savefig(os.path.join(path, 'death_and_recovered'))


def graph_fatality_rate(df_by_date, path):
    fig, ax = plt.subplots()
    ax.plot(df_by_date["last_update"],
             df_by_date['deaths'] / df_by_date['confirmed'] * 100)

    plt.ylabel('Доля умерших среди зараженных, %')
    plt.xlabel('Дата')
    plt.savefig(os.path.join(path, 'fatality_rate'))


def graph_fatality_recovered_rate(df_by_date, labels, path):
    fig, ax = plt.subplots()
    for label in labels:
        ax.plot(df_by_date['last_update'],
                df_by_date[label] / df_by_date['confirmed'] * 100,
                label=labels[label])
    plt.ylabel('Доли умерших и выздоровевших зараженных, %')
    plt.xlabel('Дата')
    plt.legend()
    plt.savefig(os.path.join(path, 'fatality_recovered_rate'))


qs = TimeSeries.objects.all()
df = read_frame(qs)
df_by_date = df.groupby(['last_update']).sum().reset_index(drop=None)
path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media', 'graph')

mpl.rcParams['figure.figsize'] = [12.0, 5.0]
mpl.rcParams['figure.dpi'] = 200
labels = {"deaths": "Умерли", "recovered": "Выздоровели"}


graph_confirm(df_by_date, path)
graph_death_recovered(df_by_date, labels, path)
graph_fatality_rate(df_by_date, path)
graph_fatality_recovered_rate(df_by_date, labels, path)
