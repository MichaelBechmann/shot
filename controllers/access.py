# Static analyzer import helpers: (STATIC_IMPORT_MARK)
if 0:
    from gluon import *
    from gluon.languages import translator as T
    global request
    global response
    global session
    global shotdb
    global SQLField
    global auth
    global config
    global shotdb
    
from shotconfig import EMailAccount
from shotdbutil import User
from urlutils import URLWiki

auth.settings.login_next           = URL('info' )
auth.settings.logout_next          = URLWiki('start')
auth.settings.reset_password_next  = URL('info')
auth.settings.change_password_next = URL('info')
auth.settings.profile_next         = URL('info')


auth.settings.request_reset_password_next = URL('msg')
auth.settings.register_next               = URL('msg')
auth.settings.retrieve_username_next      = URL('msg')

account = EMailAccount('postmaster')
auth.settings.mailer.settings.server = account.server
auth.settings.mailer.settings.sender = account.sender
auth.settings.mailer.settings.login  = '%s:%s' % (account.login, account.passwd)

auth.settings.login_after_registration = False
auth.settings.registration_requires_approval = True
auth.settings.remember_me_form = False

auth.messages.invalid_login        = 'Ihr Anmeldeversuch ist fehlgeschlagen. Prüfen Sie bitte Benutzernamen und Paßwort.'
auth.messages.registration_pending = 'Sie haben sich erfolgreich als Secondhand-Teammitglied registriert. Ihr Benutzerkonto muß noch vom Administrator aktiviert werden.'
auth.messages.profile_updated      = 'Ihr Profil wurde aktualisiert.'
auth.messages.password_changed     = 'Ihr Paßwort wurde geändert.'
auth.messages.email_sent           = 'An die angegebene Adresse wurde eine E-Mail gesandt. Bitte folgen Sie den Instruktionen darin, um den Vorgang zu beenden.'

auth.messages.access_denied        = 'Für diese Aktion fehlt Ihnen die Zugriffsberechtigung! Um weitergehende Berechtigungen zu erhalten, wenden Sie sich bitte an Ihren Administrator.'

auth.settings.actions_disabled = ['impersonate', 'verify_email']


def user():
    response.flash_custom_display = True #prevent standard display of flash message
    return dict(form=auth())

def msg():
    response.flash_custom_display = True
    return dict()

@auth.requires_login()
def info():
    response.flash_custom_display = True
    u = User(shotdb, auth.user.id)
        
    roles = SQLTABLE(u.get_groups(),
                     columns  = ('auth_group.role', 'auth_group.description'),
                     headers  = {'auth_group.role': 'Rolle', 'auth_group.description': 'Beschreibung'},
                     truncate = None,
                     _class   = 'list')
    
    return dict(name = auth.user.first_name, roles = roles)
