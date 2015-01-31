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
import sys

'''
This function goes through the sorted wait list after its resolution. 
An denial email is sent to each person who did not get a sale number.
'''

logger_bg.info('start with script "send_waitlist_denial_mail.py" ...')
logger_bg.info('command line arguments: ' + str(sys.argv))

# extract limit from parameter
if len(sys.argv) > 1:
    limit = int(sys.argv[1])
else:
    limit = 0
try:
    wl = WaitList(shotdb)
    if Numbers(shotdb, wl.eid).b_numbers_available():
        logger_bg.warning('There are still sale numbers available! Nothing is done.')
        
    else:
        count = 0
        for row in wl.get_denials(limit):
            
            shotdb(shotdb.wait.id == row.id).update(denial_sent = True)
            shotdb.commit()
            
            m = WaitDenialMail(shotdb, row.person, mass = True)
            if count == 0:
                # output account settings
                logger_bg.info('The following account settings are used:')
                logger_bg.info('server: %s, sender: %s' % (m.account.server, m.account.sender))
            else:
                # wait before sending next mail
                sleep(10)          
            
            m.send()
            count += 1
            logger_bg.info('#%d, id: %d\t%s, %s' % (count, row.id, row.person.name, row.person.forename))
        logger_bg.info('all done.')

except Exception, e:
    logger_bg.error(str(e)) 