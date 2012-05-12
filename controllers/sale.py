'''
This file contains everything related to the sale data (sale number, contributions, etc.).
'''

# Static analyzer import helpers: (STATIC_IMPORT_MARK)
if 0: 
    from gluon.languages import translator as T
    from gluon import *
    import gluon
    global request
    global response
    global session
    global db
    
from shotmail import *

T.force('de')

def __validate_contributions(form):
    '''
    Functions that take arguments or start with a double underscore are not publicly exposed and can only be called by other functions.
    
    This validation function checks whether or not a t least one of the possible contribution checkbox fields has been checked.
    '''
    
    count = 0
    b_no_contrib_checked = False
    s_no_contrib_label = ''
    for c in config.contribution_data:
        name = c['name']
        if name in form.vars:
            if form.vars[name] != None:
                count += 1
                if name == 'no_contribution':
                    b_no_contrib_checked = True
                    s_no_contrib_label = c['label']
        
    if count == 0:
        form.errors.msg = T('You didn\'t check any of the contribution options! Please confirm that you cannot contribute anything.')
    elif count > 1 and b_no_contrib_checked:
        form.errors.msg = T('You made an inconsistent choice! Please either check some contribution or confirm that you cannot contribute anything.')



def form():
    # check whether or not the sale information form shall be displayed
    if session.id == None or db.vendor(session.id).number != None:
        redirect(URL('main', 'index'))
    
    sale = Sale(session.id)
    l = sale.getfreenumbers()
    
    if len(l) == 0:
        redirect(URL('no_numbers'))
    
    l.insert(0, sale.nonumber)
    formgroups = []
    formgroups.append(FIELDSET(T('My desired sale number:'), SELECT(l, _name='number'), _id = 'form_group_sale_number', _class = 'form_group'))
    
    if config.debug == True:
        response.flash = 'counts: '
  
  
  
    for group in config.contribution:
        elements = [] 
        
        if 'title' in group:
            elements.append(DIV(T(group['title']), _class = 'form_group_title'))
        
        for c in group['data']:
            name = c['name']
            # check if target number for this contribution has been reached already
            count = 0
            for row in db(db.vendor[name] == True).select():
                count += 1
    
            if config.debug == True:
                response.flash = response.flash + ' ' + name + ': ' + str(count) + ' '            
            
            b_display_option = True   
            if 'target' in c:
                if count >= c['target']:
                    b_display_option = False
            
            # construct checkbox form elements including style information
            contents   = []
            attributes = {}
            
            if b_display_option: 
                attributes['_class'] = 'checkbox_active'
                contents.append(INPUT(_type = 'checkbox', _name = name)) 
            else:
                attributes['_class'] = 'checkbox_inactive'
                contents.append('--- ') 
                
            contents.append(T(c['label']))
            elements.append(DIV(*contents, **attributes))
  
        formgroups.append(DIV(*elements, _id = group['id'], _class = 'form_group'))
  
  
        
    formgroups.append(DIV(T('My message:'), TEXTAREA(_type = 'text', _name='message', _cols = 50,_rows = 5),   _id = 'form_group_message', _class = 'form_group'))
    formgroups.append(DIV(INPUT(_type = 'submit', _class = 'button', _value = T('submit')), _id = 'form_group_submit',  _class = 'form_group'))

    form = FORM(*formgroups)
    
    # pre-populate the form in case of re-direction from form_vendor_confirm() (back button pressed)
    # see book, section 'Pre-populating the form' in chapter 'Forms and Validators'
    if session.sale_vars:
        form.vars = session.sale_vars
     

    if form.validate(onvalidation = __validate_contributions):      
        session.sale_vars = form.vars
        sale.setnumber(session.sale_vars)
        redirect(URL('confirm'))
    
    if session.sale_error_msg:
        form.errors.msg = session.sale_error_msg
        session.sale_error_msg = None
        
      
    return dict(form = form, id = session.id, assigned = sale.assigned)


