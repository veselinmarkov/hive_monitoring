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

    def test_01_authorization(self):
        ''' Test JWT authorization, interfaces /user/create/; /token/obtain/; /token/refresh/'''
        print('\nCreate a test user')
        user_url = reverse('create_user')
        response = self.client.post(user_url, {"email": "test@test.com", "username": "test", "password": "test_pass"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        """ print(type(json.loads(response.content)), json.loads(response.content))
        print(type(response.json), response.json) """

        print('Get tokens')
        token_url = reverse('token_create')
        response = self.client.post(token_url, {"username": "test", "password": "test_pass"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        # print(type(body), body)
        self.assertTrue('refresh' in body and 'access' in body)
        refresh_token = body['refresh']

        print('Refresh tokens')
        token_url = reverse('token_refresh')
        response = self.client.post(token_url, {"refresh": refresh_token}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        # print(type(body), body)
        self.assertTrue('refresh' in body and 'access' in body)

    def test_02_POST_GET_DELETE_sample(self):
        """
        Testing main interface /sample for POST/GET single sample. 
        Also the /samples interface for GETting multiple automatic aggregated samples 
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
        
        print('Test NOT Authorized GET method {"hive": 1, "sample_time": "2020-06-30T20:05:00Z"}')
        response = self.client.get(url, {"hive": 1, "sample": "2020-06-30T20:05:00Z"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        data = {"hive": 1, "sample1": "2020-04-01T00:05:00Z", "sample2": "2020-06-30T23:05:00Z"}
        print('Test NOT Authorized multiple samples GET method %s' % data)
        response = self.client.get(reverse('sample_range'), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        print('Create a test user')
        user_url = reverse('create_user')
        response = self.client.post(user_url, {"email": "test@test.com", "username": "test", "password": "test_pass"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        print('Get tokens') 
        token_url = reverse('token_create')
        response = self.client.post(token_url, {"username": "test", "password": "test_pass"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        # print(type(body), body)
        # self.assertTrue('refresh' in body and 'access' in body)
        access_token = body['access']

        print('Test the GET method {"hive": 1, "sample_time": "2020-06-30T20:05:00Z"}')
        # print('JWT {}'.format(SamplesTest.access_token)) #HTTP_AUTHORIZATION
        response = self.client.get(url, {"hive": 1, "sample": "2020-06-30T20:05:00Z"}, HTTP_AUTHORIZATION='JWT {}'.format(access_token))
        # print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), good_data)
        
        data = {"hive": 1, "sample1": "2020-04-01T00:05:00Z", "sample2": "2020-06-30T23:05:00Z"}
        print('Test multiple samples GET method %s' % data)
        response = self.client.get(reverse('sample_range'), data, HTTP_AUTHORIZATION='JWT {}'.format(access_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # print(response.json())
        self.assertEqual(response.json()['data']['totalItems'], 2)

        print('Test the DELETE method {"hive": 1, "sample_time": "2020-06-30T20:05:00Z"}')
        url = '/api/sample/?sample=2020-06-30T20:05:00.000Z&hive=1'
        response = self.client.delete(url, {"hive": 1, "sample": "2020-06-30T20:05:00Z"}, HTTP_AUTHORIZATION='JWT {}'.format(access_token))
        # response = self.client.delete(url, HTTP_AUTHORIZATION='JWT {}'.format(access_token))
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Samples.objects.count(), 1)

        print('Test the DELETE method {"hive": 1, "sample_time": "2020-04-13T11:53:12Z"}')
        url = '/api/sample/?sample=2020-04-13T11:53:12Z&hive=1'
        #response = self.client.delete(url, {"hive": 1, "sample": "2020-06-30T20:05:00Z"})
        response = self.client.delete(url, HTTP_AUTHORIZATION='JWT {}'.format(access_token))
        #print(response.content, response.status_code)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Samples.objects.count(), 0)

    def test_03_POST_GET_PUT_DELETE_hive(self):
        """ Testing interface /hive and /hive/<int:pk> """
        url = reverse('hive')
        print('\nTest NOT Authorized /hive POST method')
        data = {"name": "Test hive"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        print('Create a test user')
        user_url = reverse('create_user')
        response = self.client.post(user_url, {"email": "test@test.com", "username": "test", "password": "test_pass"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        print('Get tokens') 
        token_url = reverse('token_create')
        response = self.client.post(token_url, {"username": "test", "password": "test_pass"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        access_token = body['access']

        url = reverse('hive')
        print('Test /hive POST method')
        data = {"name": "Test_hive"}
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='JWT {}'.format(access_token))
        # print(response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        print('Test /hive GET method')
        response = self.client.get(url, HTTP_AUTHORIZATION='JWT {}'.format(access_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        record = response.json()['data']['items'][0]
        # print(response.json())
        self.assertEqual(record['name'], 'Test_hive')
        hive_id = record['id']
        user = record['user']

        print('Test /hive PUT method')
        data = {"user": user, "name": "New_hive"}
        response = self.client.put(url+str(hive_id)+'/', data, HTTP_AUTHORIZATION='JWT {}'.format(access_token))
        # print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], 'New_hive')

        print('Test /hive DELETE method')
        response = self.client.delete(url+str(hive_id)+'/', HTTP_AUTHORIZATION='JWT {}'.format(access_token))
        # print(response.json())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # self.assertEqual(response.json()[0]['name'], 'Test_hive')

        print('Test again /hive GET method to confirm deletion')
        response = self.client.get(url, HTTP_AUTHORIZATION='JWT {}'.format(access_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # print(response.json())
        self.assertEqual(response.json()['data']['totalItems'], 0)
