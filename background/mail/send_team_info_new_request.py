if 0:
    from gluon.languages import translator as T
    from gluon import *
    import gluon
    global request
    global response
    global session
    global shotdb
    global auth

from time import sleep
from shotlogging import logger_bg
from shotconfig import *
from shotdbutil import Team
from shotmail import AppropriationRequestTeamInfoMail

import sys

'''
This function is invoked immediately after a new appropriation request has been submitted.
It loops through all active team members for which this email type is configured. For each an email with a direct link to the new request is sent.
'''

logger_bg.info('start with script "send_team_info_new_request.py" ...')
logger_bg.info('command line arguments: ' + str(sys.argv))


try:
    # extract id of the appropriation request from parameters
    if len(sys.argv) > 1:
        aid = int(sys.argv[1])
    else:
        aid = None

    if not aid:
        logger_bg.info('There is no proper request ID, abort!')
    else:
        logger_bg.info('ID of the appropriation request: %d' % aid)

        count = 0
        rows = Team(shotdb).get_all_members_for_info_email()
        logger_bg.info('Number of emails to be sent: %d' % len(rows))
        for row in rows:
            m = AppropriationRequestTeamInfoMail(auth, row.auth_user.id, aid)
            m.set_error_handling_parameters(number_attempts = config.bulk_email_number_attempts, delay_next_attempt = config.bulk_email_number_delay_next_attempt)
            if count == 0:
                # output account settings
                logger_bg.info('The following account settings are used:')
                logger_bg.info('server: %s, sender: %s' % (m.account.server, m.account.sender))
            else:
                sleep(float(config.bulk_email_delay))

            m.send()
            count += 1
            logger_bg.info('#%d, id: %d\t%s, %s' % (count, row.auth_user.id, row.auth_user.last_name, row.auth_user.first_name))

        logger_bg.info('all done.')

except Exception, e:
    logger_bg.error(str(e))
    logger_bg.info('script aborted!')
