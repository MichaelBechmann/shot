# -*- coding: utf-8 -*-
'''
creation: bechmann, May 29, 2014

'''
if 0:
    global auth
    global config
    global URL

from shotconfig import *
from shotdbutil import User
from gluon.html import *
from gluon import current

def createMenu():
    
    menu = [
            ['Start', False, URL('main','wiki', args=['start'])],
            ['Informationen für Verkäufer', False, URL('main','vendorinfo')]
           ]
    
    if config.enable_registration:
        menu.extend([['Registrierung', False, URL('registration','form')]])  
    
    if config.enable_requests:        
        menu.extend([['Fördermittel beantragen', False, URL('appropriation','introduction')]])
        
    menu.extend([
                 ['Datenschutz', False, URL('main','privacy')],
                 ['Kontakt', False, URL('contact','form')]
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
            menu.extend([['Dashboard',        False, URL('staff','dashboard')]])
        
        if 'staff' in auth.user_groups.values():
            menu.extend([['Organize', False, '#',
                          [['Person summary',    False, '/staff/person_summary'],
                           ['Number summary',    False, '/staff/number_summary'],
                           ['Number status map', False, '/staff/number_status_map'],
                           ['Manage help',       False, '/staff/manage_help'],
                           ['Manage donations',  False, '/staff/manage_donations']
                       ]
                      ],
                      ['Tables', False, '#',
                        [['Persons',   False, URL('staff','table', args=['person'])],
                         ['Sale',      False, URL('staff','table', args=['sale'])],    
                         ['Wait',      False, URL('staff','table', args=['wait'])],   
                         ['Help',      False, URL('staff','table', args=['help'])],
                         ['Bring',     False, URL('staff','table', args=['bring'])],
                         ['Shifts',    False, URL('staff','table', args=['shift'])],
                         ['Donations', False, URL('staff','table', args=['donation'])],
                         ['Messages',  False, URL('staff','table', args=['message'])],
                         ['Requests',  False, URL('staff','table', args=['request'])]
                        ]
                      ]
                     ])

        if 'configurator' in auth.user_groups.values():
            menu.extend([['Config Event', False, URL('config','config_event')]])
            
        if 'task executor' in auth.user_groups.values():
            menu.extend([['Tasks', False, URL('tasks','start')]])

        if 'admin' in auth.user_groups.values():
            menu.extend([['Admin', False, '#',
                          [['Manage users',     False,  URL('admin_','manage_users')],
                           ['Configuration',    False,  URL('admin_','configuration')],
                           ['benchmark',        False,  '/admin_/benchmark']
                          ]
                         ]
                        ])  

        menu.extend([['Account', False, '#',
                      [['Logout',          False, URL('access','user', args=['logout'])],
                       ['Info',            False, URL('access','info')],
                       ['Profile',         False, URL('access','user', args=['profile'])],
                       ['Change password', False, URL('access','user', args=['change_password'])],
                      ]
                     ]
                    ])
        
        # wiki menue
        controller = 'main'
        function = 'wiki'
        
        if 'wiki_editor' in auth.user_groups.values() or 'wiki_author' in auth.user_groups.values():
            wiki_menu = [['Manage pages', False, URL(controller, function, args=['_pages'])],
                         ['Search pages', False, URL(controller, function, args=['_search'])],
                        ]
            if not str(current.request.args(0)).startswith('_'):
                slug = current.request.args(0)
                wiki_menu.append(['Edit this page', False, URL(controller, function, args=('_edit', slug))])
            
            
            menu.extend([['Wiki', False, '#', wiki_menu]])
                

    return (DIV(MENU(menu, _class = '', li_class = 'expand'), _id='menu_staff'))
