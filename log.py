from __future__ import with_statement 
import glob
import logging
import logging.handlers
import sys, os
#http://pymotw.com/2/logging/
#https://docs.python.org/2/howto/logging-cookbook.html

username='test'
LOG_PATH = '/home/'+username+'/'
#LOG_PATH = '/var/log/'
#putting it in '/var/log/' would mean trouble for multi-user systems, and
#you'd manually create and chmod the file accordingly for your each user

llevel=logging.DEBUG

#create logger
def create(logname):
	global llevel
	LOG_FILENAME= LOG_PATH + logname + '.log'
	if os.path.isfile(LOG_FILENAME):
		os.remove(LOG_FILENAME)#remove the old one if it exists

	logging.basicConfig(filename=LOG_FILENAME,
						level=llevel,
						format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
						datefmt='%m-%d %H:%M:%S'
						)



def dunno():					
	f = open(LOG_FILENAME, 'rt')
	try:
		body = f.read()
	finally:
		f.close()

	print('FILE:')
	print(body)


LEVELS = { 'debug':logging.DEBUG,
            'info':logging.INFO,
            'warning':logging.WARNING,
            'error':logging.ERROR,
            'critical':logging.CRITICAL,
            }

if len(sys.argv) > 1:
    level_name = sys.argv[1]
    level = LEVELS.get(level_name, logging.NOTSET)
    logging.basicConfig(level=level)

def testlog():	
	logging.debug('This is a debug message')
	logging.info('This is an info message')
	logging.warning('This is a warning message')
	logging.error('This is an error message')
	logging.critical('This is a critical error message')
	


def verbose(var):
    global llevel
    if var:
        llevel=logging.DEBUG
    else :
        llevel=logging.WARNING
