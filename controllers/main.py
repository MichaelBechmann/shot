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
    global auth
    
from shotdbutil import Events
from shotmail import ErrorMail
from shotconfig import config
from gluon.storage import Storage
from urlutils import URLWiki
T.force('de')



def error():
    if config.enable_error_mail:
        ErrorMail().send()
    ticket = request.vars.ticket
    if config.redirect_to_ticket and ticket:
            redirect(config.shotticketurl + ticket)
    redirect(URLWiki('error'))

def redirect_https():

    c = 'main'
    f = 'index'
    args = []
    
    l = len(request.args)
    
    if l >= 2:
        c = request.args[0]
        f = request.args[1]
    if l > 2:
        args = request.args[2:]

    redirect(URL(c = c, f = f, args = args, scheme = 'http'))



def wiki():
    
    wiki = auth.wiki(render = 'multiple', menu_groups=['nobody'])
    
    wiki_ctrl = Storage()

    if str(request.args(0)).startswith('_'):
        wiki_ctrl.cmd = request.args(0)     
    else:
        wiki_ctrl.slug = request.args(0)
        
    wiki['wiki_ctrl'] = wiki_ctrl
    
    return wiki

def announcement_events():
    announcements = Events(shotdb).get_visible()
    if announcements:
        return TABLE([TD('%s am %s, %s' % (r.label, r.date, r.time)) for r in announcements], _id="tbl_next_event_date")

    else:
        return SPAN('Die Termine für die nächsten Märkte stehen noch nicht fest.')

def announcement_enroll():
    enrol_dates = Events(shotdb).get_visible()
    if enrol_dates:
        return TABLE([TD('ab ', SPAN(r.enrol_date, _id = 'enrol_date'), ' für den %s  am %s' % (r.label, r.date)) for r in enrol_dates], _id = 'tbl_enrol_dates')
    else:
        return 'Die Anmeldetermine für die nächsten Märkte stehen noch nicht fest.'

    