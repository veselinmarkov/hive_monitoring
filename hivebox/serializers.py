from rest_framework.serializers import ModelSerializer, Serializer, SerializerMethodField
from .models import SamplesH, Samples, Hives
from datetime import datetime
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User


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

""" class SamplesRange_seri(ModelSerializer):
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
            return sample_time """

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)
        token['user_name'] = user.username
        return token

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)  # as long as the fields are the same, we can just use this
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class HivesSerializer(ModelSerializer):
    class Meta:
        model = Hives
        fields = ['hive_id', 'user', 'group', 'name']
