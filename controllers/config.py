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


@auth.requires_membership('configurator')
def config_event():
    
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
    
    tableeventtype = shotdb['event_type']
    tableevent     = shotdb['event']
    tableshift     = shotdb['shift']
    tabledonation  = shotdb['donation']
    
    crudeventtype_response = None
    crudevent_response     = None
    crudshift_response     = None
    cruddonation_response  = None
    
    
    if(request.args(0) == 'addeventtype'):
        crudeventtype_response = crudevent.create(tableeventtype)
    elif(request.args(0) == 'addevent'):
        crudevent_response = crudevent.create(tableevent)
    elif(request.args(0) == 'addshift'):
        crudshift_response = crudshift.create(tableshift)     
    elif(request.args(0) == 'adddonation'):
        cruddonation_response = cruddonation.create(tabledonation)
    elif(request.args(0) == 'editeventtype' and request.args(1) != None):
        crudeventtype_response = crudeventtype.update(tableeventtype, request.args(1)) 
    elif(request.args(0) == 'editevent' and request.args(1) != None):
        crudevent_response = crudevent.update(tableevent, request.args(1))          
    elif(request.args(0) == 'editshift' and request.args(1) != None):
        crudshift_response = crudshift.update(tableshift, request.args(1))
    elif(request.args(0) == 'editdonation' and request.args(1) != None):
        cruddonation_response = cruddonation.update(tabledonation, request.args(1))        
        
    else:
        tableeventtype.id.represent = lambda id, row: A(id,_href=URL('config_event/editeventtype', args=(id)))
        crudeventtype_response = crudeventtype.select(tableeventtype)
        
        tableevent.id.represent = lambda id, row: A(id,_href=URL('config_event/editevent', args=(id)))
        crudevent_response = crudevent.select(tableevent)
        
        tableshift.id.represent = lambda id, row: A(id,_href=URL('config_event/editshift', args=(id)))
        crudshift_response = crudshift.select(tableshift)
        
        tabledonation.id.represent = lambda id, row: A(id,_href=URL('config_event/editdonation', args=(id)))
        cruddonation_response = cruddonation.select(tabledonation)
      
    
    # The _name arguments are important as the one of the pressed button will appear in request.vars.
    button = FORM(INPUT(_type = 'submit', _class = 'button', _name = 'submit', _value = T('view form')))
        
    if 'submit' in request.vars:
        session.form_passive = True
        redirect(URL('sale', 'form'))    

    return dict(crudeventtype_response = crudeventtype_response, crudevent_response = crudevent_response, crudshift_response = crudshift_response, cruddonation_response = cruddonation_response, button = button)


 
def _config_event_4():
    '''
    This function adds the configuration for the third event.
    '''
    
    if session.admin != True:
        return 'no way!'
     
    # add event
    #shotdb.event.update_or_insert(label = 'Herbst 2013', active = True, number_ranges = '200-250, 300-350, 400-450, 500-550', numbers_limit = 195)
     
    # add donations
    shotdb.donation.update_or_insert(event = 4, item = 'Kuchen',     target_number = 30, enable_notes = True)
    shotdb.donation.update_or_insert(event = 4, item = 'Waffelteig', target_number = 10, enable_notes = False)

    # add shifts
    shotdb.shift.update_or_insert(event = 4, activity = 'Sortieren',            day = 'Freitag, 27.9.', time = '14:30 - 17 Uhr', target_number = 20, display = 'a1')
    shotdb.shift.update_or_insert(event = 4, activity = 'Küche',                day = 'Samstag, 28.9.', time = '8:30 - 11 Uhr',  target_number = 3,  display = 'a2')
    shotdb.shift.update_or_insert(event = 4, activity = 'Auflegen',             day = 'Samstag, 28.9.', time = '9 - 11:30 Uhr',  target_number = 6,  display = 'b1')
    shotdb.shift.update_or_insert(event = 4, activity = 'Kasse',                day = 'Samstag, 28.9.', time = '8:30 - 11 Uhr',  target_number = 4,  display = 'a2')
    shotdb.shift.update_or_insert(event = 4, activity = 'Kuchentheke',          day = 'Samstag, 28.9.', time = '9 - 11:30 Uhr',  target_number = 2,  display = 'b1')    
    shotdb.shift.update_or_insert(event = 4, activity = 'Waffelstand',          day = 'Samstag, 28.9.', time = '9 - 11:30 Uhr',  target_number = 2,  display = 'b1')
    shotdb.shift.update_or_insert(event = 4, activity = 'Küche',                day = 'Samstag, 28.9.', time = '12 - 14:30 Uhr', target_number = 3,  display = 'b2')    
    shotdb.shift.update_or_insert(event = 4, activity = 'Rücksortieren',        day = 'Samstag, 28.9.', time = '12 - 14:30 Uhr', target_number = 25, display = 'b2')
    shotdb.shift.update_or_insert(event = 4, activity = 'Kistenkontrolle',      day = 'Samstag, 28.9.', time = '13:30 - 15 Uhr', target_number = 25, display = 'c1')
    shotdb.shift.update_or_insert(event = 4, activity = 'Ich helfe nach Bedarf (nach Rücksprache).',       day = 'Samstag, 28.9.', time = 'flexibel', target_number = 15, display = 'c2')    
 
    redirect(URL('config', 'config_event'))
