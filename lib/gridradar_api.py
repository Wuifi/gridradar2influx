#!/usr/bin/python3
import requests
import json
import pprint
from datetime import datetime, timedelta

def metric_request_creator(metric,metrics_dict,querypmu):
    settings = metrics_dict[metric]
    #calculate metric specific timerange    
    #starttime = "2021-05-26T02:36:17.3Z"
    #endtime = "2021-05-26T02:36:17.6Z"
    endtime = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    #print(endtime)
    starttime = (datetime.utcnow() - timedelta(hours=settings['timerange'])).strftime("%Y-%m-%dT%H:%M:%SZ")
    #print(starttime)
    request = {
            "metric": metric,
            #"func":"difference", #"mean",
            "pmus": querypmu,   
            "from": starttime, 
            "to": endtime, 
            "aggr": settings['aggr'], 
            "format": "json",
            "ts": "rfc3339"
        }
    return request

##################
#### backlog #####
##################

#!/usr/bin/python3

import logging
import os
import requests
import json
import pprint
import time
from datetime import datetime
import math


#!/usr/bin/python3

import logging
import os
import requests
import json
import pprint
import time
from datetime import datetime
import math

from lib.app_functions import *
#######


default_log_level = logging.INFO


def getdatafromapi(url,token,request):
    response={}
    try:
        headers = {'Content-type': 'application/json',
                   'Authorization': 'Bearer '+token}
        ## Converting the Python dictionary to a JSON string
        json_request = json.dumps(request)
        ## Request execution and response reception
        response = requests.post(url, data=json_request, headers=headers)
    except Exception as e:
        logging.error(str(e))       
    return response

def convert_dataset(response_dict,config):
    outDB=[]
    try:
        logging.debug("gridradar-API - response: %s", response_dict)
        messdaten=response_dict[0]
        
        for values in messdaten['datapoints']:
            #print(type(values[0]))
            if math.isnan(values[0])==False:
                outDB_new = {'measurement': config.get('influxdb', 'measurement_name'),
                             'tags': {'location': config.get('influxdb', 'location')},
                             'fields': {messdaten['target']: values[0]},
                             'time':timestamp_convert(values[1])}
                outDB.append(outDB_new)
    except Exception as e:
        logging.error(str(e))
    return(outDB)


def grapi2influx(request,influxdb_client,config):
    logging.debug("gridradar-API config  - request: %s", request)
    out_influxDB=None
    duration=0
    start = int(datetime.utcnow().timestamp() * 1000)  
    try:
        # query data
        api_response=getdatafromapi(url=config.get('gridradar', 'url'),
                                    token=config.get('gridradar', 'token'),
                                    request=request)
        ## Converting the JSON response string to a Python dictionary
        result_dict = json.loads(api_response.content)        
        
        out_influxDB=convert_dataset(result_dict,config)
        #data = {
        #    "measurement": config.get('influxdb', 'measurement_name'),
        #    "time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        #    "fields": query_services(grapi_freq, services_to_query)
        #}
        logging.info("Writing data to InfluxDB")

        logging.debug("InfluxDB - measurement: %s" % out_influxDB) #.get("measurement")

        influxdb_client.write_points(out_influxDB,database= config.get('influxdb', 'database'),
                                    time_precision="ms",
                                    batch_size=10000,
                                    protocol='json')
    except Exception as e:
        logging.error("Failed to write to InfluxDB <%s>: %s" % (config.get('influxdb', 'host'), str(e)))
        logging.error("out_influxDB <%s>: ",  out_influxDB)

    duration = int(datetime.utcnow().timestamp() * 1000) - start
    logging.debug("Duration of requesting gridradar-API and sending data to InfluxDB: %0.3fs" % (duration / 1000)) 
    return duration







###################################################
#convert data to pandas df instead of influx
def gridradar2df(result_dict):
    import pandas as pd    
    try:
        messdaten=result_dict[0]
        df=pd.DataFrame.from_dict(messdaten['datapoints'])
        df['datetime']=pd.to_datetime(df[1])
        df[messdaten['target']]=df[0]
        df=df.drop([0,1], axis=1)
    except Exception as e:
        logging.error(str(e))
    return df

#######################################


def getdatafromapi(url,token,request):
    response={}
    try:
        headers = {'Content-type': 'application/json',
                   'Authorization': 'Bearer '+token}
        ## Converting the Python dictionary to a JSON string
        json_request = json.dumps(request)
        ## Request execution and response reception
        response = requests.post(url, data=json_request, headers=headers)
    except Exception as e:
        logging.error(str(e))       
    return response

