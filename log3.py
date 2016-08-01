#!/usr/bin/python3
#https://docs.python.org/2.6/library/logging.html


import logging
import logging.handlers


def setup(lfile, level):
    #levels:
    #logging.DEBUG,
    #logging.INFO
    #logging.WARNING
    #logging.ERROR
    #logging.CRITICAL
    
    #log handle
    mylog = logging.getLogger(lfile)
    mylog.setLevel(level)
    
    
    #beef up logging by adding safeguards
    handler = logging.handlers.RotatingFileHandler(lfile, maxBytes=1000000, backupCount=3)# approx. 1MB per file
    handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(process)d]: %(levelname)s %(message)s'))
            #    '%(asctime)s %(pathname)s [%(process)d]: %(levelname)s %(message)s'))
            
    mylog.addHandler(handler)

    return mylog
