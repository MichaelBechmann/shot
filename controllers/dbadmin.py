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
import subprocess
 

def _renew_ver_codes():
    '''
    This function resets all verification codes and writes the old codes to the log.
    '''
    if session.admin != True:
        return 'no way!'
    
    for row in shotdb(shotdb.person.id > 0).select():
        c  = row.code
        id = row.id
        if c != None:
            l = 'code renewed by admin (was: ' + c + ')'
            Log(shotdb).person(id, l) 
            row.update_record(code = Ident().code)
            
    redirect(URL('staff', 'personlist')) 
    

def convert_db():
    '''
    Temporary function for conversion of the database from sqlite to mysql
    '''
    if session.admin != True:
        return 'no way!'
    
    # action is allowed
    subprocess.Popen(['python', 'web2py.py', '-S', config.appname , '-M', '-R', 'applications/' + config.appname + '/background/database_conversion/convert_database.py'])
    return('converting database ...')

def regularize_names():
    '''
    Function to regularize person names, street names etc. according to the same rules applied at form level.
    '''
    if session.admin != True:
        return 'no way!'
    
    # action is allowed
    subprocess.Popen(['python', 'web2py.py', '-S', config.appname , '-M', '-R', 'applications/' + config.appname + '/background/database_conversion/regularize_names.py'])
    return('converting database ...')  
    
    
def _config_event_5():
    '''
    This function adds the configuration for the second event.
    Shall be removed with issue #41!
    '''
    if session.admin != True:
        return 'no way!'
    # add event
    shotdb.event.update_or_insert(label = 'Frühjahr 2014', active = True, number_ranges = '200-250, 300-350, 400-450, 500-550')
    
    # add donations
    shotdb.donation.update_or_insert(event = 5, item = 'Kuchen',        target_number = 20, enable_notes = True)
    shotdb.donation.update_or_insert(event = 5, item = 'Torte',         target_number = 15, enable_notes = True)
    shotdb.donation.update_or_insert(event = 5, item = 'Waffelteig',    target_number = 12, enable_notes = False)
    
    # add shifts
    shotdb.shift.update_or_insert(event = 5, activity = 'Aufbau ( Männer)',         day = 'Donnerstag, 13.3.',  time = '19 - 21 Uhr',       target_number = 4,  display = 'a1')
    shotdb.shift.update_or_insert(event = 5, activity = 'Sortieren',                day = 'Freitag, 14.3.',     time = '14:30 - 17 Uhr',    target_number = 36, display = 'a2', comment = 'Das Aussortieren und Zurücklegen von Ware ist diesmal streng untersagt und wird mit öffentlichem Auspeitschen bestraft!')
    shotdb.shift.update_or_insert(event = 5, activity = 'Küche',                    day = 'Samstag, 15.3.',     time = '8 - 10 Uhr',        target_number = 2,  display = 'b1')
    shotdb.shift.update_or_insert(event = 5, activity = 'Auflegen',                 day = 'Samstag, 15.3.',     time = '8 - 10 Uhr',        target_number = 7,  display = 'b1')
    shotdb.shift.update_or_insert(event = 5, activity = 'Kasse',                    day = 'Samstag, 15.3.',     time = '8 - 10 Uhr',        target_number = 5,  display = 'b1')
    shotdb.shift.update_or_insert(event = 5, activity = 'Kuchentheke',              day = 'Samstag, 15.3.',     time = '8 - 10 Uhr',        target_number = 1,  display = 'b1')
    shotdb.shift.update_or_insert(event = 5, activity = 'Kuchentheke',              day = 'Samstag, 15.3.',     time = '10 - 12 Uhr',       target_number = 2,  display = 'b2')
    shotdb.shift.update_or_insert(event = 5, activity = 'Küche',                    day = 'Samstag, 15.3.',     time = '10 - 12 Uhr',       target_number = 2,  display = 'b2')
    shotdb.shift.update_or_insert(event = 5, activity = 'Auflegen',                 day = 'Samstag, 15.3.',     time = '10 - 12 Uhr',       target_number = 6,  display = 'b2')
    shotdb.shift.update_or_insert(event = 5, activity = 'Kasse',                    day = 'Samstag, 15.3.',     time = '10 - 12 Uhr',       target_number = 3,  display = 'b2')
    shotdb.shift.update_or_insert(event = 5, activity = 'Küche',                    day = 'Samstag, 15.3.',     time = '12 - 14:30 Uhr',    target_number = 1,  display = 'c1')
    shotdb.shift.update_or_insert(event = 5, activity = 'Rücksortieren',            day = 'Samstag, 15.3.',     time = '12 - 14:30 Uhr',    target_number = 28, display = 'c1')
    shotdb.shift.update_or_insert(event = 5, activity = 'Kistenkontrolle/ Rückgabe',day = 'Samstag, 15.3.',     time = '14 - 16:30 Uhr',    target_number = 8,  display = 'c2')
    shotdb.shift.update_or_insert(event = 5, activity = 'Abbau ( Männer)',          day = 'Samstag, 15.3.',     time = '14 - 16:30 Uhr',    target_number = 2,  display = 'c2')
    shotdb.shift.update_or_insert(event = 5, activity = 'Küche',                    day = 'Samstag, 15.3.',     time = '14 - 16:30 Uhr',    target_number = 2,  display = 'c2')
    
    shotdb.shift.update_or_insert(event = 5, activity = 'Ich helfe nach Bedarf (nach Rücksprache).',       day = 'Samstag, 15.3.', time = 'Zeit flexibel', target_number = 11, display = 'd1')    

    
    redirect(URL('config', 'config_event'))