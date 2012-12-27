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
    global db

from shotdbutil import *
from shotmail import *
from time import *

def _migrate_db_to_shotdb():
    '''
    This function migrates the data of the event spring 2012 (db) to the new database structure (shotdb)
    '''
    
    # add event
    shotdb.event.update_or_insert(label = 'Frühjahr 2012', active = False, number_ranges = '200-250, 300-350, 400-450', number_ranges_kg = '500-599')
    
    # add donations
    shotdb.donation.update_or_insert(event = 1, item = 'Kuchen',     target_number = 30, enable_notes = False)
    shotdb.donation.update_or_insert(event = 1, item = 'Waffelteig', target_number = 10, enable_notes = False)
    
    # add shifts
    shotdb.shift.update_or_insert(event = 1, activity = 'Sortieren',    day = 'Freitag', time = '14:30 - 17 Uhr', target_number = 20, display = 'a1')
    shotdb.shift.update_or_insert(event = 1, activity = 'Küche',        day = 'Samstag', time = '8:30 - 11 Uhr',  target_number = 3,  display = 'a2')
    shotdb.shift.update_or_insert(event = 1, activity = 'Auflegen',     day = 'Samstag', time = '8:30 - 11 Uhr',  target_number = 8,  display = 'a2')
    shotdb.shift.update_or_insert(event = 1, activity = 'Kasse',        day = 'Samstag', time = '8:30 - 11 Uhr',  target_number = 4,  display = 'a2')
    shotdb.shift.update_or_insert(event = 1, activity = 'Kuchentheke',  day = 'Samstag', time = '8:30 - 11 Uhr',  target_number = 2,  display = 'a2')    
    shotdb.shift.update_or_insert(event = 1, activity = 'Waffelstand',  day = 'Samstag', time = '8:30 - 11 Uhr',  target_number = 1,  display = 'a2')
    shotdb.shift.update_or_insert(event = 1, activity = 'Küche',        day = 'Samstag', time = '11 - 13:30 Uhr', target_number = 3,  display = 'b1')    
    shotdb.shift.update_or_insert(event = 1, activity = 'Auflegen',     day = 'Samstag', time = '11 - 13:30 Uhr', target_number = 5,  display = 'b1')
    shotdb.shift.update_or_insert(event = 1, activity = 'Kasse',        day = 'Samstag', time = '11 - 13:30 Uhr', target_number = 0,  display = 'b1')    
    shotdb.shift.update_or_insert(event = 1, activity = 'Kuchentheke',  day = 'Samstag', time = '11 - 13:30 Uhr', target_number = 1,  display = 'b1')
    shotdb.shift.update_or_insert(event = 1, activity = 'Waffelstand',  day = 'Samstag', time = '11 - 13:30 Uhr', target_number = 2,  display = 'b1')    
    shotdb.shift.update_or_insert(event = 1, activity = 'Küche',        day = 'Samstag', time = '12:30 - 15 Uhr', target_number = 0,  display = 'b2')     
    shotdb.shift.update_or_insert(event = 1, activity = 'Rücksortieren',day = 'Samstag', time = '12:30 - 15 Uhr', target_number = 20, display = 'b2') 
    
        
    # loop over the single table of db
    
    currentevent = 1
    count_id = 0
    for row in db(db.vendor.id > 0).select():
        
        # table vendor
        vendor_new ={}
        
        vendor_new['name']          = row.name   
        vendor_new['forename']      = row.forename 
        vendor_new['place']         = row.place 
        vendor_new['zip_code']      = row.zip_code 
        vendor_new['street']        = row.street 
        vendor_new['house_number']  = row.house_number
        vendor_new['telephone']     = row.telephone
        vendor_new['email']         = row.email   
        vendor_new['kindergarten']  = row.kindergarten
        vendor_new['code']          = row.code
        
        if row.verified == True:
            vendor_new['verified']  = currentevent
            
        id = shotdb.vendor.update_or_insert(**vendor_new)
        
        if id != None:
            Log(shotdb).vendor(id, 'migrated')   
            
            
        # table sale
        count_id += 1
        sale_new = {}
        
        sale_new['event']           = currentevent
        sale_new['vendor']          = count_id
        
        number = row.number
        if number != None and count_id < 229: # the last four numbers have not been valid
            sale_new['number']          = number
            sale_new['number_assigned'] = row.number_assigned
            sale_new['number_unikey']   = '1:' + str(number)
        
        shotdb.sale.update_or_insert(**sale_new)  
        
        
        # donations
        if row.cake == True:
            shotdb.bring.update_or_insert(donation = 1 , vendor = count_id)
        if row.waffle == True:
            shotdb.bring.update_or_insert(donation = 2 , vendor = count_id)
        
        
        # shifts
        if row.shift_fr_0  == True: shotdb.help.update_or_insert(shift = 1  , vendor = count_id)
        if row.shift_sa_0  == True: shotdb.help.update_or_insert(shift = 2  , vendor = count_id)
        if row.shift_sa_1  == True: shotdb.help.update_or_insert(shift = 3  , vendor = count_id)
        if row.shift_sa_2  == True: shotdb.help.update_or_insert(shift = 4  , vendor = count_id)        
        if row.shift_sa_3  == True: shotdb.help.update_or_insert(shift = 5  , vendor = count_id)
        if row.shift_sa_4  == True: shotdb.help.update_or_insert(shift = 6  , vendor = count_id)
        if row.shift_sa_5  == True: shotdb.help.update_or_insert(shift = 7  , vendor = count_id)
        if row.shift_sa_6  == True: shotdb.help.update_or_insert(shift = 8  , vendor = count_id)          
        if row.shift_sa_7  == True: shotdb.help.update_or_insert(shift = 9  , vendor = count_id)
        if row.shift_sa_8  == True: shotdb.help.update_or_insert(shift = 10 , vendor = count_id)
        if row.shift_sa_9  == True: shotdb.help.update_or_insert(shift = 11 , vendor = count_id)
        if row.shift_sa_10 == True: shotdb.help.update_or_insert(shift = 12 , vendor = count_id)          
        if row.shift_sa_11 == True: shotdb.help.update_or_insert(shift = 13 , vendor = count_id) 
        
        
        # messages
        if row.message != '' and row.message != None:
            shotdb.message.update_or_insert(event = currentevent , vendor = count_id, text = row.message)
        
    redirect(URL('staff', 'vendorlist'))
    
