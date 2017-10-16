'''
Student Name: Joaquin Saldana 
Assignment 3 - REST Planning and Implementation 

Description: This is the main file that the app.yaml file will read in order to deploy the 
REST for the assignment which involves a Marina with a Boat and Slip 
'''


from google.appengine.ext import ndb 
import webapp2
import json 
import datetime

# =========================================
# ENTITY MODELS 
# =========================================

# entity model for the Boat object/data 
class Boat(ndb.Model):
    name = ndb.StringProperty(required=True)
    type = ndb.StringProperty(required=True)
    length = ndb.IntegerProperty(required=True)
    at_sea = ndb.BooleanProperty(default=True)
    
    
# entity model that will be used to keep a list of the departed vessels in the Slip class 
class Departure_History(ndb.Model):
    departure_date = ndb.StringProperty(required=True) 
    departed_boat = ndb.StringProperty(required=True) 
    
    
# entity model for the Slip object/data  
class Slip(ndb.Model):
    slip_number = ndb.IntegerProperty(required=True)
    current_boat = ndb.StringProperty()
    arrival_date = ndb.StringProperty() 
    depart_history =  ndb.StructuredProperty(Departure_History, repeated=True)
    # This is the optional property for the Slip class that holds an array of data with the boat id and 
    # departure date/time of each boat that has departed from this slip.  


# =========================================
# REQUEST HANDLERS  
# =========================================


# This is the request handler for the Boat entity model.  In this class we define the GET, POST, PATCH, and DELETE 
# actions of this REST API related to this entity model 
class BoatHandler(webapp2.RequestHandler):
    def post(self):
        self.response.content_type='application/json'
        boat_PostData=json.loads(self.request.body)
        
        new_boat = Boat(name=boat_PostData['name'], 
                        type=boat_PostData['type'], 
                        length=boat_PostData['length'])
        
        new_boat.put()
        boat_dict=new_boat.to_dict()
        boat_dict['self'] = '/boats/' + new_boat.key.urlsafe()
        boat_dict['boat_id'] = str(new_boat.key.urlsafe())
        
        self.response.write(json.dumps(boat_dict))
        self.response.status_int = 201
        self.response.status_message='Boat successfully Created'
    
    def get(self, boat_id=None):
        self.response.content_type='application/json'
        
        # if the user provided a key/id to a boat 
        # then we GET it and return it by searching via that key 
        # else, we just return the entire list of boats in our datastore 
        if boat_id: 
            boat_GetData=ndb.Key(urlsafe=boat_id).get() 
            boat_dict2=boat_GetData.to_dict()
            boat_dict2['self']='/boats/' + boat_id
            boat_dict2['boat_id'] = str(boat_id)
            
            self.response.write(json.dumps(boat_dict2))
            self.response.status_int = 201
        else: 
            boats=Boat.query()
            boat_list=[]
            for boat in boats:    
                boat_dict3=boat.to_dict()
                boat_dict3['self']='/boats/' + boat.key.urlsafe()
                boat_dict3['boat_id'] = str(boat.key.urlsafe())
                
                boat_list.append(boat_dict3)
                
            self.response.write(json.dumps(boat_list))
            self.response.status_int = 201
                        
    def delete(self, boat_id=None):
        self.response.content_type='application/json'

        boat = ndb.Key(urlsafe=boat_id).get() 
        
        if boat: 

            slips=Slip.query()
            
            for slip in slips: 
                
                print slip.current_boat
                
                if boat_id == slip.current_boat: 
                    # means the boat is currently docked at a slip             
                    slip.current_boat = None 
                    
                    departures = []
                     
                    for departs in slip.depart_history: 
                            departures.append(departs)
                    
                    today=datetime.date.today()
                    departures.append(Departure_History(departure_date=today.strftime("%b-%m-%Y"),
                                                departed_boat=boat.key.urlsafe()))
                    
                    slip.depart_history = departures
                    slip.arrival_date = None 
                    boat.at_sea = True 
                    
                    boat.put() 
                    slip.put() 
                    

            boat_key = boat.key 
            boat_key.delete() 
            self.response.status_int = 201
            self.response.status_message='Boat successfully Deleted'
            self.response.out.write('Boat successfully Deleted')
                    
        else: 
            self.response.status_int = 505
            self.response.status_message="Boat key not included or is invalid key"
            self.response.out.write('Boat key not included or is invalid key')
            
    def patch(self, boat_id=None):
        self.response.content_type = 'application/json'
        boat_PatchData = json.loads(self.request.body)
        boat = ndb.Key(urlsafe=boat_id).get() 
        
        if boat: 
            if 'name' in boat_PatchData: 
                boat.name=boat_PatchData['name']
            if 'type' in boat_PatchData: 
                boat.type=boat_PatchData['type']
            if 'length' in boat_PatchData: 
                boat.length=boat_PatchData['length']
                
            boat.put() 
            
            boat_dict=boat.to_dict() 
            boat_dict['self'] = '/boats/' + boat.key.urlsafe()
            boat_dict['boat_id'] = str(boat.key.urlsafe())
            
            self.response.status_int = 201
            self.response.write(json.dumps(boat_dict))
            
        else: 
            self.response.status_int = 505 
            self.response.status_message ="Boat was not found.  Invalid key"
            self.response.out.write('Boat was not found.  Invalid key')

    
    def put(self, boat_id):
        self.response.content_type='application/json'
        boat_PutData=json.loads(self.request.body)
        boat = ndb.Key(urlsafe=boat_id).get() 
        
        if boat: 
            boat.name=boat_PutData['name']
            boat.type=boat_PutData['type']
            boat.length=boat_PutData['length']
            
            boat.put() 
            
            boat_dict=boat.to_dict() 
            boat_dict['self'] = '/boats/' + boat.key.urlsafe()
            boat_dict['boat_id'] = str(boat.key.urlsafe())
            
            self.response.status_int = 201
            self.response.write(json.dumps(boat_dict))
        else: 
            self.response.status_int = 505 
            self.response.status_message ="Boat was not found.  Invalid key"
            self.response.out.write('Boat was not found.  Invalid key')
            
        
