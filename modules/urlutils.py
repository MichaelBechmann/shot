# -*- coding: utf-8 -*-
'''
creation: bechmann, Aug 21, 2013

This module contains miscellaneous general utility functions
'''

from gluon.html import URL


def URLWiki(args = 'start'):
    return URL('main', 'wiki', args = args)

def URLTable(args = 'wait', vars = None):
    return URL('staff','table', args = args, vars = vars)

def URLUser(args = 'profile'):
    return URL('access','user', args = args)

def URLTask(args = 'send_invitation'):
    return URL('tasks', 'start', args = args)