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
This function goes through the sorted wait list after its resolution. 
An denial email is sent to each person who did not get a sale number.
'''

f = open('applications/' + config.appname + '/background/mail/send_waitlist_denial_mail.log', 'w', 1)
    
f.write('shotpath: ' + config.shotpath + '\n')
f.write('start resolving wait list:\n')

wl = WaitList(shotdb)
    
count = 0
for row in wl.rows_sorted:
    if row.sale == None:
        count += 1
        shotdb(shotdb.wait.id == row.id).update(sale = 0)
        shotdb.commit()
        WaitDenialMail(shotdb, row.person).send()
        t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        f.write(str(count) + '\t' + t + '\t' + 'wait id ' + str(row.id) + '\t' + row.person.name + ', ' + row.person.forename + '\n')
        sleep(30)         
                
f.write('all done.')  
f.close()