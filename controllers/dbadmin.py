# -*- coding: utf-8 -*-
# Static analyzer import helpers: (STATIC_IMPORT_MARK)
if 0: 
    from gluon.languages import translator as T
    from gluon import *
    import gluon
    global request
    global response
    global session
    global shotdb

from shotdbutil import *
import subprocess
 
def _config_event_3():
    '''
    This function adds the configuration for the third event.
    '''
    if session.admin != True:
        return 'no way!'
    
    # add event
    shotdb.event.update_or_insert(label = 'Frühjahr 2013', active = False, number_ranges = '200-250, 300-350, 400-450', number_ranges_kg = '500-550')
    
    # add donations
    shotdb.donation.update_or_insert(event = 3, item = 'Kuchen',     target_number = 30, enable_notes = True)
    shotdb.donation.update_or_insert(event = 3, item = 'Waffelteig', target_number = 10, enable_notes = False)
#    
    # add shifts<br />
    shotdb.shift.update_or_insert(event = 3, activity = 'Sortieren',    day = 'Freitag', time = '14:30 - 17 Uhr', target_number = 20, display = 'a1')
    shotdb.shift.update_or_insert(event = 3, activity = 'Küche',        day = 'Samstag', time = '8:30 - 11 Uhr',  target_number = 3,  display = 'a2')
    shotdb.shift.update_or_insert(event = 3, activity = 'Auflegen',     day = 'Samstag', time = '9 - 11:30 Uhr',  target_number = 6,  display = 'b1')
    shotdb.shift.update_or_insert(event = 3, activity = 'Kasse',        day = 'Samstag', time = '8:30 - 11 Uhr',  target_number = 4,  display = 'a2')
    shotdb.shift.update_or_insert(event = 3, activity = 'Kuchentheke',  day = 'Samstag', time = '9 - 11:30 Uhr',  target_number = 2,  display = 'b1')    
    shotdb.shift.update_or_insert(event = 3, activity = 'Waffelstand',  day = 'Samstag', time = '9 - 11:30 Uhr',  target_number = 2,  display = 'b1')
    shotdb.shift.update_or_insert(event = 3, activity = 'Küche',        day = 'Samstag', time = '12 - 14:30 Uhr', target_number = 3,  display = 'b2')    
    shotdb.shift.update_or_insert(event = 3, activity = 'Rücksortieren',day = 'Samstag', time = '12 - 14:30 Uhr', target_number = 25, display = 'b2')
    shotdb.shift.update_or_insert(event = 3, activity = 'Ich helfe nach Bedarf (nach Rücksprache).',       day = 'Samstag', time = 'flexibel', target_number = 15, display = 'c1')    
    shotdb.shift.update_or_insert(event = 3, activity = 'Ich bin Elternbeirat und helfe wie besprochen.',  day = 'Samstag', time = 'flexibel', target_number = 12, display = 'c1')

    
    redirect(URL('config', 'config_event'))

def _renew_ver_codes():
    '''
    This function resets all verification codes and writes the old codes to the log.
    '''
    if session.admin != True:
        return 'no way!'
    
    for row in shotdb(shotdb.person.id > 0).select():
        c  = row.code
        id = row.id
        if c != None:
            l = 'code renewed by admin (was: ' + c + ')'
            Log(shotdb).person(id, l) 
            row.update_record(code = Ident().code)
            
    redirect(URL('staff', 'personlist')) 
    

def send_invitation_mail():
    ''' There seems to be a problem with subprocess in web2py
    see: https://groups.google.com/forum/?fromgroups=#!topic/web2py/zOB0B1xO93Y
    os.system works fine, but waits for the job to finish.
    '''
    if session.admin != True:
        return 'no way!'

    subprocess.Popen(['python', 'web2py.py', '-S', config.appname , '-M', '-R', 'applications/' + config.appname + '/background/mail/send_invitation_mail.py'])
    
    return('Sending mail. Please be patient!')


def resolve_waitlist():
    '''
    This function resolves the waitlist, i.e.:
        - assigns sale numbers
        - sends number mails
    '''
    if session.admin != True:
        return 'no way!'
    else:
        # action is allowed
        b_go = False
        if (len(request.args) > 0 and request.args[0] == 'go'):
            b_go = True

        if b_go:
            subprocess.Popen(['python', 'web2py.py', '-S', config.appname , '-M', '-R', 'applications/' + config.appname + '/background/mail/resolve_waitlist.py'])
            return 'wait list has been resolved, now sending number mail ...'
        else: 
            return str(SQLTABLE(WaitList(shotdb).rows_sorted))
    
def waitlist_denial():
    '''
    This function sends denial mails to persons on the waitlist who got no sale number.
    '''
    if session.admin != True:
        return 'no way!'
    else:
        # action is allowed
        subprocess.Popen(['python', 'web2py.py', '-S', config.appname , '-M', '-R', 'applications/' + config.appname + '/background/mail/send_waitlist_denial_mail.py'])
        return('sending mail ...')
    

def send_helper_mail():
    '''
    This sends a reminder to all helpers.
    '''
    if session.admin != True:
        return 'no way!'
    else:
        # action is allowed
        subprocess.Popen(['python', 'web2py.py', '-S', config.appname , '-M', '-R', 'applications/' + config.appname + '/background/mail/send_helper_mail.py'])
        return('sending helper mail ...')
    