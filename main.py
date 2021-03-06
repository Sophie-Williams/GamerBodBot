import discord
import os
import requests
from random import randint
import json

class ApiError(Exception):
    pass

# Class to handle commands
class CommandHandle:

    def __init__(self, client):
        self.client = client
        self.commands = []

    # Function to add a command to the commands list
    #
    # @Param command        The command to add to the list
    def add_command(self, command):
        self.commands.append(command)

    # Funciton to handle messages to check if they are commands
    #
    # @Param message        The message to handle
    #
    def handle_command(self, message):
        for command in self.commands:
            if message.content.startswith(command['trigger']):
                args = message.content.split(' ')
                
                # If the message starts with a trigger
                if args[0] == command['trigger']:
                    args.pop(0)

                    # If there are no arguments in the selected command, return the response
                    if command['number_args'] == 0:
                        return self.client.send_message(message.channel, str(command['function'](self, message, self.client, args)))
                    else:
                        # If there are a correct number of arguments, return a response. Else return an error message
                        if len(args) >= command['number_args']:
                            return self.client.send_message(message.channel, str(command['function'](self, message, self.client, args)))
                        else:
                            return self.client.send_message(message.channel, 'command "{}" requires {} argument(s): "{}"'.format(command['trigger'], command['number_args'], ', '.join(command['args_val'])))
                else:
                    break




# Create instance of the discord client
client = discord.Client()

# Create the CommandHandle object passing in the client
handler = CommandHandle(client)

def refresh_token():
    resp = requests.get("https://gamerbodbot-api.herokuapp.com/refresh", headers={"Authorization": "Bearer " + os.environ.get('JWT_TOKEN')})

## ALL FUNCTIONS FOR COMMANDS GO HERE WITH HANDLER BELOW RESPECTIVE FUNCTION

# Simple function for hello command
def function_greetings(self, message, client, args):
    try:
        return "Hello {}".format(message.author.mention)
    except Exception as e:
        return e
    
handler.add_command({
    'trigger': '!hello',
    'function': function_greetings,
    'number_args': 0,
    'args_val': [],
    'desc': 'Sends greetings to the user'
})

# Function to handle the commands command
#
# Returns a list of the commands
def function_commands(self, message, client, args):
    try:
        response = "Commands:\n```"
        
        for command in self.commands:
            response += command['trigger']

            # Add the args (if any) to the response
            if command['trigger'] == "!backlog":
                response += " {} <{}>".format(command['args_val'][0], command['args_val'][1])
            else:
                for arg in command['args_val']:
                    response += " <{}>".format(arg)
            

            response += ": {}\n\n".format(command['desc'])

        response+= "```"

        return response
    except Exception as e:
        return e
    
handler.add_command({
    'trigger': '!commands',
    'function': function_commands,
    'number_args': 0,
    'args_val': [],
    'desc': 'Lists commands'
})

# Function to handle the help command
def function_help(self, message, client, args):
    try:
        return "Type in command as ```!<command>``` or type in ```!commands``` for list of commands"
    except  Exception as e:
        return e

handler.add_command({
    'trigger': '!help',
    'function': function_help,
    'number_args': 0,
    'args_val': [],
    'desc': 'Helps user'
})

# Function to handle the meme command
#
# References the google custom search api and a created custom google search to search multiple sites for a meme. Returns a random image.
#
def function_meme(self, message, client, args):
    try:
        # Make request for the meme
        resp = requests.get("https://gamerbodbot-api.herokuapp.com/meme", headers={"Authorization": "Bearer " + os.environ.get('JWT_TOKEN')})

        if resp.status_code != 200:
            if resp.status_code == 401:
                raise ApiError('Get error {}, unauthorized. Message contents: ```javascript\n{}\n```'.format(resp.status_code, resp.json()))
            else:
                raise ApiError('Get error {}. Message contents: ```javascript\n{}\n```'.format(resp.status_code, resp.json()))
            
        meme = resp.json()["Meme"]
        return meme

    except ApiError as a:
        return a
    except Exception as e:
        return e

handler.add_command({
    'trigger': '!meme',
    'function': function_meme,
    'number_args': 0,
    'args_val': [],
    'desc': 'Sends a meme to user'
})

def function_backlog(self, message, client, args):
    try:
        # If game has multiple work titles, join the multiple words from args list
        game = ' '.join(args[1:])

        if args[0] == "add":
            resp = requests.post("https://gamerbodbot-api.herokuapp.com/backlog/{}".format(message.author.display_name), data={"game": "{}".format(game), "status": "unplayed"}, headers={"Authorization": "Bearer " + os.environ.get('JWT_TOKEN')})
        elif args[0] == "finished":
            resp = requests.put("https://gamerbodbot-api.herokuapp.com/backlog/{}".format(message.author.display_name), data={"game": "{}".format(game), "status": "finished"}, headers={"Authorization": "Bearer " + os.environ.get('JWT_TOKEN')})
        elif args[0] == "playing":
            resp = requests.put("https://gamerbodbot-api.herokuapp.com/backlog/{}".format(message.author.display_name), data={"game": "{}".format(game), "status": "playing"}, headers={"Authorization": "Bearer " + os.environ.get('JWT_TOKEN')})
        elif args[0] == "all":
            pass
        elif args[0] == "view":
            resp = requests.get("https://gamerbodbot-api.herokuapp.com/backlog/{}".format(message.author.display_name), data={"game": "{}".format(game)}, headers={"Authorization": "Bearer " + os.environ.get('JWT_TOKEN')})

        if resp.status_code != 200:
            if resp.status_code == 401:
                raise ApiError('Get error {}, unauthorized. Message contents: ```javascript\n{}\n```'.format(resp.status_code, resp.json()))
            else:
                raise ApiError('Get error {}. Message contents: ```javascript\n{}\n```'.format(resp.status_code, resp.json()))
        
        return resp.json()['message']
    except ApiError as a:
        return a
    except Exception as e:
        return e


handler.add_command({
    'trigger': '!backlog',
    'function': function_backlog,
    'number_args': 1,
    'args_val': ['add/finished/playing/view', 'game'],
    'desc': 'Command to interact (add, finish, update, get) backlog items'
})

@client.event  # event decorator/wrapper (anytime some event is going to occur)
async def on_ready():
    try:
        print(f"We have logged in as {client.user}")
    except Exception as e:
        print(e)

@client.event
async def on_message(message):
    # For messages from itself
    if message.author == client.user:
        pass
    else:
        try:
            await handler.handle_command(message)

        # Message does not have a command, just pass
        except TypeError as t:
            pass

        except Exception as e:
            print(e)


client.run(os.environ.get('TOKEN'))
