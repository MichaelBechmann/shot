# -*- coding: utf-8 -*-
'''
creation: bechmann, May 29, 2014

'''
from gluon.contrib.pg8000.core import TRUE
if 0:
    global auth
    global config
    global URL


from shotconfig import *
from shotdbutil import User
from gluon.html import *
from gluon import current
from urlutils import *



class extendedMENU(MENU):
    """
    This is an extension of the gluon html helper to generate menus.
    The extension is that each menu item can be given an individual css class definition. This individual class is combined with the generic classes (see below).
    The method serialize() has been copied from the parent class MENU and modified.

    Args:
        _class: defaults to 'web2py-menu web2py-menu-vertical'
        ul_class: defaults to 'web2py-menu-vertical'
        li_class: defaults to 'web2py-menu-expand'
        li_first: defaults to 'web2py-menu-first'
        li_last: defaults to 'web2py-menu-last'

    Use like::

        menu = MENU([['name', False, URL(...), [submenu], 'optional individual css class name'], ...])
        {{=menu}}

    """

    def serialize(self, data, level=0):
        li_list = []
        b_active = False

        for item in data:
            if isinstance(item, LI):
                li_list.append(item)
            else:
                li_classes = ''
                (name, active, link) = item[:3]
                if isinstance(link, DIV):
                    li = LI(link)
                elif 'no_link_url' in self.attributes and self['no_link_url'] == link:
                    li = LI(DIV(name))
                elif isinstance(link, dict):
                    li = LI(A(name, **link))
                elif link:
                    if active:
                        link = '#'
                    li = LI(A(name, _href=link))
                elif not link and isinstance(name, A):
                    li = LI(name)
                else:
                    li = LI(A(name, _href='#', _onclick='javascript:void(0);return false;'))
                if level == 0 and item == data[0]:
                    li_classes = self['li_first']
                elif level == 0 and item == data[-1]:
                    li_classes = self['li_last']
                if len(item) > 3 and isinstance(item[3], list) and item[3]:
                    li_classes = self['li_class']

                    sub = self.serialize(item[3], level + 1)
                    li.append(sub[0])
                    if sub[1]:
                        b_active = True
                        li_classes = self['li_sub_active']

                    # This fixes a bug in gluon/tools.py in Expose.menu(), line 6382 (request.args(0) == title_page).
                    # This condition is too simple. Links out of the Wiki (e.g., Kontakt) have no slug, i.e., request.arg(0) = None
                    # which renders all parent elements active!
                    active = False

                if active or ('active_url' in self.attributes and self['active_url'] == link):
                    if li_classes:
                        li_classes = li_classes + ' '
                    li_classes = li_classes + self['li_active']
                    b_active = True

                if len(item) >= 4 and isinstance(item[-1], str):
                    individual_class = item[-1]
                    if individual_class:
                        if li_classes:
                            li_classes = li_classes + ' '
                        li_classes = li_classes + individual_class

                if li_classes:
                    li['_class'] = li_classes

                li_list.append(li)

        if level == 0:
            ul = UL(**self.attributes)
        else:
            c = self['ul_class']
            if b_active:
                c = c + ' ' + self['ul_active']
            ul = UL(_class=c)
        ul.append(li_list)

        if level == 0:
            return ul
        else:
            return [ul, b_active]

