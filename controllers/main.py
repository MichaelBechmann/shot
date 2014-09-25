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
    
from shotdbutil import Events
from shotmail import ErrorMail
from shotconfig import config

T.force('de')

def index():
    return dict(announcements = Events(shotdb).get_visible())

def vendorinfo():
    return dict(enrol_dates = Events(shotdb).get_visible())

def privacy():
    return dict()

def legal():
    return dict()

def error():
    if config.enable_error_mail:
        ErrorMail().send()
    ticket = request.vars.ticket
    if config.redirect_to_ticket and ticket != 'None':
            redirect(config.shotticketurl + ticket)
    return dict()

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
