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
    length = ndb.StringProperty(required=True)
    at_sea = ndb.BooleanProperty(default=True)
    
    
# entity model that will be used to keep a list of the departed vessels in the Slip class 
class Departure_History(ndb.Model):
    departure_date = ndb.DateProperty(required=True) 
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
        self.response.write(json.dumps(boat_dict))
    
    def get(self, boat_id=None):
        self.response.content_type='application/json'
        
        # if the user provided a key/id to a boat 
        # then we GET it and return it by searching via that key 
        # else, we just return the entire list of boats in our datastore 
        if boat_id: 
            boat_GetData=ndb.Key(urlsafe=boat_id).get() 
            boat_dict2=boat_GetData.to_dict()
            boat_dict2['self']='/boats/' + boat_id
            self.response.write(json.dumps(boat_dict2))
        else: 
            boats=Boat.query()
            boat_list=[]
            for boat in boats: 
                boat_dict3=boat.to_dict() 
                boat_dict3['self']='/boats/' + boat.key.urlsafe()
                boat_list.append(boat_dict3)
                self.response.write(json.dumps(boat_list))
                        
        
        
# This is the request handler for the Slip entity model.  In this class we define the GET, POST, PATCH and DELETE 
# actions of this REST API related to this entity model 
class SlipHandler(webapp2.RequestHandler):
    def post(self):
        self.response.content_type='application/json'
        slip_PostData=json.loads(self.request.body)
        
        new_slip = Slip(slip_number=slip_PostData['slip_number'])
        
        new_slip.put()
        slip_dict=new_slip.to_dict()
        slip_dict['self'] = '/slips/' + new_slip.key.urlsafe()
        self.response.write(json.dumps(slip_dict)) 
    
    def get(self, slip_id=None):
        self.response.content_type='application/json'
        
        # if the user provided a key/id to a slip 
        # then we GET it and return it by searching via that key 
        # else, we just return the entire list of boats in our datastore 
        if slip_id: 
            slip_GetData=ndb.Key(urlsafe=slip_id).get() 
            slip_dict2=slip_GetData.to_dict()
            slip_dict2['self']='/slips/' + slip_id
            self.response.write(json.dumps(slip_dict2))
        else: 
            slips=Slip.query()
            slip_list=[]
            for slip in slips: 
                slip_dict3=slip.to_dict() 
                slip_dict3['self']='/slips/' + slip.key.urlsafe()
                slip_list.append(slip_dict3)
                self.response.write(json.dumps(slip_list))
        
        
        
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
# app = webapp2.WSGIApplication([
#     ('/', MainPage), 
#     ('/boats', BoatHandler), 
#     ('/boats/<boat_id>', BoatHandler), 
#     ('/slip', SlipHandler)
#     ], debug=True) 


app = webapp2.WSGIApplication([
    webapp2.Route(r'/', MainPage), 
    webapp2.Route(r'/boats', BoatHandler), 
    webapp2.Route(r'/boats/<boat_id>', BoatHandler), 
    webapp2.Route(r'/slips', SlipHandler),
    webapp2.Route(r'/slips/<slip_id>', SlipHandler)
    ], debug=True) 




