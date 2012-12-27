# -*- coding: utf-8 -*-
# Static analyzer import helpers: (STATIC_IMPORT_MARK)
if 0: 
    from gluon.languages import translator as T
    from gluon import *


from shotconfig import *


T.force('de')

# There is one single database containing the data of all market events.

shotdb= DAL('sqlite://shotdb.sqlite')

# The table 'event' contains all configuration data of the market events.
shotdb.define_table('event',
        
    Field('label',      'string',   label = T('event label'),          requires=IS_NOT_EMPTY(error_message = T('Please enter a unique identifying label for the event.'))),       
    
    # Is the event active, i.e., the current event?
    Field('active',    'boolean',  label = T('active')),
    
    # the available sale numbers; adjacent pairs define ranges
    Field('number_ranges',    'string', label = T('number ranges'),                 requires = IS_NOT_EMPTY(error_message = T('Please enter pairs of numbers, like 200-250; 300-350.'))),
    Field('number_ranges_kg', 'string', label = T('number ranges kindergarten'),    requires = IS_NOT_EMPTY(error_message = T('Please enter pairs of numbers, like 200-250; 300-350.'))),
 
    # define how a record is represented if referenced from other tables
    format='%(label)s'
                    
) # end of 'event'

# The table 'vendor' contains all data personal data of the vendors
shotdb.define_table('vendor',
                    
    Field('name',           'string',   label = T('name'),          requires=IS_NOT_EMPTY(error_message = T('Please enter your name.'))),                               
    Field('forename',       'string',   label = T('forename'),      requires=IS_NOT_EMPTY(error_message = T('Please enter your forename.'))),                
    Field('place',          'string',   label = T('place'),         requires=IS_NOT_EMPTY(error_message = T('Please enter your place of living.'))),
    Field('zip_code',       'string',   label = T('zip code'),      requires=IS_NOT_EMPTY(error_message = T('Please enter your zip code.'))),          
    Field('street',         'string',   label = T('street'),        requires=IS_NOT_EMPTY(error_message = T('Please enter the street name.'))),
    Field('house_number',   'string',   label = T('house number'),  requires=IS_NOT_EMPTY(error_message = T('Please enter your house number.'))),   
    Field('telephone',      'string',   label = T('telephone'),     requires=IS_NOT_EMPTY(error_message = T('Please enter your telephone number.'))),
    Field('email',          'string',   label = T('email'),         requires=IS_EMAIL(    error_message = T('Please enter your valid email address.'))),      
    Field('kindergarten',   'string',   label = T('kindergarten'),  requires=IS_IN_SET([(config.no_kindergarten_id, T('no, in neither one')), 
                                                                                        ('St. Marien',              T('yes, in St. Marien')), 
                                                                                        ('St. Michael',             T('yes, in St. Michael'))],
                                                                                          error_message = T('Please choose.') )),                                                                                        

    # random string for verification of the email address
    Field('code',           'string',   requires=IS_NOT_EMPTY()),
    
    # id of the most recent event for which the email address has been verified with
    Field('verified',       'integer'),
    
    # automatically generated log data when the record is updated
    Field('log',            'text'),
    
    # define how a record is represented if referenced from other tables
    format='%(name)s, %(forename)s'
) # end of 'vendor'


# The table 'sale' contains all data directly related to the sale of each vendor at the markets.
shotdb.define_table('sale',
                    
    # relation to the sale event
    Field('event', shotdb.event),
                        
    # relation to the vendor
    Field('vendor', shotdb.vendor),
    
    # the sale number          
    Field('number',             'integer',  label = T('number')),
    
    # did the vendor choose the number or has it been assigned automatically
    Field('number_assigned',    'boolean'),
    
    # This shall ensure that the combiation of event and number is unique on database level.
    # Note: The unique attribute must be present already when the sqlite database file is created. Otherwise it will not take effect!
    # Apparently it cannot be changed lateron.
    Field('number_unikey',      'string',  unique = True, compute=lambda r: str(r['event']) + ':' + str(r['number'])),   
              
) # end of 'sale'


# The table 'shift' contains the configuration data for the helper shifts.
shotdb.define_table('shift',
                    
    # relation to the sale event
    Field('event', shotdb.event),
    
    # a short description of the activity which will appear in the registration form
    Field('activity',   'string'),
    
    # time and duration of the shift
    Field('day',        'string'),
    Field('time',       'string'),
    
    # How many helper are required for this shift?
    Field('target_number', 'integer'),
    
    # display property is used to sort and arrange the shifts in the sale form view
    Field('display',    'string'),
    
    # define how a record is represented if referenced from other tables
    format='%(activity)s, %(day)s, %(time)s (%(event)s)'
    
)
class VirtualFieldsShift():
    def actual_number(self):
        # This field indicates how many people are currently registered for the particular shift.
        return len(shotdb(shotdb.help.shift == self.shift.id).select())
        
