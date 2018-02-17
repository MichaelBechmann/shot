# -*- coding: utf-8 -*-
#from gluon.custom_import import track_changes
#track_changes(True)

# This module comprises all configuration constants for the application shot


import siteconfig

class EMailAccount:
    # This class defines all email account information like addresses, smtp servers, passwords, etc.
    # The first constructor argument selects the account to be used,
    # the second if a special mass mail server shall be used if available.
    def __init__(self, account_id, mass = False):

        if account_id == 'postmaster' or account_id == 'team' or account_id == 'help':
            self.port   = 465
            self.login, self.passwd, self.sender  = siteconfig.email_auth[account_id]
            if mass:
                self.server = siteconfig.email_server['mass']
            else:
                self.server = siteconfig.email_server['normal']

        elif account_id == 'fallback':
            self.server = 'smtp.web.de'
            self.port   = 587
            self.login, self.passwd, self.sender  = siteconfig.email_auth['web.de']
        else:
            # not implemented yet
            pass


class ConfigurationConstants:
    class ConfigMail:
        pass
    mail = ConfigMail()

    class ConfigVerification:
        pass
    verification = ConfigVerification()

    class ConfigNumbers:
        pass
    numbers = ConfigNumbers()

    class ConfigFormName:
        pass
    formname = ConfigFormName()

    class ConfigCssId:
        pass
    cssid = ConfigCssId()

    class ConfigCssClass:
        pass
    cssclass = ConfigCssClass()

    class ConfigMsgClass:
        pass
    msg = ConfigMsgClass()

    class ConfigProgress:
        pass
    progress = ConfigProgress()

    pass

    def __init__(self):
        '''
        Initialize all parameters which are later updated from the database.
        '''
        self.enable_debug           = False # show debug output on each page
        self.enable_extended_menue  = False # expose additional menu items for staff members even when not logged in
        self.enable_registration    = False # expose registration menu item and activate registration.
        self.enable_requests        = False # expose appropriation request menu item
        self.enable_tasks           = False # enable execution of tasks (e.g., send invitation mail etc.)
        self.simulate_mail          = True  # send all generated mails to test address
        self.enable_backup_mail     = False # send additional backup mails to test address
        self.enable_error_mail      = True  # send mail with debug information to admin
        self.redirect_to_ticket     = False # immediately display ticket page

    def update(self, db):
        '''
        This method retrieves ALL configuration parameters from the database and updates the attributes accordingly.
        '''
        for row in db(db.config.id > 0).select():
            if not row.value:
                # no value given => boolean parameter
                setattr(self, row.name.strip(), row.active)

            else:
                setattr(self, row.name.strip(), row.value)


config = ConfigurationConstants()

config.db_connection_string = siteconfig.db_connection_string
config.db_backup_command = siteconfig.db_backup_command

# bulk email error handling
config.bulk_email_number_attempts = 10
config.bulk_email_number_delay_next_attempt = 60 # seconds


config.shoturl          = siteconfig.shoturl
config.shotticketurl    = siteconfig.shotticketurl
config.shotpath         = siteconfig.shotpath
config.appname          = siteconfig.appname

config.mail.simulate_to     = siteconfig.email_simulate_to
config.mail.backup_to       = siteconfig.email_backup_to
config.mail.error_to        = siteconfig.email_error_to
config.mail.contactmail_to  = siteconfig.email_contactmail_to

config.verification.params   = siteconfig.verification_params
config.verification.codelen  = siteconfig.verification_codelen

# strings used as identifying names of form input elements
config.formname.no_contrib      = 'fnnoco'
config.formname.shift           = 'fnshif'
config.formname.donation        = 'fndona'
config.formname.note            = 'fnnote'
config.formname.person_message  = 'fnvmsg'
config.formname.sale_number     = 'fnsnum'

