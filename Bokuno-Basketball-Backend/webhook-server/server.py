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


@db_session  # db_session decorator manages the transactions
def add_values(userid, searchtext, searchintent, imagelink, searchkeyword):
  Search(user = User.get(user_id = userid), searchText = searchtext, searchIntent =searchintent, imageLink=imagelink, searchKeyWord = searchkeyword)

@db_session
def create_user(userid, password):
  User(user_id = userid, password = password, searchQ = None)




@app.route('/') # this is the home page route
def hello_world(): # this is the home page function that generates the page code
    return "Hello world!"

active_user = "hol"

@app.route('/login', methods =  ["POST"])
def login():
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
  if not active_user:
    return "Sorry you need to be logged in to use this endpoint"
  else:
    a = select(s.searchKeyWord for s in Search if s.user.user_id == active_user)[:]
    a = list(a)
    return " ".join(a)

  
@app.route('/register', methods = ['POST'])
def signup():
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
  x = IwantToLearn("python")
  return x
  
  test()
  test()
  # Search()
  print(active_user)
  return 'added'

def MLHhacks():
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
  try:
    add_values(userid = active_user, searchtext = searchtext,searchintent= searchintent,  imagelink = "yoImage", searchkeyword = searchkeyword)
    return "Added"
    
  except Exception as e:
    if "Attribute" in str(e):
      return "Not Log In"




@app.route('/webhook', methods=['POST'])
def webhook():

  returnText = "Ooops, Something Went Wrong"
  theWhatIntentReturnText = ""
  try:
    req = request.get_json(force = True, silent = True)

    res = req.get('queryResult')
 
    # print(searchKeyword)
    intent = req.get('queryResult').get("intent").get('displayName')
    if intent == "FindNextMLHHack":
      searchtext = res.get("queryText")
      searchKeyword = res.get("parameters").get("geo-country")
      return_text = MLHhacks()
      text = try_add_values(userid = active_user, searchtext = searchtext, searchintent = intent, searchkeyword = searchKeyword, imagelink = "yo")
      if text == "Not Log In":
        
      
        return {
            "fulfillmentText": return_text,
            "source":"webhook"
          }
      
      
    # print("Control def not here not here")
    
    if intent == "FindMeSomeInspiration":
      # print('here')
      searchtext = res.get("queryText")
      searchKeyword = res.get("parameters").get("geo-country")
      return_text = FindSomeHacks()
      text = try_add_values(userid = active_user, searchtext = searchtext, searchintent = intent, searchkeyword = searchKeyword, imagelink = "yo")
      
      return {
            "fulfillmentText": return_text,
            "source":"webhook"
          }
    
    if intent == "IwantToLearn":
      # print('here')
      searchtext = res.get("queryText")
      searchKeyword = res.get("parameters").get("any")
      return_text = IwantToLearn(searchKeyword)
      text = try_add_values(userid = active_user, searchtext = searchtext, searchintent = intent, searchkeyword = searchKeyword, imagelink = "yo")
      
      return {
            "fulfillmentText": return_text,
            "source":"webhook"
          }

    



      
      
    
      return {
          "fulfillmentText": returnText,
          "source": 'webhook'
      }

    
  except Exception as e:
    print("def not here")
    return {
        "fulfillmentText": str(e),
        "source": 'webhook'
    }
  print("hell not here")
  
  return {
        "fulfillmentText": 'Something is probably wrong',
        "source": 'webhook'
    }
   
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080) 
