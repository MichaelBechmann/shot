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
This function loops through all persons in the database.
For each person which has not disabled general mail the invitation mail is sent.
'''
f = open('applications/' + config.appname + '/background/mail/send_invitation_mail.log', 'w', 1)
    
f.write('shotpath: ' + config.shotpath + '\n')
f.write('start sending invitation mail:\n')

count = 0   
for row in shotdb(shotdb.person.id > 0).select():  
    if row.mail_enabled == None or row.mail_enabled == True:
        InvitationMail(shotdb, row.id).send() 
        t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        count += 1
        f.write(str(count) + '\t' + t + '\t' + str(row.id) + '\t' + row.name + ', ' + row.forename + '\n')
        sleep(30)
    
f.write('all done.')  
f.close()