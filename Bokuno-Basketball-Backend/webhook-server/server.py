from flask import Flask, request, jsonify, make_response
import wikipedia as wiki
import random
from math import floor
# from cockroach import Cockroach
from pony.flask import Pony
from pony.orm import *
from datetime import datetime
# import PIL

# app = Flask(__name__)
db_params = dict(provider='cockroach', user='rudransh', host='free-tier.gcp-us-central1.cockroachlabs.cloud', port=26257, database='shiny-wolf-1947.defaultdb', password = "rudranshsharma123")


app = Flask(__name__)
app.config.update(dict(
    DEBUG = True,
    PONY = db_params
))
Pony(app)


db = Database()
class User(db.Entity):
    # def __init__(self, table,userid, password, )
    
    _table_ = 'PILOT'
    user_id = PrimaryKey(str)
    password = Required(str)
    searchQ = Set('Search')

class Search(db.Entity):
  _table_ = 'CO'
  # id = PrimaryKey(int)
  user = Required('User')
  searchText = Required(str)
  searchIntent = Required(str)
  imageLink = Required(str)
  searchKeyWord = Required(str)



sql_debug(True)  # Print all generated SQL queries to stdout
db.bind(**db_params)  # Bind Database object to the real database
db.generate_mapping(create_tables=True)  


@db_session  # db_session decorator manages the transactions it is used to add values to the database
def add_values(userid, searchtext, searchintent, imagelink, searchkeyword):
  Search(user = User.get(user_id = userid), searchText = searchtext, searchIntent =searchintent, imageLink=imagelink, searchKeyWord = searchkeyword)

@db_session
def create_user(userid, password):
  User(user_id = userid, password = password, searchQ = None)




@app.route('/') # this is the home page route
def hello_world(): # this is the home page function that generates the page code
    return "Hello world!"


"""
Removed the Login and registering functionality becasue the application didnt need it, and it isnt really secure either ways
if the active user is set like 
active_user = ""
then the login and signuop functionality would return 
"""
active_user = ""

@app.route('/login', methods =  ["POST"])
def login():
  """
  This endpoint is for the logging in of the user. At the moment it is not been used because the value of active user has been fixed, (or hardcoded)
  However, this endpoint works and I have used it during testing but I did not feel any particular need to include this endpioint in the final build
  """
  
  global active_user
  req = request.get_json(force = True, silent = True)
  # print(req.get('username'))
  try:
    user = User.get(user_id = req.get('username'))
    if not user:
      return "UserNotFound"
    # request.args
    # active_user = req.get('username')
    elif user.password != req.get('password'):
      return "WrongPassword"
    else:
      active_user = req.get('username')
      return "success"
  except Exception as e:
    return str(e)


@app.route('/pets', methods = ['GET'])
def return_pets():
  """
  This is just to add cutenss while I worked on the project. I have a VS code extention which I have built which uses this endoint to feed me with cute pics 
  of Doggos, by going to a specific API
  """
  import requests
  d = []
  for i in range(10):
    r=requests.get("https://random.dog/woof.json")
    d.append(r.json()['url'])
  
  print(d)
  
  response = jsonify(images = d)

    # Enable Access-Control-Allow-Origin
  response.headers.add("Access-Control-Allow-Origin", "*")
  return response

@app.route('/wordcloud', methods = ['GET'])
def return_words():
  """
  this endpoint is used to generate word cloud. the way this fucntion works is that it searches for all the searches made by a particular user, and the it returns,
  the string, all joined. I didnt get time to add the frontend for this enpoint which I had made previously. So, with addition of one scren this endpoint too will work, 
  It is evident from the nav bar at the bottom of the flutter aplication 
  """
  
  
  if not active_user:
    return "Sorry you need to be logged in to use this endpoint"
  else:
    a = select(s.searchKeyWord for s in Search if s.user.user_id == active_user)[:]
    a = list(a)
    return " ".join(a)

  
@app.route('/register', methods = ['POST'])
def signup():
  """
  This is the registering endpoint, wherein the users would be allowed to create an ID which would then be saved into the Database, 
  However, due to time limitations and very limited need in the project I decided not to use it this time 
  Howeveer, this endpoint works. To make it work all thats needed to be done is to make the active user, as an empty string.
  """
  
  global active_user
  req = request.get_json(force = True, silent = True)  
  username = req.get('username')
  password = req.get('password')
  # print(user, password)
  try:
    user = User.get(user_id = username)
    if not user:
      print('i was here')
        # create_user(userid = user, password = password)
      User(user_id = username, password = password)
      active_user = username;
      return "SUCESSS, Your ID is created"
    else:
      return "FALIURE, Your ID was already taken"
  except Exception as e:
    return str(e)




def ProperNounExtractor(text):
    """
	As the namme suggests, I was trying to get all the proper nouns out of the search text which would halp me in searching for things which are being asked much better, 
	however, there is this 5 second Webhook window in which I have to send out the results which just made using this function harder, I could have tried 
	Chainnng intents but that would have made things much harder and time was also a factor while I was developing the project, 
	I have heard that this issue is much easily solved in the DiagFlow CX, but that being paid, and to avoid even accidentally paying anything, I had decided not to use that in the past
	"""
	
	# Importing the required libraries
    import nltk 
    from nltk.corpus import stopwords 
    # from nltk.tokenize import word_tokenize, sent_tokenize
    print('PROPER NOUNS EXTRACTED :')
    ans = []
    sentences = nltk.sent_tokenize(text)
    for sentence in sentences:
        words = nltk.word_tokenize(sentence)
        words = [word for word in words if word not in set(stopwords.words('english'))]
        tagged = nltk.pos_tag(words)
        for (word, tag) in tagged:
            if "NN" in tag: # If the word is a proper noun
                ans.append(word)
                print(word)
    return ans


