from django.conf import settings
from django.http.response import Http404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import logging

from rest_framework.serializers import Serializer
from rest_framework.views import APIView

from web_project import settings
from .models import SamplesH, Samples, SamplesRange, Hives
from .serializers import SamplesH_seri, Samples_seri, UserSerializer, HivesSerializer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer
from hivebox.permissions import IsAuthenticatedOrPOSTmethod
from django.utils.decorators import method_decorator


logger = logging.getLogger(__name__)

#get the thresholds from settings file
THR_LOW = settings.HIVEBOX.get('AGGREGATE_THRESHOLD_LOW', 100) if settings.HIVEBOX else 100
THR_HIGH = settings.HIVEBOX.get('AGGREGATE_THRESHOLD_HIGH', 500) if settings.HIVEBOX else 500

AGGR_STR = ["",
    "date_format(sample_time, '%%Y-%%m-%%d %%H:%%i:00')",
    "concat(date_format(sample_time, '%%Y-%%m-%%d %%H:'),lpad(floor(minute(sample_time)/5)*5, 2, '0'))",
    "concat(date_format(sample_time, '%%Y-%%m-%%d %%H:'),lpad(floor(minute(sample_time)/15)*15, 2, '0'))",
    "date_format(sample_time, '%%Y-%%m-%%d %%H:00:00')",
    "concat(date_format(sample_time, '%%Y-%%m-%%d '),lpad(floor(hour(sample_time)/6)*6, 2, '0'))",
    "date_format(sample_time, '%%Y-%%m-%%d')"
]
AGGR_NAMES = ['20s','1m', '5m', '15m', '1h', '6h', '1d']
AGGR_PERIOD = [1, 60, 5*60, 15*60, 60*60, 6*60*60, 24*60*60]
SAMPLE_PERIOD_SECONDS = 20
AGGR_START_STEP = 1

API_RETURN_TEMPLATE = {
    "api_version": 1.0,
    "params": {},
    "data": {
        "aggregation": "",
        "totalItems": 0,
        "items": []
    },
}

HIVE_RETURN_TEMPLATE = {
    "api_version": 1.0,
    "user": "",
    "data": {
        "totalItems": 0,
        "items": []
    },
}