def _config_event_2():
    '''
    This function adds the configuration for the second event.
    '''
    # add event
    shotdb.event.update_or_insert(label = 'Herbst 2012', active = False, number_ranges = '200-250, 300-350, 400-450', number_ranges_kg = '500-550')
    
    # add donations
    shotdb.donation.update_or_insert(event = 2, item = 'Kuchen',     target_number = 30, enable_notes = True)
    shotdb.donation.update_or_insert(event = 2, item = 'Waffelteig', target_number = 10, enable_notes = False)
    
    # add shifts
    shotdb.shift.update_or_insert(event = 2, activity = 'Sortieren',    day = 'Freitag', time = '14:30 - 17 Uhr', target_number = 20, display = 'a1')
    shotdb.shift.update_or_insert(event = 2, activity = 'Küche',        day = 'Samstag', time = '8:30 - 11 Uhr',  target_number = 3,  display = 'a2')
    shotdb.shift.update_or_insert(event = 2, activity = 'Auflegen',     day = 'Samstag', time = '9 - 11:30 Uhr',  target_number = 6,  display = 'b1')
    shotdb.shift.update_or_insert(event = 2, activity = 'Kasse',        day = 'Samstag', time = '8:30 - 11 Uhr',  target_number = 4,  display = 'a2')
    shotdb.shift.update_or_insert(event = 2, activity = 'Kuchentheke',  day = 'Samstag', time = '9 - 11:30 Uhr',  target_number = 2,  display = 'b1')    
    shotdb.shift.update_or_insert(event = 2, activity = 'Waffelstand',  day = 'Samstag', time = '9 - 11:30 Uhr',  target_number = 2,  display = 'b1')
    shotdb.shift.update_or_insert(event = 2, activity = 'Küche',        day = 'Samstag', time = '12 - 14:30 Uhr', target_number = 3,  display = 'b2')    
    shotdb.shift.update_or_insert(event = 2, activity = 'Rücksortieren',day = 'Samstag', time = '12 - 14:30 Uhr', target_number = 25, display = 'b2')
    shotdb.shift.update_or_insert(event = 2, activity = 'Ich helfe nach Bedarf (nach Rücksprache).',       day = 'Samstag', time = 'flexibel', target_number = 15, display = 'c1')    
    shotdb.shift.update_or_insert(event = 2, activity = 'Ich bin Elternbeirat und helfe wie besprochen.',  day = 'Samstag', time = 'flexibel', target_number = 12, display = 'c1')

    
    redirect(URL('config', 'config_event'))

