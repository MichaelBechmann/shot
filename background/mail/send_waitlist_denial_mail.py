if 0: 
    from gluon.languages import translator as T
    from gluon import *
    import gluon
    global request
    global response
    global session
    global shotdb

from shotdbutil import WaitList, Numbers
from shotmail import WaitDenialMail
from time import sleep
from shotlogging import logger_bg

'''
This function goes through the sorted wait list after its resolution. 
An denial email is sent to each person who did not get a sale number.
'''

logger_bg.info('start with script "send_waitlist_denial_mail.py" ...')

try:
    wl = WaitList(shotdb)
    if Numbers(shotdb, wl.eid).b_numbers_available():
        logger_bg.warning('There are still sale numbers available! Nothing is done.')
        
    else:
        count = 0
        for row in wl.rows_denial:
            count += 1
            shotdb(shotdb.wait.id == row.id).update(denial_sent = True)
            shotdb.commit()
            WaitDenialMail(shotdb, row.person).send()
            logger_bg.info('#%d, id: %d\t%s, %s' % (count, row.id, row.person.name, row.person.forename))
            sleep(30)
        logger_bg.info('all done.')

except Exception, e:
    logger_bg.error(str(e)) 