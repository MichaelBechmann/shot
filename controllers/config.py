# Static analyzer import helpers: (STATIC_IMPORT_MARK)
if 0:
    from gluon import *
    from gluon.languages import translator as T
    global request
    global response
    global session
    global shotdb   

from gluon.tools import Crud



def config_event():
    
    crudevent = Crud(shotdb)
    crudevent.settings.controller = 'config'
    crudevent.settings.create_next = URL('config_event')
    crudevent.settings.update_next = URL('config_event')
    crudevent.settings.update_deletable = True
    crudevent.settings.showid = True  

    crudshift = Crud(shotdb)
    crudshift.settings.controller = 'config'
    crudshift.settings.create_next = URL('config_event')
    crudshift.settings.update_next = URL('config_event')
    crudshift.settings.update_deletable = True
    crudshift.settings.showid = True
    
    cruddonation = Crud(shotdb)
    cruddonation.settings.controller = 'config'
    cruddonation.settings.create_next = URL('config_event')
    cruddonation.settings.update_next = URL('config_event')
    cruddonation.settings.update_deletable = True
    cruddonation.settings.showid = True    
    
    tableevent    = shotdb['event']
    tableshift    = shotdb['shift']
    tabledonation = shotdb['donation']
    
    crudevent_response    = None
    crudshift_response    = None
    cruddonation_response = None
    
    
    if(request.args(0) == 'addevent'):
        crudevent_response = crudevent.create(tableevent)  
    elif(request.args(0) == 'addshift'):
        crudshift_response = crudshift.create(tableshift)     
    elif(request.args(0) == 'adddonation'):
        cruddonation_response = crudshift.create(tabledonation)        

    elif(request.args(0) == 'editevent' and request.args(1) != None):
        crudevent_response = crudevent.update(tableevent, request.args(1))          
    elif(request.args(0) == 'editshift' and request.args(1) != None):
        crudshift_response = crudshift.update(tableshift, request.args(1))
    elif(request.args(0) == 'editdonation' and request.args(1) != None):
        cruddonation_response = cruddonation.update(tabledonation, request.args(1))        
        
        
    else: 
        tableevent.id.represent = lambda id, row: A(id,_href=URL('config_event/editevent', args=(id)))
        crudevent_response = crudevent.select(tableevent)
        
        tableshift.id.represent = lambda id, row: A(id,_href=URL('config_event/editshift', args=(id)))
        crudshift_response = crudshift.select(tableshift)
        
        tabledonation.id.represent = lambda id, row: A(id,_href=URL('config_event/editdonation', args=(id)))
        cruddonation_response = crudshift.select(tabledonation)
      
    
    # The _name arguments are important as the one of the pressed button will appear in request.vars.
    button = FORM(INPUT(_type = 'submit', _class = 'button', _name = 'submit', _value = T('view form')))
        
    if 'submit' in request.vars:
        session.form_passive = True
        redirect(URL('sale', 'form'))    

    return dict(crudshift_response = crudshift_response, cruddonation_response = cruddonation_response, crudevent_response = crudevent_response, button = button)