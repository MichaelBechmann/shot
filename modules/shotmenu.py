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
from urlutils import URLWiki, URLTable, URLUser

def createMenu():
    
    menu = [
            ['Start', False, URLWiki('start')],
            ['Informationen für Verkäufer', False, URLWiki('vendorinfo')]
           ]
    
    if config.enable_registration:
        menu.extend([['Registrierung', False, URL('registration','form')]])  
    
    if config.enable_requests:        
        menu.extend([['Fördermittel beantragen', False, URLWiki('appropriation-start')]])
        
    menu.extend([
                 ['Datenschutz', False, URLWiki('dataprivacy')],
                 ['Kontakt', False, URL('contact','form')]
                ])
                      
    return(DIV(MENU(menu), _id='menu'))


def createStaffMenu(auth, wiki_ctrl = None):

    menu = [] 
    if not auth.is_logged_in():
        if config.enable_extended_menue:
            menu.extend([['login', False, URLUser('login')]
                        ])
        else:
            return ''
    else:
        if 'team' in auth.user_groups.values():
            menu.extend([['Dashboard',        False, URL('staff','dashboard')]])
        
        if 'staff' in auth.user_groups.values():
            menu.extend([['Organize', False, '#',
                          [['Person summary',    False, URL('staff', 'person_summary')],
                           ['Number summary',    False, URL('staff', 'number_summary')],
                           ['Number status map', False, URL('staff', 'number_status_map')],
                           ['Manage help',       False, URL('staff', 'manage_help')],
                           ['Manage donations',  False, URL('staff', 'manage_donations')]
                       ]
                      ],
                      ['Tables', False, '',
                        [['Persons',   False, URLTable('person')],
                         ['Sale',      False, URLTable('sale')],    
                         ['Wait',      False, URLTable('wait')],   
                         ['Help',      False, URLTable('help')],
                         ['Bring',     False, URLTable('bring')],
                         ['Shifts',    False, URLTable('shift')],
                         ['Donations', False, URLTable('donation')],
                         ['Messages',  False, URLTable('message')],
                         ['Requests',  False, URLTable('request')]
                        ]
                      ]
                     ])

        if 'configurator' in auth.user_groups.values():
            menu.extend([['Config Event', False, URL('config','config_event')]])
            
        if 'task executor' in auth.user_groups.values():
            menu.extend([['Tasks', False, URL('tasks','start')]])

        if 'admin' in auth.user_groups.values():
            menu.extend([['Admin', False, '',
                          [['Manage users',     False,  URL('admin_', 'manage_users')],
                           ['Configuration',    False,  URL('admin_', 'configuration')],
                           ['benchmark',        False,  URL('admin_', 'benchmark')],
                           ['Actions',          False,  URL('admin_', 'actions')],
                          ]
                         ]
                        ])  

        menu.extend([['Account', False, '',
                      [['Logout',          False, URLUser('logout')],
                       ['Info',            False, URL('access','info')],
                       ['Profile',         False, URLUser('profile')],
                       ['Change password', False, URLUser('change_password')],
                      ]
                     ]
                    ])
        
        # wiki menue
        
        if 'wiki_editor' in auth.user_groups.values() or 'wiki_author' in auth.user_groups.values():
            wiki_menu = [['Manage pages', False, URLWiki('_pages')],
                         ['Search pages', False, URLWiki('_search')],
                        ]
            
            if 'wiki_author' in auth.user_groups.values():
                wiki_menu.append(['Create new page', False, URLWiki('_create')])
            
            if wiki_ctrl and not wiki_ctrl['cmd']:
                wiki_menu.append(['Edit this page', False, URLWiki(('_edit', wiki_ctrl['slug']))])
            
            
            menu.extend([['Wiki', False, '#', wiki_menu]])
                
    
    return (DIV(MENU(menu, _class = '', li_class = 'expand'), _id='menu_staff'))
