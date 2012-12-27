# -*- coding: utf-8 -*-
#from gluon.custom_import import track_changes
#track_changes(True)
"""
This module comprises all configuration constants for the application shot
"""

import siteconfig

class EMailAccount:
    """
    This class defines all email account information like addresses, smtp servers, passwords, etc.
    The costructor argument selects the account to be used:
        shot_staff - for all Second Hand Ottersweier staff members
    """
    def __init__(self, id):
        if id == 'shot_staff':
            self.server = 'smtp.web.de'
            self.port   = 587
            self.login   = 'secondhand.ottersweier'
            self.passwd = siteconfig.passwd_mail
            self.sender = 'Second Hand Ottersweier <secondhand.ottersweier@web.de>'
        else:
            # not implemented yet
            pass
          

class ConfigurationConstants:
    class ConfigMail:
        pass
    regmail     = ConfigMail()
    invmail     = ConfigMail()  
    numbermail  = ConfigMail()
    contactmail = ConfigMail()
    
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

config.debug            = siteconfig.debug
config.enableregis      = siteconfig.enableregis
config.showadminitems   = siteconfig.showadminitems

config.shoturl          = siteconfig.shoturl

config.staffpassword = siteconfig.passwd_staff
config.adminpassword = siteconfig.passwd_admin

config.backup_to     = 'michael_bechmann@yahoo.de'

config.regmail.template       = siteconfig.shotpath + 'static/mail_templates/registration_de.html'
config.regmail.subject        = 'Registrierung als Verkäufer'
config.regmail.linkbase       = siteconfig.shoturl + 'vendor/check/'

config.invmail.template       = siteconfig.shotpath + 'static/mail_templates/invitation_de.html'
config.invmail.subject        = 'Einladung zum Markt'
config.invmail.linkbase       = siteconfig.shoturl + 'vendor/form/'

config.numbermail.template        = siteconfig.shotpath + 'static/mail_templates/sale_number_de.html'
config.numbermail.subject         = 'Ihre Kommissionsnummer'
config.numbermail.attachment      = siteconfig.shotpath + 'static/Richtlinien.pdf'
config.numbermail.attachmentname  = 'Richtlinien für die Annahme.pdf'


config.contactmail.template = siteconfig.shotpath + 'static/mail_templates/contact_de.html'
config.contactmail.subject  = 'Kontaktanfrage'
config.contactmail.to       = {'general':   'secondhand.ottersweier@web.de',
                               'help':      'ninabugner@yahoo.de',
                               'tech':      'michael_bechmann@yahoo.de'
                               }

# database id of the current event
config.currentevent = 2


# available sale number ranges
#config.numbers.available       = [[200, 250], [300,350], [400,450]]

#config.numbers.available_kg    = [[500, 599]]

config.no_kindergarten_id   = ' - '


# strings used as identifying names of form input elements
config.formname.no_contrib      = 'fnnoco'
config.formname.shift           = 'fnshif'
config.formname.donation        = 'fndona'
config.formname.note            = 'fnnote'
config.formname.vendor_message  = 'fnvmsg'
config.formname.sale_number     = 'fnsnum'

# strings used as ids and classes of html elements
# These must fit the CSS selectors in style sheets and jQuery functions!
config.cssid.salenumber         = 'isnum'
config.cssid.nocontrib          = 'inoctrb'
config.cssid.contribtblshifts   = 'itblshifts'
config.cssid.contribtbldons     = 'itbldons'
config.cssid.tblsubmit          = 'itblsubm'

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
config.cssclass.configwarn      = 'ccnfwarn'

config.cssclass.tggl            = 'ctggl'
config.cssclass.tggltrig        = 'ctggltrig'

config.msg.wait                 = 'The processing of your data takes some time. Please be patient ...'



config.colsets = {}      
config.colsets['sale'] = { 'sets':{'details' : ['sale.id', 'sale.event', 'vendor.name', 'vendor.forename', 'sale.number', 'sale.number_unikey', 'sale.number_assigned'], 
                                   'default'  : ['sale.event', 'vendor.name', 'vendor.forename', 'sale.number'],
                                   'sign list': ['sale.number','vendor.name', 'vendor.forename', 'vendor.place', 'vendor.street', 'vendor.house_number', 'vendor.telephone']
                                   },
                           'default': 'default'
                         }
config.colsets['bring'] = { 'sets':{'details': ['bring.id', 'donation.event', 'vendor.name', 'vendor.forename', 'vendor.place', 'donation.item', 'bring.note'], 
                                   'default'  : ['vendor.name', 'vendor.forename', 'donation.item', 'bring.note']
                                   },
                           'default': 'default'
                         }
