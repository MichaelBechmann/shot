# -*- coding: utf-8 -*-
'''
creation: bechmann, Aug 10, 2013

This module contains controllers to start some special organisation tasks.
These controllers shall be accessible only for authorised roles.
'''
from __builtin__ import True

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
    task_id = request.args(0)
    
    b_preview = False       
    if session.task_preview:
        b_preview = True
        session.task_preview = False
    
    
    form_rows = []
    if task_id == 'resolve_waitlist':
        form_rows.extend([TR(INPUT(_type = 'radio', _name = 'option_helper_numbers', _value = 'keep', _checked = 'checked'),
                                    TD('Es sollen ausschließlich freie Nummern neu vergeben werden, d.h. Helfernummern sollen reserviert bleiben.')
                            ),
                         TR(INPUT(_type = 'radio', _name = 'option_helper_numbers', _value = 'use'),
                                    TD('Es können auch Helfernummern neu vergeben werden.')
                            ),
                          TR(INPUT(_type = 'text', _name = 'limit', requires = IS_EMPTY_OR(IS_INT_IN_RANGE(0, 10000, error_message = 'Das ist kein sinnvolles Limit!'))),
                                    TD('Hier kann optional die maximale Anzahl der zu bearbeitenten Positionen angegeben werden.')
                            )
                          ])
    elif task_id == 'send_denial':
        form_rows.extend([TR(INPUT(_type = 'text', _name = 'limit', requires = IS_EMPTY_OR(IS_INT_IN_RANGE(-10000, 10000, error_message = 'Das ist kein sinnvolles Limit!'))),
                                    TD('Hier kann optional die maximale Anzahl der zu bearbeitenten Positionen spezifiziert werden.')
                            )
                          ])
    
    # generate task parameter form
    if config.enable_tasks and b_preview:
        btn_execute = INPUT(_type = 'submit', _name = 'execute', _value = 'Ausführen', _class = 'irreversible')
    else:
        btn_execute = SPAN('Ausführen', _class = 'btn_inactive')
        
    form_rows.append(TR(
                        TD(INPUT(_type = 'submit', _name = 'preview', _value = 'Vorschau')),
                        TD(btn_execute)
                        )
                     )
    form = FORM(TABLE(*form_rows, _id = 'task_form'))
    
    # prepopulate the form
    if session.task_form_vars:
        form.vars = session.task_form_vars
    
    
    b_execute = False
    n_limit = 0
    if form.validate():
        if 'preview' in request.vars:
            # redirect is necessary to pre-populate the form; didn't find another way
            session.task_form_vars = form.vars
            session.task_preview = True
            redirect(URL('start', args = [task_id]))
            
        elif 'execute' in request.vars:
            b_execute = True
            
            
    if form.vars.limit:
        n_limit = int(form.vars.limit)
    
    
    if task_id == 'send_invitation':
        script = 'background/mail/send_invitation_mail.py'
        parameters = []
        if b_preview:
            rows = InvitationList(shotdb).get_all_persons()
            colset = ['person.name', 'person.place', 'person.mail_enabled', 'person.email']
            
            
    elif task_id == 'send_reminder':
        script = 'background/mail/send_reminder_mail.py'
        parameters = []
        if b_preview:
            rm = Reminder(shotdb)
            rows = rm.get_all_persons()
            colset = ['person.name', 'person.place']
            
            
    elif task_id == 'resolve_waitlist':
        script = 'background/mail/resolve_waitlist.py'
        if b_preview:
            if form.vars.option_helper_numbers == 'use':
                b_option_use_helper_numbers = True
            else:
                b_option_use_helper_numbers = False
            rows = WaitList(shotdb).get_sorted(n_limit, b_option_use_helper_numbers)
            colset = ['person.name', 'person.place', 'wait.denial_sent']
        elif b_execute:
            parameters = [str(n_limit), form.vars.option_helper_numbers]
            
            
    elif task_id == 'send_denial':
        script = 'background/mail/send_waitlist_denial_mail.py'
        parameters = []
        if b_preview:
            rows = WaitList(shotdb).get_denials(n_limit)
            colset = ['person.name', 'person.place']
        elif b_execute:
            parameters = [str(n_limit)]
    
    
    if b_preview:
        shotdb.person.name.represent = lambda x, row: A('%s, %s' % (row.person.name, row.person.forename), _href=URL('staff', 'person_summary', args = [row.person.id]))
        
        table = SQLTABLE(rows,
                         columns = colset,
                         headers = 'fieldname:capitalize', _class = 'list',
                         truncate = None
                         )
        number = len(rows)
        
    elif b_execute:
        script_path = 'applications/%s/%s' % (config.appname, script)
        args = ['python', 'web2py.py', '-S', config.appname , '-M', '-R', script_path, '-A']
        args.extend(parameters)
        subprocess.Popen(args)
        redirect(URL('final'))
        
    else:
        table = None
        number = None
    
    return dict(task_id = task_id, form = form, table = table, number = number)


@auth.requires_membership('task executor')
def final():
    return dict()

    


