from os import defpath
from numpy import diff
import requests
from urllib.request import Request, urlopen


"""
The scrapper file which I have written to gather the data which would be used for both jina flow which uses text and images 
"""

"""
API endpoint, I am using the Pexels api in this case, I have thus found the Unsplash api actually works better in terms of the overall experince and the 
nquality and the accuaracy of the images which I ahve thus found
"""
from os import defpath
from numpy import diff
import requests
from urllib.request import Request, urlopen

def send_request():
    url = "https://api.pexels.com/v1/search?query=basketball&per_page=100"
    api_token = "563492ad6f917000010000019b0c05ab5204447bbfe5189198fa2166"
    headers = {
        "Authorization":api_token,
        
    }
    '''
    Since the API is free and has no restrictiion in terms of the usage so it doesnt matter that my api key is public but the main work of this file is to get the images from the API
    then find the captions which were used when the files were originaly uploaded. 
    '''


    v = 10
    req = requests.get(url= url, headers=headers)
    res = req.json()
    return res

imagesList = send_request()['photos']
images = []

def fetchImages():
    ''' gets the images and downloads them into the hard drive '''
    for v, i in enumerate(imagesList):
        re = requests.get(i["src"]['tiny'],headers= {'User-Agent': 'Mozilla/5.0'} )
        with open('{k}.jpg'.format(k = v), "wb") as f:
            f.write(re.content)

def fetchCaptions():
    """ Since, there were no direct captions available so I decided to use tha actual URL to which had a small description of what the image entails, I plannned to add
        custom captioning but the lack of time didnt allowed me to.
    """
    data = {"name":[], "captions":[]}
    for v, i in enumerate(imagesList):
        x = str(i["url"])
        y = " ".join(x.replace("https://www.pexels.com/photo/", "").split('-')[:-1])
        data['name'].append('{k}.jpg'.format(k = v))
        data["captions"].append(y)
    import pandas as pd
    df = pd.DataFrame(data= data)
    df.to_csv('caption1s.csv')

def win():
    '''
    This is the function which scrapes the data from the website known as wisdom jobs. It had a nice selection of questions and answers through which I decided to use 
    them to feed them into the Jina Chatbot
    '''
    sel = '#loadmore'
    url = "https://www.wisdomjobs.com/e-university/basketball-interview-questions.html"
    from requests_html import HTMLSession
    print(url)
    session = HTMLSession()
    response = session.get(url)
    raw_reponse = response.html.find('.interview_questions', first = True).text
    data = {}
    x = [x for x in raw_reponse.split('\n') if "else" not in x]
    print(x)
    for i, v in enumerate(x):
        if v.startswith("Question"):
            data[v] = []
            while i+1 < len(x) and not x[i+1].startswith("Question"):
                data[v].append(x[i+1])
                i+=1
            data[v] = "\n".join(data[v])
    import pandas as pd
    col = list(data.keys())
    ind = list(data.values())
    d = {'question' :[], 'ans' : [], 'website':url}
    for i, v in enumerate(col):
        d['question'].append(v)
        d['ans'].append(ind[i])
    df = pd.DataFrame(data= d)
    df.to_csv("t2est.csv")

win()



