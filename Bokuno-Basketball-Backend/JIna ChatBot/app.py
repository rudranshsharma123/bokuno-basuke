import os
import urllib.request
import webbrowser
from pathlib import Path

from jina import Flow
from jina.types.document.generators import from_csv



workspace_dir = os.path.join(os.path.abspath('workspace'))
"""
I did this because there was the issue with the circular imports. Since the transformer and executors are defined in the python file I had to import them to use them in the flow
There since have been a better way that I have discovered is by simply doing them in a Yaml File and using the Hub executors for the functionality I wanted
"""

if __name__ == '__main__':
    from flow.executers import MyTransformer, MyIndexer
else:
    from executers import MyTransformer, MyIndexer


def _get_flow():
    """ returns the flow object. This was done such that both indexing and querrying used the same flow and hence I did not have to use the click commands in this one.
        this type of thing works fine when there are low number of moving parts as in this only text is being used so only text tranformation would be required. But with 
        the other Image flow, this could have proved to be problematic. That is why I kept it only here.
    """
    return (
        Flow(cors=True)
        .add(uses=MyTransformer)
        .add(uses=MyIndexer, workspace=workspace_dir)
    )


def auto_bot_assemble():
    """
    gets the flow from the function above and then does indexing and querrying, at the same time. 
    """

    f = _get_flow()

    # index it!
    with f, open('data.csv') as fp:
        f.index(from_csv(fp, field_resolver={'question': 'text'}), show_progress=True)

        # switch to REST gateway at runtime
        """
        This way I can define the port at which it runs, since there would be two Jina flows, having them on two different port would be highly essential 
        """
        f.protocol = 'http'
        f.port_expose = '34567'

      
        f.block()




if __name__ == '__main__':
    auto_bot_assemble()
