'''
This file contains everything related to the vendor registration.
'''
# Static analyzer import helpers: (STATIC_IMPORT_MARK)
if 0: 
    from gluon.languages import translator as T
    from gluon import *
    import gluon
    global request
    global response
    global session
    global shotdb    


from shotmail import *

T.force('de')

def form():
    # check if vendor registration  is enabled
    if config.enableregis == False:
        redirect(URL('main', 'index'))
        
        
    display_fields = ['forename', 'name', 'place', 'zip_code', 'street', 'house_number', 'telephone', 'email', 'kindergarten']
    comments = {'kindergarten': T('Please indicate if you have a child in one of the kindergartens in Ottersweier.')}
    i=Ident()  
    form = SQLFORM(shotdb.vendor, fields = display_fields, hidden = {'code': i.code}, submit_button = T('submit'), col3 = comments)
    
    # pre-populate the form in case of re-direction from form_vendor_confirm() (back button pressed)
    # see book, section 'Pre-populating the form' in chapter 'Forms and Validators'
    form.vars.kindergarten = '' # do not use config.no_kindergarten_id here to initialize form with empty field
    if session.vendor:
        form.vars = session.vendor
    
    
    # Copy request to form field as described in web2py book, chapter 'Forms and Validators'
    form.vars.code = request.vars.code
    
    
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
                         INPUT(_type = 'submit', _class = 'button', _name = 'submit send', _value = T('go!'))
                         )
                       )
                )
        
    if 'submit back' in request.vars:
        redirect(URL('form'))
    elif 'submit send' in request.vars:
        #response.flash = 'Send button has been pressed!'
            
        # Add the vendor information to the database and send mail:
        if session.vendor != None:  
            id = db.vendor.insert(**session.vendor)
            session.vendor = None # prevent multiple database entries
            rm = RegistrationMail(db.vendor(id).as_dict())
            rm.send()         
            #response.flash = 'Registration mail has been sent!'
            redirect(URL('final'))
    else:
        #response.flash = 'Nothing has been pressed!'
        pass
        
    return(dict(data = data, form = form))



def check():
    
    b_success = False
    try:
        i = Ident()
        i.set_linkcode(request.args[0])
        b_success = i.verify()
        session.id = i.id
    except:
        pass
    
    
    if(b_success):
        msg = 'Your email address has been verified. You may proceed to the next step.'
        url = URL('sale', 'form')
    else:
        msg = 'A problem occurred. Please try again.'
        url = URL('main', 'index')

    form = FORM(INPUT(_type = 'submit', _class = 'button', _value = T('proceed to the sale numbers')), _action = url)

    
    return dict(form = form, id = session.id)


def final():
    return dict()                               

##################################################################################################################
'''
Unfortunately, I didn't manage to move the material below to the modules folder.
'''

import random
import string
import re


class Ident():
    '''
    This class provides methods for the generation of identification codes and their verification.
    The identification link shall not display the variables used. Instead a single identification string
    comprising the database id and the code shall be used.
    '''
    
    def __init__(self):
        '''
        This method generates a random identification code.
        The code shall start with a first letter, not a digit.
        '''
        char = string.ascii_lowercase + string.digits
        self.code = random.choice(string.ascii_lowercase) + ''.join([random.choice(char) for i in range(12)])
        

    def set_linkcode(self, linkcode):
        self.linkcode = linkcode
        self.id = 0
        
        p = re.compile('([0-9]+)')
        m = p.match(self.linkcode)
        if(m):
            self.id = int(m.group(0))
            self.code = self.linkcode.replace(m.group(0),'',1)
        
    def verify(self):
        '''
        This method checks if the code matches the data base entry referenced by the id.
        If so, the successful code verification is stored in the data base.
        '''
        
        b_match = False
        vendor = db.vendor(self.id)
        if(vendor != None):            
            if(self.code == vendor.code):
                b_match = True
                db(db.vendor.id == self.id).update(verified = True)
              
        return b_match
