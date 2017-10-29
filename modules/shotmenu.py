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
from urlutils import URLWiki, URLTable, URLUser


def createMenu(auth):
    if not current.response.menu:
        auth.force_shotmenu()
    menu = current.response.menu
    if not config.enable_registration:
        for e in menu:
            if 'registration' in e[2]:
                menu.remove(e)
                break

    if not config.enable_requests:
        for e in menu:
            if 'appropriation-start' in e[2]:
                menu.remove(e)
                break   

    return (DIV(MENU(menu, _class = '', li_class = 'expand'), _id='menu_public', _class='menu'))


def createStaffMenu(auth, wiki_ctrl = None):

    menu = [] 
    if not auth.is_logged_in():
        if config.enable_extended_menue:
            menu.extend([['login', False, URLUser('login')]
                        ])
        else:
            return ''
    else:
        user_groups = auth.user_groups.values()
        
        if 'team' in user_groups:
            menu.extend([['Dashboard',  False, URL('staff', 'dashboard')],
                         ['Requests',    False, URL('staff', 'requests')]
                         ])
        
        
        items_organize = []
        if 'staff' in user_groups:
            items_organize = [
                              ['Person summary',    False, URL('staff', 'person_summary')],
                              ['Number summary',    False, URL('staff', 'number_summary')],
                              ['Number status map', False, URL('staff', 'number_status_map')],
                              ['Manage help',       False, URL('staff', 'manage_help')],
                              ['Manage donations',  False, URL('staff', 'manage_donations')] 
                            ]
            items_tables   = [
                              ['Persons',   False, URLTable('person')],
                              ['Sale',      False, URLTable('sale')],
                              ['Wait',      False, URLTable('wait')],
                              ['Help',      False, URLTable('help')],
                              ['Bring',     False, URLTable('bring')],
                              ['Shifts',    False, URLTable('shift')],
                              ['Donations', False, URLTable('donation')],
                              ['Messages',  False, URLTable('message')],
                              ['Requests',  False, URLTable('request')]
                            ] 
            
        else:
            items_organize = [
                              ['Number status map', False, URL('staff', 'number_status_map')]
                            ]
            
            items_tables   = [
                              ['Requests',  False, URLTable('request')]
                            ]
            
            
        
        if 'staff' in user_groups or 'team' in user_groups:
            menu.extend([['Organize', False, '', items_organize],
                         ['Tables',   False, '', items_tables]
                        ])

        if 'configurator' in auth.user_groups.values():
            menu.extend([['Config Event', False, URL('config','config_event')]])
            
        if 'task executor' in auth.user_groups.values():
            menu.extend([['Tasks', False, '',
                          [['Einladungen senden',   False, URL('tasks', 'start', args = ['send_invitation'])],
                           ['Warteliste auflösen',  False, URL('tasks', 'start', args = ['resolve_waitlist'])],
                           ['Absagen senden',       False, URL('tasks', 'start', args = ['send_denial'])],
                           ['Erinnerungen senden',  False, URL('tasks', 'start', args = ['send_reminder'])],
                           ['Infos danach senden',  False, URL('tasks', 'start', args = ['send_infos_after_market'])]
                          ]
                         ]
                        ])

        if 'admin' in auth.user_groups.values():
            menu.extend([['Admin', False, '',
                          [['Manage users',     False,  URL('admin_', 'manage_users')],
                           ['Configuration',    False,  URL('admin_', 'configuration')],
                           ['Benchmark',        False,  URL('admin_', 'benchmark')],
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
            wiki_menu = [['Guidlines',    False, URL('main', 'wiki', args = ['wiki-guidelines'])],
                         ['Manage pages', False, URLWiki('_pages')],
                         ['Search tags',  False, URLWiki('_search')],
                        ]
            
            if 'wiki_author' in auth.user_groups.values():
                wiki_menu.append(['Create new page', False, URLWiki('_create')])
                wiki_menu.append(['Edit the menu',   False, URLWiki(('_edit', 'wiki-menu'))])
            
            if wiki_ctrl and wiki_ctrl.slug:
                wiki_menu.append(['Edit this page', False, URLWiki(('_edit', wiki_ctrl.slug))])
                wiki_menu.append(['Edit page media', False, URLWiki(('_editmedia', wiki_ctrl.slug))])
            
            menu.extend([['Wiki', False, '#', wiki_menu]])
                
    
    return (DIV(MENU(menu, _class = '', li_class = 'expand'), _id='menu_staff', _class='menu'))