shotdb.shift.virtualfields.append(VirtualFieldsShift())
# end of 'shift'

# The auxiliary table 'help' links the vendors to the shifts
shotdb.define_table('help',
                    
    # relation to the shit
    Field('shift', shotdb.shift),
    
    # relation to the vendor
    Field('vendor', shotdb.vendor),
                 
                    
) #end of 'help'
    
# The table 'donation' contains all things people are asked to bring, like cake, waffle dough, etc.
shotdb.define_table('donation',
                    
    # relation to the sale event
    Field('event', shotdb.event),
    
    # short description of item to bring
    Field('item',   'string'),
    
    # How many are needed of the kind?
    Field('target_number', 'integer'),
    
    # Shall the users be able to leave notes (related to the field 'note' in table 'bring')?
    Field('enable_notes', 'boolean'),
    
    # define how a record is represented if referenced from other tables
    format='%(item)s (%(event)s)'
    
) 
class VirtualFieldsDonation():
    def actual_number(self):
        # This field indicates how many people are currently registered for the particular donation.
        return len(shotdb(shotdb.bring.donation == self.donation.id).select())
        
shotdb.donation.virtualfields.append(VirtualFieldsDonation())
# end of 'donation'

# The auxiliary table 'bring' links the vendors to the donations
shotdb.define_table('bring',
                    
    # relation to the donation
    Field('donation', shotdb.donation),
    
    # relation to the vendor
    Field('vendor', shotdb.vendor),
    
    # The field 'note' is intended to be provide a simple communication about the donations.
    Field('note', 'string'),          
                    
) # end of 'bring'

# The table 'message' contains all messages the people leave via the forms.
# An extra table is used because messages do not relate solely to sales, shifts, or donations.
shotdb.define_table('message',
    
    # relation to the sale event
    Field('event', shotdb.event),
                               
    # relation to the vendor
    Field('vendor', shotdb.vendor),
    
    # a text message the vendor can leave when the sale number is chosen
    Field('text',        'text',     label = T('message'),      )
    
) # end of 'message'  


# Below is the simple single-table database use for the first event.

# This file defines the complete shot database.
# The table "vendor" contains all vendor information: peronal data, contacts, registration data, etc.
# I decided to use only one single table because the relations between vendors, sale numbers, and contributions
# are simply one-to-one.
# This will change when real user accounts will be used. Then several sale numbers and contributions from 
# different market events will be linked to one account ...

# idea for translation: switch off translation in this file by T.force(None) and define the fields with T('name') etc.

db = DAL('sqlite://storage.sqlite')

db.define_table('vendor',
    Field('name',           'string',   label = T('name'),          requires=IS_NOT_EMPTY(error_message = T('Please enter your name.'))),                               
    Field('forename',       'string',   label = T('forename'),      requires=IS_NOT_EMPTY(error_message = T('Please enter your forename.'))),                
    Field('place',          'string',   label = T('place'),         requires=IS_NOT_EMPTY(error_message = T('Please enter your place of living.'))),
    Field('zip_code',       'string',   label = T('zip code'),      requires=IS_NOT_EMPTY(error_message = T('Please enter your zip code.'))),          
    Field('street',         'string',   label = T('street'),        requires=IS_NOT_EMPTY(error_message = T('Please enter the street name.'))),
    Field('house_number',   'string',   label = T('house number'),  requires=IS_NOT_EMPTY(error_message = T('Please enter your house number.'))),   
    Field('telephone',      'string',   label = T('telephone'),     requires=IS_NOT_EMPTY(error_message = T('Please enter your telephone number.'))),
    Field('email',          'string',   label = T('email'),         requires=IS_EMAIL(    error_message = T('Please enter your valid email address.'))),      
    Field('kindergarten',   'string',   label = T('kindergarten'),  requires=IS_IN_SET([(config.no_kindergarten_id, T('no, in neither one')), 
                                                                                        ('St. Marien',              T('yes, in St. Marien')), 
                                                                                        ('St. Michael',             T('yes, in St. Michael'))],
                                                                                          error_message = T('Please choose.') )),
                                                                                          
    Field('code',           'string',   requires=IS_NOT_EMPTY()),
    Field('verified',       'boolean'),
    Field('number',         'integer',  label = T('number'),      unique=True),   
    Field('number_assigned','boolean'), 
    Field('message',        'text',     label = T('message'),      ),
    *[Field(c['name'], 'boolean') for c in config.contribution_data]
    )