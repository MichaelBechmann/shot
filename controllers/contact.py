'''
This file contains everything related to the contact form.
'''

# Static analyzer import helpers: (STATIC_IMPORT_MARK)
if 0:
    from gluon.packages.dal.pydal.validators import *
    from gluon import *
    import gluon
    global request
    global response
    global session
    global shotdb
    global T

from shotmail import *
from formutils import *
from urlutils import URLWiki
from shoterrors import ShotErrorRobot

T.force('de')

def form():
    '''
    To reuse the fields and validator messages from the database SQLForm is used instead of FORM.
    Database IO is not intended.
    '''

    display_fields = ['forename', 'name', 'email']

    extra_fields = [Field('category', 'string', label = 'Ihre Nachrich betrifft:', widget = lambda field, value: FoundationWidgetRadio(field, value, config.radio_options_contact, 'general')),

                    Field('message', 'text', label = 'Nachricht:', widget = FoundationWidgetText,
                          comment  = 'Geben Sie hier bitte Ihre Nachricht oder Frage an uns ein.',
                          requires = IS_NOT_EMPTY(error_message = 'Bitte vergessen Sie Ihr Anliegen nicht.'))
                    ]

    form = SQLFORM(shotdb.person,
                   fields = display_fields,
                   extra_fields = extra_fields,
                   formstyle= generateFoundationForm,
                   buttons = [FormButton().send('Nachricht senden')])


    if form.validate(onvalidation = regularizeFormInputPersonForm):
        name  = form.vars.forename + ' ' + form.vars.name
        msg   = form.vars.message
        email = form.vars.email

        if not form.vars.category:
            raise ShotErrorRobot('no category selection in contact form; name: %s, email: %s, msg: %s' % (name, email, msg))
        cat   = form.vars.category

        ContactMail(cat, msg, name, email).send()
        redirect(URLWiki('contact-final'))

    return dict(form=form)
