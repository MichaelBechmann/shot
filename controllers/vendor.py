'''
This file contains everything related to the vendor registration.
'''
# Static analyzer import helpers: (STATIC_IMPORT_MARK)
if 0:
    from gluon import *
    from gluon.languages import translator as T
    global request
    global response
    global session
    global shotdb    
    global config


from shotconfig import * 
from shotmail import *
from shotdbutil import *
from gluon.storage import Storage

T.force('de')

def form():
    # check if vendor registration  is enabled
    if config.enableregis == False:
        redirect(URL('main', 'index'))
        
    i = Ident(shotdb, *request.args)
        
    display_fields = ['forename', 'name', 'place', 'zip_code', 'street', 'house_number', 'telephone', 'email', 'kindergarten']
    comments = {'kindergarten': T('Please indicate if you have a child in one of the kindergartens in Ottersweier.')} 
    form = SQLFORM(shotdb.vendor, fields = display_fields, submit_button = T('submit'), col3 = comments)
    
    form.vars.kindergarten = '' # do not use config.no_kindergarten_id here to initialize form with empty field
    if session.vendor:
        # pre-populate the form in case of re-direction from form_vendor_confirm() (back button pressed)
        # see book, section 'Pre-populating the form' in chapter 'Forms and Validators'
        form.vars = session.vendor
    elif i.b_verified:
        # pre-populate form if function is called with vendor code link
        # To prevent mixing up fields (e.g., id, log, verified, code) between vendors only the fields displayed in the form must be copied to vars!!!
        # Note that errors "IntegrityError: PRIMARY KEY must be unique" occur if false 'id' fields of the form would propagate to the insert or update operations!
        form.vars = Storage()
        for f in display_fields:
            form.vars[f] = i.vendor[f]
        # Note: The SQLFORM constructor augmentes the list of fields with 'id'!
        del form.vars['id']
                
        form.vars.kindergarten = ''
        session.vendor_id = i.id
    
    # There is a mistake in the book: form.validate() returns True or False. form.process() returns the form itself
    # see http://osdir.com/ml/web2py/2011-11/msg00467.html
    if form.validate():  
        session.vendor = form.vars 
        redirect(URL('confirm'))
        
    return dict(form=form)

def confirm():
    # check if there is vendor information to be confirmed
    if session.vendor == None:
        redirect(URL('main', 'index'))

    # construct display of data to be confirmed
    data_items = [
                   TR(T('Your name:'), session.vendor['forename'] + ' ' + session.vendor['name']),
                   TR(T('Your address:'), session.vendor['zip_code'] + ' ' + session.vendor['place'] + ', ' + session.vendor['street'] + ' ' + session.vendor['house_number'] ),
                   TR(T('Your telephone number:'), session.vendor['telephone']),
                   TR(T('Your email address:'), session.vendor['email'])
                ]
    if session.vendor['kindergarten'] != config.no_kindergarten_id:
        data_items.append(TR(T('You have a child in:'), session.vendor['kindergarten']))
        
    data = TABLE(*data_items)           
    
    
    # The _name arguments are important as the one of the pressed button will appear in request.vars.
    form = FORM(TABLE(TR(
                         INPUT(_type = 'submit', _class = 'button', _name = 'submit back', _value = T('back')),
                         INPUT(_type = 'submit', _class = 'button', _name = 'submit send', _value = T('go!'), _id = config.cssid.waitmsgtrig)
                         )
                       ),
                DIV(T(config.msg.wait), _id = config.cssid.waitmsg)
                )

        
    if 'submit back' in request.vars:
        redirect(URL('form'))
    elif 'submit send' in request.vars:
        if session.vendor != None:
            
            ve = VendorEntry(session.vendor)
            
            # Prevent multiple database entries
            # Note: The reference to the object session.vendor can be deleted here.
            # The data persist in memory and the object ve contains a duplicate private reference.
            session.vendor = None 
            
            if (ve.verified):
                # The vendor is known and the email has been verified already.
                ve.update(send_regmail = False)
                session.vendor_id = ve.id
                redirect(URL('sale', 'form'))
                
            if (ve.exists):
                # The vendor is known but the email is to be verified.
                ve.update(send_regmail = True)
                redirect(URL('final'))
            
            else:
                # Vendor is not known yet.
                ve.insert()
                redirect(URL('final'))                

    return(dict(data = data, form = form))


def check():
    i = Ident(shotdb, request.args[0])

    if i.b_verified:
        session.vendor_id = i.id
        session.msg = T('Your email address has been verified.')
        redirect(URL('vendor', 'info'))     
    else:
        msg = T('A problem occurred. Please try again.')

    return dict(msg = msg)


def info():
    
    url = URL('sale', 'form')
    form = FORM(INPUT(_type = 'submit', _class = 'button', _value = T('proceed to the sale numbers')), _action = url)
    
    return dict(msg = session.msg, form = form)


def final():
    return dict()                               

##################################################################################################################          

class VendorEntry():
    '''
    This class provides all methods to add new vendors or to update existing vendor records.  
    '''
    
    def __init__(self, vendor):
        '''
        vendor is a reference to a dict containing the the form/database fields of the vendor record.
        '''
        self.vendor   = vendor
        # self.vendor must not contain an id!
        # Otherwise an error "IntegrityError: PRIMARY KEY must be unique" will occur at the insert and update operations
        # if this id is different from self.id.
        # The only relevant id here is self.id!
        if self.vendor.has_key('id'):
            del self.vendor['id']
            
        self.id       = None
        self.exists   = False
        self.verified = False
        
        # check if vendor is already known to the database      
        q  = shotdb.vendor.name     == self.vendor['name']
        q &= shotdb.vendor.forename == self.vendor['forename']
        q &= shotdb.vendor.email    == self.vendor['email']  
        rows = shotdb(q).select()

        if (len(rows) > 0):
            self.id     = rows[0].id
            self.exists = True
            
            # Check if email address has already been verified.
            ev = rows[0].verified # event number of verification
            if (ev != None and ev > 0):
                self.verified = True
            
    def insert(self):
        '''
        method to add a new vendor to the database
        '''
        self.vendor.code = Ident().code  
        id = shotdb.vendor.insert(**self.vendor)
        Log(shotdb).vendor(id, 'initial')      
        RegistrationMail(shotdb.vendor(id).as_dict()).send()

    def update(self, send_regmail = False):
        '''
        method to update the non-essential fields of a database record
        '''
        # construct string with the old values of the fields to be modified
        oldvendor = shotdb.vendor(self.id)
        s = 'update fields: '
        sep = ''
        for f, v in self.vendor.iteritems():
            ov =oldvendor[f] 
            if ov!= v:
                s +=sep + f + ' (' + str(ov) + ')'
                sep = ', '
        
        shotdb(shotdb.vendor.id == self.id).update(**self.vendor)
        Log(shotdb).vendor(self.id, s)
         
        if (send_regmail):    
            RegistrationMail(shotdb.vendor(self.id).as_dict()).send() 