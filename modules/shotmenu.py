# -*- coding: utf-8 -*-
'''
creation: bechmann, May 29, 2014

'''
if 0:
    global auth
    global config

from shotconfig import *
from shotdbutil import User
from gluon.html import *

def createMenu():
    
    menu = [['Start', False, '/main/index'],
            ['Informationen für Verkäufer', False, '/main/vendorinfo']
           ]
    
    if config.enable_registration:
        menu.extend([['Registrierung', False, '/registration/form']])  
    
    if config.enable_requests:        
        menu.extend([['Fördermittel beantragen', False, '/appropriation/introduction']])
        
    menu.extend([
                 ['Datenschutz', 'False', '/main/privacy'],
                 ['Kontakt', False, '/contact/form']
                ])
                      
    return(DIV(MENU(menu), _id='menu'))


def createStaffMenu(auth):

    menu = [] 
    if not auth.is_logged_in():
        if config.enable_extended_menue:
            menu.extend([['login', False, URL('access', 'user', args='login')]
                        ])
        else:
            return ''
    else:
        if 'team' in auth.user_groups.values():
            menu.extend([['Dashboard',        False, '/staff/dashboard']])
        
        if 'staff' in auth.user_groups.values():
            menu.extend([['Organize', False, '#',
                          [['Person summary',   False, '/staff/person_summary'],
                           ['Manage help',      False, '/staff/manage_help'],
                           ['Manage donations', False, '/staff/manage_donations']
                       ]
                      ],
                      ['Tables', False, '#',
                        [['Persons',   False, '/staff/table/person'],
                         ['Sale',      False, '/staff/table/sale'],    
                         ['Wait',      False, '/staff/table/wait'],   
                         ['Help',      False, '/staff/table/help'],
                         ['Bring',     False, '/staff/table/bring'],
                         ['Shifts',    False, '/staff/table/shift'],
                         ['Donations', False, '/staff/table/donation'],
                         ['Messages',  False, '/staff/table/message'],
                         ['Requests',  False, '/staff/table/request']
                        ]
                      ]
                     ])

        if 'configurator' in auth.user_groups.values():
            menu.extend([['Config Event', 'False', '/config/config_event']])
            
        if 'task executor' in auth.user_groups.values():
            menu.extend([['Tasks', 'Fasle', '/tasks/start']])

        if 'admin' in auth.user_groups.values():
            menu.extend([['Admin', False, '#',
                          [['manage users',     False,  '/admin_/manage_users'],
                           ['configuration',    False,  '/admin_/configuration'],
                          ]
                         ]
                        ])  

        menu.extend([['Account', False, '#',
                      [['logout',          False, '/access/user/logout'],
                       ['info',            False, '/access/info'],
                       ['profile',         False, '/access/user/profile'],
                       ['changepassword',  False, '/access/user/change_password'],
                      ]
                     ]
                    ])
        
    return (DIV(MENU(menu, _class = '', li_class = 'expand'), _id='menu_staff'))