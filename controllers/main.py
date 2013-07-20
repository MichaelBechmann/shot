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
    
from shotmail import *

T.force('de')

def index():
    return dict()

def privacy():
    return dict()

def legal():
    return dict()

def error():
    msg  = 'ERROR ERROR ERROR'
    msg += str(BR())
    msg += 'session\n' + BEAUTIFY(session).xml()
    msg += 'request.env\n' + BEAUTIFY(request.env).xml() 
        
    ContactMail('tech', msg, 'anonymous', 'no email').send()
    return dict()




















