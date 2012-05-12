import re


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
        nextpage = 'list_vendors'
        if session.frompage:
            nextpage = session.frompage
            session.frompage = None
            
        redirect(URL(nextpage))
        
    #elif form.errors:
        

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
    
    n = Numbers()
    
    return dict(count_free_general      = n.count_free_general,
                count_free_kg           = n.count_free_kg, 
                count_assigned_total    = n.count_assigned_total, 
                count_assigned_general  = n.count_assigned_general,
                count_assigned_kg       = n.count_assigned_kg,
                free_general            = n.free_general, 
                free_kg                 = n.free_kg,
                )


def contributions():
        __login(role = 'staff', frompage = 'numbers')
        
        buttons= FORM(TABLE(TR(
                         INPUT(_type = 'submit', _class = 'button', _name = 'cake',   _value = T('cake')),
                         INPUT(_type = 'submit', _class = 'button', _name = 'waffle',   _value = T('waffle')),
                         INPUT(_type = 'submit', _class = 'button', _name = 'shifts',   _value = T('shifts'))
                         )
                       )
                )
        if 'cake' in request.vars:
            button = 'cake'
        elif 'waffle' in request.vars:
            button = 'waffle'
        elif 'shifts' in request.vars:
            button = 'shifts'
        else:
            button = ''
        
        list = ''
        columns = ['name', 'forename', 'telephone', 'email']
        
        if button != '':
            if button == 'cake' or button == 'waffle':
                query = db.vendor[button] == True 
                columns.append(button)
                headers = map(lambda x: T(x), columns)
                
            else:
                shifts  = []
                query   = (db.vendor['id'] < 0) # initialize with trivial query
                headers = map(lambda x: T(x), columns)
                for c in config.contribution_data:
                    name = c['name']
                    if re.match('shift_', name):
                        shifts.append(name)
                        columns.append(name)
                        query = query | (db.vendor[name] == True)
                        headers.append(T(c['title']) + ', ' + T(c['label']))
            
               
            columnsfull = map(lambda x: 'vendor.' + x, columns)
            headersfull = dict(zip(columnsfull, headers))
            table = SQLTABLE(db(query).select(orderby = 'name'), columns = columnsfull, headers=headersfull)
            
            
            p = re.compile('False|None')
            list = p.sub('', table.xml())
            
            p = re.compile('<td>True')
            list = p.sub('<td class = "true">X', list)
            
        return dict(buttons = buttons, list = list, headers = columns)

def test():
    __login(role = 'admin', frompage = 'test')   
    
    return dict()
    
    
#######################################
class ButtonBar():
    '''
    This class is a custom HTML helper which generates a configurable button bar.
    
    arguments: b is a list of dictionaries each describing a button.
    '''
    def __init__(self, b):
        pass

class Numbers():
    '''
    This class provides methods to display all kinds of information on sale numbers.
    '''
    def __init__(self): 
        
        self.assigned = []
        self.free_general = [] 
        self.free_kg = [] 
        self.assigned_general = []
        self.assigned_kg = []
        self._get_assigned()
        self._general()
        self._kg()
        
        self.count_free_general   = len(self.free_general)
        self.count_free_kg        = len(self.free_kg) 
        self.count_assigned_general   = len(self.assigned_general)
        self.count_assigned_kg        = len(self.assigned_kg) 
        self.count_assigned_total     = self.count_assigned_general + self.count_assigned_kg

            
    def _get_assigned(self):
        for row in db(db.vendor.number != None).select():
            self.assigned.append(row.number)      
    
    def _general(self):
        for r in config.numbers.available:
            for n in range(r[0], r[1] + 1):
                if n in self.assigned:
                    self.assigned_general.append(n)
                else:
                    self.free_general.append(n)

    def _kg(self):
        for r in config.numbers.available_kg:
            for n in range(r[0], r[1] + 1):
                if n in self.assigned:
                    self.assigned_kg.append(n)
                else:
                    self.free_kg.append(n)           

      