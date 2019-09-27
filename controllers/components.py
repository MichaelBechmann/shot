# -*- coding: utf-8 -*-
# Static analyzer import helpers: (STATIC_IMPORT_MARK)
if 0:
    from gluon.languages import translator as T
    from gluon import *
    import gluon
    global request
    global response
    global shotdb
    global auth

from shotdbutil import Events


def error():
    return DIV('Diese Komponente konnte aufgrund eines Fehlers nicht geladen werden!')

def announcement_events():
    return dict(events = Events(shotdb).get_visible())

def all_dates_events():
    return dict(events = Events(shotdb).get_visible_all_dates())

def all_flyers_events():
    return dict(events = Events(shotdb).get_visible())