from rest_framework import serializers
from .models import SamplesH

class SamplesH_seri(serializers.ModelSerializer):
    class Meta:
        model = SamplesH
        fields = ['hive', 'sample_time', 'temp_low', 
        'temp_high', 'temp_hot', 'temp_out', 'temp_target', 'humi_in', 'humi_out',
        'heat_pwr', 'fan', 'mode', 'heater_breakers']

