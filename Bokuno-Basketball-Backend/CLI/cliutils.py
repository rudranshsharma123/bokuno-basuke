## CLI UTILS AHEAD ----->>>>>>>


import os
import requests
from time import sleep
# from untils.utils import datafile
datafile = '/mnt/d/My projects/selfiehacks/jina/data/smol.csv'

def clear_everything():
    os.system('cls' if os.name == 'nt' else 'clear')

def type_writer_anim(textBlob):
    """
    Just a fancy way to printing out the texts
    """
    for char in textBlob:
        print(char, end="", flush=True)
        sleep(0.02)



def get_ans(text):
    '''
    A simple function which goes to the Jina endpoint of the chatbot and deliveres the answeer to the question asked.
    '''
    
    headers = {
        'Content-Type': 'application/json',
    }

    data = '{"top_k":1,"mode":"search","data":["' + text + '"]}'

    response = requests.post(
        'http://0.0.0.0:34567/search', headers=headers, data=data)

    res = response.json()
    return_text = res["data"]['docs'][0]['matches'][0]['tags']['ans']
    type_writer_anim(return_text)
    
    print('\n')
    
