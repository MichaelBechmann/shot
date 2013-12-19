# -*- coding: utf-8 -*-
# Static analyzer import helpers: (STATIC_IMPORT_MARK)
if 0: 
    from gluon.languages import translator as T
    from gluon import *


from shotconfig import *


T.force('de')

# There is one single database containing the data of all market events.

shotdb = DAL(config.db_connection_string)

# The table 'event' contains all configuration data of the market events.
shotdb.define_table('event',
        
    Field('label',      'string',   label = T('event label'),          requires=IS_NOT_EMPTY(error_message = T('Please enter a unique identifying label for the event.'))),       
    
    # Is the event active, i.e., the current event?
    Field('active',    'boolean',  label = T('active')),
    
    # Date of the event
    Field('date',  'string',   label = T('date'),     requires=IS_NOT_EMPTY(error_message = T('Please enter a date string, e.g., "Samstag, den 28. September 2013".'))),
    
    # Date of the start of the enrolment of the vendors
    Field('enrol_date',  'string',   label = T('enrol date'),     requires=IS_NOT_EMPTY(error_message = T('Please enter a date string, e.g., "Samstag, den 24. August 2013".'))),    
    
    # the available sale numbers; adjacent pairs define ranges
    Field('number_ranges',    'string', label = T('number ranges'),                 requires = IS_NOT_EMPTY(error_message = T('Please enter pairs of numbers, like 200-250; 300-350.'))),
 
    # optional limit of sale numbers
    Field('numbers_limit', 'integer', label = T('numbers limit')),
    
    # define how a record is represented if referenced from other tables
    format='%(label)s'
                    
) # end of 'event'

# The table 'person' contains all data personal data of the registered people.
shotdb.define_table('person',
                    
    Field('name',           'string',   label = T('name'),          requires=IS_NOT_EMPTY(error_message = T('Please enter your name.'))),                               
    Field('forename',       'string',   label = T('forename'),      requires=IS_NOT_EMPTY(error_message = T('Please enter your forename.'))),                
    Field('place',          'string',   label = T('place'),         requires=IS_NOT_EMPTY(error_message = T('Please enter your place of living.'))),
    Field('zip_code',       'string',   label = T('zip code'),      requires=IS_NOT_EMPTY(error_message = T('Please enter your zip code.'))),          
    Field('street',         'string',   label = T('street'),        requires=IS_NOT_EMPTY(error_message = T('Please enter the street name.'))),
    Field('house_number',   'string',   label = T('house number'),  requires=IS_NOT_EMPTY(error_message = T('Please enter your house number.'))),   
    Field('telephone',      'string',   label = T('telephone'),     requires=IS_NOT_EMPTY(error_message = T('Please enter your telephone number.'))),
    Field('email',          'string',   label = T('email'),         requires=IS_EMAIL(    error_message = T('Please enter your valid email address.'))),                                                                                         

    # random string for verification of the email address
    Field('code',           'string',   requires=IS_NOT_EMPTY()),
    
    # id of the most recent event for which the email address has been verified with
    Field('verified',       'integer'),
    
    # flag indicating if round mails are enabled
    Field('mail_enabled',   'boolean'),
    
    # automatically generated log data when the record is updated
    Field('log',            'text'),
    
    # define how a record is represented if referenced from other tables
    format='%(name)s, %(forename)s'
) # end of 'person'


# The table 'sale' contains all data directly related to the sale of each vendor at the markets.
shotdb.define_table('sale',
                    
    # relation to the sale event
    Field('event', shotdb.event),
                        
    # relation to the person
    Field('person', shotdb.person),
    
    # the sale number          
    Field('number',             'integer',  label = T('number')),
    
    # This shall ensure that the combination of event and number is unique on database level.
    # Note: The unique attribute must be present already when the sqlite database file is created. Otherwise it will not take effect!
    # Apparently it cannot be changed lateron.
    Field('number_unikey',      'string',  length=255, unique = True, compute=lambda r: str(r['event']) + ':' + str(r['number'])),  
    
    # define how a record is represented if referenced from other tables
    format='%(number)s (sale id %(id)s)'
              
) # end of 'sale'


# The table 'wait' collects all persons who are waitlisted for a given event and contains all related information.
shotdb.define_table('wait',
                    
    # relation to the sale event
    Field('event', shotdb.event),
                        
    # relation to the person
    Field('person', shotdb.person),
    
    # relation to the sale (if a person on the wait list finally gets a sale number)
    Field('sale', shotdb.sale),
    
    # information whether or not a denial mail has been sent
    Field('denial_sent',    'boolean'),

) # end of 'wait'



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

# The auxiliary table 'help' links the persons to the shifts
shotdb.define_table('help',
                    
    # relation to the shit
    Field('shift', shotdb.shift),
    
    # relation to the person
    Field('person', shotdb.person),
                 
                    
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

# The auxiliary table 'bring' links the persons to the donations
shotdb.define_table('bring',
                    
    # relation to the donation
    Field('donation', shotdb.donation),
    
    # relation to the person
    Field('person', shotdb.person),
    
    # The field 'note' is intended to be provide a simple communication about the donations.
    Field('note', 'string'),          
                    
) # end of 'bring'

# The table 'message' contains all messages the people leave via the forms.
# An extra table is used because messages do not relate solely to sales, shifts, or donations.
shotdb.define_table('message',
    
    # relation to the sale event
    Field('event', shotdb.event),
                               
    # relation to the person
    Field('person', shotdb.person),
    
    # a text message the person can leave during the actual enrolment for an event
    Field('text',        'text',     label = T('message'),      )
    
) # end of 'message'  

# The table 'request' contains all data related to appropriation requests (information provided by the applicant as well as status and decision information from the shot team). 
shotdb.define_table('request',
    # relation to the person
    Field('person', shotdb.person),
    
    Field('project',            'string',   label = 'Projektbezeichnung',         requires = IS_NOT_EMPTY(error_message = 'Bitte geben Sie eine Bezeichnung Ihres Projektes an.')),
    Field('organization',       'string',   label = 'Organisation',               requires = IS_NOT_EMPTY(error_message = 'Bitte geben Sie Ihren Verein oder Ihre Institution oder "privat" an.')),
    Field('amount_total',       'integer',  label = 'Gesamtkosten (EUR)',         requires = IS_INT_IN_RANGE(0, 1e100, error_message = 'Bitte geben Sie in Ziffern (ohne Punkt, Komma oder EUR!) die geschätzten Gesamtkosten Ihres Projektes an.')),
    Field('amount_requested',   'integer',  label = 'Beantragte Mittel (EUR)',    requires = IS_INT_IN_RANGE(0, 1e100, error_message = 'Bitte geben Sie in Ziffern (ohne Punkt, Komma oder EUR!) an, welchen Betrag Sie als Förderung beantragen möchten.')),
    Field('description',        'text',     label = 'Projektbeschreibung',        requires = IS_NOT_EMPTY(error_message = 'Bitte beschreiben Sie Ihr Projekt kurz und begründen Sie Ihren Antrag.')),
    Field('date_of_receipt',    'string'    ),
    Field('comment',            'text'      ),
    Field('amount_spent',       'integer',  requires = IS_INT_IN_RANGE(0, 1e100)),
    Field('status',             'string'    )
    ) # end of request
