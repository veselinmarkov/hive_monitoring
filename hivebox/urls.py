from django.conf.urls import url
from django.urls import path
from .views import SamplesHView, SamplesView, SamplesRangeView
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('sample/', SamplesView, name='sample'),
    path('samples/', SamplesRangeView, name='sample_range'),
    path('sample_hourly/', SamplesHView, name='sample_hourly'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
