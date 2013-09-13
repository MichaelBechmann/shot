# -*- coding: utf-8 -*-
'''
creation: bechmann, Jul 23, 2013

This function copies all relevant data from old sqlite database to the new mysql database
'''

if 0: 
    from gluon.languages import translator as T
    from gluon import *
    import gluon
    global request
    global response
    global session
    global shotdbold
    global shotdb

from shotdbutil import *
import datetime
import logging


f = open('applications/' + config.appname + '/__etc/logs/background/debug.log', 'w', 1)
    
f.write('shotpath: ' + config.shotpath + '\n')
f.write('start conversion:\n')

try:
    # logging, according to http://docs.python.org/2/howto/logging.html
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # for log file
    filename = 'applications/%s/__etc/logs/background/%s__convert_database.log' % (config.appname, datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S"))
    fh = logging.FileHandler(filename = filename)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
except Exception, e:
    f.write(str(e))
    f.close()

tables = ('event', 'shift', 'donation', 'person', 'sale', 'bring',  'help',  'message', 'wait')

try:
    for tablename in tables:
        logger.info('Start with table %s' % str(tablename))
        
        t_source = shotdbold[tablename]
        t_target = shotdb[tablename]
        
        for row in shotdbold(t_source.id > 0).select():
            logger.info('start with %s, id %d' % (tablename, row.id))
            
            data = row.as_dict()
            
            # remove kindergarten
            if tablename == 'person':
                del data['kindergarten']
            if tablename == 'event':
                del data['number_ranges_kg']
            
            # remove virtual fields
            if tablename == 'shift' or tablename == 'donation':
                del data['actual_number']
                
            # remove empty relations
            if tablename == 'wait':
                if data['sale'] == 0:
                    del data['sale']
            
            t_target.update_or_insert(**data)
      
except Exception, e:
        f.write(str(e))
        f.close()
        logger.error(str(e))
        
        
else:
    logger.info('all done.')
    f.close()
    