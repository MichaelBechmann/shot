# Static analyzer import helpers: (STATIC_IMPORT_MARK)
if 0:
    from gluon import *
    from gluon.languages import translator as T
    global request
    global response
    global session
    global shotdb   

import re
#import sys
from shotdbutil import *

T.force('de')



def __login(role, frompage):
    if (role == 'staff' and session.staffmember != True) or (role == 'admin' and session.admin != True):
        session.frompage = frompage
        redirect(URL('login'))

def __check_password(form):
    if form.vars.password == config.staffpassword:
        session.staffmember = True
    elif form.vars.password == config.adminpassword:
        session.staffmember = True
        session.admin = True
    else:
        session.staffmember = None
        session.admin = None
        form.errors.msg = 'The password is not correct!'
        


def login():
    form = FORM(TABLE(TR("Staff password:", 
                         INPUT(_type = 'password', _name = 'password'), INPUT(_type = 'submit')
                         )
                      )
                )


    if form.validate(onvalidation = __check_password):        
        nextpage = 'vendorlist'
        if session.frompage:
            nextpage = session.frompage
            session.frompage = None
            
        redirect(URL(nextpage))
        
    return dict(form = form)


def __list_ordered(query = db.vendor['id'] > 0):
    # This function handles the ordering.
    
    # o is an object of class db Field which defines the order column
    o = db.vendor.id
    
    # Checking the type appeared to be the best way to whether or not the variable is set.
    if (type(request.vars.orderby) == str):
        f = request.vars.orderby.split('.')[-1]
        if(session.vendorlistorderfield == f):
            o = ~getattr(db.vendor,f)
            session.vendorlistorderfield = ''
        else:
            o = getattr(db.vendor,f)
            session.vendorlistorderfield = f
    else:
        session.vendorlistorderfield = ''
    
    return db(query).select(orderby = o)
    

def list_vendors():
    __login(role = 'staff', frompage = 'list_vendors')
    return dict(rows = __list_ordered())


def vendorlist():
    __login(role = 'staff', frompage = 'vendorlist')
    query = shotdb.vendor.id > 0
    f = Filter('vendor', query, displayeventfilter = False)
    
    return dict(form = f.form, sqltab = f.sqltab)
    



#################################################################################

from gluon.tools import Crud

crud = Crud(db)
crud.settings.controller = 'staff'
crud.settings.create_next = URL('vendor_control')
crud.settings.update_next = URL('vendor_control')
crud.settings.update_deletable = True
crud.settings.showid = True



def vendor_control():
    __login(role = 'admin', frompage = 'vendor_control')
    
    table = db['vendor']
    
    if(request.args(0) == 'add'):
        crud_response = crud.create(table)  
    elif(request.args(0) == 'edit' and request.args(1) != None):
        crud_response = crud.update(table, request.args(1))
    else: 
        table.id.represent = lambda id, row: A(id,_href=URL('vendor_control/edit', args=(id)))
        crud_response = crud.select(table)

    return dict(crud_response = crud_response)

def numbers():
    __login(role = 'staff', frompage = 'numbers')
    
    eid = shotdb(shotdb.event.active == True).select().last().id
    n = Numbers(shotdb, eid)
    
    return dict(
                assigned  = n.assigned(),
                free      = n.free(), 
                free_kg   = n.free_kg(),
                )

def helplist():
    __login(role = 'staff', frompage = 'helplist')
    query  = (shotdb.help.vendor == shotdb.vendor.id)
    query &= (shotdb.help.shift  == shotdb.shift.id)
    f = Filter('help', query, eventtable = 'shift')
    return dict(form = f.form, sqltab = f.sqltab)

def bringlist():
    __login(role = 'staff', frompage = 'bringlist')
    query =  (shotdb.bring.vendor   == shotdb.vendor.id)
    query &= (shotdb.bring.donation == shotdb.donation.id)
    f = Filter('bring', query, eventtable = 'donation')
    return dict(form = f.form, sqltab = f.sqltab)

def messagelist():
    __login(role = 'staff', frompage = 'messagelist')
    query = (shotdb.message.vendor == shotdb.vendor.id)
    f = Filter('message', query)
    return dict(form = f.form, sqltab = f.sqltab)
   
def salelist():
    __login(role = 'staff', frompage = 'salelist')   
    query =  (shotdb.sale.vendor == shotdb.vendor.id)
    f = Filter('sale', query = query)
    return dict(form = f.form, sqltab = f.sqltab)


