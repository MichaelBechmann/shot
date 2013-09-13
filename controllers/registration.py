'''
This file contains everything related to the registration of persons.
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
from shoterrors import ShotError
from miscutils import regularizeName

T.force('de')


def __regularize_form_input(form):
    '''
    This function brings the user input to standard.
    '''
    form.vars.forename = regularizeName(form.vars.forename)
    form.vars.name     = regularizeName(form.vars.name)
    form.vars.street   = regularizeName(form.vars.street)
    form.vars.place    = regularizeName(form.vars.place)
    

def form():

    # do the identity check first so that users can verify their email contact by clicking on the invitation link
    i = Ident(shotdb, *request.args)
    
    # check if registration  is enabled    
    if config.enableregis == False:
        redirect(URL('registration', 'locked'))

        
    display_fields = ['forename', 'name', 'place', 'zip_code', 'street', 'house_number', 'telephone', 'email']
    form = SQLFORM(shotdb.person, fields = display_fields, submit_button = T('submit'))
    
    if i.b_verified:
        # pre-populate form if function is called with personal code link
        # To prevent mixing up fields (e.g., id, log, verified, code) between persons only the fields displayed in the form must be copied to vars!!!
        # Note that errors "IntegrityError: PRIMARY KEY must be unique" occur if false 'id' fields of the form would propagate to the insert or update operations!
        form.vars = Storage()
        for f in display_fields:
            form.vars[f] = i.person[f]
        # Note: The SQLFORM constructor augments the list of fields with 'id'!
        del form.vars['id']
        # prevent wrong initialization of the later sale form when several users register from the same machine 
        session.sale_vars = None
        
    elif session.person:
        # pre-populate the form in case of re-direction from confirmation page (back button pressed)
        # see book, section 'Pre-populating the form' in chapter 'Forms and Validators'
        form.vars = session.person        
        
    
    # There is a mistake in the book: form.validate() returns True or False. form.process() returns the form itself
    # see http://osdir.com/ml/web2py/2011-11/msg00467.html
    if form.validate(onvalidation = __regularize_form_input):
        session.person = form.vars 
        redirect(URL('registration','confirm'))
        
    return dict(form=form)

def confirm():
    # check if there is personal information to be confirmed
    if session.person == None:
        raise ShotError('Registration confirm page entered without identified person.')

    # construct display of data to be confirmed
    data_items = [
                   TR(T('Your name:'), session.person['forename'] + ' ' + session.person['name']),
                   TR(T('Your address:'), session.person['zip_code'] + ' ' + session.person['place'] + ', ' + session.person['street'] + ' ' + session.person['house_number'] ),
                   TR(T('Your telephone number:'), session.person['telephone']),
                   TR(T('Your email address:'), session.person['email'])
                ]
        
    data = TABLE(*data_items, _id = config.cssid.tblconfirmdata)           
    
    
    # The _name arguments are important as the one of the pressed button will appear in request.vars.
    form = FORM(TABLE(TR(
                         INPUT(_type = 'submit', _class = 'button', _name = 'submit back', _value = T('back')),
                         INPUT(_type = 'submit', _class = 'button', _name = 'submit send', _value = T('go!'), _id = config.cssid.waitmsgtrig)
                         )
                       ),
                DIV(T(config.msg.wait), _id = config.cssid.waitmsg)
                )

        
    if 'submit back' in request.vars:
        redirect('form')
    elif 'submit send' in request.vars:
        if session.person != None:
            
            pe = PersonEntry(session.person)
            
            # Prevent multiple database entries
            # Note: The reference to the object session.person can be deleted here.
            # The data persist in memory and the object pe contains a duplicate private reference.
            session.person = None 
            if (pe.verified):
                # The person is known and the email has been verified already.
                pe.update(send_regmail = False)
                session.person_id = pe.id
                nextpage = URL('sale', 'form')
                    
            elif (pe.exists):
                # The person is known but the email is to be verified.
                pe.update(send_regmail = True)
                nextpage = URL('final')  
                
            else:
                # person is not known yet.
                pe.insert()
                nextpage = URL('final')  
            
            
            redirect(nextpage)

    return(dict(data = data, form = form))


def check():
    # check if registration is enabled
    if config.enableregis == False:
        redirect(URL('registration', 'locked'))
        
    i = Ident(shotdb, request.args[0])

    if i.b_verified:
        session.clear()
        session.person_id = i.id
        redirect(URL('info'))
   
    return dict()


def info():
    url = URL('sale', 'form')
    form = FORM(INPUT(_type = 'submit', _class = 'button', _value = 'Weiter zu den Helferschichten und Kommissionsnummern'), _action = url)
    return dict(form = form)

def final():
    return dict()    

def disable_mail(): 
    # This function is called from a dedicated personal link in e-mails.
    # The personal id and code are checked and a disable flag is set in the database for the respective person entry. 
    c = None
    i = Ident(shotdb, request.args[0])
    if i.b_verified:
        pe = PersonEntry(i.person.as_dict())
        pe.disable_mail()
        c = i.person.forename + ' ' + i.person.name + ', ' + i.person.email

    return dict(c = c)             

def locked():
    return dict()
##################################################################################################################          

class PersonEntry():
    '''
    This class provides all methods to add new persons or to update existing person records.  
    '''
    
    def __init__(self, person):
        '''
        person is a reference to a dict containing the the form/database fields of the person record.
        '''
        self.person   = person
        # self.person must not contain an id!
        # Otherwise an error "IntegrityError: PRIMARY KEY must be unique" will occur at the insert and update operations
        # if this id is different from self.id.
        # The only relevant id here is self.id!
        if self.person.has_key('id'):
            del self.person['id']
            
        self.id       = None
        self.exists   = False
        self.verified = False
        
        # check if person is already known to the database      
        q  = shotdb.person.name     == self.person['name']
        q &= shotdb.person.forename == self.person['forename']
        q &= shotdb.person.email    == self.person['email']  
        rows = shotdb(q).select()

        if (len(rows) > 0):
            self.id     = rows[0].id
            self.exists = True
            
            # Check if email address has already been verified.
            ev = rows[0].verified # event number of verification
            if (ev != None and ev > 0):
                self.verified = True
                
        # By default, every registration of a person (new or update) (re-) enables round mails.
        self.person['mail_enabled'] = True
            
    def insert(self):
        '''
        method to add a new person to the database
        '''
        self.person.code = Ident().code  
        id = shotdb.person.insert(**self.person)
        Log(shotdb).person(id, 'initial')      
        RegistrationMail(shotdb, id).send()

    def update(self, send_regmail = False):
        '''
        method to update the non-essential fields of a database record
        '''
        # construct string with the old values of the fields to be modified
        oldperson = shotdb.person(self.id)
        s = 'update fields: '
        sep = ''
        for f, v in self.person.iteritems():
            op =oldperson[f] 
            if op != v:
                s +=sep + f + ' (' + str(op) + ')'
                sep = ', '
        
        shotdb(shotdb.person.id == self.id).update(**self.person)
        Log(shotdb).person(self.id, s)
         
        if (send_regmail):    
            RegistrationMail(shotdb, self.id).send() 
            
    def disable_mail(self):
        '''
        This method sets the flag in the person entry to disable round mails.
        '''
        self.person['mail_enabled'] = False
        self.update(False)
        
        