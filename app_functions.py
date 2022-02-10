#!/usr/bin/python3

import logging
import os
import requests
import json
import pprint
import time
from datetime import datetime
import math



default_log_level = logging.INFO

def timestamp_convert(s):
    #from input format s="2021-09-18 21:20:12"
    #to output format timestamp_convert(s)
    #"2009-11-10T23:00:00Z"
    s=s.replace(" ", "T")
    s=s+"Z"
    return s

def str2dict(string):
    #converts a string already in dict format into a dictionary
    #string='{"Jan" : "January", "Feb" : "February", "Mar" : "March"}'
    import ast  
    return ast.literal_eval(string)

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