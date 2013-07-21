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
This function sends a special reminder email to each person which helps at the current event
'''


f = open('applications/' + config.appname + '/background/mail/send_helper_mail.log', 'w', 1)
    
f.write('shotpath: ' + config.shotpath + '\n')
f.write('start sending helper mails:\n')

# get all persons which help
eid = Events(shotdb).current_id
query  = (shotdb.help.person == shotdb.person.id)
query &= (shotdb.help.shift  == shotdb.shift.id)
query &= (shotdb.shift.event == eid)

rows = shotdb(query).select(shotdb.person.id, shotdb.person.name, shotdb.person.forename, shotdb.shift.id)

# remove duplicates
helper_list = []
count = 0
count_total = 0
for row in rows:
    count_total += 1
    
    
    
    if row.person.id not in helper_list and row.shift.id != 32 and row.shift.id != 33:
        count += 1        
        helper_list.append(row.person.id)
        
        HelperMail(shotdb, row.person.id).send()
        
        t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        f.write(str(count) + '\t' + t + '\t' + 'person id ' + str(row.person.id) + '\t' + row.person.name + ', ' + row.person.forename + '\n')
        sleep(30)     


f.write('\ntotal help shifts: ' + str(count_total) + '\n')  
f.write('\nall done.')  
f.close()