""" @csrf_exempt
@permission_classes([IsOwnerOrReadOnly])
@api_view(['GET']) """
class SamplesRangeView(APIView):
    '''Return multiple records based on the time interval beteen 
    sample1 and sample2 and hive parameters.
    The returned records are automatically time aggregated if the row number is higher than 
    "settings.AGGREAGTE_THRESHOLD_HIGH or lower than AGGREGATE_THRESHOLD_LOW". 
    The aggreagtion steps are as follows:
    "no aggreagtion" -> "1min" -> "5min" -> "15min" -> "hourly" ->"6 hours" -> "daily" '''

    @staticmethod
    def estimate_samples(date1, date2, aggr_step):
        #date1, date2 are datetime objects
        assert(aggr_step >=0)
        assert(aggr_step < len(AGGR_PERIOD))
        delta_sec = (date2 - date1).total_seconds()
        if aggr_step == 0:
            return delta_sec / SAMPLE_PERIOD_SECONDS
        else:
            return delta_sec / AGGR_PERIOD[aggr_step]

    @staticmethod
    def adapt_aggregation_level(row_number, aggr_step):
        #modify the step if not in required range
        logger.debug('Check if the row number is adequate, number: %d, step: %d' % (row_number, aggr_step))
        init_step = aggr_step
        if (row_number > THR_HIGH and 
            aggr_step < len(AGGR_NAMES) -1):
            aggr_step += 1
        if ( row_number < THR_LOW and aggr_step > 0):
            aggr_step -= 1
        return aggr_step != init_step, aggr_step

    def get(self, request, format=None):
        r = API_RETURN_TEMPLATE.copy() 
        r['params'] = request.GET
        if 'sample1' not in request.GET or 'sample2' not in request.GET or 'hive' not in request.GET: 
            r['error'] = 'Parameters sample1, sample2 and hive are expected'
            del r['data']
            return Response( r, status=status.HTTP_400_BAD_REQUEST)
        try:
            sampletime1 = request.GET['sample1']
            sampletime2 = request.GET['sample2']
            sample1_utc = datetime.fromisoformat(sampletime1.replace("Z", "+00:00"))
            sample2_utc = datetime.fromisoformat(sampletime2.replace("Z", "+00:00"))
            hive = int(request.GET['hive'])
        except ValueError as e:
            r['error'] = 'Incorrect format for parameters sample1, samples2 or hive; ' + str(e)
            del r['data']
            return Response( r, status=status.HTTP_400_BAD_REQUEST)
        if sample1_utc >= sample2_utc:
            r['error'] = 'samples2 must be later than samples1'
            del r['data']
            return Response( r, status=status.HTTP_400_BAD_REQUEST)
        # find the correct aggregation step; start with AGGR_START_STEP
        step = AGGR_START_STEP
        steps_try = 0
        row_estimation = SamplesRangeView.estimate_samples(sample1_utc, sample2_utc, step)
        steps_hist = [step]
        logger.debug('First estimation, step: %d row_estimation: %d' % (step, row_estimation))
        while (( row_estimation < THR_LOW or row_estimation > THR_HIGH) and steps_try < 5):
            step_changed ,step = SamplesRangeView.adapt_aggregation_level(row_estimation, step)
            if step_changed:
                steps_hist.append(step)
                row_estimation = SamplesRangeView.estimate_samples(sample1_utc, sample2_utc, step)
                logger.debug('Estimation step change: %d, new row_estimation: %d' % (step, row_estimation))
            steps_try += 1
        # make the query and find the real number of records; adapt the step if necessary
        steps_repeated = set([x for x in steps_hist if steps_hist.count(x) >1])
        if len(steps_repeated) >0 and min(steps_repeated) < step:
            logger.debug('Lower repeated value assigned to step old: %d' % (step))
            step = min(steps_repeated)
            logger.debug('step new: %d , Repated values: %s' % (step, steps_repeated))
        steps_try = 2
        while steps_try > 0:
            if steps_try == 1 and step > 0 and len(rows) < THR_LOW:
                # attempt a new query on lower aggregatio if the number of actual rows is lower than THR_LOW
                step -= 1
                logger.debug('New query on step changed to: %d old row number: %d' % (step, len(rows)))
            if step == 0:
                rows = Samples.objects.filter(sample_time__range = (sample1_utc, sample2_utc), hive__exact = hive)
            else:
                query = '''SELECT min(id) as id, hive, 
                    {sample_time} as sample_time, 
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
                    max(heater_breakers) as heater_breakers FROM samples WHERE 
                    sample_time >= %s and sample_time < %s and hive = %s 
                    group by hive, {sample_time}'''.format(sample_time = AGGR_STR[step])
                rows = SamplesRange.objects.raw(query, [sampletime1, sampletime2, hive])
            steps_try -= 1
        logger.debug('rows returned: %d' % (len(rows)))
        samples_seri = Samples_seri(rows,  many=True)
        #r = API_RETURN_TEMPLATE.copy()
        r["data"]["items"] = samples_seri.data
        r['data']['totalItems'] = len(rows)
        r['data']['aggregation'] = AGGR_NAMES[step]
        return Response(r)


@csrf_exempt
# @permission_classes([IsOwnerOrReadOnly])
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