def confirm():
    # check if there is vendor information to be confirmed
    if session.sale_vars == None:
        redirect(URL('main', 'index'))
    
    # construct display of data to be confirmed
    data_elements = []
    
    vendor_name = db.vendor(session.id).forename + ' ' + db.vendor(session.id).name  
    data_elements.append(TR(T('You are:'), vendor_name))
    data_elements.append(TR(T('Your sale number is:'), DIV(session.sale_vars['number'], _id = 'sale_number')))
    
    for c in config.contribution_data:
        if c['name'] in session.sale_vars: # This clumsy construct is necessary as there is an error if one of the contributions is full and therefore not in form.vars!
            if session.sale_vars[c['name']] != None:
                t = ''
                if 'title' in c:
                    t = T(c['title']) + ', ' 
                data_elements.append(TR(T('Your contribution:'), t + T(c['label'])))
    
    if session.sale_vars['message']:
        data_elements.append(TR(T('You left a message:'), session.sale_vars['message']))
    
    data = TABLE(*data_elements)
        
    
    # The _name arguments are important as the one of the pressed button will appear in request.vars.
    form = FORM(TABLE(TR(
                         INPUT(_type = 'submit', _class = 'button', _name = 'submit back', _value = T('back')),
                         INPUT(_type = 'submit', _class = 'button', _name = 'submit send', _value = T('go!')))
                        )
                )
        
    if 'submit back' in request.vars:
        redirect(URL('form'))
    elif 'submit send' in request.vars:
            
        # Add the sale information to the database and send mail:
        if session.sale_vars != None:  
            sale = Sale(session.id)
            try:
                # Add submitted information to database record.
                sale.setdbentries(session.sale_vars)
                session.sale_vars = None # prevent multiple database entries
                
                # send mail with sale number
                sale.sendnumbermail()
                next = URL('final')
                
            except:
                '''
                If the number to be added is already in the table for some reason the 'unique' attribute of the field 'number'
                causes an exception.
                '''
                session.sale_vars.number = None     # Do not pre-populate form with number which is already assigned!
                session.sale_error_msg = T('Oops! Your sale number has just been assigned to someone else. Please choose another one.')
                next = URL('form')
              
            redirect(next)      
        
    return(dict(form = form, data = data))

def final():
    return dict()

def no_numbers():
    return dict()


class Sale():
    '''
    This class provides methods for handling all sale related information like sale numbers or help/pay information.
    These methods include all interaction with the database.
    '''
    def __init__(self, id):  
        self.id = id
        self.assigned = []
        self.free = []
        self.nonumber = ' - '

    def _get_assigned(self):

        for row in db(db.vendor.number != None).select():
            self.assigned.append(row.number)

    
    def getfreenumbers(self):
        '''
        This method constructs a list of all still free numbers. It starts with a list of 
        all numbers in the configured ranges. Then the already assigned numbers are removed.
        '''
        
        if db.vendor(self.id).kindergarten != config.no_kindergarten_id:
            number_ranges = config.numbers.available_kg
        else:    
            number_ranges = config.numbers.available
        
        for r in number_ranges:
            self.free.extend(range(r[0], r[1] + 1))
        
        self._get_assigned()
        for n in self.assigned:
            if n in self.free:
                self.free.remove(n)

        return(self.free)

    def setnumber(self, vars):
        # This function checks if a sale number has been chosen.
        # If not the number is assigned automatically. Note that the form.vars object passes to this function (by reference) is modified!
        # To keep track of the user input a new boolean field is added.
        vars.number_assigned = False
        if vars.number == self.nonumber:
            vars.number_assigned = True
            self.getfreenumbers()
            vars['number'] = self.free[-1]
            
        
        
        
    def setdbentries(self, vars):
        # vars is passed as reference. A local copy of the dict shall be used such that vars is not modified.
        local_vars = {}  
     
        # convert on, None => True, False
        for k, v in vars.iteritems():
            if v != self.nonumber:
                if v == None:
                    v = False
                elif v == 'on':
                    v = True
            local_vars[k] = v

        # add sale number and all contributions data to data base 
        db(db.vendor.id == self.id).update(**local_vars) 

    def __construct_contributions(self, vendor):
        # This code is based on sale.py/confirm()
        # The contributions for the sale number mail are constructed here because the T()-operator and the HTML helpers naturally are available.
        data_elements = []
        for c in config.contribution_data:
            if c['name'] in vendor:
                if vendor[c['name']] == True:
                    t = ''
                    if 'title' in c:
                        t = T(c['title']) + ', ' 
                    data_elements.append(LI(t + T(c['label'])))
          
        return(str(UL(*data_elements)))
        
    def sendnumbermail(self):
        vendor = db.vendor(self.id).as_dict()
        contributions = self.__construct_contributions(vendor)
        m = NumberMail(vendor, contributions)
        m.send()
        