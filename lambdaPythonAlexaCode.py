"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG

** Change this to now be a very basic shell that just replies with a random Poz fact that 
is first built into an array. Setup a script that can publish the new code into lambda automatically 
as a zip file. Use this then to create a new Poz skill and build upon that using boto3 to interact with 
other AWS services.

"""
from __future__ import print_function
import boto3
from boto3.dynamodb.conditions import Key, Attr
import random


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Alexa Poz Python Framework Skills sample. "
                
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Hello Dumbo."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Poz Python Framework Skills sample. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))



#
# This function will get all of the family facts that exist in the database, and then randomly select
# one for Alexa to say.
#
def get_family_fact(intent, session):

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False   
    # Let's get a family fact from our dynamodb PozFamilyFact table.
    #
    # Get the service resource.
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('PozFamilyFacts')
    #
    # Let's use a scan and get all of the family facts that exist.
    #
    response = table.scan()
    items = response['Items'] 
    # Select a random integer between 0 and the length of items
    #
    random_integer = random.randint(0, (len(items)-1))       
    # Now use the random number generated to get a family fact out of the list of entries
    #
    speech_output = items[random_integer]['fact']
    reprompt_text = ""
                    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

#
# This function will state a fact about an individual listed in the Poz Family Facts database.
#
def get_individual_fact(intent, session):

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False 
    # Let's get a family fact from our dynamodb PozFamilyFact table.
    #
    # Get the service resource.
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('PozFamilyFacts')    
    # 
    # Who do we want a fact about?
    #
    family_member = intent['slots']['family_member']['value']
    #
    # Let's get all of the facts about Tyler.
    #
    response = table.scan(
        FilterExpression=Attr('family_member').eq(family_member)
    )
    items = response['Items']
    print(items)  
    # Select a random integer between 0 and the length of items
    #
    random_integer = random.randint(0, (len(items)-1))    
    # Now use the random number generated to get an individual fact out of the list of entries
    #
    speech_output = items[random_integer]['fact']
    reprompt_text = ""
                    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
    
    
#
# This function will allow us to add a fact to the poz family facts database
#
def update_fact_database(intent, session):

    card_title = intent['name']
    should_end_session = False 
    session_attributes = {}
    #
    # There are different utterances that will get us into this intent. In order to update the database
    # with a fact, we will need to collect who the fact will be about, as well as the fact itself. To understand 
    # where we are in this process, let's check if any slot information was carried along with the request.
    #
    if (intent['slots']['family_member'].get('value')):
        #
        # family_member was populated, so let's get its value and put it in the session.
        #
        family_member = intent['slots']['family_member']['value']
        session_attributes.update({'family_member' : family_member})
        speech_output = "What is the fact that you would like to add about" + family_member
        reprompt_text = ""
    else :
        #
        # We need to get the family member for the fact.
        #
        speech_output = "Who would you like the fact to be about?"
        reprompt_text = ""
        
                 
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "PozFactIntent":
        return get_family_fact(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "PozIndividualFact":
        return get_individual_fact(intent, session)
    elif intent_name == "PutIntent":
        return update_fact_database(intent, session)
    elif intent_name == "Goodbye":
        return handle_session_end_request()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
 

{
  "session": {
    "sessionId": "SessionId.21dffc00-602b-4a3c-91b5-f29a3d6fadf8",
    "application": {
      "applicationId": "amzn1.ask.skill.f95d6302-e53d-4e98-8f84-3c206701ef29"
    },
    "attributes": {},
    "user": {
      "userId": "amzn1.ask.account.AHDOPLZ6O5SVQ52SJ2NFNN75TIJGOEEQ4LPSOCDVIMK2BIEM7SG3RET32WV2OB5E7CGOR6BY2PE6T6N7I4AESFGLBLKAK5RT3GF42ND7F22RPIFBJF7JKODCCMIJDVT4HJU6XW4PJCYURPPIWLFMUR4LJJ6IUNDV3SUKX55EKNAT5AQQVJIBVTJYBPOPP4EQCZKYOC765MQOM2Y"
    },
    "new": true
  },
  "request": {
    "type": "IntentRequest",
    "requestId": "EdwRequestId.81a005dd-1d61-48c3-95fa-dd141accb2cf",
    "locale": "en-US",
    "timestamp": "2017-05-29T21:41:30Z",
    "intent": {
      "name": "PozFactIntent",
      "slots": {
        "family_member": {
          "name": "family_member",
          "value": "Tyler"
        }
      }
    }
  },
  "version": "1.0"
}  
    
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function. POZ test...again...
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
