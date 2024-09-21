from webex_bot.models.command import Command
from webexteamssdk import WebexTeamsAPI
import json
import re
import pandas as pd
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


class SendCardCommand(Command):
    def __init__(self):
        super().__init__(
            command_keyword="sendcard",
            help_message="Send a card to specified recipients.\nUsage: /sendcard recipient1@example.com,recipient2@example.com {json}",
            card=None,
        )
        self.webexapi = WebexTeamsAPI(access_token=webex_teams_api_token)

    def execute(self, message, attachment_actions, activity):
        # get the roomId
        roomId = activity['target']['globalId']
        # Remove the command keyword
        content = message.replace('/sendcard', '', 1).strip()
        # Parse content to get recipient_emails and json
        match = re.match(r'([^\s]+)\s+(.*)', content)
        if not match:
            # Send an error message
            self.webexapi.messages.create(
                roomId=roomId,
                markdown="**Error:** Invalid format.\nUsage: `/sendcard recipient1@example.com,recipient2@example.com {json}`"
            )
            return

        recipients = match.group(1)
        print('this is recipients:', recipients)
        json_payload = match.group(2)
        print('this is json_payload:', json_payload)

        recipient_emails = recipients.split(',')

        # Parse the JSON payload
        try:
            card_content = json.loads(json_payload)
        except json.JSONDecodeError:
            self.webexapi.messages.create(
                roomId=roomId,
                markdown="**Error:** Invalid JSON payload."
            )
            return

        # Send the message to each recipient
        for email in recipient_emails:
            try:
                self.webexapi.messages.create(
                    toPersonEmail=email.strip(),
                    text='',
                    attachments=[card_content]
                )
            except Exception as e:
                self.webexapi.messages.create(
                    roomId=roomId,
                    markdown=f"**Error:** Could not send message to {email.strip()}. {str(e)}"
                )