config.colsets['help'] = { 'sets':{'details' : ['help.id', 'shift.event', 'vendor.name', 'vendor.forename', 'vendor.place', 'shift.activity', 'shift.day', 'shift.time'], 
                                   'default'  : ['vendor.name', 'vendor.forename', 'shift.activity', 'shift.day', 'shift.time'],
                                   },
                           'default': 'default'
                         }

config.colsets['message'] = { 'sets':{'details': ['message.id', 'message.event', 'vendor.name', 'vendor.forename', 'vendor.place', 'message.text'], 
                                       'default': ['vendor.name', 'vendor.forename', 'message.text']
                                   },
                           'default': 'default'
                         }
config.colsets['vendor'] = { 'sets':{'details':  ['vendor.id', 'vendor.name', 'vendor.forename', 'vendor.place', 'vendor.zip_code', 'vendor.street', 'vendor.house_number', 'vendor.email', 'vendor.telephone'],
                                     'default' : ['vendor.name', 'vendor.forename', 'vendor.kindergarten', 'vendor.place', 'vendor.email', 'vendor.telephone'],
                                     'technical':['vendor.id', 'vendor.name', 'vendor.forename', 'vendor.kindergarten', 'vendor.code', 'vendor.verified', 'vendor.log']
                                   },
                           'default': 'default'
                         }

# A list is used here instead of a dictionary because the order is important, e.g., in the database list views.
# usage of the dict members
# group: information how to group the form elements
#    id: id of the div tags embracing the form groups, used for positioning the form elements by CSS
# name: database field, form validation
# label: used in the form, visible by the user
# target: how many are needed
config.contribution = [
                      {
                      'id': 'form_group_no_contribution',
                      'data':  [
                                {'name': 'no_contribution', 'label': 'I cannot help nor bring anything!'}
                               ]
                      },

                      {
                      'id': 'form_group_donation', 'title': 'Donations',
                      'data':  [
                                {'name': 'cake',      'label': 'I bring a cake.',         'target': 30}, 
                                {'name': 'waffle',    'label': 'I bring waffle dough.',   'target': 10}
                                #{'name': 'donation',  'label': 'I make a small donation of 2 to 5 Euro.'}
                               ]
                      },
                      
                      {
                      'id': 'form_group_shift_fr',   'title': 'Shift friday, 2:30 pm - 5:00 pm',
                      'data':  [
                                {'name': 'shift_fr_0', 'label': 'sorting', 'target': 20},
                               ]
                      },
                      
                      {
                      'id': 'form_group_shift_sa_1',   'title': 'Shift saturday, 8:30 am - 11:00 am',
                      'data':  [
                                {'name': 'shift_sa_0', 'label': 'kitchen',        'target': 3}, 
                                {'name': 'shift_sa_1', 'label': 'arranging',      'target': 8}, 
                                {'name': 'shift_sa_2', 'label': 'cash desk',      'target': 4}, 
                                {'name': 'shift_sa_3', 'label': 'cake sale',      'target': 2},
                                {'name': 'shift_sa_4', 'label': 'waffle sale',    'target': 1},
                               ]
                      },
                      
                      {
                      'id': 'form_group_shift_sa_2',   'title': 'Shift saturday, 11:00 am - 1:30 pm',
                      'data':  [
                                {'name': 'shift_sa_5', 'label': 'kitchen',        'target': 3},
                                {'name': 'shift_sa_6', 'label': 'arranging',      'target': 5},
                                {'name': 'shift_sa_7', 'label': 'cash desk',      'target': 0},
                                {'name': 'shift_sa_8', 'label': 'cake sale',      'target': 1},
                                {'name': 'shift_sa_9', 'label': 'waffle sale',    'target': 2}
                               ]
                      },
                      {
                      'id': 'form_group_shift_sa_3',   'title': 'Shift saturday, 12:30 am - 3:00 pm',
                      'data':  [
                                {'name': 'shift_sa_10', 'label': 'kitchen',        'target': 0},
                                {'name': 'shift_sa_11', 'label': 'back sorting',   'target': 20},
                               ]
                      },                     
                      
                      
                      
                      ]
# To simplify some loops prepare a list with the 'data' elements
config.contribution_data = []
for group in config.contribution:
    x = group['data']
    if 'title' in group:
        t = group['title']
        for xx in x:
            xx['title'] = t
            
    config.contribution_data.extend(x)
