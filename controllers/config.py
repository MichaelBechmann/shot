# Static analyzer import helpers: (STATIC_IMPORT_MARK)
if 0:
    from gluon import *
    from gluon.languages import translator as T
    global request
    global response
    global session
    global shotdb
    global auth

from gluon.tools import Crud
from shotdbutil import Events, CopyConfig

@auth.requires_membership('configurator')
def config_event():
    
    if 'submit_view_form' in request.vars:
        session.form_passive = True
        redirect(URL('sale', 'form'))
    
    crudeventtype = Crud(shotdb)
    crudeventtype.settings.controller = 'config'
    crudeventtype.settings.create_next = URL('config_event')
    crudeventtype.settings.update_next = URL('config_event')
    crudeventtype.settings.update_deletable = True
    crudeventtype.settings.showid = True  
    
    crudevent = Crud(shotdb)
    crudevent.settings.controller = 'config'
    crudevent.settings.create_next = URL('config_event')
    crudevent.settings.update_next = URL('config_event')
    crudevent.settings.update_deletable = True
    crudevent.settings.showid = True  
    
    tableeventtype = shotdb['event_type']
    tableevent     = shotdb['event']
    
    crudeventtype_response = None
    crudevent_response     = None
    
    
    if(request.args(0) == 'addeventtype'):
        crudeventtype_response = crudevent.create(tableeventtype)
    elif(request.args(0) == 'addevent'):
        crudevent_response = crudevent.create(tableevent)
    elif(request.args(0) == 'editeventtype' and request.args(1) != None):
        crudeventtype_response = crudeventtype.update(tableeventtype, request.args(1)) 
    elif(request.args(0) == 'editevent' and request.args(1) != None):
        crudevent_response = crudevent.update(tableevent, request.args(1))              
    else:
        tableeventtype.id.represent = lambda id, row: A(id,_href=URL('config_event/editeventtype', args=(id)))
        crudeventtype_response = crudeventtype.select(tableeventtype, _class = 'list')
        
        tableevent.id.represent = lambda id, row: A(id,_href=URL('config_event/editevent', args=(id)))
        crudevent_response = crudevent.select(tableevent, _class = 'list')
    
    # The _name arguments are important as the one of the pressed button will appear in request.vars.
    button_view_form = FORM(INPUT(_type = 'submit', _class = 'button', _name = 'submit_view_form', _value = T('view form')))
    
    
    e = Events(shotdb)
    le = e.get_all_labels_sorted()
    le.insert(0, ' Please select ...')
    
    copy_form = FORM(TABLE(TR('Source Event: ', SELECT(le, _name = 'event'),
                                    INPUT(_type = 'submit', _class = 'button', _name = 'submit_copy', _value = T('copy configuration')))))  
        
    if copy_form.process().accepted:
        selev = copy_form.vars['event']
        if selev not in e.all:    
            response.flash = 'Please select a source event!'
        else:
            cc = CopyConfig(shotdb, e.all[selev])
            
            # copy shifts
            n_s = cc.copy_shifts()
            
            # copy donations
            n_d = cc.copy_donations()
            
            response.flash = 'Inserted or updated %d shifts and %d donations.' % (n_s, n_d)


    return dict(crudeventtype_response = crudeventtype_response,
                crudevent_response = crudevent_response,
                button_view_form = button_view_form,
                copy_form = copy_form)
    
