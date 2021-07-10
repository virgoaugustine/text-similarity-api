from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
from pymongo import MongoClient
from datetime import date
import os

import bcrypt
import spacy

app = Flask(__name__)
CORS(app)
api = Api(app)



client = MongoClient(os.environ['MONGO_URI'], connect=False)
db = client.similaritiesDB
users = db['Users']



############### FUNCTIONS ####################
def checkUserExists(username):
    if users.count_documents({'username': username}) == 1:
        return True #User exists
    else:
        return False #User not exists

def checkEmailExists(email):
    True if users.countDocuments({'email':email}) == 1 else False
        

def verifyPassword(username, password):
    #Fetch user's hashed password in the database
    hashed_password = users.find({'username':username})[0]['password']

    #Compare hashed password from database to password hashed here and see if they match

    if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
        return True
    else:
        return False

def countTokens(username):
    return users.find({'username':username})[0]['tokens']

def fetchName(username):
    return users.find({'username':username})[0]['name']

############# END OF FUNCTIONS #################################


############################# CLASSES ###############################
class Register(Resource):
    def post(self):
        #Get username and password data
        data = request.get_json()
        name = data['name']
        username = data['username']
        email = data['email']
        password = data['password']
        joined = date.today().strftime("%B %d, %Y")

        #Check if username exists in database
        if checkUserExists(username):
            
            retJson = {
                'Message': 'Username taken, try a different username.',
            }
            #Error code 417 - Expectation failed.
            return (retJson, 417)

        #If not, create user, hash password and return 200(ok)
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users.insert({
            'name': name,
            'username': username,
            'email': email,
            'password': hashed_password,
            'tokens': 5, 
            'joined': joined
        })

        retJson = {
            'Message': 'Registration successful', 
            'payload': {
                'name': name,
                'username': username,
                'tokens': countTokens(username)
            }
        }
        return (retJson, 200)

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        password = data['password']
    
        if verifyPassword(username, password):
            retJson = {
                'Message': 'Login successful',
                'payload': {
                    'name': fetchName(username),
                    'username': username,
                    'tokens':countTokens(username)
                }
            }
            return (retJson, 200)

        retJson = {
            'Message': 'Sorry, could not login',
        }
        return (retJson,401)

        

class Detect(Resource):
    def post(self):
        #Get data from user
        data = request.get_json()
        username = data['username']
        text1 = data['text1']
        text2 = data['text2']

        #verify login credentials
        if not checkUserExists(username):
            retJson = {
                'Message': 'Username does not exist',
            }
            return (retJson, 403)
        #Check if user has tokens to complete further processes
        num_tokens = countTokens(username)
        if num_tokens <= 0:
            retJson = {
                'Message': 'Insufficient tokens',
            }
            return (retJson, 403)

        #convert sentences to nlp, calculate ratio and subtract a token for transaction
        nlp = spacy.load("en_core_web_sm")
        text1 = nlp(text1)
        text2 = nlp(text2)
        
        ratio = text1.similarity(text2)

     

        #Return ratio to user
        result = '{0:.2f}%'.format((ratio*100))
        retJson = {
            'Message': f'The two texts are {result} similar',
        }
        return (retJson, 200)

class UpdateTokens(Resource):
    def put(self):
        data = request.get_json()
        username = data['username']

        if countTokens(username) > 0:
            users.update(
                {'username': username},
                {"$set": {'tokens': countTokens(username)-1}}
            )
            retJson = {
                'Message':'tokens updated',
                'payload': countTokens(username)
            }
            return (retJson, 200)
        
        return('Could not update tokens', 400)


class Refill(Resource):
    def post(self):
        #Get username and admin password
        data = request.get_json()
        username = data['username']
        admin_password = data['admin_password']
        refillNumber = data['refillNumber']

        #Verify admin password is correct before adding tokens. For the purpose of simplicity I will use a plain password stored here.
        if admin_password != admin_pass:   
            retJson = {
            'Message': 'Invalid Admin Password',
            'Status': 302
            }
            return jsonify(retJson)

        #Check if user exists in database
        if not checkUserExists(username):
            retJson = {
            'Message': 'User does not exist.',
            'Status': 303
            }
            return jsonify(retJson)

        #Check number of tokens user currently has
        currentTokens = int(countTokens(username))
        refillNumber = int(refillNumber)

        #Add number of tokens you wish to fill plus current number of tokens user has
        users.update_one(
            {'username':username},
            {"$set": {'tokens': currentTokens + refillNumber}}
        )
        retJson = {
        'Message' : 'Tokens refilled successfully.',
        'Status' : 200
        }
        
        return jsonify(retJson)


############################# END OF CLASSES ###############################


@app.route('/')
def test():
    return 'API is running'

################## Add API Resources ##################################
api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(Detect, '/detect')
api.add_resource(UpdateTokens, '/tokenCount')
api.add_resource(Refill, '/refill')
################## End of Add API Resources ##################################
if __name__ == '__main__':
    app.run(debug=True)
