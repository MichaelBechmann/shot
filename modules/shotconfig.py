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
                self.server = 'mass.selfhost.de'
            else:
                self.server = 'mail.selfhost.de'
            
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
   
    pass

    def __init__(self):
        '''
        Initialize all parameters which are later updated from the database.
        '''
        # flag to check whether of not the config object shall be updated after definition of the database model
        self.initial_update = False #
        
        self.enable_debug           = False # show debug output on each page
        self.enable_extended_menue  = False # expose additional menu items for staff members even when not logged in
        self.enable_registration    = False # expose registration menu item and activate registration.
        self.enable_requests        = False # expose appropriation request menu item
        self.enable_tasks           = False # enable execution of tasks (e.g., send invitation mail etc.)
        self.simulate_mail          = True  # send all generated mails to test address
        self.enable_backup_mail     = False # send additional backup mails to test address
        

    def update(self, db):
        '''
        This method retrieves ALL configuration parameters from the database and updates the attributes accordingly.
        '''
        for row in db(db.config.id > 0).select():
            if not row.value and row.active != None:
                # no value given => boolean parameter
                setattr(self, row.name.strip(), row.active)

        
    def update_initial(self, db):
        '''
        The parameter update from the database can be done only after the database model has been executed!
        This method is used to avoid that this update is done EVERY TIME the database model is executed.
        '''
        if not self.initial_update:
            self.update(db)
        self.initial_update = True


config = ConfigurationConstants()

config.db_connection_string = siteconfig.db_connection_string
config.db_backup_command = siteconfig.db_backup_command


config.shoturl          = siteconfig.shoturl
config.shotpath         = siteconfig.shotpath
config.appname          = siteconfig.appname

config.mail.simulate_to     = siteconfig.email_simulate_to
config.mail.backup_to       = siteconfig.email_backup_to
config.mail.error_to        = siteconfig.email_error_to
config.mail.contactmail_to  = siteconfig.email_contactmail_to


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

config.msg.wait                 = 'The processing of your data takes some time. Please be patient ...'



config.colsets = {}      
config.colsets['sale'] = { 'sets':{'details' : ['sale.id', 'sale.event', 'person.name', 'person.forename', 'person.place', 'sale.number', 'sale.number_unikey'], 
                                   'default'  : ['sale.event', 'person.name', 'person.forename', 'sale.number'],
                                   'sign list': ['sale.number','person.name', 'person.forename', 'person.place', 'person.street', 'person.house_number', 'person.telephone']
                                   },
                           'default': 'default'
                         }
config.colsets['wait'] = { 'sets':{'details' : ['wait.id', 'wait.event', 'person.name', 'person.forename', 'sale.number', 'wait.denial_sent'],
                                   },
                           'default': 'details'
                         }

config.colsets['bring'] = { 'sets':{'details': ['bring.id', 'donation.event', 'person.name', 'person.forename', 'person.place', 'donation.item', 'bring.note'], 
                                   'default'  : ['person.name', 'person.forename', 'donation.item', 'bring.note']
                                   },
                           'default': 'default'
                         }
config.colsets['help'] = { 'sets':{'details' : ['help.id', 'shift.event', 'person.name', 'person.forename', 'person.place', 'shift.activity', 'shift.day', 'shift.time'], 
                                   'default'  : ['person.name', 'person.forename', 'shift.activity', 'shift.day', 'shift.time'],
                                   },
                           'default': 'default'
                         }

config.colsets['message'] = { 'sets':{'details': ['message.id', 'message.event', 'person.name', 'person.forename', 'person.place', 'message.text'], 
                                       'default': ['person.name', 'person.forename', 'message.text']
                                   },
                           'default': 'default'
                         }
config.colsets['person'] = { 'sets':{'details':  ['person.id', 'person.name', 'person.forename', 'person.place', 'person.zip_code', 'person.street', 'person.house_number', 'person.email', 'person.telephone'],
                                     'default' : ['person.name', 'person.forename', 'person.place', 'person.email', 'person.telephone'],
                                     'technical':['person.id', 'person.name', 'person.forename', 'person.code', 'person.verified', 'person.mail_enabled', 'person.log']
                                   },
                           'default': 'default'
                         }
config.colsets['request'] = { 'sets':{'request':  ['request.id', 'request.project', 'request.organization', 'request.amount_total', 'request.amount_requested', 'request.description'],
                                      'appropriation' : ['request.id', 'request.project', 'request.person', 'request.status', 'request.amount_total', 'request.amount_requested', 'request.amount_spent', 'request.comment']
                                   },
                           'default': 'request'
                         }
config.colsets['shift'] = { 'sets':{'config':  ['shift.id', 'shift.activity', 'shift.target_number', 'shift.day', 'shift.time', 'shift.display'],
                                    'comment': ['shift.id', 'shift.activity', 'shift.day', 'shift.time', 'shift.comment']
                                   },
                           'default': 'config'
                         }
config.colsets['donation'] = { 'sets':{'all':  ['donation.id', 'donation.item', 'donation.target_number', 'donation.enable_notes']
                                   },
                           'default': 'all'
                         }



config.colsets_auth = {}
config.colsets_auth['user'] = ['auth_user.id', 'auth_user.username', 'auth_user.first_name', 'auth_user.last_name', 'auth_user.email', 'auth_user.registration_key', 'auth_user.created_on']
config.colsets_auth['group'] = ['auth_group.id', 'auth_group.role', 'auth_group.description']
config.colsets_auth['permission'] = ['auth_permission.id', 'auth_permission.group_id', 'auth_permission.name', 'auth_permission.table_name', 'auth_permission.record_id']
config.colsets_auth['membership'] = ['auth_membership.id', 'auth_membership.user_id', 'auth_membership.group_id']

# waffle recipe
config.recipe_list = (('300 g', 'Margarine'),
                      ('200 g', 'Zucker'),
                      ('2  Päckchen', 'Vanillezucker'),
                      ('1 Prise', 'Salz'),
                      ('6', 'Eier'), 
                      ('500 g', 'Mehl'),
                      ('2 Teelöffel', 'Backpulver'),
                      ('500 ml', 'Wasser')
                     )
