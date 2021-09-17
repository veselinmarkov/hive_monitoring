from django.http.response import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from .models import SamplesH
from .serializers import SamplesH_seri
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

# Create your views here.
@csrf_exempt
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

