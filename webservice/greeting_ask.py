from flask import Flask
from flask_ask import Ask, statement, question, session
import datetime
import os
import logging
import requests


app = Flask(__name__)
app.config['ASK_APPLICATION_ID'] = 'amzn1.ask.skill.ef12e20b-9428-4d86-9303-87d87e41f348'
ask = Ask(app, '/alexa_endpoint')


if os.environ.get('GREETING_ASK_DEBUG', '').lower() == 'true':
    logging.getLogger('flask_ask').setLevel(logging.DEBUG)

@ask.launch
def launch():
    speech_text = '<speak>Welcome to Greetings Skill. Using our skill you can greeting your guests. Whom you want to greet?</speak>'
    reprompt_text = '<speak>You can say for example, say hello to John.</speak>'
    return question(speech_text).reprompt(reprompt_text)


@ask.intent('HelloIntent', mapping={'first_name' : 'FirstName'}, default={'first_name' : 'Unknown'})
def hello(first_name):
    speech_text = 'Hello {0}. '.format(first_name)
    speech_text += get_wish()
    quote = get_quote()
    speech_text += ' {0}'.format(quote)
    return statement(get_ssml(speech_text))

@ask.intent('QuoteIntent')
def quote_intent():
    speech_text, reprompt_text = get_quote_text()
    session.attributes['quote_intent'] = True
    return question(speech_text).reprompt(reprompt_text)

@ask.intent('NextQuoteIntent')
def next_quote_intent():
    if 'quote_intent' in session.attributes:
        speech_text, reprompt_text = get_quote_text()
        return question(speech_text).reprompt(reprompt_text)
    else:
        speech_text = get_ssml('Wrong invocation of this intent. Please say get me a quote to get quote.')
        return statement(speech_text)

@ask.session_ended
def session_ended():
    return "", 200

@ask.intent('AMAZON.StopIntent')
def stop_intent():
    speech_text = get_ssml('Good Byte.')
    return statement(speech_text)

@ask.intent('AMAZON.CancelIntent')
def stop_intent():
    speech_text = get_ssml('Good Byte.')
    return statement(speech_text)


def get_quote_text():
    speech_text = get_quote()
    speech_text += ' Do you want to listen to one more quote? '
    reprompt_text = ' You can say yes or one more. '
    speech_text = get_ssml(speech_text)
    reprompt_text = get_ssml(reprompt_text)
    return speech_text, reprompt_text

def get_ssml(text):
    return "<speak>{}</speak>".format(text)

def get_quote():
    r = requests.get('http://api.forismatic.com/api/1.0/json?method=getQuote&lang=en&format=json')
    s = r._content.decode('unicode_escape')
    s = s.replace('\\', '')
    r._content = str.encode(s, 'ascii', 'ignore')
    quote = r.json()['quoteText']
    return quote

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
    port = int(os.getenv('PORT', 5000))
    print('Starting app on port ' + str(port))
    app.run(port = port, host = '0.0.0.0') 