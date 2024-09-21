from webex_bot.commands.echo import EchoCommand
from webex_bot.webex_bot import WebexBot
import os
import pandas as pd
# main ai rag bot functions
from aibot import aibot
# send card command for bot to process sending webex json card
from aisendcard import SendCardCommand


# linux
# encrypted webex api token
# from cryptography.fernet import Fernet
# with open('encryptionkeywebex.key', 'rb') as key_file:
#     key2 = key_file.read()
# cipher_suite2 = Fernet(key2)
# with open('encrypted_webexapikey.txt', 'rb') as encrypted_file:
#     encrypted_webex_api_key = encrypted_file.read()
# decrypted_webex_api_key = cipher_suite2.decrypt(
#     encrypted_webex_api_key).decode()


# local windows
webexapikey = pd.read_csv('webexTeamsApiKey.csv')
webexapikey = webexapikey['apikey'][0]
webex_teams_api_token = webexapikey


bot = WebexBot(teams_bot_token=webex_teams_api_token,
               # approved_domains=['yourdomain.com']  # optional, add your email domain if you want to restrict the bot to only your domain users
               )
               
bot.commands.clear()

# commands for the bot to listen out for.
bot.add_command(aibot())
bot.add_command(SendCardCommand())

# set new command
bot.help_command = aibot()

bot.run()
