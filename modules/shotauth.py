# -*- coding: utf-8 -*-
from gluon.tools import Auth, Wiki

class ShotAuth(Auth):
    '''
    This class provides a customized version of the web2py Auth class with some standard settings. 
    '''
    
    def shotwiki(self):
        return self.wiki(render = 'multiple', menu_groups='nobody')
    
    def get_wiki_rendering(self, db = None, slug = None):
        '''
        This method returns the individual rendering method saved with the page record.
        returns string 'html' or 'markmin' (default)
        '''
        render = 'markmin'
        
        if slug and db:
            query = db.wiki_page.slug == slug
            row = db(query).select(db.wiki_page.render).first()
            if row:
                render = row.render
        return render
    
    def force_shotmenu(self):
        Wiki(self, controller='main', function='wiki', menu_groups='nobody').automenu()