def convert_dataset(response_dict,config):
    outDB=[]
    try:
        logging.debug("gridradar-API - response: %s", response_dict)
        messdaten=response_dict[0]
        
        for values in messdaten['datapoints']:
            #print(type(values[0]))
            if math.isnan(values[0])==False:
                outDB_new = {'measurement': config.get('influxdb', 'measurement_name'),
                             'tags': {'location': config.get('influxdb', 'location')},
                             'fields': {messdaten['target']: values[0]},
                             'time':timestamp_convert(values[1])}
                outDB.append(outDB_new)
    except Exception as e:
        logging.error(str(e))
    return(outDB)
########################
def convert_dataset2(response,measurement,location,ctr,uptime):
    pprint.pprint(response.status_code)
    logging.debug("API response status code: {}".format(response.status_code))
    #pprint.pprint(response.content)
    ## Converting the JSON response string to a Python dictionary
    result_dict = json.loads(response.content)
    #pprint.pprint(result_dict)
    messdaten=result_dict[0]

    outDB=[]
    for values in messdaten['datapoints']:
        #print(type(values[0]))
        if math.isnan(values[0])==False:
            outDB_new = {
                'measurement': measurement,
                'tags': {'location': location},
                'fields': {'value': values[0]},
                'time':timestamp_convert(values[1])
                }
            outDB.append(outDB_new)
    # add response state and time to data output for debugging purposes
    if measurement=='median_frequency':
        request_type=1
    elif measurement=='net_time':
        request_type=2
    else:
        request_type=0

    debug_info = {
        'measurement': 'API_stats',
        'tags': {'location': location},
        'fields': {
            'request_counter': ctr,
            'request_type':request_type,
            'stat_code':response.status_code,
            'uptime':int(uptime)},
            'time':time_now()}
    outDB.append(debug_info)
    #print(type(outDB))
    #outDB
    return(outDB)

###################################################
#convert data to publish to influx
def grapi2influx(request,influxdb_client,config):
    logging.debug("gridradar-API config  - request: %s", request)
    out_influxDB=None
    duration=0
    start = int(datetime.utcnow().timestamp() * 1000)  
    try:
        # query data
        api_response=getdatafromapi(url=config.get('gridradar', 'url'),
                                    token=config.get('gridradar', 'token'),
                                    request=request)
        ## Converting the JSON response string to a Python dictionary
        result_dict = json.loads(api_response.content)        
        
        out_influxDB=convert_dataset(result_dict,config)
        #data = {
        #    "measurement": config.get('influxdb', 'measurement_name'),
        #    "time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        #    "fields": query_services(grapi_freq, services_to_query)
        #}
        logging.info("Writing data to InfluxDB")

        logging.debug("InfluxDB - measurement: %s" % out_influxDB) #.get("measurement")

        influxdb_client.write_points(out_influxDB,database= config.get('influxdb', 'database'),
                                    time_precision="ms",
                                    batch_size=10000,
                                    protocol='json')
    except Exception as e:
        logging.error("Failed to write to InfluxDB <%s>: %s" % (config.get('influxdb', 'host'), str(e)))
        logging.error("out_influxDB <%s>: ",  out_influxDB)

    duration = int(datetime.utcnow().timestamp() * 1000) - start
    logging.debug("Duration of requesting gridradar-API and sending data to InfluxDB: %0.3fs" % (duration / 1000)) 
    return duration

def data_wrangler(url,request,measurement,location,headers,ctr,uptime):
    try:
        ctr=ctr+1
        ## Converting the Python dictionary to a JSON string
        json_request = json.dumps(request)
        ## Request execution and response reception
        response = requests.post(url, data=json_request, headers=headers)

        out_influxDB=convert_dataset(response,measurement,location,ctr,uptime)
        #pprint.pprint(out_influxDB)
        #logging.debug("Read initial value: {:.2f}".format(m3abs))
        
        client.write_points(out_influxDB, database='gridradar', time_precision='ms', batch_size=10000, protocol='json') 
        #print('gridradar2influx.py  --  request counter: ',str(ctr),'for ',measurement,' written to InfluxDB')
        logging.info('gridradar2influx.py  --  request counter: {} for {} written to InfluxDB'.format(ctr,measurement))
        #logging.info("Read initial value: {:.2f}".format(m3abs))
    except (ValueError, TypeError) as ex:
        #debug_str='"%s" cannot be converted to an float: %s' % (raw_content, ex)
        print(ex)
        
    return ctr

###################################################
#convert data to pandas df instead of influx
def gridradar2df(result_dict):
    import pandas as pd    
    try:
        messdaten=result_dict[0]
        df=pd.DataFrame.from_dict(messdaten['datapoints'])
        df['datetime']=pd.to_datetime(df[1])
        df[messdaten['target']]=df[0]
        df=df.drop([0,1], axis=1)
    except Exception as e:
        logging.error(str(e))
    return df

##############################




