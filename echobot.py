#Adopted with modifications from https://courses.ryerson.ca/d2l/le/content/173555/viewContent/1850399/View
#Distributed under MIT license

#CPS847 Group 19
#echobot v1.0
#Members:
#   Jay Patel
#   Neelkanth Patel
#   Julian Sengboupha
#   Tommmy Tran
#   Kelvin Liu
#   Nikola Stevanovic
#   Yahye Mohamud

import os
import time
import re
from slackclient import SlackClient

import json #used for debug printing
import requests

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "?"
MENTION_REGEX = "^<@(|[WU].+)>(.*)"
WEATHER = "!"
API_KEY = '66ee6b4784750a5094708018e3dbc75b'

def weather_search(city_name):
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&APPID={}&units=metric'.format(city_name,API_KEY)
    json_data = requests.get(url).json()
    if json_data['cod'] == '404':
        return "Error 404: City name not found"
    elif json_data['cod'] == '401':
        return "Error 401: Invalid APIID. Contact Admin for support."
    elif json_data['cod'] == '503':
        return "Error 503: Server Error. Please try again later."
    else:
        temp = float(json_data['main']['temp'])
        description = json_data['weather'][0]['description']
        response = 'The weather in {} is described as {} with a temperature {} degrees Celcius'.format(city_name.capitalize(),description,int(round(temp)))
        return response

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
    	#uncomment line below to debug print
    	#print json.dumps(event, indent = 2, sort_keys = True)

        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            #uncomment line below to debug print
            #print user_id, " : ", message
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    #default_response = "Sorry. That didn't work. Try adding *{}* to then end".format(EXAMPLE_COMMAND)
    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.endswith(EXAMPLE_COMMAND):
        response = "*{}*".format(command)
    if command.startswith(WEATHER):
        response = weather_search(command[1:])
    else:
        default_response = "Sorry. That didn't work. Try adding *{}* to then end for echo or *{}* to the beginning for weather".format(EXAMPLE_COMMAND, WEATHER)

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

if __name__ == "__main__":
	# avm: connect is designed for larger teams,
	# see https://slackapi.github.io/python-slackclient/real_time_messaging.html
	# for details
    if slack_client.rtm_connect(with_team_state=False):
        print("Echo Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
