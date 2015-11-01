if 0: 
    from gluon.languages import translator as T
    from gluon import *
    import gluon
    global request
    global response
    global session
    global shotdb
    global auth

from shotdbutil import *
from shotmail import NumberFromWaitlistMail, NumberFromWaitlistMailSuccession
from time import sleep
from shotlogging import logger_bg
from shotconfig import *
import sys

'''
This function goes through the sorted wait list and assigns sale numbers as long as there are numbers left.
An email is sent to each person who got a sale number this way.
'''

logger_bg.info('start with script "resolve_waitlist" ...')
logger_bg.info('command line arguments: ' + str(sys.argv))

# extract limit from parameter
# The code below relies on a matching implementation of the task parameterization in the controller function.
limit          = int(sys.argv[1])
option_helpers = sys.argv[2]
logger_bg.info('    limit = %d' % limit)
logger_bg.info('    option_helpers = %s' % option_helpers)


b_log_account_number_mail       = True
b_log_account_number_mail_succ  = True

if option_helpers == 'use':
    b_option_use_helper_numbers = True
else:
    b_option_use_helper_numbers = False

try:
    wl = WaitList(shotdb)
    count = 0
    for row in wl.get_sorted(limit, b_option_use_helper_numbers):
        if Numbers(shotdb, wl.eid).b_numbers_available():
            if count > 0:
                # wait before sending next mail
                sleep(float(config.bulk_email_delay))
            
            count += 1
            logger_bg.debug('Start with row number %d' % count)
            
            msg = '#%d, id: %d\t%s, %s' % (count, row.person.id, row.person.name, row.person.forename)
            sid = NumberAssignment(shotdb, row.person.id, b_option_use_helper_numbers).assign_number()
            
            logger_bg.debug('Sale number has been determined successfully! sid = %d' %sid)
            
            if sid > 0:
                shotdb.commit()
                logger_bg.debug('Database has been commited.')
                
                msg = msg + ', sale id: ' + str(sid)
                
                if row.wait.denial_sent:
                    m = NumberFromWaitlistMailSuccession(auth, row.person.id, mass = True)
                    m.set_error_handling_parameters(number_attempts = config.bulk_email_number_attempts,
                                                    delay_next_attempt = config.bulk_email_number_delay_next_attempt)
                    m.send()
                    if m.errors:
                        logger_bg.warning('Intermediate errors occurred:')
                        for error in m.errors:
                            logger_bg.warning(error)
                    if b_log_account_number_mail_succ:
                        # output account settings
                        logger_bg.info('The following account settings are used (succession from wait list):')
                        logger_bg.info('server: %s, sender: %s' % (m.account.server, m.account.sender))
                        b_log_account_number_mail_succ = False
                    
                    msg = msg + ' (succession)'
                else:
                    m = NumberFromWaitlistMail(auth, row.person.id, mass = True)
                    m.set_error_handling_parameters(number_attempts = config.bulk_email_number_attempts,
                                                    delay_next_attempt = config.bulk_email_number_delay_next_attempt)
                    m.send()
                    if m.errors:
                        logger_bg.warning('Intermediate errors occurred:')
                        for error in m.errors:
                            logger_bg.warning(error)
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
                