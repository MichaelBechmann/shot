# -*- coding: utf-8 -*-
'''
This function loops through all persons in the database.
For each person which has not disabled general mail the invitation mail is sent.
'''

if 0: 
    from gluon import *
    import gluon
    global request
    global response
    global session
    global shotdb
    global auth

from shotmail import InvitationMail
from shotlogging import logger_bg
from shotconfig import *
from time import sleep

logger_bg.info('start with script "send_invitation_mail" ...')

try:
    count = 0   
    for row in shotdb(shotdb.person.id > 0).select():  
        if row.mail_enabled == None or row.mail_enabled == True:
            
            m = InvitationMail(auth, row.id, mass = True)
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
            logger_bg.info('#%d, id: %d\t%s, %s' % (count, row.id, row.name, row.forename))
            if m.errors:
                logger_bg.warning('Intermediate errors occurred:')
                for error in m.errors:
                    logger_bg.warning(error)
        
    logger_bg.info('all done.')

except Exception, e:
    logger_bg.error(str(e)) 