class ShotMenu(object):
    def __init__(self):
        self.active_controller = current.request.controller
        self.active_function   = current.request.function
        self.active_args       = current.request.args
        self.active_arg        = current.request.args(0)

    def _checkActiveURLWiki(self, *args):
        # tupel has to be converted to list for the comparison with the active arguments
        args_list = list(args)

        if self.active_controller == 'main' and self.active_function == 'wiki' and args_list == self.active_args:
            b_active = True
            link     = '#'
        else:
            b_active = False
            link     = URLWiki(args)
        return [b_active, link]

    def _checkActiveURL(self, c, f):
        if self.active_controller == c and self.active_function == f:
            b_active = True
            link     = '#'
        else:
            b_active = False
            link     = URL(c, f)
        return [b_active, link]

    def _checkActiveURLTable(self, t):
        if self.active_controller == 'staff' and self.active_function == 'table' and self.active_arg == t:
            b_active = True
            link     = '#'
        else:
            b_active = False
            link     = URLTable(t)
        return [b_active, link]

    def _checkActiveURLUser(self, action):
        if self.active_controller == 'access' and self.active_function == 'user' and self.active_arg == action:
            b_active = True
            link     = '#'
        else:
            b_active = False
            link     = URLUser(action)
        return [b_active, link]

    def _checkActiveURLTask(self, task):
        if self.active_controller == 'tasks' and self.active_function == 'start' and self.active_arg == task:
            b_active = True
            link     = '#'
        else:
            b_active = False
            link     = URLTask(task)
        return [b_active, link]

    def createQuickMenu(self):
        quick_menu_items = [['Termine',                     self._checkActiveURLWiki('start')],
                            ['Fördermittel beantragen',     self._checkActiveURLWiki('appropriation-start')],
                            ['Kontakt',                     self._checkActiveURL    ('contact', 'form')]
                           ]
        if config.enable_registration:
            quick_menu_items.insert(1,
                             ['Als Verkäufer registrieren', self._checkActiveURL('registration', 'form')])

        buttonlist = []
        for (text, (b_active, link)) in quick_menu_items:
            c = 'button'
            if b_active:
                c = c + ' active'

            buttonlist.append(A(text, _href = link, _class = c))

        return(buttonlist)


    def createSideMenu(self, auth):
        if 'wiki_ctrl' in current.response._vars:
            wiki_ctrl = current.response._vars['wiki_ctrl']
        else:
            wiki_ctrl = None

        if not current.response.menu:
            auth.force_shotmenu()
        menu = current.response.menu

        if auth.is_logged_in():
            user_groups = auth.user_groups.values()

            if 'team' in user_groups:
                menu.extend([['Dashboard'] + self._checkActiveURL('staff', 'dashboard') + ['team'],
                             ['Requests']  + self._checkActiveURL('staff', 'requests')  + ['team']
                             ])

            if 'team' in user_groups:
                if 'team' in user_groups:
                    items_organize = [['Person summary'] + self._checkActiveURL('staff', 'person_summary') + ['team'],
                                      ['Number summary'] + self._checkActiveURL('staff', 'number_summary') + ['team']
                                    ]
                else:
                    items_organize = []

                items_organize.extend([['Number status map'] + self._checkActiveURL('staff', 'number_status_map') + ['team'],
                                       ['Manage help']       + self._checkActiveURL('staff', 'manage_help')       + ['team'],
                                       ['Manage donations']  + self._checkActiveURL('staff', 'manage_donations')  + ['team']
                                      ])

                menu.extend([['Organize', False, '#', items_organize, 'team']
                            ])


            if 'team' in user_groups:
                items   = [['Persons']   + self._checkActiveURLTable('person')   + ['team'],
                           ['Sale']      + self._checkActiveURLTable('sale')     + ['team'],
                           ['Wait']      + self._checkActiveURLTable('wait')     + ['team'],
                           ['Help']      + self._checkActiveURLTable('help')     + ['team'],
                           ['Bring']     + self._checkActiveURLTable('bring')    + ['team'],
                           ['Shifts']    + self._checkActiveURLTable('shift')    + ['team'],
                           ['Donations'] + self._checkActiveURLTable('donation') + ['team'],
                           ['Messages']  + self._checkActiveURLTable('message')  + ['team'],
                           ['Requests']  + self._checkActiveURLTable('request')  + ['team']
                          ]
                menu.extend([['Tables',   False, '#', items, 'team']])

            # wiki sub-menue
            if 'wiki_editor' in user_groups or 'wiki_author' in user_groups:
                wiki_menu = [['Guidlines']    + self._checkActiveURLWiki('wiki-guidelines') + ['team'],
                             ['Manage pages'] + self._checkActiveURLWiki('_pages')          + ['team'],
                             ['Search tags']  + self._checkActiveURLWiki('_search')         + ['team'],
                            ]

                if 'wiki_author' in user_groups:
                    wiki_menu.append(['Create new page'] + self._checkActiveURLWiki('_create')            + ['team'])
                    wiki_menu.append(['Edit the menu']   + self._checkActiveURLWiki('_edit', 'wiki-menu') + ['team'])

                if wiki_ctrl and wiki_ctrl.slug and not wiki_ctrl.slug == 'wiki-menu':
                    wiki_menu.append(['Edit this page']  + self._checkActiveURLWiki('_edit',      wiki_ctrl.slug) + ['team'])
                    wiki_menu.append(['Edit page media'] + self._checkActiveURLWiki('_editmedia', wiki_ctrl.slug) + ['team'])

                menu.extend([['Wiki', False, '#', wiki_menu, 'team']])

            # account sub-menu
            items = [['Logout']          + self._checkActiveURLUser('logout')          + ['team'],
                     ['Info']            + self._checkActiveURL('access','info')       + ['team'],
                     ['Profile']         + self._checkActiveURLUser('profile')         + ['team'],
                     ['Change password'] + self._checkActiveURLUser('change_password') + ['team'],
                    ]
            menu.extend([['Account', False, '#', items, 'team']])

            # admin sub-menus
            if 'configurator' in user_groups:
                menu.extend([['Config Event'] + self._checkActiveURL('config','config_event') + ['admin']])

            if 'task executor' in user_groups:
                items = [['Einladungen senden']   + self._checkActiveURLTask('send_invitation')         + ['admin'],
                         ['Warteliste auflösen']  + self._checkActiveURLTask('resolve_waitlist')        + ['admin'],
                         ['Absagen senden']       + self._checkActiveURLTask('send_denial')             + ['admin'],
                         ['Erinnerungen senden']  + self._checkActiveURLTask('send_reminder')           + ['admin'],
                         ['Infos danach senden']  + self._checkActiveURLTask('send_infos_after_market') + ['admin']
                        ]
                menu.extend([['Tasks', False, '#', items, 'admin']])

            if 'admin' in user_groups:

                items = [['Manage users']  + self._checkActiveURL('admin_', 'manage_users')  + ['admin'],
                         ['Configuration'] + self._checkActiveURL('admin_', 'configuration') + ['admin'],
                         ['Benchmark']     + self._checkActiveURL('admin_', 'benchmark')     + ['admin'],
                         ['Actions']       + self._checkActiveURL('admin_', 'actions')       + ['admin']
                        ]

                menu.extend([['Admin', True, '#', items, 'admin']])


        classes = { '_class'                : 'menu vertical',
                    '_data-responsive-menu' : 'accordion',
                    'ul_class'              : 'menu nested',
                    'ul_active'             : 'is-active',
                    'li_sub_active'         : 'is-active',
                    'li_class'              : '',
                    'li_first'              : '',
                    'li_last'               : '',
                    'li_active'             : 'active',
                    'mobile'                : ''
           }

        return (extendedMENU(menu, **classes))
