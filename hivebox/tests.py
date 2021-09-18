from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Samples
#from .serializers import SamplesH_seri
import json

# Create your tests here.
class SamplesTest(APITestCase):
    """ Test module for GET, POST, DELETE in Samples """

    def setUp(self):
        pass

    def test_POST_GET_DELETE_sample(self):
        """
        Ensure we can POST, GET and DELETE a sample.
        """
        print('\nPOST an invalid record "hive": None')
        url = reverse('sample')
        bad_data = {"hive": None, "sample_time": "2020-06-30T20:05:00Z", "temp_low": 28.823, 
            "temp_high": None, "temp_hot": 31.663, "temp_out": 24, "temp_target": -10.000, 
            "humi_in": 47.13, "humi_out": None, "heat_pwr": 0, "fan": 758, 
            "mode": "monitor", "heater_breakers": 10}
        response = self.client.post(url, bad_data, format='json')
        #self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        print('POST an invalid record "hive" missing')
        url = reverse('sample')
        bad_data = {"sample_time": "2020-06-30T20:05:00Z", "temp_low": 28.823, 
            "temp_high": None, "temp_hot": 31.663, "temp_out": 24, "temp_target": -10.000, 
            "humi_in": 47.13, "humi_out": None, "heat_pwr": 0, "fan": 758, 
            "mode": "monitor", "heater_breakers": 10}
        response = self.client.post(url, bad_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        print('POST a valid record')
        good_data = {"hive": 1, "sample_time": "2020-06-30T20:05:00Z", "temp_low": 28.823, 
            "temp_high": None, "temp_hot": 31.663, "temp_out": 24, "temp_target": -10.000, 
            "humi_in": 47.13, "humi_out": None, "heat_pwr": 0, "fan": 758, 
            "mode": "monitor", "heater_breakers": 10}
        response = self.client.post(url, good_data, format='json')
        #print(type(json.loads(response.content)), json.loads(response.content))
        #print(type(response.data), response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content), good_data)
        self.assertEqual(Samples.objects.count(), 1)

        print('POST another valid record sample_time=1586778792')
        good_data2 = {"hive": 1, "sample_time": 1586778792, "temp_low": 28.823, 
            "temp_high": None, "temp_hot": 31.663, "temp_out": 24, "temp_target": -10.000, 
            "humi_in": 47.13, "humi_out": None, "heat_pwr": 0, "fan": 758, 
            "mode": "monitor", "heater_breakers": 10}
        response = self.client.post(url, good_data2, format='json')
        #print(type(json.loads(response.content)), json.loads(response.content))
        #print(type(response.data), response.data)
        #print(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        #self.assertEqual(json.loads(response.content), good_data)
        self.assertEqual(Samples.objects.count(), 2)

        print('Test the GET method {"hive": 1, "sample_time": "2020-06-30T20:05:00Z"}')
        response = self.client.get(url, {"hive": 1, "sample": "2020-06-30T20:05:00Z"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), good_data)
        
        print('Test the DELETE method {"hive": 1, "sample_time": "2020-06-30T20:05:00Z"}')
        url = '/sample/?sample=2020-06-30T20:05:00.000Z&hive=1'
        #response = self.client.delete(url, {"hive": 1, "sample": "2020-06-30T20:05:00Z"})
        response = self.client.delete(url)
        #print(response.content, response.status_code)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Samples.objects.count(), 1)

        print('Test the DELETE method {"hive": 1, "sample_time": "2020-04-13T11:53:12Z"}')
        url = '/sample/?sample=2020-04-13T11:53:12Z&hive=1'
        #response = self.client.delete(url, {"hive": 1, "sample": "2020-06-30T20:05:00Z"})
        response = self.client.delete(url)
        #print(response.content, response.status_code)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Samples.objects.count(), 0)
