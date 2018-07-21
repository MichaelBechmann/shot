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

def schedule():
    return dict(announcements = Events(shotdb).get_visible())