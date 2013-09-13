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

from shotdbutil import *

def _helper_numbers():
    
    if len(request.args) > 0:
        eid = int(request.args[0])
    else:
        eid = 0
    
    n = Numbers(shotdb, eid)
    # convert long to int (to not display the suffix L)
    l = [int(x) for x in n.helper()]
    
    if len(l) > 0:
        s = str(len(l)) + ' ---- ' + str(l)
    else:
        s = "sorry, nothing found!"
    
    return s

def _number_assignment():
    if len(request.args) > 0:
        pid = int(request.args[0])
    else:
        pid = 1
        
    na = NumberAssignment(shotdb, pid)
    
    n = na.determine_number()
    
    t = TABLE('person id: ' + str(pid), 
              'old number: ' + str(na.on),
              'determined sale number: ' + str(n), 
              'person helped at previous event: ' + str(na.b_helped_previous_event),
              'current event: ' + str(na.e.current.id),
              'previous event: ' + str(na.previousevent)
              
              )
    
    
    return t