def _renew_ver_codes():
    '''
    This function resets all verification codes and writes the old codes to the log.
    '''
    for row in shotdb(shotdb.vendor.id > 0).select():
        c  = row.code
        id = row.id
        if c != None:
            l = 'code renewed by admin (was: ' + c + ')'
            Log(shotdb).vendor(id, l) 
            row.update_record(code = Ident().code)
            
    redirect(URL('staff', 'vendorlist')) 
    

def _send_invitation_mail():
    '''
    This function loops through all vendors.
    For each vendor the invitation mail is sent.
    '''
    for row in shotdb(shotdb.vendor.id < 2).select():  
        # row.email = 'michael_bechmann@yahoo.de'
        InvitationMail(row.as_dict()).send() 
    
    redirect(URL('staff', 'vendorlist'))
    
    
def _send_waitlist_mail():
    '''
    This function loops through all vendors.
    The waitlist mail is sent to those vendors which did not get a number for the current event.
    '''
    l = []
    for v in shotdb(shotdb.vendor.verified == 2).select():  
    #for v in shotdb(shotdb.vendor.id == 349).select():     
        s = shotdb((shotdb.sale.vendor == v.id) & (shotdb.sale.event == 2)).select().last()
        if s == None and v.id != 105 and v.id != 203 and v.id > 0 and v.kindergarten == config.no_kindergarten_id:
            l.append(str(v.id) + ', ' + str(v.verified) + ', ' + v.name + ', ' + v.forename)
        
            # row.email = 'ninabugner@yahoo.de'
            #v.email = 'michael_bechmann@yahoo.de'
            WaitlistMail(v.as_dict()).send() 
            sleep(12)
    
    #redirect(URL('staff', 'vendorlist')) 
    
    return dict(l = l)

def send_unzhurst_mail():
    '''
    special one time function
    '''
    l = []
    out = [160, 285]
    for v in shotdb(shotdb.vendor.verified == 2).select():  
    #for v in shotdb(shotdb.vendor.id == 349).select():     
        s = shotdb((shotdb.sale.vendor == v.id) & (shotdb.sale.event == 2)).select().last()
        # if v.id == 1:
        if s == None and v.id not in out and v.id >= 50 and v.kindergarten == config.no_kindergarten_id:
            l.append(str(v.id) + ', ' + str(v.verified) + ', ' + v.name + ', ' + v.forename)
        
            # v.email = 'ninabugner@yahoo.de'
            # v.email = 'michael_bechmann@yahoo.de'
            UnzhurstMail(v.as_dict()).send() 
            sleep(15)
    
    #redirect(URL('staff', 'vendorlist')) 
    
    return dict(l = l)
    