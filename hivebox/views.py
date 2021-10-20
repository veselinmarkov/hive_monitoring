from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse

from web_project.settings import HIVEBOX
from .models import SamplesH, Samples, SamplesRange
from .serializers import SamplesH_seri, Samples_seri, SamplesRange_seri
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from rest_framework import permissions
from hivebox.permissions import IsOwnerOrReadOnly

@csrf_exempt
@permission_classes([IsOwnerOrReadOnly])
@api_view(['GET'])
def SamplesRangeView(request, format=None):
    '''Return multiple records based on the time interval beteen 
    sample1 and sample2 and hive parameters. The tree parameters are mandatory.
    If the returned number of records if higher of settings.AGGREAGTE_NUMBER_THRESHOLD,
     the next level of time aggregation is used. For example the first level is a plain query 
     which return records per minute (no aggreagtion), the next level is aggreagation per hour'''
    if request.method == 'GET':
        if 'sample1' not in request.GET or 'sample2' not in request.GET or 'hive' not in request.GET: 
            return Response('Parameters sample1, sample2 and hive expected', status=status.HTTP_400_BAD_REQUEST)
        try:
            sampletime1 = request.GET['sample1']
            sampletime2 = request.GET['sample2']
            sample1_utc = datetime.fromisoformat(sampletime1.replace("Z", "+00:00"))
            sample2_utc = datetime.fromisoformat(sampletime2.replace("Z", "+00:00"))
            hive = int(request.GET['hive'])
        except ValueError:
            return Response('Incorrect format for parameters sample1, samples2 or hive', status=status.HTTP_400_BAD_REQUEST)
        #print(hive, sample1_utc, sample2_utc)    
        row_count = SamplesH.objects.filter(sample_time__range = (sample1_utc, sample2_utc), hive__exact = hive).count()
        #print(row_count)
        if row_count <= HIVEBOX['AGGREGATE_NUMBER_THRESHOLD']:
            rows = SamplesH.objects.filter(sample_time__range = (sample1_utc, sample2_utc), hive__exact = hive)
            samples_seri = SamplesH_seri(rows, many=True)
            return Response(samples_seri.data)
        # The number of row is high, so need to aggregate the result
        # Try daily aggregate
        rows = SamplesRange.objects.raw('''SELECT min(id) as id, hive, 
            date_format(sample_time, '%%Y-%%m-%%d') as sample_time, 
            round(avg(temp_low),3) as temp_low,
            round(avg(temp_high),3) as temp_high,
            round(avg(temp_hot),3) as temp_hot,
            round(avg(temp_out),3) as temp_out,
            round(avg(temp_target),3) as temp_target,
            round(avg(humi_in),2) as humi_in,
            round(avg(humi_out),2) as humi_out,
            floor(avg(heat_pwr)) as heat_pwr,
            floor(avg(fan)) as fan,
            max(mode) as mode,
            max(heater_breakers) as heater_breakers FROM samples_h WHERE 
            sample_time >= %s and sample_time < %s and hive = %s 
            group by hive, date_format(sample_time, '%%Y-%%m-%%d')''', 
            [sampletime1, sampletime2, hive])
        #print(rows[0])
        samples_seri = SamplesH_seri(rows, many=True)
        #print(samples_seri.data)
        return Response(samples_seri.data)

@csrf_exempt
@permission_classes([IsOwnerOrReadOnly])
@api_view(['GET', 'POST', 'DELETE'])
def SamplesHView(request, format=None):

    def get_sample(request):
        #print('GET dict:', request.GET)
        if 'sample' not in request.GET or 'hive' not in request.GET: 
            return Response('Parameters sample and hive expected', status=status.HTTP_400_BAD_REQUEST)
        sampletime = request.GET['sample']
        hive = request.GET['hive']
        try:
            sample = SamplesH.objects.get(sample_time =sampletime, hive =hive)
        except SamplesH.DoesNotExist:
            return Response('The requested record was not found', status=status.HTTP_204_NO_CONTENT)
        return sample

    """ content = {
        'user': str(request.user),  # `django.contrib.auth.User` instance.
        'auth': str(request.auth),  # None
    } """
    #print(content)
    if request.method == 'GET':
        sample = get_sample(request)
        if isinstance(sample, Response):
            return sample
        sample_seri = SamplesH_seri(sample)
        #print(sample_seri.data)
        return Response(sample_seri.data)
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        if 'hive' not in data or 'sample_time' not in data:
            return Response('both "hive" and "sample_time" items are required', status=status.HTTP_400_BAD_REQUEST)
        try:
            timestamp = int(data['sample_time'])
        except ValueError:
            timestamp = None
        if timestamp:
            data['sample_time'] = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%SZ')
        #print(data['sample_time'])
        sample_seri = SamplesH_seri(data =data)
        if sample_seri.is_valid():
            sample_seri.save()
            return Response(sample_seri.validated_data, status=status.HTTP_201_CREATED)
        return Response(sample_seri.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        sample = get_sample(request)
        if isinstance(sample, Response):
            #print('Could not retreive the record')
            return sample
        sample.delete()
        return Response('Record deleted', status=status.HTTP_200_OK)

@csrf_exempt
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
@api_view(['GET', 'POST', 'DELETE'])
def SamplesView(request, format=None):

    def get_sample(request):
        #print('GET dict:', request.GET)
        if 'sample' not in request.GET or 'hive' not in request.GET: 
            return Response('Parameters sample and hive expected', status=status.HTTP_400_BAD_REQUEST)
        sampletime = request.GET['sample']
        hive = request.GET['hive']
        try:
            sample = Samples.objects.get(sample_time =sampletime, hive =hive)
        except Samples.DoesNotExist:
            return Response('The requested record was not found', status=status.HTTP_204_NO_CONTENT)
        return sample

    if request.method == 'GET':
        sample = get_sample(request)
        if isinstance(sample, Response):
            return sample
        sample_seri = Samples_seri(sample)
        #print(sample_seri.data)
        return Response(sample_seri.data)
    elif request.method == 'POST':
        #print('in POST')
        #print(request.data)
        data = JSONParser().parse(request)
        if 'hive' not in data or 'sample_time' not in data:
            return Response('both "hive" and "sample_time" items are required', status=status.HTTP_400_BAD_REQUEST)
        try:
            timestamp = int(data['sample_time'])
        except ValueError:
            timestamp = None
        if timestamp:
            data['sample_time'] = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%SZ')
        #print(data)
        sample_seri = Samples_seri(data =data)
        if sample_seri.is_valid():
            sample_seri.save()
            return Response(sample_seri.validated_data, status=status.HTTP_201_CREATED)
        return Response(sample_seri.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        sample = get_sample(request)
        if isinstance(sample, Response):
            #print('Could not retreive the record')
            return sample
        sample.delete()
        return Response('Record deleted', status=status.HTTP_200_OK)

