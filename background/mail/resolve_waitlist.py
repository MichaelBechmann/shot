if 0: 
    from gluon.languages import translator as T
    from gluon import *
    import gluon
    global request
    global response
    global session
    global shotdb

from shotdbutil import *
from shotmail import NumberFromWaitlistMail, NumberFromWaitlistMailSuccession
from time import sleep
from shotlogging import logger_bg
import sys

'''
This function goes through the sorted wait list and assigns sale numbers as long as there are numbers left.
An email is sent to each person who got a sale number this way.
'''

logger_bg.info('start with script "resolve_waitlist" ...')
logger_bg.info('command line arguments: ' + str(sys.argv))

# extract limit from parameter
if len(sys.argv) > 1:
    limit = int(sys.argv[1])
else:
    limit = 0

b_log_account_number_mail       = True
b_log_account_number_mail_succ  = True

try:
    wl = WaitList(shotdb)
    count = 0
    for row in wl.get_sorted(limit):
        if Numbers(shotdb, wl.eid).b_numbers_available():
            if count > 0:
                # wait before sending next mail
                sleep(10)
            
            count += 1
            msg = '#%d, id: %d\t%s, %s' % (count, row.id, row.person.name, row.person.forename)
            sid = NumberAssignment(shotdb, row.person).assign_number()
            if sid > 0:
                shotdb.commit()

                msg = msg + ', sale id: ' + str(sid)
                
                if row.denial_sent:
                    m = NumberFromWaitlistMailSuccession(shotdb, row.person)
                    m.send()
                    if b_log_account_number_mail_succ:
                        # output account settings
                        logger_bg.info('The following account settings are used (succession from wait list):')
                        logger_bg.info('server: %s, sender: %s' % (m.account.server, m.account.sender))
                        b_log_account_number_mail_succ = False
                    
                    msg = msg + ' (succession)'
                else:
                    m = NumberFromWaitlistMail(shotdb, row.person)
                    m.send()
                    if b_log_account_number_mail:
                        # output account settings
                        logger_bg.info('The following account settings are used (number from wait list):')
                        logger_bg.info('server: %s, sender: %s' % (m.account.server, m.account.sender))
                        b_log_account_number_mail = False
                
                logger_bg.info(msg)
            else:
                logger_bg.info(msg + 'Something is wrong! Sale number could not be assigned!')
        else:
            logger_bg.info('There are no numbers available any more. No further actions are done.') 
            break
    logger_bg.info('all done.')
    
except Exception, e:
    logger_bg.error(str(e)) 
                