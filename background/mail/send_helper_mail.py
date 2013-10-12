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
        m = HelperMail(shotdb, row.person.id, mass = True)
        if count == 0:
            # output account settings
            logger_bg.info('The following account settings are used:')
            logger_bg.info('server: %s, sender: %s' % (m.account.server, m.account.sender))
        else:
            sleep(1)
            
        m.send()
        count += 1 
        logger_bg.info('#%d, id: %d\t%s, %s   (%s)' % (count, row.person.id, row.person.name, row.person.forename, str(HelperMail)))
        
    logger_bg.info('all done.')

except Exception, e:
    logger_bg.error(str(e)) 