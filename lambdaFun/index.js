'use strict';

var http = require('http');

exports.handler = function(event, context, callback) {
  try {
    log(JSON.stringify(event, null, 2));
    let request = event.request;
    let session = event.session;

    if (!event.session.attributes) {
      event.session.attributes = {};
    }

    if (request.type === 'LaunchRequest') {
      handleLaunchRequest(event, context, callback);
    }
    else if (request.type === 'IntentRequest') {
      if (request.intent.name === 'HelloIntent') {
        handleHelloIntent(event, context, callback);
      }
      else if (request.intent.name === 'QuoteIntent') {
        handleQuoteIntent(event, context, callback);
      }
      else if (request.intent.name === 'NextQuoteIntent') {
        handleNextQuoteIntent(event, context, callback);
      }
      else if (request.intent.name === 'AMAZON.CancelIntent' || request.intent.name === 'AMAZON.StopIntent') {
        callback(null, buildResponse({
          speechText: 'Goodbye',
          endSession: true
        }));
      }
      else {
        throw new Error('Unknown intent');
      }
    }
    else if (request.type === 'SessionEndedRequest') {
    }
    else {
      const error = new Error('Unknown intent type');
      throw error;
    }
  } catch (e) {
    callback(e, null);
  }
};

function getWish() {
  let mDate = new Date();
  let mHour = mDate.getUTCHours();
  if (mHour < 12) {
    return 'Good morning.';
  }
  else if (mHour < 18) {
    return 'Good afternoon.';
  }
  else {
    return 'Good evening.';
  }
}

function buildResponse(options) {
  log(JSON.stringify(options, null, 2));
  let response = {
    version: '1.0',
    response: {
      outputSpeech: {
        type: 'SSML',
        ssml: '<speak>' + options.speechText + '</speak>'
      },
      shouldEndSession: options.endSession
    }
  };
  if (options.repromptText) {
    response.response.reprompt = {
      outputSpeech: {
        type: 'SSML',
        ssml: '<speak>' + options.repromptText + '</speak>'
      }
    };
  }
  if (options.cardTitle) {
    response.response.card = {
      type: 'Simple',
      title: options.cardTitle
    };

    if (options.imageUrl) {
      response.response.card.type = 'Standard';
      response.response.card.content = options.cardContent;
      response.response.card.image = {
        smallImageUrl: options.imageUrl,
        largeImageUrl: options.imageUrl
      };
    }
    else {
      response.response.card.content = options.cardContent;
    }
  }
  if (options.session && options.session.attributes) {
    response.sessionAttributes = options.session.attributes;
  }
  log(JSON.stringify(response, null, 2));
  return response;
}

function getQuote(callback) {
  let url = 'http://api.forismatic.com/api/1.0/json?method=getQuote&lang=en&format=json';
  let req = http.get(url, function(res) {
    var body = '';
    res.on('data', function(chunk) {
      body += chunk;
    });
    res.on('end', function() {
      body = body.replace(/\\/g, '');
      let quote = JSON.parse(body);
      callback(null, quote.quoteText);
    });
  });
  req.on('error', function(err) {
    callback(err, null);
  });
}

function handleLaunchRequest(event, context, callback) {
  const resp = buildResponse({
    speechText: 'Welcome to Greetings Skill. Using our skill you can greeting your guests. Whom you want to greet?',
    repromptText: 'You can say for example, say hello to John.',
    endSession: false
  });
  callback(null, resp);
}

function handleHelloIntent(event, context, callback) {
  let request = event.request;
  let name = request.intent.slots.FirstName.value;
  let options = {};
  options.speechText = `Hello <say-as interpret-as="spell-out">${name}</say-as> ${name}. `;
  options.speechText += getWish();
  options.cardTitle = `Hello ${name}`;

  getQuote(function(err, quote) {
    if (quote) {
      options.speechText += ' ';
      options.speechText += quote;
      options.cardContent = quote;
      options.imageUrl = 'https://upload.wikimedia.org/wikipedia/commons/5/5b/Hello_smile.png';
    }
    options.endSession = true;
    callback(null, buildResponse(options));
  });  
}

function handleQuoteIntent(event, context, callback) {
  let request = event.request;
  let session = event.session;
  let options = {};
  options.session = session;
  getQuote(function(err, quote) {
    if (quote) {
      options.speechText = quote;
      options.speechText += ' Do you want to listen to one more quote?';
      options.repromptText = 'You can say yes or one more.';
      options.endSession = false;
      options.session.attributes.quoteIntent = true;
      callback(null, buildResponse(options));
    } else {
      callback(err);
    }
  });  
}

function handleNextQuoteIntent(event, context, callback) {
  let request = event.request;
  let session = event.session;
  let options = {};
  options.session = session;
  if (session.attributes.quoteIntent) {
    getQuote(function(err, quote) {
      if (quote) {
        options.speechText = quote;
        options.speechText += ' Do you want to listen to one more quote?';
        options.repromptText = 'You can say yes or one more.';
        options.endSession = false;
        callback(null, buildResponse(options));
      } else {
        callback(err);
      }
    });
  }
  else {
    options.speechText = 'Wrong invocation of this intent.';
    options.endSession = true;
    callback(null, buildResponse(options));
  }

}

function log(message) {
  if (process.env.NODE_DEBUG_ON) {
    console.log(message);
  }
}
