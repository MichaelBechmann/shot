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
from formutils import regularizeFormInputPersonorm, getPersonDataTable
import re

T.force('de')


def form():

    # do the identity check first so that users can verify their email contact by clicking on the invitation link
    i = Ident(shotdb, *request.args)
    
    # check if registration  is enabled    
    if config.enable_registration == False:
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
        
    elif session.registration_person:
        # pre-populate the form in case of re-direction from confirmation page (back button pressed)
        # see book, section 'Pre-populating the form' in chapter 'Forms and Validators'
        form.vars = session.registration_person        
        
    
    # There is a mistake in the book: form.validate() returns True or False. form.process() returns the form itself
    # see http://osdir.com/ml/web2py/2011-11/msg00467.html
    if form.validate(onvalidation = regularizeFormInputPersonorm):
        session.registration_person = form.vars
        session.b_registration_active = True
        redirect(URL('registration','confirm'))
        
    return dict(form=form)

def confirm():
    # check if there is personal information to be confirmed
    if session.registration_person == None:
        redirect(URL('main','index'))

    # construct display of data to be confirmed
    data = getPersonDataTable(session.registration_person)          
    
    
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
            
        pe = PersonEntry(shotdb, session.registration_person)
        # By default, every registration of a person (new or update) (re-) enables round mails.
        pe.set_mail_enabled()
        
        # Prevent multiple database entries
        # Note: The reference to the object session.registration_person can be deleted here.
        # The data persist in memory and the object pe contains a duplicate private reference.
        session.registration_person = None 
        if (pe.verified):
            # The person is known and the email has been verified already.
            pe.update()
            session.registration_person_id = pe.id
            nextpage = URL('sale', 'form')
                
        elif (pe.exists):
            # The person is known but the email is to be verified.
            pe.update()
            shotdb.commit()
            RegistrationMail(shotdb, pe.id).send() 
            nextpage = URL('final')  
            
        else:
            # person is not known yet.
            pe.insert()
            shotdb.commit()
            RegistrationMail(shotdb, pe.id).send()
            nextpage = URL('final')  
        
        redirect(nextpage)

    return(dict(data = data, form = form))


def check():
    # check if registration is enabled
    if config.enable_registration == False:
        redirect(URL('registration', 'locked'))
        
    i = Ident(shotdb, request.args[0])

    if i.b_verified:
        session.clear()
        session.registration_person_id = i.id
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
        pe = PersonEntry(shotdb, i.person.as_dict())
        pe.disable_mail()
        c = i.person.forename + ' ' + i.person.name + ', ' + i.person.email

    return dict(c = c)             

def locked():
    return dict()
            
        
        