""" @csrf_exempt
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
@api_view(['GET', 'POST', 'DELETE']) """
class SamplesView(APIView):
    permission_classes = (IsAuthenticatedOrPOSTmethod,)
    # authentication_classes = ()

    @staticmethod
    def get_sample(request):
        if 'sample' not in request.GET or 'hive' not in request.GET: 
            return Response('Parameters sample and hive expected', status=status.HTTP_400_BAD_REQUEST)
        sampletime = request.GET['sample']
        hive = request.GET['hive']
        try:
            sample = Samples.objects.get(sample_time =sampletime, hive =hive)
        except Samples.DoesNotExist:
            return Response('The requested record was not found', status=status.HTTP_204_NO_CONTENT)
        return sample

    def get(self, request, format=None):
        # sample = self.get_sample(request)
        if 'sample' not in request.GET or 'hive' not in request.GET: 
            return Response('Parameters sample and hive expected', status=status.HTTP_400_BAD_REQUEST)
        sampletime = request.GET['sample']
        hive = request.GET['hive']
        try:
            sample = Samples.objects.get(sample_time =sampletime, hive =hive)
        except Samples.DoesNotExist:
            return Response('The requested record was not found', status=status.HTTP_204_NO_CONTENT)
        """ return sample
        if isinstance(sample, Response):
            return sample """
        sample_seri = Samples_seri(sample)
        #print(sample_seri.data)
        return Response(sample_seri.data)
        
    def post(self, request, format=None):
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
        
    def delete(self, request, format=None):
        sample = self.get_sample(request)
        """ print(request.resolver_match.kwargs)
        if 'sample' not in request.DELETE or 'hive' not in request.DELETE: 
            return Response('Parameters sample and hive expected', status=status.HTTP_400_BAD_REQUEST)
        sampletime = request.DELETE['sample']
        hive = request.DELETE['hive']
        try:
            sample = Samples.objects.get(sample_time =sampletime, hive =hive)
        except Samples.DoesNotExist:
            return Response('The requested record was not found', status=status.HTTP_204_NO_CONTENT) """
        # return sample
        if isinstance(sample, Response):
            #print('Could not retreive the record')
            return sample
        sample.delete()
        return Response('Record deleted', status=status.HTTP_200_OK)


class ObtainTokenWithUserName(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = MyTokenObtainPairSerializer


# @method_decorator(csrf_exempt, name='dispatch')
class UserCreate(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request, format='json'):
        # print(request.data)
        seri = UserSerializer(data=request.data)
        # print(seri)
        if seri.is_valid():
            seri.save()
            return Response(seri.data, status=status.HTTP_201_CREATED)
        return Response(seri.errors, status=status.HTTP_400_BAD_REQUEST)


class HivesView(APIView):
    ''' GET return a list of Hives which belongs to the user.
    POST requires {name: "hive_name"} in the body'''
    
    def get(self, request, format=None):
        hives = Hives.objects.filter(user_id = request.user.id)
        serializer = HivesSerializer(hives, many=True)
        r = HIVE_RETURN_TEMPLATE.copy() 
        r['user'] = request.user.id
        r['data']['items'] = serializer.data
        r['data']['totalItems'] = len(hives)
        return Response(r)

    def post(self, request, format=None):
        # data = request.data
        data = JSONParser().parse(request)
        """ print(type(request.user), request.user)
        print(type(request.data), request.data)
        data = {**(request.data), "user": request.user.id} """
        data["user"] = request.user.id
        serializer = HivesSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HivesViewDetail(APIView):
    ''' PUT, DELETE require pk in url /hives/<pk>/'''
    
    def get_object(self, pk):
        try:
            return Hives.objects.get(pk=pk)
        except Hives.DoesNotExist:
            raise Http404

    def put(self, request, pk, format=None):
        # print('Hello from /hive PUT %s' % pk)
        hive = self.get_object(pk)
        serializer = HivesSerializer(hive, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        hive = self.get_object(pk)
        hive.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


""" class HiveGroupsCRUD(APIView):
    ''' return a list of Hives groups which belongs to the user.'''
    
    def get_object(self, pk):
        try:
            return Hives.objects.get(pk=pk)
        except Hives.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        hive = self.get_object(pk)
        serializer = HivesSerializer(hive)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = HivesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        hive = self.get_object(pk)
        serializer = HivesSerializer(hive, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        hive = self.get_object(pk)
        hive.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
 """

""" class UserInfo(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()
    def get(sekf, request):
        return Response({ "isAuthenticated": request.user.is_authenticated, "name": request.user.username },
        status=status.HTTP_200_OK) """

