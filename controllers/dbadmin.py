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
    
    