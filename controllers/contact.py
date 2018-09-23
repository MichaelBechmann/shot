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
from shoterrors import ShotErrorRobot

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


    form[0].insert(-1, TR('',                TD( INPUT(_type='radio', _name='category', _value = 'help'),                       'betrifft die Helferschichten oder Spenden.')))
    form[0].insert(-1, TR(T('My message:'),  TD( INPUT(_type='radio', _name='category', _value = 'tech'),                       'betrifft technische Probleme mit dieser Seite.')))
    form[0].insert(-1, TR(T(''),             TD( INPUT(_type='radio', _name='category', _value = 'data'),                       'Anliegen zum Schutz persönlicher Daten, z.B. einen Löschauftrag.')))
    form[0].insert(-1, TR('',                TD( INPUT(_type='radio', _name='category', _value = 'general', value = 'general'), 'betrifft sonstiges.')))

    form[0].insert(-1, TR('',   TEXTAREA(_type = 'text', _name='message', _cols = 50, _rows = 8)))


    if form.validate(onvalidation = __regularize_form_input):
        name  = form.vars.forename + ' ' + form.vars.name
        msg   = form.vars.message
        email = form.vars.email

        if not form.vars.category:
            raise ShotErrorRobot('no category selection in contact form; name: %s, email: %s, msg: %s' % (name, email, msg))
        cat   = form.vars.category

        ContactMail(cat, msg, name, email).send()
        redirect(URLWiki('contact-final'))

    return dict(form=form)
