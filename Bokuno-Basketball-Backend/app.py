"""
Imports
"""
import os
import sys

import click
from jina import Flow, Document
import logging
from jina.logging.profile import TimeContext

from dataset import input_index_data
"""
Need to define the max docs which Jina would both index and query the same thing could be done in the YAML file as well, but since I am using .PY file
for the executors so It was best to define it like that
"""

MAX_DOCS = int(os.environ.get("JINA_MAX_DOCS", 50))
cur_dir = os.path.dirname(os.path.abspath(__file__))



def config():
    """
    This function defines the main things which are needed for Jina to work properly, the main thing here, which is absolutely needed is the workspace DIR
    Everytime Jina indexes documents, it makes a folder, named Workspace, which contains all the key things which It will need during Indexing
    """
    
    os.environ['JINA_PARALLEL'] = os.environ.get('JINA_PARALLEL', '1')
    os.environ['JINA_SHARDS'] = os.environ.get('JINA_SHARDS', '1')
    os.environ["JINA_WORKSPACE"] = os.environ.get("JINA_WORKSPACE", "workspace")
    os.environ['JINA_PORT'] = '45678'


def index_restful():
    """
    This enpoint is supposed to index all the documents dynamically, all it needs is a post request on this endpoint to add the documents into the indexed documents which could 
    be the used to querry
    """

    flow = Flow().load_config('flows/flow-index.yml', override_with={'protocol': 'http'})
    with flow:
        flow.block()


def check_index_result(resp):
    """
    for testing if the idexing is done correctly or not
    """
    for doc in resp.data.docs:
        _doc = Document(doc)
        print(f'{_doc.id[:10]}, buffer: {len(_doc.buffer)}, mime_type: {_doc.mime_type}, modality: {_doc.modality}, embed: {_doc.embedding.shape}, uri: {_doc.uri[:20]}')


def check_query_result(resp):
    """
    this does a single request on the server to check if the returned documents is correct. Meaning, text and the images are being retuened or not
    """
    for doc in resp.data.docs:
        _doc = Document(doc)
        print(f'{_doc.id[:10]}, buffer: {len(_doc.buffer)}, embed: {_doc.embedding.shape}, uri: {_doc.uri[:20]}, chunks: {len(_doc.chunks)}, matches: {len(_doc.matches)}')
        if _doc.matches:
            for m in _doc.matches:
                print(f'\t+- {m.id[:10]}, score: {m.scores["doc_score"].value}, text: {m.text}, modality: {m.modality}, uri: {m.uri[:20]}')


def index(data_set, num_docs, request_size):
    """
    This function is the heart of any Jina flow. It goes through all the documents and then it indexes them, which the query flow would use to return the results.
    """

    flow = Flow().load_config('flows/flow-index.yml')
    with flow:
        with TimeContext(f'QPS: indexing {num_docs}', logger=flow.logger):
            flow.index(
                inputs=input_index_data(num_docs, request_size, data_set),
                request_size=request_size,
                on_done=check_index_result
            )


def query():
    """
    Used to give only a single post request. This function works best for testing as can be seen by the on done callback, since this fucntion would open up
    a new query flow each time it is called, it is neither time effiecient nor memory and cannot scale or be used to put into production
    """

    flow = Flow().load_config('flows/flow-query.yml')
    with flow:
        flow.search(inputs=[
            Document(text='a black dog and a spotted dog are fighting', modality='text'),
            Document(uri='toy-data/images/1000268201_693b08cb0e.jpg', modality='image')
        ],
            on_done=check_query_result)


def query_restful():
    """
    Main function which is used to call the query flow and it usses the Rest interface to serve search queries and return the results from the indexed database 
    """
    flow = Flow().load_config('flows/flow-query.yml', override_with={'protocol': 'http'})
    with flow:
        flow.block()


"""
using the click module to run this script in the terminal, mainly one should use the -t index and the -t query_restful
"""


@click.command()
@click.option('--task', '-t', type=click.Choice(['index', 'index_restful', 'query_restful', 'query']), default='index')
@click.option("--num_docs", "-n", default=MAX_DOCS)
@click.option('--request_size', '-s', default=16)
@click.option('--data_set', '-d', type=click.Choice(['f30k', 'f8k', 'toy-data'], case_sensitive=False), default='toy-data')
def main(task, num_docs, request_size, data_set):
    config()
    workspace = os.environ['JINA_WORKSPACE']
    logger = logging.getLogger('cross-modal-search')
    if 'index' in task:
        if os.path.exists(workspace):
            logger.error(
                f'\n +------------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                           | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again.  | \
                    \n |                                   🤖🤖🤖                                           | \
                    \n +------------------------------------------------------------------------------------+'
            )
            sys.exit(1)
    if 'query' in task:
        if not os.path.exists(workspace):
            logger.error(f'The directory {workspace} does not exist. Please index first via `python app.py -t index`')
            sys.exit(1)

    if task == 'index':
        index(data_set, num_docs, request_size)
    elif task == 'index_restful':
        index_restful()
    elif task == 'query':
        query()
    elif task == 'query_restful':
        query_restful()


if __name__ == '__main__':
    main()
