# Bokuno-Basketball-Backend



# How to use guide


### Clone the Repository

```bash
     https://github.com/rudranshsharma123/Bokuno-Basketball-Backend.git
```

### Install the Requirements

```bash
    pip install -r requirements.txt
```

### Running the backend

-   First, you need to index the main search app so

```bash
    $ python3 app.py -t index
```
-  Now you need to run the app to accept queries

```bash
    $ python3 app.py -t query_restful
```
- Now that the main app is accepting traffic, you need to run the chatbot app

```bash
    $ cd JIna Chatbot
    $ python3 app.py
```
- Now The jina side is done. You now need to run the flask server which links everything together and provides a single endpoint for the frontend
```bash
    $ cd flask
    $ python3 server.py
```
- It's done. One last thing to ensure is that, edit the endpoints of Jina in the server. Your IP might change so make sure it is set correctly for the app to work

### Go over to the frontend and follow those steps