@app.route('/test')
def hola():
  """
  Just a testing endpoint for me to test every function I wrote
  """
  
  x = IwantToLearn("python")
  return x
  
  test()
  test()
  # Search()
  print(active_user)
  return 'added'

def MLHhacks():
  """
  This function, is supposed to handle the MLH, hack intent. It goes to the MLH website and then finds the hacks, which are lined up. for this seasonm,
  It also does minimal data cleaning too
  """
  
  url = "https://mlh.io/seasons/2022/events"
  from requests_html import HTMLSession
  print(url)
  session = HTMLSession()
  response = session.get(url)
  raw_reponse = response.html.find('.event ')
  print(len(raw_reponse))
  x = [x.text.replace("DIGITAL", "").replace("HIGH SCHOOL", "") for x in raw_reponse]
 
  return "\n".join(x)

def FindSomeHacks():
  """
  Find me some hacks, is actually named a little ambigously, It hanndles the Inspiration segement of the webhoook,
  so, the way it works is that, it will go to this specific google search and then return the featured snippet which contains some of the great 
  hackathon project 
  """
  
  url = "https://www.google.com/search?q=cool+hackathon+projects&oq=cool+hackathon+projects&aqs=chrome..69i57.5869j0j1&sourceid=chrome&ie=UTF-8"
  from requests_html import HTMLSession
  print(url)
  session = HTMLSession()
  response = session.get(url)
  raw_reponse = response.html.find('.g ', first = True)
  # print(len(raw_reponse))
  # x = [x.text for x in raw_reponse]
  x = raw_reponse.text
  return x
  
def IwantToLearn(learn):
  """
  This is the brains of the I want to learn intent, It handles the call and returns the needed results. 
  The way this function is written is that, it will be passed on the pharse which is needed to be learnt, and then it will do a quick google search, 
  pick up the featured snippet and then return that snippet with minimal formatiing. It usses HTMLSession instead of the requests module because it makes the thinsg much easier
  """
  
  url = "https://www.google.com/search?q=I+want+to+learn+{learn}".format(learn = learn)
  from requests_html import HTMLSession
  print(url)
  session = HTMLSession()
  response = session.get(url)
  raw_reponse = response.html.find('.g ', first = True)
  # print(len(raw_reponse))
  # x = [x.text for x in raw_reponse]
  x = raw_reponse.text
  return x


    
def try_add_values(userid, searchtext, searchintent, imagelink, searchkeyword):
	"""
	This function was created to circumevent the login process which I have impplemented, 
	I did not wanted to change the main code of the login and registerting processes so it was best to add in a new fucntion which would handle that for me 
	"""
	
	try:
		x = add_values(userid = active_user, searchtext = searchtext,searchintent= searchintent,  imagelink = "yoImage", searchkeyword = searchkeyword)
		print(x)
		return "Added"
    
	except Exception as e:
		if "Attribute" in str(e):
			return "Not Log In"




@app.route('/webhook', methods=['POST'])
def webhook():
	"""
	This function handles the webhook for the Diagflow Bot. It has been written keeping in mind the different intents which the diagflow bot
	has been trained to do. There are three intents as of now, 
	
	1------> Find Next MLH hack, as the name suggests this intent is supposed to give you a list of all the upcoming MLH hackathons, 
	2------> I want to learn Intnet, this one is supposed to handle the requests like, I want to learn this I want to learn that by giving neccasory information about each
	3------> Find me some Inspiration, this intent is supposed to give the users a list of hackathon projects that they would want to try out in the next hackathon

	Other than this, the bot has been trained to handle the small talks wherein it is immaterial that this server is running or not.  

	"""
	returnText = "Ooops, Something Went Wrong"
	theWhatIntentReturnText = ""
	try:
		req = request.get_json(force = True, silent = True)
		res = req.get('queryResult')
 		# print(active_user)
		intent = req.get('queryResult').get("intent").get('displayName')
		if intent == "FindNextMLHHack":
				searchtext = res.get("queryText")
				searchKeyword = res.get("parameters").get("any")
				print(searchKeyword)
				return_text = MLHhacks()
				# def add_values(userid, searchtext, searchintent, imagelink, searchkeyword):
				text = add_values(userid = active_user, searchtext = searchtext, searchintent = intent, imagelink = "yo", searchkeyword = searchKeyword)
				print(text)
				if text == "Not Log In":
					return {
								"fulfillmentText": return_text,
								"source":"webhook"
							}
				else:
					return {
								"fulfillmentText": return_text,
								"source":"webhook"
							}
							
		if intent == "FindMeSomeInspiration":
			searchtext = res.get("queryText")
			searchKeyword = res.get("parameters").get("any")
			return_text = FindSomeHacks()
			text = add_values(userid = active_user, searchtext = searchtext, searchintent = intent, searchkeyword = searchtext, imagelink = "yo")
			
			return {
					"fulfillmentText": return_text,
					"source":"webhook"
				}
		
		if intent == "IwantToLearn":
			searchtext = res.get("queryText")
			searchKeyword = res.get("parameters").get("any")
			return_text = IwantToLearn(searchKeyword)
			text = try_add_values(userid = active_user, searchtext = searchtext, searchintent = intent, searchkeyword = searchKeyword, imagelink = "yo")
			
			return {
					"fulfillmentText": return_text,
					"source":"webhook"
				}

    
	except Exception as e:
		print("def not here")
		return {
			"fulfillmentText": str(e),
			"source": 'webhook'
		}
  
	#There is no reason why this should trigger I have kept this as an additional failsafe althourgh the ssame is been guarentted by the Diagflow side of things
	return {
			"fulfillmentText": 'Something is probably wrong',
			"source": 'webhook'
		}
	
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080) # This line is required to run Flask on repl.it
