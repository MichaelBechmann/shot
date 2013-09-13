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

'''
This function goes through the sorted wait list and assigns sale numbers as long as there are numbers left.
An email is sent to each person who got a sale number this way.
'''

logger_bg.info('start with script "resolve_waitlist" ...')

try:
    wl = WaitList(shotdb)
    count = 0
    for row in wl.rows_sorted:
        if Numbers(shotdb, wl.eid).b_numbers_available():
            count += 1
            msg = '#%d, id: %d\t%s, %s' % (count, row.id, row.person.name, row.person.forename)
            if row.sale == None or not row.sale > 0:
                sid = NumberAssignment(shotdb, row.person).assign_number()
                if sid > 0:
                    shotdb(shotdb.wait.id == row.id).update(sale = sid)
                    shotdb.commit()
                    
                    msg = msg + ', sale id: ' + str(sid)
                    
                    if row.denial_sent:
                        NumberFromWaitlistMailSuccession(shotdb, row.person).send()
                        msg = msg + ' (succession)'
                    else:
                        NumberFromWaitlistMail(shotdb, row.person).send()
                    
                    logger_bg.info(msg)
                    sleep(30)
                else:
                    logger_bg.info(msg + 'Something is wrong! Sale number could not be assigned!')
            else:
                logger_bg.info(msg + ' has sale number already.')
        else:
            logger_bg.info('There are no numbers available any more. No further actions are done.') 
            break
    logger_bg.info('all done.')
    
except Exception, e:
    logger_bg.error(str(e)) 
                