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
    announcements = Events(shotdb).get_visible()
    if announcements:
        return TABLE([TD('%s am %s, %s' % (r.label, r.date, r.time)) for r in announcements], _id="tbl_next_event_date")

    else:
        return SPAN('Die Termine für die nächsten Märkte stehen noch nicht fest.')

    return dict(heading='Alle Termine')