# strings used as ids and classes of html elements
# These must fit the CSS selectors in style sheets and jQuery functions!
config.cssid.salenumber         = 'isnum'
config.cssid.salenumberform     = 'isnumform'
config.cssid.salenumberstatus   = 'isnumstatus'
config.cssid.nocontrib          = 'inoctrb'
config.cssid.contribtblshifts   = 'itblshifts'
config.cssid.contribtbldons     = 'itbldons'
config.cssid.tblsubmit          = 'itblsubm'

config.cssclass.tblconfirmdata  = 'ctblconfdat'
config.cssid.message            = 'imsg'
config.cssid.salesubmit         = 'isubm'
config.cssid.waitmsgtrig        = 'iwaitmsgtrig'
config.cssid.waitmsg            = 'iwaitmsg'

# actual/target display for shifts and donations
config.cssclass.actnumberlow    = 'cactnl'
config.cssclass.actnumbermed    = 'cactnm'
config.cssclass.actnumberhigh   = 'cactnh'
config.cssclass.contribpassive  = 'cctrbpasv'
config.cssclass.contribactive   = 'cctrbactv'
config.cssclass.contribheading  = 'cctrbhead'
config.cssclass.contribnote     = 'ccrtbnote'
config.cssclass.shiftgrouphead  = 'csftgrphead'
config.cssclass.shiftgrouptbl   = 'csftgrptbl'
config.cssclass.shifttblrow     = 'csfttblrow'
config.cssclass.shiftcomment    = 'csftcomment'
config.cssclass.confirmcomment  = 'ccfrmcomment'
config.cssclass.configwarn      = 'ccnfwarn'

config.cssclass.tggl            = 'ctggl'
config.cssclass.tggltrig        = 'ctggltrig'

config.cssclass.progressbar     = 'cprogressbar'
config.cssclass.progresslabel   = 'cprogresslabel'
config.cssclass.progresssteps   = 'cprogresssteps'
config.cssclass.progressdone    = 'cprogressdone'
config.cssclass.progressmissing = 'cprogressmissing'
config.cssclass.progresscurrent = 'cprogresscurrent'

config.msg.wait                 = 'The processing of your data takes some time. Please be patient ...'



config.progress.registration_sale = {'label': 'Ihr Gesamtfortschritt bei der Anmeldung',
                                     'steps': ['Registrierungsformular ausfüllen',
                                               'Registrierung überprüfen und absenden',
                                               'E-Mail-Adresse verifizieren',
                                               'Anmeldeformular zum Markt ausfüllen',
                                               'Anmeldung zum Markt überprüfen und absenden']
                                     }
config.progress.appropriation     = {'label': 'Ihr Fortschritt',
                                     'steps': ['Antragsformular ausfüllen',
                                               'Antrag überprüfen und absenden']
                                     }



config.colsets = {}
config.colsets['sale'] = { 'sets':{'edit':      ['sale.id', 'sale.person', 'person.place', 'sale.number', 'sale.number_unikey'],
                                   'default':   ['sale.person', 'person.place', 'sale.number'],
                                   'event':     ['sale.event', 'sale.person', 'person.place', 'sale.number'],
                                   'sign list': ['sale.number', 'person.name', 'person.forename', 'person.place', 'person.street', 'person.house_number', 'person.telephone']
                                   },
                           'default': 'default'
                         }
config.colsets['wait'] = { 'sets':{'edit':      ['wait.id', 'wait.person', 'sale.number', 'wait.denial_sent'],
                                   'default':   ['wait.person', 'sale.number', 'wait.denial_sent'],
                                   'event':     ['wait.event', 'wait.person', 'sale.number', 'wait.denial_sent']
                                   },
                           'default': 'default'
                         }

