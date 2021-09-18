from django.conf.urls import url
from django.urls import path
from .views import SamplesHView, SamplesView
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('sample/', SamplesView, name='sample'),
    path('sample_hourly/', SamplesHView, name='sample'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
