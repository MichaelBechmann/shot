# -*- coding: utf-8 -*-
'''
creation: bechmann, Aug 22, 2013

This background task is to regularize person names, street names etc. according to the same rules applied at form level.
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
    
from shotlogging import logger_bg
from miscutils import regularizeName

logger_bg.info('start with script "resolve_waitlist" ...')

try:
    count = 0
    for row in shotdb(shotdb.person.id > 0).select():
        count += 1
        msg = '#%d, id: %d\t%s, %s' % (count, row.id, row.name, row.forename)
        logger_bg.info(msg)
        
        new = {
               'forename' : regularizeName(row.forename),
               'name'     : regularizeName(row.name),
               'place'    : regularizeName(row.place),
               'street'   : regularizeName(row.street)
        }
    
        shotdb(shotdb.person.id == row.id).update(**new)
    
        shotdb.commit()
    
    
    logger_bg.info('all done.')
    
except Exception, e:
    logger_bg.error(str(e)) 