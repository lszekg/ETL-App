from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('test/', views.save_file, name='save_file'),
    path('clear/', views.clear_database, name='clear_database'),
]
