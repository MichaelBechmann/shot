if 0: 
    from gluon.languages import translator as T
    from gluon import *
    import gluon
    global request
    global response
    global session
    global shotdb
    global auth

from shotdbutil import Reminder
from shotmail import AfterMarketMail
from time import sleep
from shotlogging import logger_bg
from shotconfig import *

'''
This function sends an email with thanks and after market information to each person who partizipates in the current event.
Note: The receivers are the same as for the reminder email.
'''

logger_bg.info('start with script "send_after_market_mail" ...')

try:
    count = 0
    for row in Reminder(shotdb).get_all_persons():
        m = AfterMarketMail(auth, row.person.id, mass = True)
        m.set_error_handling_parameters(number_attempts = config.bulk_email_number_attempts,
                                        delay_next_attempt = config.bulk_email_number_delay_next_attempt)
        if count == 0:
            # output account settings
            logger_bg.info('The following account settings are used:')
            logger_bg.info('server: %s, sender: %s' % (m.account.server, m.account.sender))
        else:
            sleep(float(config.bulk_email_delay))
            
        m.send()
        count += 1 
        logger_bg.info('#%d, id: %d\t%s, %s' % (count, row.person.id, row.person.name, row.person.forename))
        if m.errors:
            logger_bg.warning('Intermediate errors occurred:')
            for error in m.errors:
                logger_bg.warning(error)
        
    logger_bg.info('all done.')

except Exception, e:
    logger_bg.error(str(e)) 