    # -*- coding: utf-8 -*-
'''
creation: bechmann, Aug 10, 2013

This module contains controllers to start some special organisation tasks.
These controllers shall be accessible only for authorised roles.
'''

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


def start():
    if session.admin != True:
        return 'You are not authorized to access this page!'
    
    tasklist = ((0, 'Send invitation mail to all former vendors.',  '/background/mail/send_invitation_mail.py',         False),
                (1, 'Resolve waitlist and send sale number mail.',  '/background/mail/resolve_waitlist.py',             True),
                (2, 'Send waitlist denial mail.',                   '/background/mail/send_waitlist_denial_mail.py',    True),
                (3, 'Send reminder mail to all helpers.',           '/background/mail/send_helper_mail.py',             True),
                (4, 'Backup database',                              '/background/backup/backup_db.py',                  False)
                )
    rows = [TR(t[1], 
               INPUT(_type = 'submit', _class = 'button', _name = str(t[0]), _value = T('go!')),
               INPUT(_type = 'submit', _class = 'button', _name = 'test_' + str(t[0]), _value = T('test')) if t[3] else TD('')
               ) for t in tasklist]
    form = FORM(TABLE(*rows, _class = 'caution'))

    rows_out = None
    if 'test_1' in request.vars.iterkeys():
        rows_out = WaitList(shotdb).get_sorted()
        columns = ['wait.id', 'wait.person']

    elif 'test_2' in request.vars.iterkeys():
        rows_out = WaitList(shotdb).get_denials()
        columns = ['wait.id', 'wait.person']
        
    elif 'test_3' in request.vars.iterkeys():
        rows_out = HelperList(shotdb).rows_compact
        columns = ['person.id', 'help.person']

    if rows_out != None:
        return DIV(SPAN('Number of mails: %d' % len(rows_out)), SQLTABLE(rows_out, columns = columns, headers='fieldname:capitalize'))
                   

    if config.enable_tasks:
        for k in request.vars.iterkeys():
            subprocess.Popen(['python', 'web2py.py', '-S', config.appname , '-M', '-R', 'applications/' + config.appname + tasklist[int(k)][2]])
            redirect('final')
            break

    return dict(form = form)


def final():
    return dict()

def send_invitation_mail():
    '''
    There seems to be a problem with subprocess in web2py
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
    
    

