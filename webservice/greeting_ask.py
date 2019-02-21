from flask import Flask
from flask_ask import Ask, statement, question
import datetime
import os

app = Flask(__name__)
ask = Ask(app, '/alexa_endpoint')

@ask.launch
def launch():
    speech_text = '<speak>Welcome to Greetings Skill. Using our skill you can greeting your guests. Whom you want to greet?</speak>'
    reprompt_text = '<speak>You can say for example, say hello to John.</speak>'
    return question(speech_text).reprompt(reprompt_text)


@ask.intent('HelloIntent', mapping={'first_name' : 'FirstName'}, default={'first_name' : 'Unknown'})
def hello(first_name):
    speech_text = 'Hello {0}. '.format(first_name)
    speech_text += get_wish()
    return statement("<speak>{}</speak>".format(speech_text))

@ask.session_ended
def session_ended():
    return "", 200

def get_wish():
    current_time = datetime.datetime.utcnow()
    hours = current_time.hour
    if hours < 12:
        return 'Good morning.'
    elif hours < 18:
        return 'Good afternoon.'
    else:
        return 'Good evening.'


if __name__ == '__main__':
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
    app.run()