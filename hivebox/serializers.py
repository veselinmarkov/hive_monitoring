from rest_framework.serializers import ModelSerializer, Serializer, SerializerMethodField
from .models import SamplesH, Samples
from datetime import datetime


class SamplesH_seri(ModelSerializer):
    class Meta:
        model = SamplesH
        fields = ['hive', 'sample_time', 'temp_low', 
        'temp_high', 'temp_hot', 'temp_out', 'temp_target', 'humi_in', 'humi_out',
        'heat_pwr', 'fan', 'mode', 'heater_breakers']


class Samples_seri(ModelSerializer):
    class Meta:
        model = Samples
        fields = ['hive', 'sample_time', 'temp_low', 
        'temp_high', 'temp_hot', 'temp_out', 'temp_target', 'humi_in', 'humi_out',
        'heat_pwr', 'fan', 'mode', 'heater_breakers']

class SamplesRange_seri(ModelSerializer):
    sample_time = SerializerMethodField()

    class Meta:
        model = Samples
        fields = ['hive', 'sample_time', 'temp_low', 
        'temp_high', 'temp_hot', 'temp_out', 'temp_target', 'humi_in', 'humi_out',
        'heat_pwr', 'fan', 'mode', 'heater_breakers']

    def get_sample_time(self, obj):
        sample_time = obj.get('sample_time')
        if type(sample_time) =='str':
            return datetime.fromisoformat(sample_time.replace("Z", "+00:00"))
        else:
            return sample_time

""" class Raw_samples_seri(Serializer):
    hive = SerializerMethodField()
    sample_time = SerializerMethodField()
    temp_low = SerializerMethodField()
    temp_high = SerializerMethodField()
    temp_hot = SerializerMethodField()
    temp_out = SerializerMethodField()
    temp_target = SerializerMethodField()
    humi_in = SerializerMethodField()
    humi_out = SerializerMethodField()
    heat_pwr = SerializerMethodField()
    fan = SerializerMethodField()
    mode = SerializerMethodField()
    heater_breakers = SerializerMethodField()

    def get_key1(self, obj):
        # do some calculations, let's say we want to return input1 multiplied by 2
        # I'm accessing obj data and if it's empty assigning 0, you can add your own check instead
        return obj.get('input1', 0)*2

    def get_hive(self, obj):
        return obj[0]
    def get_sample_time(self, obj):
        return obj[1]
    def get_temp_low(self, obj):
        return obj[2]
    def get_temp_high(self, obj):
        return obj[3]
    def get_temp_hot(self, obj):
        return obj[4]
    def get_temp_out(self, obj):
        return obj[5]
    def get_temp_target(self, obj):
        return obj[6]
    def get_humi_in(self, obj):
        return obj[7]
    def get_humi_out(self, obj):
        return obj[8]
    def get_heat_pwr(self, obj):
        return obj[9]
    def get_fan(self, obj):
        return obj[10]
    def get_mode(self, obj): 
        return obj[11]
    def get_heater_breakers(self, obj):
        return obj[12] """