if 0: 
    from gluon.languages import translator as T
    from gluon import *
    import gluon
    global request
    global response
    global session
    global shotdb

from shotdbutil import Reminder
from shotmail import ReminderMail
from time import sleep
from shotlogging import logger_bg

'''
This function sends a special reminder email to each person which helps at the current event
'''

logger_bg.info('start with script "send_reminder_mail" ...')

try:
    count = 0
    for row in Reminder(shotdb).get_all_persons():
        m = ReminderMail(shotdb, row.id, mass = True)
        if count == 0:
            # output account settings
            logger_bg.info('The following account settings are used:')
            logger_bg.info('server: %s, sender: %s' % (m.account.server, m.account.sender))
        else:
            sleep(5)
            
        m.send()
        count += 1 
        logger_bg.info('#%d, id: %d\t%s, %s   (%s)' % (count, row.id, row.name, row.forename, str(ReminderMail)))
        
    logger_bg.info('all done.')

except Exception, e:
    logger_bg.error(str(e)) 