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
from formutils import generateFoundationForm, FoundationWidgetString, FoundationWidgetPassWord, FormButton


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

auth.messages.invalid_login        = 'Dein Anmeldeversuch ist fehlgeschlagen. Prüfe bitte Benutzernamen und Paßwort.'
auth.messages.registration_pending = 'Du hast Dich erfolgreich als Secondhand-Teammitglied registriert. Dein Benutzerkonto muß noch vom Administrator aktiviert werden.'
auth.messages.profile_updated      = 'Dein Profil wurde aktualisiert.'
auth.messages.password_changed     = 'Dein Paßwort wurde geändert.'
auth.messages.email_sent           = 'An die angegebene Adresse wurde eine E-Mail gesandt. Bitte folge den Instruktionen darin, um den Vorgang zu beenden.'

auth.messages.access_denied        = 'Für diese Aktion fehlt Dir die Zugriffsberechtigung! Um weitergehende Berechtigungen zu erhalten, wende Dich bitte an den Administrator.'

auth.settings.actions_disabled = ['impersonate', 'verify_email']

auth.settings.formstyle = generateFoundationForm


change_form_config = [['password_two',  'Confirm password',     'Wiederhole Dein Paßwort'],
                      ['old_password',  'Old password',         'Dein jetziges Paßwort'],
                      ['new_password',  'New password',         'Dein neues Paßwort'],
                      ['new_password2', 'Confirm new password', 'Wiederhole Dein neues Paßwort']]

def __GetFormElement(i, form):
    name = change_form_config[i][0]
    shotdb.auth_user.password.name    = name
    shotdb.auth_user.password.label   = change_form_config[i][1]
    shotdb.auth_user.password.comment = change_form_config[i][2]
    elem = FoundationWidgetPassWord(shotdb.auth_user.password, None)
    if name in form.errors:
        elem[1].append(DIV(DIV(form.errors[name]), _class = 'error_wrapper'))
    return(DIV(elem))



def user():
    response.flash_custom_display = True #prevent standard display of flash message

    shotdb.auth_user.username.widget  = FoundationWidgetString
    shotdb.auth_user.username.comment = 'Dein Benutzername'

    shotdb.auth_user.password.widget  = FoundationWidgetPassWord
    shotdb.auth_user.password.comment = 'Dein Paßwort'

    shotdb.auth_user.first_name.widget  = FoundationWidgetString
    shotdb.auth_user.first_name.comment = 'Dein Vorname'

    shotdb.auth_user.last_name.widget  = FoundationWidgetString
    shotdb.auth_user.last_name.comment = 'Dein Nachname'

    shotdb.auth_user.email.widget  = FoundationWidgetString
    shotdb.auth_user.email.comment = 'jemand@irgendwo.xy'

    form = auth()


    if len(request.args) > 0:
        method = request.args[0]
    else:
        method = None

    # Some fields (e.g., confirm password field) are not fields of the database table.
    if method == 'register':
        i = 0
        for c in form[0].components:
            if isinstance(c[0], DIV) and '_id' in c[0].attributes and c[0].attributes['_id'] == 'auth_user_password_two':
                form[0].components[i] = __GetFormElement(0, form)
            i = i + 1

    elif method == 'change_password':
        form[0][0] = __GetFormElement(1, form)
        form[0][1] = __GetFormElement(2, form)
        form[0][2] = __GetFormElement(3, form)

    elif method == 'reset_password':
        form[0][0] = __GetFormElement(2, form)
        form[0][1] = __GetFormElement(3, form)


    if method == 'login':
        button_label = 'Login'
    elif method in ['profile', 'change_password']:
        button_label = 'Ändern'
    else:
        button_label = 'Senden'

    form[0][-1] = FormButton().send(button_label)

    return dict(form = form)

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


    emails =  SQLTABLE(u.get_email_subscriptions(),
                    columns  = ('auth_email_type.name','auth_email_type.description'),
                    headers  = {'auth_email_type.name': 'Typ', 'auth_email_type.description': 'Beschreibung'},
                    truncate = None,
                    _class = 'list')

    return dict(name = auth.user.first_name, roles = roles, emails = emails)
