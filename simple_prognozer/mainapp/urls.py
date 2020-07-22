from django.urls import path
import mainapp.views as mainapp

app_name = 'mainapp'

urlpatterns = [
    path('', mainapp.index, name='index'),
    path('country_page/<int:pk>/', mainapp.country_page, name='country_page'),
]
