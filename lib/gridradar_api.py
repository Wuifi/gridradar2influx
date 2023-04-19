#!/usr/bin/python3

import logging
import os
import requests
import json
import pprint
import time
from datetime import datetime, timedelta
import math

from lib.app_functions import *
#######


def metric_request_freeAPI(metric,metrics_dict):
    settings = metrics_dict[metric]
    #calculate metric specific timerange    
    #starttime = "2021-05-26T02:36:17.3Z"
    #endtime = "2021-05-26T02:36:17.6Z"
    # Minimum Data Delay: 30s
    endtime = (datetime.utcnow() - timedelta(seconds=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    #print(endtime)
    starttime = (datetime.utcnow() - timedelta(hours=settings['timerange'])).strftime("%Y-%m-%dT%H:%M:%SZ")
    #print(starttime)
    request = {
            "metric": metric,
            #"func":"difference", #"mean",
            #"pmus": location,   
            #"from": starttime, 
            #"to": endtime, 
            "aggr": settings['aggr'], 
            "format": "json",
            "ts": "rfc3339"
        }
    return request

def metric_request_individualAPI(metric,metrics_dict,location):
    settings = metrics_dict[metric]
    #calculate metric specific timerange    
    #starttime = "2021-05-26T02:36:17.3Z"
    #endtime = "2021-05-26T02:36:17.6Z"
    # Minimum Data Delay: 30s
    endtime = (datetime.utcnow() - timedelta(seconds=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    #print(endtime)
    starttime = (datetime.utcnow() - timedelta(hours=settings['timerange'])).strftime("%Y-%m-%dT%H:%M:%SZ")
    #print(starttime)
    request = {
            "metric": metric,
            #"func":"difference", #"mean",
            "pmus": location,   
            "from": starttime, 
            "to": endtime, 
            "aggr": settings['aggr'], 
            "format": "json",
            "ts": "rfc3339"
        }
    return request


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

def convert_dataset(metric,response_dict,location):
    outDB=[]
    messdaten=response_dict[0]
        
    for values in messdaten['datapoints']:
        #print(type(values[0]))
        try:
            if values[0] is not None:#math.isnan(values[0])==False:
                outDB_new = {'measurement': metric,
                             'tags': {'location': location},
                             'fields': {'value': values[0]},
                             #'fields': {messdaten['target']: values[0]},
                             'time':timestamp_convert(values[1])}
                outDB.append(outDB_new)
        except Exception as e:
            logging.error(str(e),str(values))
            #print(values)
    return(outDB)


def gridradar_API_monitor(metric,response,location,query_timer,influxdb_timer):
    outDB=[]
    try:
        logging.debug("gridradar-API - response: %s", response.status_code)
        outDB_new = {'measurement': metric,
                    'tags': {'location': location},
                    'fields': {'status_code': response.status_code,
                               'query_timer':query_timer,'influxdb_timer':influxdb_timer},
                    #'fields': {messdaten['target']: values[0]},
                    'time':timestamp_convert((datetime.utcnow()).strftime("%Y-%m-%dT%H:%M:%S"))}
        outDB.append(outDB_new)
    except Exception as e:
        logging.error(str(e))
    return(outDB)



