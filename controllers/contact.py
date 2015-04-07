'''
This file contains everything related to the contact form.
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
from formutils import regularizeName
from urlutils import URLWiki

T.force('de')

def __regularize_form_input(form):
    '''
    This function brings the user input to standard.
    '''
    for field in ('forename', 'name'):
        form.vars[field] = regularizeName(form.vars[field])

def form():
    '''
    To reuse the fields and validator messages from the database SQLForm is used instead of FORM.
    Database IO is not intended.
    '''
    
    display_fields = ['forename', 'name', 'email']
     
    form = SQLFORM(shotdb.person, fields = display_fields, submit_button = T('go!'))
    
    # Add additional elements: see web2py book, 'Forms and Validators'
    
    
    form[0].insert(-1, TR('',                TD( INPUT(_type='radio', _name='category', _value = 'help'),                       T('regards the help shifts and donations.'))))
    form[0].insert(-1, TR(T('My message:'),  TD( INPUT(_type='radio', _name='category', _value = 'tech'),                       T('regards technical problems with this webpage.'))))
    form[0].insert(-1, TR('',                TD( INPUT(_type='radio', _name='category', _value = 'general', value = 'general'), T('regards other matters.'))))
            
    form[0].insert(-1, TR('',   TEXTAREA(_type = 'text', _name='message', _cols = 50, _rows = 8)))
     
        
        
    if form.validate(onvalidation = __regularize_form_input): 
        cat   = form.vars.category 
        name  = form.vars.forename + ' ' + form.vars.name
        msg   = form.vars.message
        email = form.vars.email

        ContactMail(cat, msg, name, email).send()
        redirect(URLWiki('contact-final'))
    
    return dict(form=form)
