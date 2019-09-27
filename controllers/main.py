# -*- coding: utf-8 -*-
# Static analyzer import helpers: (STATIC_IMPORT_MARK)
if 0:
    from gluon.languages import translator as T
    from gluon import *
    import gluon
    global request
    global response
    global shotdb
    global auth

from shotdbutil import Events
from shotmail import ErrorMail
from shotconfig import config
from gluon.storage import Storage
from urlutils import URLWiki
from shoterrors import ShotError, ShotErrorInvalidPage
T.force('de')


def error():
    url = request.vars['request_url']

    if config.enable_error_mail:
        ErrorMail().send()
    ticket = request.vars.ticket

    if config.redirect_to_ticket and ticket:
            redirect(config.shotticketurl + ticket)

    if '/components/' in url:
        return DIV('Diese Komponente konnte aufgrund eines Fehlers nicht geladen werden!', _class = 'error-component')
    else:
        redirect(URLWiki('error'))




def redirect_https():

    l = len(request.args)

    if l < 2:
        c = 'main'
        f = 'wiki'
        args = ['start']
    else:
        c = request.args[0]
        f = request.args[1]
        if l > 2:
            args = request.args[2:]
        else:
            args = []

    redirect(URL(c = c, f = f, args = args, scheme = 'https'))


def wiki():

    wiki = auth.shotwiki()
    wiki_ctrl = Storage()

    if str(request.args(0)).startswith('_'):
        wiki_ctrl.cmd    = request.args(0)
        wiki_ctrl.slug   = request.args(1)
        wiki_ctrl.render = auth.get_wiki_rendering(wiki_ctrl.slug )
        response.flash_custom_display = True # hide default wiki flash messages
    else:
        wiki_ctrl.slug = request.args(0)

        if wiki_ctrl.slug == 'start':
            if config.display_flash_schedule:
                response.flash = auth.get_shotwiki_page(slug_base = 'market-schedule')

    if str(request.args(0)) != '_preview':
        wiki['wiki_ctrl'] = wiki_ctrl

    if wiki_ctrl.slug and str.lower(wiki_ctrl.slug) == 'zwillingsmarkt':
        #response.b_noindex = True
        redirect(URL('main','wiki', args = ['start']))

    return wiki


def wiki_snippet():
    slug = request.args(0)
    if slug:
        return auth.get_shotwiki_page(slug, template_set = False)
    else:
        return 'Bitte verwenden Sie einen gültigen slug: @{component:main/wiki_snippet/the_slug}'



def lost_and_found():
    '''
    This auxiliary function redirects to the most recent existing lost-and-found page wiki page.
    '''
    slug = auth.get_lost_and_found_slug()
    if slug:
        redirect(URLWiki(slug))
    else:
        raise ShotErrorInvalidPage('The current lost-and-found page could not be determined!')

