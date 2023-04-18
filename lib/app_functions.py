#!/usr/bin/env python3
def timestamp_convert(string):
    #from input format s="2021-09-18 21:20:12"
    #to output format timestamp_convert(string)
    #"2009-11-10T23:00:00Z"
    string=string.replace(" ", "T")
    string=string+"Z"
    return string


def time_now():
        # datetime object containing current date and time
    now = datetime.utcnow() #.now()
    #print("now =", now)
    # dd-mm-YY H:M:S
    dt_string = now.strftime("%d-%m-%YT%H:%M:%SZ")
    #print("date and time =", dt_string)
    return dt_string

def str2dict(string):
    #converts a string already in dict format into a dictionary
    #string='{"Jan" : "January", "Feb" : "February", "Mar" : "March"}'
    import ast  
    return ast.literal_eval(string)

######################
