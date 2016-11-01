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
    global auth


from shotconfig import * 
from shotmail import *
from shotdbutil import *
from gluon.storage import Storage
from shoterrors import ShotError, ShotErrorRobot
from formutils import regularizeFormInputPersonorm, getPersonDataTable
from urlutils import URLWiki
import re

T.force('de')


def form():
    # detect robots
    if len(request.args) > 1:
        raise ShotErrorRobot('registration form called with too many arguments: %s' % ', '.join(request.args))
    
    # do the identity check first so that users can verify their email contact by clicking on the invitation link even if the registration is closed.
    i = Ident(shotdb, *request.args)
    
    # check if registration  is enabled    
    if config.enable_registration == False:
        redirect(URLWiki('registration-locked'))
        
        
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
        # store verified person id to facilitate modification of essential person data
        session.registration_person_id = i.id
        
    elif session.registration_person:
        # pre-populate the form in case of re-direction from confirmation page (back button pressed)
        # see book, section 'Pre-populating the form' in chapter 'Forms and Validators'
        form.vars = session.registration_person        
        
    
    # There is a mistake in the book: form.validate() returns True or False. form.process() returns the form itself
    # see http://osdir.com/ml/web2py/2011-11/msg00467.html
    if form.validate(onvalidation = regularizeFormInputPersonorm):
        session.registration_person = form.vars
        redirect(URL('registration','confirm'))
        
    return dict(form=form)

def confirm():
    # check if there is personal information to be confirmed
    if session.registration_person == None:
        redirect(URLWiki('start'))
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
            
        pe = PersonEntry(shotdb, session.registration_person, session.registration_person_id)
        # By default, every registration of a person (new or update) (re-) enables round mails.
        pe.set_mail_enabled()
        
        # Prevent multiple database entries
        # Note: The reference to the object session.registration_person can be deleted here.
        # The data persist in memory and the object pe contains a duplicate private reference.
        session.registration_person = None 
        if pe.verified:
            # The person is known and the email has been verified already.
            pe.update()
            session.registration_person_id = pe.id
            nextpage = URL('sale', 'form')
                
        elif pe.exists:
            # The person is known but the email is yet to be verified.
            if pe.email_changed :
                pe.reset_verification()
            pe.update()
            session.registration_person_id = None
            shotdb.commit()
            RegistrationMail(auth, pe.id).send()
            nextpage = URLWiki('registration-final')
            
        else:
            # person is not known yet.
            pe.insert()
            session.registration_person_id = None
            shotdb.commit()
            RegistrationMail(auth, pe.id).send()
            nextpage = URLWiki('registration-final')
        
        redirect(nextpage)

    return(dict(data = data, form = form))


def check():
    # check if registration is enabled
    if config.enable_registration == False:
        redirect(URLWiki('registration-locked'))
    
    if request.args:
        code = request.args[0]
    else:
        code = None
       
    i = Ident(shotdb, code)

    if i.b_verified:
        
        # remove all data from session object in order to not mix up data from different persons in the following sale form
        # Note: session.clear() must not be used because then the session file will not be written anymore and the id below will get lost!
        keys = [k for k in session.iterkeys()]
        for k in keys:
            del session[k]
            
        session.registration_person_id = i.id
        redirect(URLWiki('registration-email-cofirmed'))
   
    redirect(URLWiki('registration-check-error'))


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

            
        
        