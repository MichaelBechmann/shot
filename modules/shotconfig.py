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

config = ConfigurationConstants()

config.db_connection_string = siteconfig.db_connection_string
config.db_backup_command = siteconfig.db_backup_command

config.debug            = siteconfig.debug
config.enableregis      = siteconfig.enableregis
config.enablerequest    = siteconfig.enablerequest
config.enable_tasks     = siteconfig.enable_tasks
config.showadminitems   = siteconfig.showadminitems

config.shoturl          = siteconfig.shoturl
config.shotpath         = siteconfig.shotpath
config.appname          = siteconfig.appname

config.staffpassword = siteconfig.passwd_staff
config.adminpassword = siteconfig.passwd_admin

config.mail.simulate_mail   = siteconfig.simulate_mail
config.mail.simulate_to     = siteconfig.email_simulate_to
config.mail.backup_to       = siteconfig.email_backup_to
config.mail.error_to        = siteconfig.email_error_to
config.mail.contactmail_to  = siteconfig.email_contactmail_to

config.email_backup_enabled = siteconfig.email_backup_enabled


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
