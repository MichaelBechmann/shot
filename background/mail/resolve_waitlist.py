if 0: 
    from gluon.languages import translator as T
    from gluon import *
    import gluon
    global request
    global response
    global session
    global shotdb

from shotdbutil import *
from shotmail import *
from time import *
import datetime

'''
This function goes through the sorted wait list and assigns sale numbers as long as there are numbers left.
An email is sent to each person who got a sale number this way.
'''

f = open('applications/' + config.appname + '/background/mail/resolve_waitlist.log', 'w', 1)
    
f.write('shotpath: ' + config.shotpath + '\n')
f.write('start resolving wait list:\n')

wl = WaitList(shotdb)
    
count = 0
for row in wl.rows_sorted:
    if Numbers(shotdb, wl.eid).get_b_numbers_free():
        count += 1  
        t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        if row.sale == None or not row.sale > 0:
            sid = NumberAssignment(shotdb, row.person).assign_number()
            if sid > 0:
                shotdb(shotdb.wait.id == row.id).update(sale = sid)
                shotdb.commit()
                NumberFromWaitlistMail(shotdb, row.person).send()
                f.write(str(count) + '\t' + t + '\t' + 'wait id ' + str(row.id) + '\t' + 'sale id: ' + str(sid) + '\t' + row.person.name + ', ' + row.person.forename + '\n')
                sleep(30)
            else:
                f.write(str(count) + '\t' + t + '\t' + 'wait id ' + str(row.id) + '\t' + row.person.name + ', ' + row.person.forename + ': Something is wrong! Sale number could not be assigned!\n')  
        else:
            f.write(str(count) + '\t' + t + '\t' + 'wait id ' + str(row.id) + '\t' + row.person.name + ', ' + row.person.forename + ' has sale number already.\n')  
    else:
        f.write('There are no free numbers left any more. No further actions are done.\n') 
        break     
                
f.write('all done.')  
f.close()