# This is the request handler for the Slip entity model.  In this class we define the GET, POST, PATCH and DELETE 
# actions of this REST API related to this entity model 
class SlipHandler(webapp2.RequestHandler):
    # POST method will check to see if the slip number already exists.  If it does then it will not complete 
    # the POST because the number already exists
    def post(self):
        self.response.content_type='application/json'
        slip_PostData=json.loads(self.request.body)

        slips=Slip.query()
        
        new_slipNumber=slip_PostData['slip_number']
        
        slipNumberExists=False
        
        if slips: 
            
            for slip in slips: 
                if new_slipNumber == slip.slip_number: 
                    slipNumberExists=True
                    break
    
            if slipNumberExists: 
                self.response.status_int = 505 
                self.response.status_message ="Slip number already exists"
                self.response.out.write('Slip number already exists')
            else: 
                new_slip = Slip(slip_number=slip_PostData['slip_number'])
                new_slip.put()
                slip_dict=new_slip.to_dict()
                slip_dict['self'] = '/slips/' + new_slip.key.urlsafe()
                slip_dict['slip_id'] = str(new_slip.key.urlsafe())  
                self.response.write(json.dumps(slip_dict)) 
                print "The new slip was added"
                self.response.status_int = 201
        else: 
            new_slip = Slip(slip_number=slip_PostData['slip_number'])
            new_slip.put()
            slip_dict=new_slip.to_dict()
            slip_dict['self'] = '/slips/' + new_slip.key.urlsafe()
            slip_dict['slip_id'] = str(new_slip.key.urlsafe())  
            self.response.write(json.dumps(slip_dict)) 
            self.response.status_int = 201
            print "The new slip was added because none existed"
            
           
    def get(self, slip_id=None):
        self.response.content_type='application/json'
        
        # if the user provided a key/id to a slip 
        # then we GET it and return it by searching via that key 
        # else, we just return the entire list of boats in our datastore 
        if slip_id: 
            slip_GetData=ndb.Key(urlsafe=slip_id).get() 
            slip_dict2=slip_GetData.to_dict()
            slip_dict2['self']='/slips/' + slip_id
            slip_dict2['slip_id'] = str(slip_id)
            
            self.response.write(json.dumps(slip_dict2))
        else: 
            slips=Slip.query()
            slip_list=[]
            for slip in slips: 
                slip_dict3=slip.to_dict() 
                slip_dict3['self']='/slips/' + slip.key.urlsafe()
                slip_dict3['slip_id'] = str(slip.key.urlsafe())
                
                slip_list.append(slip_dict3)
                
            self.response.write(json.dumps(slip_list))
        
    def delete(self, slip_id=None):
        self.response.content_type='application/json'
        slip = ndb.Key(urlsafe=slip_id).get() 
        if slip: 
            if slip.current_boat: 
                boat=ndb.Key(urlsafe=slip.current_boat).get()
                boat.at_sea=True 
                boat.put() 
                  
            slip_key = slip.key 
            slip_key.delete() 
            self.response.status_int = 201
            self.response.status_message='Slip successfully Deleted'
            self.response.out.write('Slip successfully Deleted')
        else: 
            self.response.status_int = 505 
            self.response.status_message ="Slip key not included or is invalid key"
            self.response.out.write('Slip key not included or is invalid key')


    def patch(self, slip_id=None):
        self.response.content_type = 'application/json'
        slip_PatchData = json.loads(self.request.body)
        slip = ndb.Key(urlsafe=slip_id).get() 
        
        if slip: 

            slipsList=Slip.query()
            
            new_slipNumber=slip_PatchData['slip_number']
            slipNumberExists=False
        
            for s in slipsList: 
                if new_slipNumber == s.slip_number: 
                    slipNumberExists=True
                    break
    
            if slipNumberExists: 
                self.response.status_int = 505 
                self.response.status_message ="Slip number already exists"
                self.response.out.write('Slip number already exists')
            else:
                
                if 'slip_number' in slip_PatchData: 
                    slip.slip_number=slip_PatchData['slip_number']
        
                slip.put() 
                
                slip_dict=slip.to_dict() 
                slip_dict['self'] = '/slips/' + slip.key.urlsafe()
                slip_dict['slip_id'] = str(slip.key.urlsafe())
                
                self.response.status_int = 201
                self.response.write(json.dumps(slip_dict))
        else: 
            self.response.status_int = 505 
            self.response.status_message ="Slip was not found. Invalid key"
            self.response.out.write('Slip was not found.  Invalid key') 


