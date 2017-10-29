# Static analyzer import helpers: (STATIC_IMPORT_MARK)
if 0:
    from gluon import *
    from gluon.languages import translator as T
    global request
    global response
    global session
    global shotdb
    global SQLField
    global auth
    
from shotdbutil import Requests

@auth.requires_membership('team')
def requests():
    
    rows = Requests(shotdb).GetAll(reverse = True)
    return dict(rows = rows)

