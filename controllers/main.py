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
    ErrorMail().send()
    return dict()

