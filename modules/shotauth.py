# -*- coding: utf-8 -*-
from gluon.tools import Auth, Wiki
from shotdbutil import Events
from gluon.html import DIV
import re

class ShotAuth(Auth):
    '''
    This class provides a customized version of the web2py Auth class with some standard settings. 
    '''
    re_wiki_tag = re.compile('<div class="w2p_wiki_tags">.*?</div>')
    
    def __init__(self, db, controller, function):
        self.db = db
        Auth.__init__(self, db = db, controller = controller, function = function)
    
    def shotwiki(self, resolve = True):
        return self.wiki(render = 'multiple', menu_groups='nobody', resolve = resolve)
    
    def get_wiki_rendering(self, slug = None):
        '''
        This method returns the individual rendering method saved with the page record.
        returns string 'html' or 'markmin' (default)
        '''
        render = 'markmin'
        
        if slug:
            query = self.db.wiki_page.slug == slug
            row = self.db(query).select(self.db.wiki_page.render).first()
            if row:
                render = row.render
        return render
    
    def force_shotmenu(self):
        Wiki(self, controller='main', function='wiki', menu_groups='nobody').automenu()
        
    def get_shotwiki_page(self, slug_base, template_set = True):
        '''
        This method retrieves the wiki page identified by the slug base and a template set identifier if desired.
        If a template set shall be taken into account the full wiki slug is constructed. If such a slug exists the page is returned, otherwise the slug base is used as default.
        
        template_set = False:    No template set is applied, i.e. the slug base is used.
        template_set = True:     The template set from the current event is used.
        template_set = <string>: A template set is explicitly specified.
        
        tags = False: This removes the automatically generated DIV container containing the tag search links
        '''
        # initialize slug to retrieve
        slug = slug_base
        
        if template_set:
            if not isinstance(template_set, basestring):
                # use template set from current Event
                template_set = Events(self.db).current.event.template_set
            
            slug_full = '%s-ts-%s' % (slug_base, template_set)
            
            if self.db.wiki_page(slug = slug_full):
                # page with full slug exists => overwrite slug to retrieve
                slug = slug_full
                
        return self.wiki(slug)
        
    def get_lost_and_found_slug(self):
        '''
        This method determines and returns the most recent existing lost-and-found slug, i.e., the one with the highest event number.
        '''
        
        for id in range(Events(self.db).current.event.id, 0, -1):
            slug = 'lost-and-found-event-%d' % id
            if self.wiki(slug):
                break
            else:
                slug = None
        
        return slug
        