config.colsets['bring'] = { 'sets':{'edit':         ['bring.id', 'bring.person', 'person.place', 'donation.item', 'bring.note'],
                                   'default':       ['bring.person', 'person.place', 'donation.item', 'bring.note', 'sale.number'],
                                   'event':         ['donation.event', 'bring.person', 'person.place', 'donation.item', 'bring.note'],
                                   'plain to copy': ['bring.person', 'donation.item', 'bring.note', 'sale.number']
                                   },
                           'default': 'default'
                         }
config.colsets['help'] = { 'sets':{'edit':          ['help.id', 'help.person', 'person.place', 'shift.activity', 'shift.day', 'shift.time'],
                                   'default':       ['help.person', 'person.place', 'shift.activity', 'shift.day', 'shift.time'],
                                   'event':         ['shift.event', 'help.person', 'person.place', 'shift.activity', 'shift.day', 'shift.time'],
                                   'plain to copy': ['help.person', 'shift.activity', 'shift.day', 'shift.time']
                                   },
                           'default': 'default'
                         }

config.colsets['message'] = { 'sets':{'edit':    ['message.id', 'message.person', 'person.place', 'message.text'],
                                      'default': ['message.person', 'person.place', 'message.text'],
                                      'event':   ['message.event', 'message.person', 'person.place', 'message.text'],
                                   },
                           'default': 'default'
                         }
config.colsets['person'] = { 'sets':{'edit/details':  ['person.id', 'person.name', 'person.forename', 'person.place', 'person.zip_code', 'person.street', 'person.house_number', 'person.email', 'person.telephone'],
                                     'default' :      ['person.name', 'person.forename', 'person.place', 'person.email', 'person.telephone'],
                                     'technical':     ['person.id', 'person.name', 'person.forename', 'person.code', 'person.verified', 'person.mail_enabled', 'person.log']
                                   },
                           'default': 'default'
                         }
config.colsets['request'] = { 'sets':{'request':        ['request.id', 'request.project', 'request.organization', 'request.amount_total', 'request.amount_requested', 'request.description'],
                                      'appropriation':  ['request.id', 'request.project', 'request.person', 'request.status', 'request.amount_total', 'request.amount_requested', 'request.amount_spent', 'request.comment']
                                   },
                           'default': 'request'
                         }
config.colsets['shift'] = { 'sets':{'config':  ['shift.id', 'shift.activity', 'shift.scope', 'shift.target_number', 'shift.day', 'shift.time', 'shift.display'],
                                    'comment': ['shift.id', 'shift.activity', 'shift.target_number', 'shift.day', 'shift.time', 'shift.display', 'shift.comment'],
                                    'event':   ['shift.event', 'shift.activity', 'shift.target_number', 'shift.day', 'shift.time']
                                   },
                           'default': 'config'
                         }
config.colsets['donation'] = { 'sets':{'config': ['donation.id', 'donation.item', 'donation.target_number', 'donation.enable_notes'],
                                       'event':  ['donation.event', 'donation.item', 'donation.target_number', 'donation.enable_notes']
                                   },
                           'default': 'config'
                         }



config.colsets_auth = {}
config.colsets_auth['user']               = ['auth_user.id', 'auth_user.username', 'auth_user.first_name', 'auth_user.last_name', 'auth_user.email', 'auth_user.registration_key', 'auth_user.person', 'auth_user.sale_numbers']
config.colsets_auth['group']              = ['auth_group.id', 'auth_group.role', 'auth_group.description']
config.colsets_auth['permission']         = ['auth_permission.id', 'auth_permission.group_id', 'auth_permission.name', 'auth_permission.table_name']
config.colsets_auth['membership']         = ['auth_membership.id', 'auth_membership.user_id', 'auth_membership.group_id']
config.colsets_auth['event']              = ['auth_event.id', 'auth_event.user_id', 'auth_event.description', 'auth_event.time_stamp', 'auth_event.client_ip']
config.colsets_auth['email_subscription'] = ['auth_email_subscription.id', 'auth_email_subscription.user_id', 'auth_email_subscription.email_type_id']


config.shift_scopes = ('public', 'team')

