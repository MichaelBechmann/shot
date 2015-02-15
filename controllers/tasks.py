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
    global auth

from shotdbutil import *
import subprocess

@auth.requires_membership('task executor')
def start():
    
    # dummy line: prevent accidental start of first task by pressing ENTER, fix with issue #79
    
    #            id label/description                                task script                                        parameter,  test button
    tasklist = ((99, 'dummy',  'dummy',         False,      False),
                (0, 'Send invitation mail to all former vendors.',  '/background/mail/send_invitation_mail.py',         False,      False),
                (1, 'Resolve waitlist and send sale number mail.',  '/background/mail/resolve_waitlist.py',             True,       True),
                (2, 'Send waitlist denial mail.',                   '/background/mail/send_waitlist_denial_mail.py',    True,       True),
                (3, 'Send reminder mail to all participants.',      '/background/mail/send_reminder_mail.py',           False,      True),
                (4, 'Backup database',                              '/background/backup/backup_db.py',                  False,      False)
                )
    rows = [TR(t[1],
               SPAN('limit: ', INPUT(_type = 'text', requires = IS_EMPTY_OR(IS_INT_IN_RANGE(-10000, 10000, error_message = 'Not an integer!')), _name = 'param_' + str(t[0]), _size = 2)) if t[3] else TD(''),
               INPUT(_type = 'submit', _name = 'test_'  + str(t[0]), _value = T('test')) if t[4] else TD(''),
               INPUT(_type = 'submit', _name = str(t[0]), _value = T('go!'), _class = "irreversible")
               ) for t in tasklist]
    form = FORM(TABLE(*rows, _class = 'caution'))

    if form.validate():
        
        # extract parameter
        param = 0
        for t in tasklist:
            si = str(t[0])
            st = 'test_'  + si
            sp = 'param_' + si
            if t[3] and ((st in request.vars) or (si in request.vars)):
                p = request.vars[sp]
                if p:
                    param = int(p)
                break
        
        rows_out = None
        if 'test_1' in request.vars.iterkeys():
            rows_out = WaitList(shotdb).get_sorted(param)
            columns = ['wait.id', 'wait.person']
    
        elif 'test_2' in request.vars.iterkeys():
            rows_out = WaitList(shotdb).get_denials(param)
            columns = ['wait.id', 'wait.person']
            
        elif 'test_3' in request.vars.iterkeys():
            rows_out = Reminder(shotdb).get_all_persons()
            columns = ['person.id', 'person.name', 'person.forename']
    
        if rows_out != None:
            return DIV(SPAN('Number of mails: %d' % len(rows_out)), SQLTABLE(rows_out, columns = columns, headers='fieldname:capitalize'))
    
        if config.enable_tasks:
            for t in tasklist:
                idx = t[0]
                if not idx == 99 and str(idx) in request.vars:
                    #subprocess.Popen(['python', 'web2py.py', '-S', config.appname , '-M', '-R', 'applications/' + config.appname + t[2], '-A', str(param)])
                    #redirect(URL('final'))
                    break
           

    return dict(form = form)


@auth.requires_membership('task executor')
def final():
    return dict()


@auth.requires_membership('task executor')
def send_invitation_mail():
    '''
    There seems to be a problem with subprocess in web2py
    see: https://groups.google.com/forum/?fromgroups=#!topic/web2py/zOB0B1xO93Y
    os.system works fine, but waits for the job to finish.
    '''
    subprocess.Popen(['python', 'web2py.py', '-S', config.appname , '-M', '-R', 'applications/' + config.appname + '/background/mail/send_invitation_mail.py'])
    return('Sending mail. Please be patient!')


@auth.requires_membership('task executor')
def resolve_waitlist():
    '''
    This function resolves the waitlist, i.e.:
        - assigns sale numbers
        - sends number mails
    '''
    b_go = False
    if (len(request.args) > 0 and request.args[0] == 'go'):
        b_go = True

    if b_go:
        subprocess.Popen(['python', 'web2py.py', '-S', config.appname , '-M', '-R', 'applications/' + config.appname + '/background/mail/resolve_waitlist.py'])
        return 'wait list has been resolved, now sending number mail ...'
    else: 
        return str(SQLTABLE(WaitList(shotdb).rows_sorted))
        
        
@auth.requires_membership('task executor')
def waitlist_denial():
    '''
    This function sends denial mails to persons on the waitlist who got no sale number.
    '''
    subprocess.Popen(['python', 'web2py.py', '-S', config.appname , '-M', '-R', 'applications/' + config.appname + '/background/mail/send_waitlist_denial_mail.py'])
    return('sending mail ...')


@auth.requires_membership('task executor')
def send_helper_mail():
    '''
    This sends a reminder to all helpers.
    '''
    subprocess.Popen(['python', 'web2py.py', '-S', config.appname , '-M', '-R', 'applications/' + config.appname + '/background/mail/send_helper_mail.py'])
    return('sending helper mail ...')