#     def put(self, slip_id):
#         self.response.content_type='application/json'
#         slip_PutData=json.loads(self.request.body)
#         slip = ndb.Key(urlsafe=slip_id).get() 
#         
#         if slip: 
#             slip.slip_number=slip_PutData['slip_number']
# 
#             slip.put() 
#             
#             slip_dict=slip.to_dict() 
#             slip_dict['self'] = '/slips/' + slip.key.urlsafe()
#             slip_dict['slip_id'] = str(slip.key.urlsafe())
#             
#             self.response.write(json.dumps(slip_dict))
#         else: 
#             self.response.status_int = 505 
#             self.response.status_message ="Slip was not found.  Invalid key"
#             self.response.out.write('Slip was not found.  Invalid key')



# This is the handler for the user to set the boat to sea and modifies the 
# properties of the Boat and the Slip that include the arrival date, departure history, 
# current boat, and more
class AtSeaHandler(webapp2.RequestHandler):
    def put(self, boat_id=None, slip_id=None):
        self.response.content_type='application/json'
    
        slip = ndb.Key(urlsafe=slip_id).get() 
        boat = ndb.Key(urlsafe=boat_id).get() 
    
        dock_DeleteData=json.loads(self.request.body)
        depart_date=dock_DeleteData['departure_date']
        
        if not slip: 
            self.response.status_int=405
            self.response.status_message="Invalid Slip ID"
            self.response.out.write("Invalid Slip ID")
        elif not boat: 
            self.response.status_int=404 
            self.response.status_message="Invalid Boat ID"
            self.response.out.write("Invalid Boat ID")
        elif boat.at_sea: 
            self.response.status_int=402
            self.response.status_message="Boat already at sea"
            self.response.out.write("Boat already at sea") 
        elif slip.current_boat is None : 
            self.response.status_int=403
            self.response.status_message="Forbidden - Slip is already empty"
            self.response.out.write("Forbidden - Slip is already empty")    
        else: 

            slip.current_boat = None 
            
            departures = []
             
            for departs in slip.depart_history: 
                    departures.append(departs)
            
            departures.append(Departure_History(departure_date=depart_date,
                                        departed_boat=boat.key.urlsafe()))
            
            slip.depart_history = departures
            slip.arrival_date = None 
            boat.at_sea = True 
            
            boat.put() 
            slip.put() 
            
            resp= []
        
            slip_dict=slip.to_dict() 
            slip_dict['self'] = '/slips/' + slip.key.urlsafe()
            slip_dict['slip_id'] = str(slip.key.urlsafe())
            
            resp.append(slip_dict)
            
            boat_dict=boat.to_dict()
            boat_dict['self']='/boats/' + boat.key.urlsafe()
            boat_dict['boat_id'] = str(boat.key.urlsafe())
            
            resp.append(boat_dict)
            
            self.response.write(json.dumps(resp))
            
            self.response.status_int=201
            self.response.status_message="Boat successfully un-docked from slip"
            self.response.out.write("Boat successfully un-docked from slip")  



