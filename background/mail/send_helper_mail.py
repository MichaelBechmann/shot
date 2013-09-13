if 0: 
    from gluon.languages import translator as T
    from gluon import *
    import gluon
    global request
    global response
    global session
    global shotdb

from shotdbutil import HelperList
from shotmail import HelperMail
from time import sleep
from shotlogging import logger_bg

'''
This function sends a special reminder email to each person which helps at the current event
'''

logger_bg.info('start with script "send_helper_mail" ...')

try:
    hl = HelperList(shotdb)
    count = 0
    for row in hl.rows_compact:
        count += 1        
        HelperMail(shotdb, row.person.id).send()
        logger_bg.info('#%d, id: %d\t%s, %s' % (count, row.person.id, row.person.name, row.person.forename))
        sleep(30)
    logger_bg.info('all done.')

except Exception, e:
    logger_bg.error(str(e)) 