def crud():
    __login(role = 'staff', frompage = 'vendorlist')  
    
    tablename = request.args(0)
    action = request.args(1)
    id = request.args(2)
    
    table = shotdb[tablename]
     
    crud = Crud(shotdb)
    crud.settings.controller = 'staff'
    crud.settings.create_next = URL(tablename + 'list')
    crud.settings.update_next = URL(tablename + 'list')
    crud.settings.update_deletable = True
    crud.settings.showid = True   
    
    if(action == 'add'):
        crud_response = crud.create(tablename)
    elif(action == 'edit' and id != None):
        crud_response = crud.update(table, id)
    else:
        crud_response = 'Nothing selected!'
        
    
    
    return dict(crud_response = crud_response)


class Filter():
    '''
    This class provides everything to add filter functions for all tables.
    '''
    
    def __init__(self, tablename, query, displayeventfilter = True, eventtable = None):
        '''
        The argument eventtable must only be given if the main table 'table' does not contain the event-id itself.
        '''
        self.tablename = tablename
        self.table = getattr(shotdb, self.tablename)
        self.displayeventfilter = displayeventfilter
        if eventtable != None:
            self.eventtable = getattr(shotdb, eventtable)
        else:
            self.eventtable = self.table
        
        self.query = query
        
        label_all = 'all events'
        name_event  = 'selev'
        name_colset = 'selcs'
          
        e = Events(shotdb)
        le = e.all
        le.insert(0, label_all)
        
        ls = config.colsets[self.tablename]['sets'].keys()
        
        # provide edit links
        shotdb[self.tablename].id.represent = lambda id, row: A(id,_href=URL('crud/' + self.tablename + '/edit', args=(id)))
        
        formelements = []
        if self.displayeventfilter:
            formelements.append(SPAN(T('event:'),      SELECT(le, _name = name_event)))
        formelements.append(SPAN(T('column set:'), SELECT(ls, _name = name_colset)))
        formelements.append(INPUT(_type = 'submit', _class = 'button', _name = 'submit', _value = T('display')))
        formelements.append(DIV(A('Click here to add new entry!',_href=URL('staff/crud', self.tablename, 'add'))))
        self.form = FORM(*formelements)

        # extract selections from session object for use in the controller and pre-populate selectors
        # event filter selection
        selev = session.selected_event
        if selev != None:
            self.form.vars[name_event] = selev
            if selev == label_all:
                self.event_id = 0
            else:
                self.event_id = e.id[selev]
        else:
            self.form.vars[name_event] = e.current
            self.event_id = e.current_id 
        
        # column set selection    
        if session.selected_colsets != None and session.selected_colsets.has_key(self.tablename):
            cs = session.selected_colsets[self.tablename]           
        else:
            cs = config.colsets[self.tablename]['default']
        self.form.vars[name_colset] = cs
        self.colset = config.colsets[self.tablename]['sets'][cs]
        
        # prosess form
        if self.form.process().accepted:
            session.selected_event = self.form.vars[name_event]
            if session.selected_colsets == None:
                session.selected_colsets = {}
            session.selected_colsets[self.tablename] = self.form.vars[name_colset]
            
            # redirect is necessary to pre-populate the form; didn't find another way
            redirect(request.env.request_uri.split('/')[-1])
        
        # construct the query for the selected event
        if self.displayeventfilter:
            if self.event_id > 0:
                queryevent = self.eventtable.event == self.event_id
            else:
                queryevent = self.eventtable.id > 0
            self.query &= queryevent    

        # get the sorting column from the selected column head   
        if request.vars.orderby:                
            if session.sort_column.has_key(self.tablename) and session.sort_column[self.tablename]== request.vars.orderby:
                # table is already sorted for this very column => sort in reverse order
                # due to the '~' operator for revers sorting the database field must be constructed (no better solution so far)
                aux = request.vars.orderby.split('.')
                self.orderby = ~getattr(getattr(shotdb,aux[-2]),aux[-1])
                del session.sort_column[self.tablename]
            else:
                # here the string is sufficient
                self.orderby = request.vars.orderby
                session.sort_column[self.tablename] = request.vars.orderby
        else:
            self.orderby = self.table.id
            session.sort_column = {self.tablename: self.tablename + '.id'} 
            
            
        # construct table
        self.sqltab = SQLTABLE(shotdb(self.query).select(orderby = self.orderby),
                               columns = self.colset,
                               headers = 'fieldname:capitalize', orderby = 'dummy')

        
    