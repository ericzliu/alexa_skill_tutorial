import greeting_ask
import unittest
import json
import os


class GreetingTestCase(unittest.TestCase):

    def setUp(self):
        if 'ASK_VERIFY_REQUESTS' in os.environ:
            verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
            if verify == 'false':
                greeting_ask.app.config['ASK_VERIFY_REQUESTS'] = False
        self.app = greeting_ask.app.test_client()

    def tearDown(self):
        pass

    def test_00_hello_intent(self):
        with open('event.json') as data_file:
            jdata = json.load(data_file)

        answer = self.app.post('/alexa_endpoint', data=json.dumps(jdata), content_type='application/json')
        resp = json.loads(answer.data)

        self.assertTrue(resp['response']['shouldEndSession'])
        self.assertRegex(resp['response']['outputSpeech']['ssml'], r'<speak>Hello.*</speak>')

    def test_01_quote_intent(self):
        with open('quote.json') as data_file:
            jdata = json.load(data_file)

        answer = self.app.post('/alexa_endpoint', data=json.dumps(jdata), content_type='application/json')
        resp = json.loads(answer.data)

        self.assertRegex(resp['response']['outputSpeech']['ssml'], r'.*Do you want to listen to one more.*')

    def test_02_next_quote_intent(self):
        with open('next_quote.json') as data_file:
            jdata = json.load(data_file)

        answer = self.app.post('/alexa_endpoint', data=json.dumps(jdata), content_type='application/json')
        resp = json.loads(answer.data)

        self.assertRegex(resp['response']['outputSpeech']['ssml'], r'.*Wrong invocation of this intent. Please say get me a quote to get quote.*')

    def test_03_next_quote_intent(self):
        with open('next_quote_attr.json') as data_file:
            jdata = json.load(data_file)

        answer = self.app.post('/alexa_endpoint', data=json.dumps(jdata), content_type='application/json')
        resp = json.loads(answer.data)

        self.assertRegex(resp['response']['outputSpeech']['ssml'], r'.*Do you want to listen to one more quote.*')

if __name__ == '__main__':
    unittest.main()
