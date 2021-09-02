from django.urls import path
from .views import SamplesHView

urlpatterns = [
    path('sample/', SamplesHView),
]