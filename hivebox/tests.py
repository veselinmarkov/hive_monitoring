from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Samples
#from .serializers import SamplesH_seri
import json
import os

from django.contrib.auth.models import User
from asymmetric_jwt_auth.models import PublicKey
from asymmetric_jwt_auth.keys import PrivateKey, RSAPrivateKey, RSAPublicKey
from asymmetric_jwt_auth.tokens import Token


class SamplesTest(APITestCase):
    """ Test module for GET, POST, DELETE in Samples """

    def setUp(self):
        pass

    #More tests need
    def test_01_user_authentication(self):
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
        Testing /sample/ (GET and DELETE) and /sample (POST) interfaces. 
        """
        client = APIClient()
        print('\nPOST a valid record no AUTH HEADER')
        good_data = {"hive":1, "time_stamp":1599596661, "t_heated_air":32.69, "t_hive_air":0.00, 
            "t_ambient_air":23.81, "fan_frequency":2233, "heater_power":0, "heater_register":0, 
            "heater_pwm":0, "t_target":9.00, "heating_mode":"monitor", "pid_previous_deviation":0.00, 
            "pid_deviation":0.00, "pid_integral":0.00, "pid_derivative":0.00, "pid_output":0.00, 
            "humidity_hive_air":0.00, "t_hive_ceiling":33.38, "heater_breakers":10}
        response = client.post(reverse('sample'), good_data, format='json')
        #print(type(json.loads(response.content)), json.loads(response.content))
        #print(type(response.data), response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        user = User.objects.create_user(username="foo")
        user.save()
        key_rsa = RSAPrivateKey.generate()
        user_key_rsa = PublicKey.objects.create(
            user=user, key=key_rsa.public_key.as_pem.decode()
        )
        """ print(key_rsa.as_pem)
        print(key_rsa.as_pem.decode()) """
        user_key_rsa.save()
        header = Token(user.username).create_auth_header(key_rsa)

        print('POST an invalid record "hive": None')
        bad_data = {"hive":None, "time_stamp":1599596661, "t_heated_air":32.69, "t_hive_air":0.00, 
            "t_ambient_air":23.81, "fan_frequency":2233, "heater_power":0, "heater_register":0, 
            "heater_pwm":0, "t_target":9.00, "heating_mode":"monitor", "pid_previous_deviation":0.00, 
            "pid_deviation":0.00, "pid_integral":0.00, "pid_derivative":0.00, "pid_output":0.00, 
            "humidity_hive_air":0.00, "t_hive_ceiling":33.38, "heater_breakers":10}
        response = client.post(reverse('sample'), bad_data, HTTP_AUTHORIZATION=header, format='json')
        # response = client.post(reverse('sample'), bad_data, format='json')
        #self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        print('POST an invalid record "hive" missing')
        bad_data = {"time_stamp":1599596661, "t_heated_air":32.69, "t_hive_air":0.00, 
            "t_ambient_air":23.81, "fan_frequency":2233, "heater_power":0, "heater_register":0, 
            "heater_pwm":0, "t_target":9.00, "heating_mode":"monitor", "pid_previous_deviation":0.00, 
            "pid_deviation":0.00, "pid_integral":0.00, "pid_derivative":0.00, "pid_output":0.00, 
            "humidity_hive_air":0.00, "t_hive_ceiling":33.38, "heater_breakers":10}
        # header = Token(user.username).create_auth_header(key_rsa)
        response = client.post(reverse('sample'), bad_data, HTTP_AUTHORIZATION=header, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        print('POST a valid record')
        """ good_data = {"hive": 1, "sample_time": "2020-06-30T20:05:00Z", "temp_low": 28.823, 
            "temp_high": None, "temp_hot": 31.663, "temp_out": 24, "temp_target": -10.000, 
            "humi_in": 47.13, "humi_out": None, "heat_pwr": 0, "fan": 758, 
            "mode": "monitor", "heater_breakers": 10} """
        good_data = {"hive":1, "time_stamp":"2020-06-30T20:05:00Z", "t_heated_air":32.69, "t_hive_air":0.00, 
            "t_ambient_air":23.81, "fan_frequency":2233, "heater_power":0, "heater_register":0, 
            "heater_pwm":0, "t_target":9.00, "heating_mode":"monitor", "pid_previous_deviation":0.00, 
            "pid_deviation":0.00, "pid_integral":0.00, "pid_derivative":0.00, "pid_output":0.00, 
            "humidity_hive_air":0.00, "t_hive_ceiling":33.38, "heater_breakers":10}
        # header = Token(user.username).create_auth_header(key_rsa)
        response = client.post(reverse('sample'), good_data, HTTP_AUTHORIZATION=header, format='json')
        #print(type(json.loads(response.content)), json.loads(response.content))
        # print(type(response.data), response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(json.loads(response.content), good_data)
        self.assertEqual(Samples.objects.count(), 1)

        print('POST valid record (sample_time=1586778792)')
        good_data2 = {"hive":1, "time_stamp":1586778792, "t_heated_air":32.69, "t_hive_air":0.00, 
            "t_ambient_air":23.81, "fan_frequency":2233, "heater_power":0, "heater_register":0, 
            "heater_pwm":0, "t_target":9.00, "heating_mode":"monitor", "pid_previous_deviation":0.00, 
            "pid_deviation":0.00, "pid_integral":0.00, "pid_derivative":0.00, "pid_output":0.00, 
            "humidity_hive_air":0.00, "t_hive_ceiling":33.38, "heater_breakers":10}        
        # header = Token(user.username).create_auth_header(key_rsa)
        response = client.post(reverse('sample'), good_data2, HTTP_AUTHORIZATION=header, format='json')
        #print(type(json.loads(response.content)), json.loads(response.content))
        #print(type(response.data), response.data)
        #print(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        #self.assertEqual(json.loads(response.content), good_data)
        self.assertEqual(Samples.objects.count(), 2)
        
        print('Test NOT Authorized GET method {"hive": 1, "sample_time": "2020-06-30T20:05:00Z"}')
        response = client.get(reverse('sample'), {"hive": 1, "sample": "2020-06-30T20:05:00Z"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        print('Test the GET method {"hive": 1, "sample_time": "2020-06-30T20:05:00Z"}')
        # header = Token(user.username).create_auth_header(key_rsa)
        response = client.get(reverse('sample'), {"hive": 1, "sample": "2020-06-30T20:05:00Z"}, HTTP_AUTHORIZATION=header, format="json")
        # print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(json.loads(response.content), good_data)        

        print('Test the DELETE method {"hive": 1, "sample_time": "2020-06-30T20:05:00Z"}')
        url = '/api/sample/?sample=2020-06-30T20:05:00.000Z&hive=1'
        # header = Token(user.username).create_auth_header(key_rsa)
        response = client.delete(url, {"hive": 1, "sample": "2020-06-30T20:05:00Z"}, HTTP_AUTHORIZATION=header, format="json")
        # response = self.client.delete(url, HTTP_AUTHORIZATION='JWT {}'.format(access_token))
        # print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Samples.objects.count(), 1)

        print('Test again the DELETE method {"hive": 1, "sample_time": "2020-04-13T11:53:12Z"}')
        url = '/api/sample/?sample=2020-04-13T11:53:12Z&hive=1'
        # header = Token(user.username).create_auth_header(key_rsa)
        response = client.delete(url, HTTP_AUTHORIZATION=header, format="json")
        #print(response.content, response.status_code)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Samples.objects.count(), 0)

    def test_03_hive_POST_GET_PUT_DELETE(self):
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
        data = {"name": "Test_hive", "hive_id": 1}
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION='JWT {}'.format(access_token))
        # print(response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        print('Test /hive GET method')
        response = self.client.get(url, HTTP_AUTHORIZATION='JWT {}'.format(access_token))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        record = response.json()['data']['items'][0]
        print(response.json())
        self.assertEqual(record['name'], 'Test_hive')
        hive_id = record['hive_id']
        # user = record['user']

        print('Test /hive PUT method')
        data = {"name": "New_hive"}
        response = self.client.put(url+str(hive_id)+'/', data, HTTP_AUTHORIZATION='JWT {}'.format(access_token))
        print(response.json())
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

    def test_04_GET_multiple_records(self):
        """Test /samples interface for GETting multiple automatic aggregated samples 
            The JWT RSA authentication is loaded from pub/priv key files
        """
        client = APIClient()
        data = {"hive": 1, "sample1": "2020-04-01T00:05:00Z", "sample2": "2020-06-30T23:05:00Z"}
        print('\nTest NOT Authorized multiple samples GET method %s' % data)
        response = client.get(reverse('sample_range'), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        user = User.objects.create_user(username="foo")
        user.save()
        base = os.path.dirname(__file__)
        pub_path = os.path.join(base, "test_fixtures/dummy_rsa.pub")
        with open(pub_path) as f1:
            exc, key_pub = RSAPublicKey.load_serialized_public_key(f1.read().encode())
        if exc:
            print(exc)
        user_key_rsa = PublicKey.objects.create(
            user=user, key=key_pub.as_pem.decode()
        )
        user_key_rsa.save()
        # wite the encoded Public key to a file for inspection
        pub_enc_path = os.path.join(base, "test_fixtures/dummy_pub_enc.bin")
        with open(pub_enc_path, 'wb') as f1:
            f1.write(key_pub.as_pem)
        """ print(key_rsa.as_pem)
        print(key_rsa.as_pem.decode()) """        
        priv_path = os.path.join(base, "test_fixtures/dummy_rsa.privkey")
        key_rsa = PrivateKey.load_pem_from_file(priv_path)
        header = Token(user.username).create_auth_header(key_rsa)
        # wite the token to a file for inspection
        token_path = os.path.join(base, "test_fixtures/dummy_token.txt")
        with open(token_path, 'w') as f1:
            f1.write(header)

        print('POST a valid record')
        good_data = {"hive":1, "time_stamp":"2020-06-30T20:05:00Z", "t_heated_air":32.69, "t_hive_air":0.00, 
            "t_ambient_air":23.81, "fan_frequency":2233, "heater_power":0, "heater_register":0, 
            "heater_pwm":0, "t_target":9.00, "heating_mode":"monitor", "pid_previous_deviation":0.00, 
            "pid_deviation":0.00, "pid_integral":0.00, "pid_derivative":0.00, "pid_output":0.00, 
            "humidity_hive_air":0.00, "t_hive_ceiling":33.38, "heater_breakers":10}
        response = client.post(reverse('sample'), good_data, HTTP_AUTHORIZATION=header, format='json')
        #print(type(json.loads(response.content)), json.loads(response.content))
        # print(type(response.data), response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(json.loads(response.content), good_data)
        self.assertEqual(Samples.objects.count(), 1)

        print('POST valid record (sample_time=1586778792)')
        good_data2 = {"hive":1, "time_stamp":"1586778792", "t_heated_air":32.69, "t_hive_air":0.00, 
            "t_ambient_air":23.81, "fan_frequency":2233, "heater_power":0, "heater_register":0, 
            "heater_pwm":0, "t_target":9.00, "heating_mode":"monitor", "pid_previous_deviation":0.00, 
            "pid_deviation":0.00, "pid_integral":0.00, "pid_derivative":0.00, "pid_output":0.00, 
            "humidity_hive_air":0.00, "t_hive_ceiling":33.38, "heater_breakers":10}        
        # header = Token(user.username).create_auth_header(key_rsa)
        response = client.post(reverse('sample'), good_data2, HTTP_AUTHORIZATION=header, format='json')
        #print(type(json.loads(response.content)), json.loads(response.content))
        #print(type(response.data), response.data)
        #print(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        #self.assertEqual(json.loads(response.content), good_data)
        self.assertEqual(Samples.objects.count(), 2)

        print('Create a test user')
        user_url = reverse('create_user')
        response = client.post(user_url, {"email": "test@test.com", "username": "test", "password": "test_pass"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        print('Get tokens') 
        token_url = reverse('token_create')
        response = client.post(token_url, {"username": "test", "password": "test_pass"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        # print(type(body), body)
        # self.assertTrue('refresh' in body and 'access' in body)
        access_token = body['access']

        data = {"hive": 1, "sample1": "2020-04-01T00:05:00Z", "sample2": "2020-06-30T23:05:00Z"}
        print('Test multiple samples GET method %s' % data)
        response = client.get(reverse('sample_range'), data, HTTP_AUTHORIZATION='JWT {}'.format(access_token), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # print(response.json())
        self.assertEqual(response.json()['data']['totalItems'], 2)
    