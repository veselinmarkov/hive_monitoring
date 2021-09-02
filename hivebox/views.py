from django.http.response import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from .models import SamplesH
from .serializers import SamplesH_seri
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
@csrf_exempt
@api_view(['GET', 'POST'])
def SamplesHView(request):
    if request.method == 'GET':
        if 'sample' not in request.GET or 'hive' not in request.GET: 
            return Response('Parameters sample and hive expected', status=status.HTTP_400_BAD_REQUEST)
        sampletime = request.GET['sample']
        hive = request.GET['hive']
        try:
            sample = SamplesH.objects.get(sample_time =sampletime, hive =hive)
        except SamplesH.DoesNotExist:
            return Response('The requested record is not found', status=status.HTTP_204_NO_CONTENT)
        sample_seri = SamplesH_seri(sample)
        return Response(sample_seri.data)
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        sample_seri = SamplesH_seri(data =data)
        if sample_seri.is_valid():
            sample_seri.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(sample_seri.errors, status=status.HTTP_400_BAD_REQUEST)

