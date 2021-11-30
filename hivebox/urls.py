from django.conf.urls import url
from django.urls import path
from .views import SampleView, SamplesRangeView, UserCreate, \
    ObtainTokenWithUserName, HivesView, HivesViewDetail
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    # path('sample/detail/', SampleView.as_view(), name='sample_detail'),
    path('sample/', SampleView.as_view(), name='sample'),
    path('samples/', SamplesRangeView.as_view(), name='sample_range'),
    # path('sample_hourly/', SamplesHView, name='sample_hourly'),
    # path('user/', UserInfo.as_view(), name='user_info'),
    path('hive/', HivesView.as_view(), name='hive'),
    path('hive/<int:pk>/', HivesViewDetail.as_view(), name='hive_detail'),
    path('token/obtain/', ObtainTokenWithUserName.as_view(), name='token_create'),  # override sjwt stock token
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('user/create/', UserCreate.as_view(), name='create_user'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
