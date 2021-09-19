'''
Imports, some of them were not used so I have thus commented them and VS code has a way of adding useless imports 
'''

import os
from flask import Flask, request, jsonify, make_response
# import random
from jina import Document
from werkzeug.serving import WSGIRequestHandler
import base64
# from cockroach import Cockroach
import io
# from PIL import Image
# from datetime import datetime
# from werkzeug.utils import send_file
# from werkzeug.wrappers import response
app = Flask(__name__)

@app.route('/') # this is the home page route
def hello_world(): # this is the home page function that generates the page code
    return "Hello world!"


def fetchImageJina(imageName):
  '''
  Use this function to get the inherent text associated with the image similar to that image. It takes in the name of the image. The name as which it is saved as in the disk.
  Then this function will send the best match Jina could find
  '''
  '''
  Should be named something like Image-to-text-Jina 
  '''
  '''
  It need the name of the image which is stored in the file system and then it will use Open cv to open the image and then parse it in Jina's primitive datatype, Document
  then it simply converts the image content into URI and then with the helo of that it send the request to the running Jina backendto to see what data it returns
  '''
  import cv2
  import requests
  x = cv2.imread(imageName)
  doc = Document(content = x)
  doc.convert_image_blob_to_uri(width=100, height=100)  

  
  headers = {
        'Content-Type': 'application/json',
    }
  
  data = '{"top_k":1,"mode":"search","data":["' + doc.uri + '"]}'

  response = requests.post(
          'http://172.31.197.41:45678/search', headers=headers, data=data)
  
  res = response.json()
  
  '''
  The issue with this function is that I have not implemented any cleanup, Like, the image which is being stored by the server remains here and thus 
  It will be an issue if it is scaled and put into production, so that's one thing I would immidiately change.
  '''

  return res["data"]['docs'][0]['matches'][0]['text']

def fetchTextJina(searchText):
  '''
  Use this function to search for images in Jina. This function takes in the text for which you would like to search the images for.
  Try Calling this function as fetchImageJina("BasketBall") and this function will return the best image match. It will save the best match image in the disk
  and return the name of the image which it is saved as
  '''
  

  import requests
  import cv2
  text = searchText
  headers = {
        'Content-Type': 'application/json',
    }
  data = '{"top_k":1,"mode":"search","data":["' + text + '"]}'
  response = requests.post(
          'http://172.31.197.41:45678/search', headers=headers, data=data)
  res = response.json()

  b64_string = res['data']['docs'][0]['matches'][0]
  '''
  The lines below are no longer needed in the latest version of Jina if passed like doc = Document(b64string) 
  I tried using that in this project but at that time it really wasnt working so I had to fiddle arouund and come to this conclusion to use these lines.
  The mateched document which Jina returns has the blob as image so, there is no need for thiss
  '''
  
  doc = Document(b64_string)
  doc.convert_image_datauri_to_blob()
  '''
  This is one thing which I would immidiately changwe. In here I am hardcoding only one image, per search, which is far from ideal, 
  I have thus added a loop, which would, now add all the images which are found in the matches. 
  '''

  cv2.imwrite("search.jpg", cv2.cvtColor(doc.blob, cv2.COLOR_RGB2BGR))
  return "search.jpg"


def fetchAns(text):
  '''
  This is a simple function which is the main thngs which works for the Chat bot. This endopoint would send the data and the, 
  answers gotten would be sent.
  '''
  
  import requests
  headers = {
        'Content-Type': 'application/json',
    }

  data = '{"top_k":1,"mode":"search","data":["' + text + '"]}'

  response = requests.post(
        'http://172.31.197.41:34567/search', headers=headers, data=data)

  res = response.json()
  return_text = res["data"]['docs'][0]['matches'][0]['tags']['ans']
  return return_text
    

"""
this enpoint works for the chatting with the Jina Chatbot
"""
@app.route('/chat', methods = ['POST'])
def chat():
  response = request.get_json(silent= True, force= True)
  # res = response.json()
  return fetchAns(response['ask'])



@app.route('/image', methods = ['POST' , 'GET'])
def hola():
    image = request.files['picture']
    print(image.filename)
    image_name = image.filename
    image.save(os.path.join(os.getcwd(), image_name)) #cwd is current working directory
    return_text = fetchImageJina(image_name)
    return jsonify({'ans':return_text})


'''
This is just the testing enpoint, it was made during testing for the image to text search functionality of the application 
'''

@app.route('/test', methods = ['POST' , 'GET'])
def h1ola():
    import cv2
    image = request.files['picture']
    image_name = image.filename
    image.save(os.path.join(os.getcwd(), image_name))
    x = cv2.imread(image_name)
#     cv2.imshow("test",x)
#     cv2.waitKey(0)
  
# # closing all open windows
#     cv2.destroyAllWindows()
    # return "done"
    # return_text = fetchImageJina(image_name)
    # return jsonify({'ans':return_text})
    with open("5.png", "rb") as image_file:
      encoded_string = base64.b64encode(image_file.read())
    return jsonify({'image':[str(encoded_string)]})


"""
ths became a testing enpoint but during development I used this enpoint to send in the images and I was using mainly the images I got from the /pets enpoint of the 
webhook server, but then I discadred the enpoint in the final endpoint
"""
@app.route('/send', methods= ['GET'])
def send():
  with open("1.jpg", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read())
  with open("2.jpg", "rb") as image_file:
    encoded_string2 = base64.b64encode(image_file.read())
  
  x = [str(encoded_string2), str(encoded_string)]
  return jsonify({'images':x})

'''
This is the enpoint which works thee searching functionality. It has the same flaw, it sends only one image which could be a simple fix 
the other main isssue I faced which I gad fixed was the way to send in the bytes of the image which was type casted to a string
this made it really difficult for me in the frontend side, to parse the sent image because of the way python encoded the string,
it added a few extra characters in front and at the back of the string which took me a while to see and realise 
'''

@app.route('/search', methods=['POST'])
def search():
  response = request.get_json(force= True, silent= True)
  print(response['search'])
  return_image = fetchTextJina(response['search'])
  
  with open(return_image, 'rb') as image_file:
    encoded_string = base64.b64encode(image_file.read())
  return jsonify({'image':[str(encoded_string)]}) #this STR Encoding is what I am talkign about. Because if i dont do that I get the error, bytle like object is not JSON seriizable 


  
  
    


if __name__ == '__main__':
  WSGIRequestHandler.protocol_version = "HTTP/1.1"
  app.run(host='0.0.0.0', port=12345)  




#Commented Code which shows my thinking and the different ways in whic I could make the sending and recieivng images work, kept it in for reference of all the things I tried and the things which eventually worked.
#1 
#def hola():
 # x = io.BytesIO(image)
    # # cv2.namedWindow('Image')
    # x = cv2.imread("1.jpg")
    # # img = Image.open('1.jpg', mode = 'r')
    # byte_arr = io.BytesIO(image)
    # base64.encodebytes(byte_arr.getvalue()).decode('ascii')
      # x = cv2.imread(image_name)
    

    # print(len(encoded_string))
    # x = [str(encoded_string2), str(encoded_string)]
    
    # # cv2.imshow(x, mat=)
    # # window_name = 'image'
    # cv2.imshow('Image', x)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # print(x.getvalue())
