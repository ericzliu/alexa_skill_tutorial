from flask import Flask
from flask import request
from flask import make_response
import datetime
import json
import os

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/alexa_endpoint", methods=['POST'])
def alexa():
    event = request.get_json()
    req = event['request']

    if req['type'] == 'LaunchRequest':
        return handle_launch_request()
    elif req['type'] == 'IntentRequest':
        if req['intent']['name'] == 'HelloIntent':
            return handle_hello_intent(event)
        else:
            return "", 400
        pass
    elif req['type'] == 'QuoteIntent':
        pass
    elif req['type'] == 'NextQuoteIntent':
        pass
    elif req['type'] == 'AMAZON.CancelIntent' or req['type'] == 'AMAZON.StopIntent':
        pass
    elif req['type'] == 'SessionEndedRequest':
        return handle_launch_request()
    else:
        pass

def handle_launch_request():
    answer = Response()
    answer.speech_text = 'Welcome to Greetings Skill. Using our skill you can greeting your guests. Whom you want to greet?'
    answer.reprompt_text = 'You can say for example, say hello to John.'
    answer.end_session = False
    return answer.build_response()

def handle_hello_intent(event):
    req = event['request']
    name = req['intent']['slots']['FirstName']['value']
    answer = Response()
    answer.speech_text = 'Hello {0}. '.format(name)
    answer.speech_text += get_wish()
    answer.end_session = True
    return answer.build_response()   

def get_wish():
    current_time = datetime.datetime.utcnow()
    hours = current_time.hour
    if hours < 12:
        return 'Good morning.'
    elif hours < 18:
        return 'Good afternoon.'
    else:
        return 'Good evening.'

class Response(object):
    """Alexa skill response"""

    def __init__(self):
        super(Response, self).__init__()
        self.speech_text = None
        self.reprompt_text = None
        self.end_session = True

    def build_response(self):
        '''
        Build Alexa skill response and returns
        '''
        body = {
            'version' : '1.0',
            'response' : {
                'outputSpeech' : {
                    'type' : 'SSML',
                    'ssml' : '<speak>' + self.speech_text + '</speak>'
                },
                'shouldEndSession' : self.end_session
            }
        }

        if self.reprompt_text:
            body['response']['reprompt'] = {
                'outputSpeech': {
                    'type' : 'SSML',
                    'ssml' : '<speak>' + self.reprompt_text + '</speak>'
                }
            }

        http_response = make_response(json.dumps(body))    
        http_response.headers['Content-Type'] = 'application/json'
        return http_response
        

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    print('Starting app on port ' + str(port))
    app.run(port = port, host = '0.0.0.0')

