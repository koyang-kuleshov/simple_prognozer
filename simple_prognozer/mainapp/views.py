from django.shortcuts import render
import csv
from services import parse

from mainapp.models import MainTable, Country, Subdivision


# Create your views here.


def index(request):

    context = {

    }
    return render(request, 'mainapp/index.html', context)