class DockHandler(webapp2.RequestHandler):
    # Docking a boat onto a slip 
    def put(self, slip_id=None, boat_id=None):
        self.response.content_type='application/json'
        
        slip = ndb.Key(urlsafe=slip_id).get() 
        boat = ndb.Key(urlsafe=boat_id).get() 
        
        dock_PutData=json.loads(self.request.body)
        arrival_date=dock_PutData['arrival_date']
                
        if not slip: 
            self.response.status_int=405
            self.response.status_message="Invalid Slip ID"
            self.response.out.write("Invalid Slip ID")
        elif not boat: 
            self.response.status_int=404 
            self.response.status_message="Invalid Boat ID"
            self.response.out.write("Invalid Boat ID")    
        elif slip.current_boat: 
            self.response.status_int=403
            self.response.status_message="Forbidden - Slip is currently taken"
            self.response.out.write("Forbidden - Slip is currently taken")                       
        elif boat.at_sea == False: 
            self.response.status_int=402
            self.response.status_message="Boat already docked"
            self.response.out.write("Boat already docked")                 
        else: 
            slip.current_boat = boat.key.urlsafe()
            slip.arrival_date = arrival_date
            boat.at_sea = False
            slip.put() 
            boat.put() 
            
            resp= []
            
            slip_dict=slip.to_dict() 
            slip_dict['self'] = '/slips/' + slip.key.urlsafe()
            slip_dict['slip_id'] = str(slip.key.urlsafe())
            slip_dict['boat_link'] = "/boats/" + boat.key.urlsafe()
            
            resp.append(slip_dict)
            
            boat_dict=boat.to_dict()
            boat_dict['self']='/boats/' + boat.key.urlsafe()
            boat_dict['boat_id'] = str(boat.key.urlsafe())
            
            resp.append(boat_dict)
            
            self.response.write(json.dumps(resp))
            
            self.response.status_int=201
            self.response.status_message="Boat successfully socked to slip"
            self.response.out.write("Boat successfully socked to slip")     
        
 
class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Joaquin Saldana - Assignment 3 - REST Planning and Implementation')


# =========================================
# APPLICATION
# =========================================


# As per video the source of the code for the PATH handler is the following: 
# https://stackoverflow.com/questions/16280496/patch-method-handler-on-google-appengine-webapp2
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods


# dont forget to add the commas here after each URL path and handler tuple else 
# the console will throw an error 
app = webapp2.WSGIApplication([
    webapp2.Route(r'/', handler=MainPage), 
    webapp2.Route(r'/boats', handler=BoatHandler), 
    webapp2.Route(r'/boats/<boat_id>', handler=BoatHandler), 
    webapp2.Route(r'/slips', handler=SlipHandler),
    webapp2.Route(r'/slips/<slip_id>', handler=SlipHandler),
    webapp2.Route(r'/slips/<slip_id>/dock/<boat_id>', handler=DockHandler), 
    webapp2.Route(r'/boats/<boat_id>/atsea/<slip_id>', handler=AtSeaHandler) 
    ], debug=True) 




