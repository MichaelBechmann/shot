# -*- coding: utf-8 -*-
# Static analyzer import helpers: (STATIC_IMPORT_MARK)
if 0: 
    from gluon.languages import translator as T
    from gluon import *


from shotconfig import *


T.force('de')

# There is one single database containing the data of all market events.

shotdb= DAL('sqlite://shotdb.sqlite')

# The table 'vendor' contains all data regarding the persons 
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
                                                                                          
    Field('code',           'string',   requires=IS_NOT_EMPTY()),
    Field('verified',       'boolean'),

) # end of 'vendor'







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