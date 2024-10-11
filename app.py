from webex_bot.commands.echo import EchoCommand
from webex_bot.webex_bot import WebexBot
import os
import pandas as pd
# main ai rag bot functions
from aibot import aibot
# send card command for bot to process sending webex json card
from aisendcard import SendCardCommand
# cryptography library for encryption/decryption
from cryptography.fernet import Fernet


# linux (can also use on local windows if cryptography is installed)
# encrypted webex api token using cryptography library for encryption/decryption 
# increases security by not storing api key on the server in plain text
with open('encryptionkeywebex.key', 'rb') as key_file:
    key2 = key_file.read()
cipher_suite2 = Fernet(key2)
with open('encrypted_webexapikey.txt', 'rb') as encrypted_file:
    encrypted_webex_api_key = encrypted_file.read()
decrypted_webex_api_key = cipher_suite2.decrypt(
    encrypted_webex_api_key).decode()


bot = WebexBot(teams_bot_token=decrypted_webex_api_key,
               # approved_domains=['yourdomain.com']  # optional, add your email domain if you want to restrict the bot to only your domain users
               )
               
bot.commands.clear()

# commands for the bot to listen out for.
bot.add_command(aibot())
bot.add_command(SendCardCommand())

# set new command
bot.help_command = aibot()

bot.run()
