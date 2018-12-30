from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('test/', views.save_file, name='save_file'),
    path('clear/', views.clear_database, name='clear_database'),
    path('refresh/', views.refresh_table, name='refresh_table'),
    path('dummy/', views.dummy, name='dummy'),
    #path('extract/', views.extract, name='extract'),
    #path('load/', views.load, name='load'),
    #path('transform/', views.transform, name='transform'),
    #path('etl/', views.etl_proces, name='etl_proces'),
]
