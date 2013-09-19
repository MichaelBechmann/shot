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
    return dict(date = Events(shotdb).current.date)

def vendorinfo():
    date = Events(shotdb).current.date
    enrol_date = Events(shotdb).current.enrol_date
    return dict(enrol_date = enrol_date, date = date)

def privacy():
    return dict()

def legal():
    return dict()

def error():  
    ErrorMail().send()
    return dict()




















