from webex_bot.models.command import Command
from webex_bot.models.response import Response
from webex_bot.formatting import quote_info
from webex_bot.models.response import response_from_adaptive_card
from webexteamssdk.models.cards import Colors, TextBlock, FontWeight, \
    FontSize, Column, AdaptiveCard, \
    ColumnSet, Text, Image, \
    HorizontalAlignment, TextInputStyle
from webexteamssdk.models.cards.actions import Submit, OpenUrl
from webexteamssdk import WebexTeamsAPI
from openai import OpenAI
from google.oauth2 import service_account
from google.cloud import datastore
import re
import pandas as pd
import os
from datetime import datetime, timedelta


# html inputs for the responses
from responsehtmls import promo_demo_html, about_us_html, communities_html, \
    customer_success_html, insights_html, botaiprompt, lca_html, metrics_html, \
    renewals_html

# Custom Webex Adaptive Cards
from responsecards import SimpleCard, MenuCard, summaryCard, \
    contact_update_demo_card, contact_update_demo3_card, reply_options_card, \
    replyabcard, email_demo_card

# actual text inputs into the cards and chatgpt prompts
from responseinputs import promoimageurl, promomainTitle, \
    promotextblock2, promotextblock3, promotextblock4, promotextblock5, \
    promoclickopenurl, promotitle, menuimageurl, menumainTitle, menu1, menu1desc, \
    menu2, menu2desc, menu3, menu3desc, menu4, menu4desc, menu5, menu5desc, \
    menu6, menu6desc, menu7, menu7desc, summaryPrompt, sentPrompt, \
    about1, about1desc, about2, about2desc, about3, about3desc, about4, \
    about4desc, about5, about5desc, about6, about6desc, about7, about7desc, \
    about8, about8desc, about9, about9desc, aboutmainTitle, aboutclickopenurl, \
    abouttitle, insights1, insights1desc, insights2, insights2desc, \
    insightsmainTitle, insightsclickopenurl, insightstitle


CLEANR = re.compile('<.*?>')


def cleanhtml(raw_html):
    cleantext = re.sub(CLEANR, ' ', raw_html)
    return cleantext


def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)


def strfloat_to_num(inputString):
    inputString = float(inputString)
    inputString = int(inputString)
    inputString = str(inputString)
    return inputString


def redact_sensitive_info(text):
    # replace any contract numbers with '00000'
    digit_pattern = r'\d{5,}'
    text = re.sub(digit_pattern, '00000', text)
    # replace any email addresses with 'redacted@email'
    # Regex pattern for detecting an email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    redacted_text = re.sub(email_pattern, 'redacted@email', text)
    return redacted_text


credentials = service_account.Credentials.from_service_account_file(
    'cx-dsxana-prod-iibi-62721217b52b-datastore-key.json')

datastore_client = datastore.Client(credentials=credentials)


# linux (can also use on local windows if cryptography is installed)
# encrypted openai key and webex api token
# from cryptography.fernet import Fernet
# with open('encryptionkeyoai.key', 'rb') as key_file:
#     key1 = key_file.read()
# with open('encryptionkeywebex.key', 'rb') as key_file:
#     key2 = key_file.read()
# cipher_suite1 = Fernet(key1)
# cipher_suite2 = Fernet(key2)
# with open('encrypted_oaiapikey.txt', 'rb') as encrypted_file:
#     encrypted_oai_api_key = encrypted_file.read()
# with open('encrypted_webexapikey.txt', 'rb') as encrypted_file:
#     encrypted_webex_api_key = encrypted_file.read()
# # Decrypt the API keys
# decrypted_oai_api_key = cipher_suite1.decrypt(
#     encrypted_oai_api_key).decode()
# decrypted_webex_api_key = cipher_suite2.decrypt(
#     encrypted_webex_api_key).decode()


# local windows
webexapikey = pd.read_csv('webexTeamsApiKey.csv')
webexapikey = webexapikey['apikey'][0]
webex_teams_api_token = webexapikey
openaiapikey = pd.read_csv('webexTeamsApiKey.csv')
openaiapikey = openaiapikey['apikey'][0]

# if using cryptography for encryption/decryption change to decrypted_webex_api_key
webexapi = WebexTeamsAPI(
    access_token=webex_teams_api_token)

# if using cryptography for encryption/decryption change to decrypted_oai_api_key
client = OpenAI(api_key=openaiapikey)


class aibot(Command):

    def __init__(self):
        super().__init__()

    def pre_execute(self, message, attachment_actions, activity):
        """
            WIP Pre-Response to send to user to indicate bot is working on inquiry or demo
        """
        if str(message).lower().strip() == 'contact update demo' \
                or str(message).lower().strip() == 'demo 1' \
                or str(message).lower().strip() == 'demo 2' \
                or str(message).lower().strip() == 'demo 3' \
                or str(message).lower().strip() == 'email demo' \
                or str(message).lower().strip() == 'help':
            print(activity)
        elif str(message).lower().strip() == 'y' \
                or str(message).lower().strip() == 'n':
            print(activity)
        else:
            text1 = TextBlock("Working on your inquiry...",
                              weight=FontWeight.BOLDER,
                              wrap=True, size=FontSize.DEFAULT,
                              horizontalAlignment=HorizontalAlignment.CENTER,
                              color=Colors.DARK
                              )
            text2 = TextBlock("Please hold tight while I process your request.",
                              wrap=True, color=Colors.DARK
                              )
            card = AdaptiveCard(
                body=[
                    ColumnSet(columns=[Column(items=[text1, text2])]),
                ])
            return response_from_adaptive_card(card)

    def execute(self, message, attachment_actions, activity):
        """
            Actual Response to the user
            Checks for known commands, sends responses from 
            responsecards.py or responsetexts.py
            Otherwise, have A.I./ChatGPT respond to general questions
        """

        """
            Log message, user, email address, timestamp,
            and if command is 360 to DataStore db
        """
        user_email = activity['actor']['emailAddress']
        user_name = activity['actor']['displayName']
        timenow = datetime.now()
        timenow = timenow.strftime('%Y-%m-%d %H:%M')
        data = {}
        data['email'] = user_email
        data['username'] = user_name
        data['message'] = str(message)
        if '360' in str(message).lower()[:3]:
            data['indicator360'] = '1'
        else:
            data['indicator360'] = '0'
        data['datetime'] = timenow
        # no entity_key
        complete_key = datastore_client.key('orgMessages')
        task = datastore.Entity(key=complete_key)
        task.update(data)
        datastore_client.put(task)

        if str(message).lower().strip() == 'start' or \
                str(message).lower().strip() == 'promo demo':
            """
                if user types command 'start' or 'promo demo' to the bot
                then return promoDemoCard from responsecards.py
                using inputs from responseinputs.py
            """
            textblocks = [promotextblock2, promotextblock3,
                          promotextblock4, promotextblock5]
            promoCard = SimpleCard(mainTitle=promomainTitle,
                                   textblocks=textblocks,
                                   imageUrl=promoimageurl
                                   )
            card = promoCard.getcard(clickOpenUrl=promoclickopenurl,
                                     title=promotitle, width=2
                                     )
            return response_from_adaptive_card(card)

        elif str(message).lower().strip() == 'help':
            """
                if user types command 'help' to the bot
                then return menuCard from responsecards.py
                using inputs from responseinputs.py
            """
            # menu items, title, and image from responseinputs.py
            menu_items = {
                menu1: menu1desc,
                menu2: menu2desc,
                menu3: menu3desc,
                menu4: menu4desc,
                menu5: menu5desc,
                menu6: menu6desc,
                menu7: menu7desc
            }
            # MenuCard accepts a dict for menu items and imageUrl is optional
            helpMenuCard = MenuCard(mainTitle=menumainTitle,
                                    menu_items=menu_items,
                                    # imageUrl=menuimageurl
                                    )
            card = helpMenuCard.getcard(width=2)
            return response_from_adaptive_card(card)

        elif str(message).lower().strip() == 'about' or  \
                str(message).lower().strip() == 'about us' or \
                str(message).lower().strip() == 'what is org' or \
                str(message).lower().strip() == 'who is org' or \
                str(message).lower().strip() == 'org':
            """
                if user types command 'about' or 'what is org' to the bot
                then return menuCard from responsecards.py
                using about inputs from responseinputs.py
            """
            # about items, title, aboutclickopenurl from responseinputs.py
            about_items = {
                about1: about1desc,
                about2: about2desc,
                about3: about3desc,
                about4: about4desc,
                about5: about5desc,
                about6: about6desc,
                about7: about7desc,
                about8: about8desc,
                about9: about9desc
            }
            # MenuCard accepts a dict for menu items and imageUrl is optional
            aboutMenuCard = MenuCard(mainTitle=aboutmainTitle,
                                     menu_items=about_items,
                                     )
            card = aboutMenuCard.getcard(width=2,
                                         clickOpenUrl=aboutclickopenurl,
                                         title=abouttitle
                                         )
            return response_from_adaptive_card(card)

        elif str(message).lower().strip() == 'communities':
            response = Response()
            response.html = communities_html
            return response
        elif str(message).lower().strip() == 'customer success':
            response = Response()
            response.html = customer_success_html
            return response
        elif str(message).lower().strip() == 'insights':
            # insights items, title, aboutclickopenurl from responseinputs.py
            insights_items = {
                insights1: insights1desc,
                insights2: insights2desc,
            }
            # MenuCard accepts a dict for menu items and imageUrl is optional
            insightsMenuCard = MenuCard(mainTitle=insightsmainTitle,
                                        menu_items=insights_items,
                                        )
            card = insightsMenuCard.getcard(width=2,
                                            clickOpenUrl=insightsclickopenurl,
                                            title=insightstitle
                                            )
            return response_from_adaptive_card(card)
        elif str(message).lower().strip() == 'lca':
            response = Response()
            response.html = lca_html
            return response
        elif str(message).lower().strip() == 'metrics':
            response = Response()
            response.html = metrics_html
            return response
        elif str(message).lower().strip() == 'renewals':
            response = Response()
            response.html = renewals_html
            return response
        elif str(message).lower().strip() == 'y' or \
                str(message).lower().strip() == 'n':
            if str(message).lower().strip() == 'y':
                todayThread = datetime.now() - timedelta(days=1)
                todayThread = todayThread.strftime('%Y-%m-%d')
                dateFilter = todayThread
                query = datastore_client.query(kind="orgThreads")
                query.add_filter("inquiry_created_date", ">=", dateFilter)
                results = list(query.fetch())
                data_list = []
                for index in range(len(results)):
                    d = dict(results[index])
                    d['keyid'] = results[index].key.id_or_name
                    data_list.append(d)
                data_list = sorted(
                    data_list, key=lambda x: x['inquiry_created_date'], reverse=True)
                df = pd.DataFrame(data_list)
                df = df[df['inquiry_request_type'] == 'Contact Update']
                df = df[df['purpose'] == 'Inquiry Automatic Reply Request']
                df = df[df['agent_approved'] == 'pending']
                roomId = activity['target']['globalId']
                df = df[df['roomId'] == roomId]
                if len(df) >= 1:
                    print('found thread to update')
                    keyid = df['keyid'].values[0]
                    keyid = int(keyid)
                    key = datastore_client.key('orgThreads', keyid)
                    task = datastore_client.get(key)
                    task['agent_approved'] = 'approved'
                    datastore_client.put(task)

                    text1 = TextBlock("Thank you, the automatic action has been triggered. Please allow 24-48 hours for it to complete.",
                                      weight=FontWeight.BOLDER, wrap=True,
                                      color=Colors.DARK
                                      )
                    card = AdaptiveCard(
                        body=[
                            ColumnSet(
                                columns=[Column(items=[text1])]),
                        ]
                    )
                    return response_from_adaptive_card(card)
                else:
                    print(
                        'no thread indicating a bot message to agent requesting approval...')
                    print(
                        'thus, the user sent a direct message to bot with the letter y for no reason')
                    print('no response will be given by bot for this message')
            else:
                todayThread = datetime.now()
                todayThread = todayThread.strftime('%Y-%m-%d')
                dateFilter = todayThread
                query = datastore_client.query(kind="orgThreads")
                query.add_filter("inquiry_created_date", ">=", dateFilter)
                results = list(query.fetch())
                data_list = []
                for index in range(len(results)):
                    d = dict(results[index])
                    d['keyid'] = results[index].key.id_or_name
                    data_list.append(d)
                data_list = sorted(
                    data_list, key=lambda x: x['inquiry_created_date'], reverse=True)
                df = pd.DataFrame(data_list)
                df = df[df['inquiry_request_type'] == 'Contact Update']
                df = df[df['purpose'] == 'Inquiry Automatic Reply Request']
                df = df[df['agent_approved'] == 'pending']
                roomId = activity['target']['globalId']
                df = df[df['roomId'] == roomId]
                if len(df) >= 1:
                    print(
                        'found thread, but no action will be taken. Rejected will be updated in agent_approved field.')
                    keyid = df['keyid'].values[0]
                    keyid = int(keyid)
                    key = datastore_client.key('orgThreads', keyid)
                    task = datastore_client.get(key)
                    task['agent_approved'] = 'rejected'
                    datastore_client.put(task)
                    text1 = TextBlock("Thank you, no action will be taken.",
                                      weight=FontWeight.BOLDER, wrap=True,
                                      color=Colors.DARK
                                      )
                    card = AdaptiveCard(
                        body=[
                            ColumnSet(
                                columns=[Column(items=[text1])]),
                        ]
                    )
                    return response_from_adaptive_card(card)
                else:
                    print(
                        'no thread indicating a bot message to agent requesting approval...')
                    print(
                        'thus, the user sent a direct message to bot with the letter n for no reason')
                    print('no response will be given by bot for this message')

        elif '360' in str(message).lower()[:3]:
            if str(message).lower()[3] == ' ':
                custName = str(message).lower()[4:]
                custName = custName.strip()
            elif str(message).lower()[3] == ':':
                custName = str(message).lower()[4:]
                custName = custName.strip()
            else:
                custName = str(message).lower()[3:]
                custName = custName.strip()
            if '@' not in custName:
                # custName = custName.title()
                text1 = TextBlock(str(custName) + " is not a valid email \
                                    address.  Please type a valid \
                                    email address after '360'.",
                                  weight=FontWeight.BOLDER, wrap=True,
                                  color=Colors.DARK
                                  )
                card = AdaptiveCard(
                    body=[
                        ColumnSet(
                            columns=[Column(items=[text1])]),
                    ]
                )
                return response_from_adaptive_card(card)
            print('this is activity: ', activity)
            userEmailwebex = activity["actor"]['emailAddress']
            query = datastore_client.query(kind="orgUSERS")
            results = list(query.fetch())
            orgusers_list = []
            for index in range(len(results)):
                d = dict(results[index])
                orgusers_list.append(d)
            dfusers = pd.DataFrame(orgusers_list)
            dfuserslist = dfusers['email'].to_list()
            if userEmailwebex not in dfuserslist:
                text1 = TextBlock("Only authorized users can use the 360 \
                                    command due to returning results \
                                    containing confidential information. \
                                    If you should be an authorized user, \
                                    please reach out to the admin.",
                                  weight=FontWeight.BOLDER, wrap=True,
                                  color=Colors.DARK
                                  )
                card = AdaptiveCard(
                    body=[
                        ColumnSet(
                            columns=[Column(items=[text1])]),
                    ]
                )
                return response_from_adaptive_card(card)
            query = datastore_client.query(kind="orgContacts")
            first_key = datastore_client.key("orgContacts", custName)
            query.key_filter(first_key, "=")
            results = list(query.fetch())
            if not results:
                # start of CDDATA Query for when user was not found in Contact Hub db
                email = custName
                query = datastore_client.query(kind="orgCDDATA")
                query.add_filter("CONTACT_EMAIL", "=", email)
                results = list(query.fetch())
                if len(results) == 0:
                    text1 = TextBlock("Sorry, " + str(custName) +
                                      " was not found in my records. \
                                        Currently, we are still in the process \
                                        of importing all Contact Hub \
                                        and CDDATA Data. Please try again later.",
                                      weight=FontWeight.BOLDER, wrap=True,
                                      color=Colors.DARK
                                      )
                    card = AdaptiveCard(
                        body=[
                            ColumnSet(
                                columns=[Column(items=[text1])]),
                        ]
                    )
                    return response_from_adaptive_card(card)
                else:
                    data_list = []
                    CDDATAContainer = []
                    for index in range(len(results)):
                        d = dict(results[index])
                        data_list.append(d)
                    data_list = sorted(
                        data_list, key=lambda x: x['BLAST_DATE'], reverse=True)
                    dfCDDATA = pd.DataFrame(data_list)
                    cxcustbuid = ''
                    crpartyid = dfCDDATA['PARTY_ID'][0]
                    crpartyname = ''
                    firstName = dfCDDATA['FIRST_NAME'][0]
                    lastName = dfCDDATA['LAST_NAME'][0]
                    jobTitle = dfCDDATA['JOB_TITLE'][0]
                    slLevel2 = ''
                    slLevel6 = dfCDDATA['SALES_LEVEL_6'][0]
                    country = ''
                    contactStatus = ''
                    isValidated = ''
                    unsubscribe = ''
                    archList = ''
                    custSumTitle = "360 Summary: " + str(custName)
                    csvfilename = 'CDDATA_' + email.replace('@', '_') + '.csv'
                    dfCDDATA.to_csv('./' + str(csvfilename))
                    csv_file_path = './' + str(csvfilename)
                    room_id = activity['target']['globalId']
                    originalMessageId = activity['id']
                    message = 'Here is the CDDATA csv file attached for: ' + \
                        str(email) + '.'
                    webexapi.messages.create(
                        roomId=room_id, parentId=originalMessageId,
                        text=message, files=[csv_file_path]
                    )
                    os.remove('./'+str(csvfilename))
                    allCDDATAMessage = "CDDATA Data File is attached above (earlier reply)."
                    # start of Data Query and saving to df
                    # and sending as attachment in webex bot
                    query = datastore_client.query(kind="orgRandDATA")
                    query.add_filter("CR_PARTY_ID", "=", crpartyid)
                    results = list(query.fetch())
                    if len(results) == 0:
                        allRandDATAMessage = "N/A: No records in RandDATA found."
                    else:
                        data_list = []
                        for index in range(len(results)):
                            d = dict(results[index])
                            data_list.append(d)
                        data_list = sorted(
                            data_list, key=lambda x: x['END_DATE'], reverse=True)
                        dfRandDATA = pd.DataFrame(data_list)
                        dfRandDATA = dfRandDATA[['END_QUARTER', 'FORMATTED_END_QUARTER',
                                         'FORMATTED_END_WEEK', 'END_DATE',
                                         'REGION', 'SALES_LEVEL_2',
                                         'SALES_LEVEL_6', 'COUNTRY', 'SUB_SEGMENT',
                                         'OFFER', 'CX_PRODUCT_CATEGORY',
                                         'BUSINESS_ENTITY',
                                         'BUSINESS_SUB_ENTITY', 'CR_PARTY_ID',
                                         'CR_PARTY_NAME', 'BE_GEO_ID',
                                         'BE_GEO_NAME', 'LCA_PARTNER',
                                         'CONTRACT_NUMBER',
                                         'CAMPAIGN_EXCLUSION_SUB_CATEGORY',
                                         'CX_BUSINESS_UNIT_ID',
                                         'CX_BUSINESS_UNIT_NAME',
                                         'DISTRIBUTOR_ID', 'DISTRIBUTOR_NAME',
                                         'ATR', 'BOOKINGS'
                                         ]]
                        crpartyname = dfRandDATA['CR_PARTY_NAME'][0]
                        cxcustbuid = dfRandDATA['CX_BUSINESS_UNIT_ID'][0]
                        country = dfRandDATA['COUNTRY'][0]
                        if cxcustbuid == 'nan' or cxcustbuid == 'None' \
                                or cxcustbuid == '' or cxcustbuid == None:
                            cxcustbuid = ''
                        csvfilename = 'RandDATA_' + \
                            email.replace('@', '_') + '.csv'
                        dfRandDATA.to_csv('./' + str(csvfilename))
                        csv_file_path = './' + str(csvfilename)
                        room_id = activity['target']['globalId']
                        originalMessageId = activity['id']
                        message = 'Here is the data csv file \
                            attached for: ' + str(
                            email) + '.'
                        webexapi.messages.create(
                            roomId=room_id, parentId=originalMessageId,
                            text=message, files=[csv_file_path]
                        )
                        os.remove('./'+str(csvfilename))
                        allRandDATAMessage = "Data File is \
                            attached above (earlier reply)."
                    # start of inbound lead cases history query
                    query = datastore_client.query(kind="agentgloballeads")
                    query.add_filter("EMAIL", "=", email)
                    results = list(query.fetch())
                    if len(results) == 0:
                        emailInteractionSummary = "N/A: No prior inbound cases found."
                        sentimentSummary = "N/A"
                    else:
                        data_list = []
                        inbContainer = []
                        msgOnlyContainer = []
                        for index in range(len(results)):
                            d = dict(results[index])
                            data_list.append(d)
                        for inbound in data_list:
                            inbMsg = str(inbound['DESCRIPTION'])
                            inbMsg = cleanhtml(inbMsg)
                            # remove any sensitive information from historical cases
                            inbMsg = redact_sensitive_info(inbMsg)
                            inbAdditionalInfo = str(
                                inbound['ADDITIONAL_INFORMATION'])
                            inbAdditionalInfo = cleanhtml(inbAdditionalInfo)
                            inbAdditionalInfo = redact_sensitive_info(
                                inbAdditionalInfo)
                            inbData = "Created Date: "+str(inbound['CREATED_DATE']) +\
                                ", Method Received: " +\
                                inbound['METHOD_RECEIVED'] +\
                                ", Request Type: " +\
                                inbound['REQUEST_TYPE'] +\
                                ", Offer: "+inbound['OFFER_NAME'] +\
                                ", Steps taken: " +\
                                inbound['AGENT_STEPS_TAKEN'] + \
                                ", Outcome: "+inbound['OUTCOME'] +\
                                ", Sub Outcome: "+inbound['SUB_OUTCOME'] +\
                                ", Lead Status: " + \
                                inbound['LEAD_STATUS']+", Message: "+inbMsg + \
                                ", Additional Message: " + inbAdditionalInfo
                            inbContainer.append(inbData)
                            msgOnlyContainer.append(inbMsg)
                        allInbounds = " ".join(inbContainer)
                        allMessagesOnly = " ".join(msgOnlyContainer)
                        promptInbounds = summaryPrompt + allInbounds
                        summaryMessages = []
                        try:
                            summaryMessages.append({
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": promptInbounds
                                    }
                                ]
                            })
                            completion = client.chat.completions.create(
                                model="gpt-4o",
                                messages=summaryMessages
                            )
                            gpt_response = completion.choices[0].message.content
                            emailInteractionSummary = gpt_response
                            promptInbounds = sentPrompt + allMessagesOnly
                            sentimentMessages = []
                            sentimentMessages.append({
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": promptInbounds
                                    }
                                ]
                            })
                            completion = client.chat.completions.create(
                                model="gpt-4o",
                                messages=sentimentMessages
                            )
                            gpt_response = completion.choices[0].message.content
                            sentimentSummary = gpt_response
                        except:
                            emailInteractionSummary = 'N/A: Sorry, busy processing \
                                                        too many requests.'
                            sentimentSummary = 'N/A'
                    card = summaryCard(custSumTitle, firstName, lastName, crpartyid,
                                       crpartyname, cxcustbuid, slLevel2, slLevel6,
                                       country, allCDDATAMessage, allRandDATAMessage,
                                       emailInteractionSummary, sentimentSummary
                                       )
                    return response_from_adaptive_card(card)

            else:
                data_list = []
                for index in range(len(results)):
                    d = dict(results[index])
                    data_list.append(d)
                dsData = data_list[0]
                cxcustbuid = dsData['CX_CUSTOMER_BU_ID']
                crpartyid = dsData['PARTY_ID']
                try:
                    crpartyname = dsData['SITE_PARTY_NAME']
                except:
                    crpartyname = ''
                firstName = dsData['FIRST_NAME']
                lastName = dsData['LAST_NAME']
                jobTitle = dsData['JOB_TITLE']
                slLevel2 = dsData['SALES_LEVEL_2']
                slLevel6 = ''
                country = dsData['SITE_ISO_COUNTRY_NAME']
                contactStatus = dsData['CONTACT_STATUS']
                isValidated = dsData['ISVALIDATED']
                unsubscribe = dsData['UNSUBSCRIBE']
                archList = dsData['ARCHITECTURE_LST']
                custSumTitle = "360 Summary: " + str(custName)
                email = custName
                # start of CDDATA Query
                query = datastore_client.query(kind="orgCDDATA")
                query.add_filter("CONTACT_EMAIL", "=", email)
                results = list(query.fetch())
                if len(results) == 0:
                    allCDDATAMessage = "N/A: No records in CDDATA found."
                else:
                    data_list = []
                    for index in range(len(results)):
                        d = dict(results[index])
                        data_list.append(d)
                    data_list = sorted(
                        data_list, key=lambda x: x['BLAST_DATE'], reverse=True)
                    dfCDDATA = pd.DataFrame(data_list)
                    slLevel6 = dfCDDATA['SALES_LEVEL_6'][0]
                    csvfilename = 'CDDATA_' + email.replace('@', '_') + '.csv'
                    dfCDDATA.to_csv('./' + str(csvfilename))
                    csv_file_path = './' + str(csvfilename)
                    room_id = activity['target']['globalId']
                    originalMessageId = activity['id']
                    message = 'Here is the CDDATA csv file attached for: ' + \
                        str(email) + '.'
                    webexapi.messages.create(
                        roomId=room_id, parentId=originalMessageId,
                        text=message, files=[csv_file_path]
                    )
                    os.remove('./'+str(csvfilename))
                    allCDDATAMessage = "CDDATA Data File is attached above (earlier reply)."

                # start of Data Query and saving to df and
                # sending as attachment in webex bot
                query = datastore_client.query(kind="orgRandDATA")
                query.add_filter("CR_PARTY_ID", "=", crpartyid)
                results = list(query.fetch())
                if len(results) == 0:
                    allRandDATAMessage = "N/A: No records in RandDATA found."
                else:
                    data_list = []
                    for index in range(len(results)):
                        d = dict(results[index])
                        data_list.append(d)
                    data_list = sorted(
                        data_list, key=lambda x: x['END_DATE'], reverse=True)
                    dfRandDATA = pd.DataFrame(data_list)
                    dfRandDATA = dfRandDATA[['END_QUARTER', 'FORMATTED_END_QUARTER',
                                     'FORMATTED_END_WEEK', 'END_DATE', 'REGION',
                                     'SALES_LEVEL_2', 'SALES_LEVEL_6', 'COUNTRY',
                                     'SUB_SEGMENT', 'OFFER', 'CX_PRODUCT_CATEGORY',
                                     'BUSINESS_ENTITY', 'BUSINESS_SUB_ENTITY',
                                     'CR_PARTY_ID', 'CR_PARTY_NAME', 'BE_GEO_ID',
                                     'BE_GEO_NAME', 'LCA_PARTNER', 'CONTRACT_NUMBER',
                                     'CAMPAIGN_EXCLUSION_SUB_CATEGORY',
                                     'CX_BUSINESS_UNIT_ID', 'CX_BUSINESS_UNIT_NAME',
                                     'DISTRIBUTOR_ID', 'DISTRIBUTOR_NAME', 'ATR',
                                     'BOOKINGS'
                                     ]]
                    crpartyname = dfRandDATA['CR_PARTY_NAME'][0]
                    if cxcustbuid == 'nan' or cxcustbuid == 'None':
                        cxcustbuid = dfRandDATA['CX_BUSINESS_UNIT_ID'][0]
                    csvfilename = 'RandDATA_' + \
                        email.replace('@', '_') + '.csv'
                    dfRandDATA.to_csv('./' + str(csvfilename))
                    csv_file_path = './' + str(csvfilename)
                    room_id = activity['target']['globalId']
                    originalMessageId = activity['id']
                    message = 'Here is the data csv file \
                        attached for: ' + str(email) + '.'
                    webexapi.messages.create(
                        roomId=room_id, parentId=originalMessageId,
                        text=message, files=[csv_file_path]
                    )
                    os.remove('./'+str(csvfilename))
                    allRandDATAMessage = "Data File is \
                        attached above (earlier reply)."
                # start of inbound lead cases history query
                query = datastore_client.query(kind="agentgloballeads")
                query.add_filter("EMAIL", "=", email)
                results = list(query.fetch())
                if len(results) == 0:
                    emailInteractionSummary = "N/A: No prior inbound cases found."
                    sentimentSummary = "N/A"
                else:
                    data_list = []
                    inbContainer = []
                    msgOnlyContainer = []
                    for index in range(len(results)):
                        d = dict(results[index])
                        data_list.append(d)
                    for inbound in data_list:
                        inbMsg = str(inbound['DESCRIPTION'])
                        inbMsg = cleanhtml(inbMsg)
                        # remove any sensitive information from historical cases
                        inbMsg = redact_sensitive_info(inbMsg)
                        inbAdditionalInfo = str(
                            inbound['ADDITIONAL_INFORMATION'])
                        inbAdditionalInfo = cleanhtml(inbAdditionalInfo)
                        inbAdditionalInfo = redact_sensitive_info(
                            inbAdditionalInfo)
                        inbData = "Created Date: " +\
                            str(inbound['CREATED_DATE']) +\
                            ", Method Received: " +\
                            inbound['METHOD_RECEIVED'] +\
                            ", Request Type: " +\
                            inbound['REQUEST_TYPE'] +\
                            ", Offer: "+inbound['OFFER_NAME'] +\
                            ", Steps taken: " +\
                            inbound['AGENT_STEPS_TAKEN'] + \
                            ", Outcome: "+inbound['OUTCOME']+", Sub Outcome: " +\
                            inbound['SUB_OUTCOME']+", Lead Status: " + \
                            inbound['LEAD_STATUS']+", Message: "+inbMsg + \
                            ", Additional Message: " + inbAdditionalInfo
                        inbContainer.append(inbData)
                        msgOnlyContainer.append(inbMsg)
                    allInbounds = " ".join(inbContainer)
                    allMessagesOnly = " ".join(msgOnlyContainer)
                    promptInbounds = summaryPrompt + allInbounds
                    summaryMessages = []
                    try:
                        summaryMessages.append({
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": promptInbounds
                                }
                            ]
                        })
                        completion = client.chat.completions.create(
                            model="gpt-4o",
                            messages=summaryMessages
                        )
                        gpt_response = completion.choices[0].message.content
                        emailInteractionSummary = gpt_response
                        promptInbounds = sentPrompt + allMessagesOnly
                        sentimentMessages = []
                        sentimentMessages.append({
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": promptInbounds
                                }
                            ]
                        })
                        completion = client.chat.completions.create(
                            model="gpt-4o",
                            messages=sentimentMessages
                        )
                        gpt_response = completion.choices[0].message.content
                        sentimentSummary = gpt_response
                    except:
                        emailInteractionSummary = 'N/A: Sorry, busy processing \
                                                    too many requests.'
                        sentimentSummary = 'N/A'
                card = summaryCard(custSumTitle, firstName, lastName, crpartyid,
                                   crpartyname, cxcustbuid, slLevel2, slLevel6,
                                   country, allCDDATAMessage, allRandDATAMessage,
                                   emailInteractionSummary, sentimentSummary
                                   )
                return response_from_adaptive_card(card)
        else:
            assistantId = 'asst_7sOPzzsiVCgAWf5iPT9vWpf9'
            emailAddress = activity['actor']['emailAddress']
            room_id = activity['target']['globalId']
            originalMessageId = activity['id']
            # remove any sensitive information user might accidentally provide
            message = redact_sensitive_info(message)
            query = datastore_client.query(kind="orgThreads")
            query.add_filter("purpose", "=", "RAG Answer")
            query.add_filter("sent_to", "=", emailAddress)
            results = list(query.fetch())
            if len(results) == 0:
                print('no oai threads found for user, creating a new thread..')
                # create a new thread since it's the first time the user is asking a general question
                thread = client.beta.threads.create(
                    messages=[
                        {
                            "role": "user",
                            "content": message,
                        }
                    ]
                )
                thread_id = thread.id
                run = client.beta.threads.runs.create_and_poll(
                    thread_id=thread_id,  # thread.id,
                    assistant_id=assistantId  # assistant.id
                )
                messages = list(client.beta.threads.messages.list(
                    thread_id=thread_id,  # thread.id,
                    run_id=run.id))
                message_content = messages[0].content[0].text
                annotations = message_content.annotations
                citations = []
                for index, annotation in enumerate(annotations):
                    message_content.value = message_content.value.replace(
                        annotation.text, '')  # f"[{index}]"
                    if file_citation := getattr(annotation, "file_citation", None):
                        cited_file = client.files.retrieve(
                            file_citation.file_id)
                        citations.append(f"[{index}] {cited_file.filename}")
                gpt_response = message_content.value
                data = {}
                data['oai_thread_id'] = thread_id
                data['id'] = originalMessageId
                data['roomId'] = room_id
                data['direction'] = 'Bot to Human'
                data['type'] = 'Webex Teams Message'
                data['purpose'] = 'RAG Answer'
                data['sent_to'] = emailAddress
                data['sent_from'] = 'AskorgBot'
                timenow = datetime.now()
                timenow = timenow.strftime('%Y-%m-%d %H:%M')
                data['datetime'] = timenow
                data['reply_email_sent'] = 'no'
                data['agent_approved'] = 'not applicable'
                data['inquiry_request_type'] = 'not applicable'
                data['inquiry_sender_email'] = activity['actor']['emailAddress']
                data['inquiry_recent_inquiry'] = message
                createdDate = datetime.now()
                createdDate = createdDate.strftime('%Y-%m-%d')
                data['inquiry_created_date'] = createdDate
                data['inquiry_suggested_response'] = 'not applicable'
                data['actual_response'] = gpt_response
                data['citations'] = citations
                # no entity_key
                complete_key = datastore_client.key('orgThreads')
                task = datastore.Entity(key=complete_key,
                                        exclude_from_indexes=[
                                            "actual_response", "citations"]
                                        )
                task.update(data)
                datastore_client.put(task)

                print('ai rag response: ', gpt_response)
                return (gpt_response)
            else:
                print('oai threads found for user, adding to existing thread..')
                data_list = []
                for index in range(len(results)):
                    d = dict(results[index])
                    data_list.append(d)
                data_list = sorted(
                    data_list, key=lambda x: x['datetime'], reverse=True)
                df = pd.DataFrame(data_list)
                thread_id = df['oai_thread_id'][0]
                # Create a new message in the existing thread
                client.beta.threads.messages.create(
                    thread_id=thread_id,
                    role="user",
                    content=message
                )
                run = client.beta.threads.runs.create_and_poll(
                    thread_id=thread_id,  # thread.id,
                    assistant_id=assistantId  # assistant.id
                )
                messages = list(client.beta.threads.messages.list(
                    thread_id=thread_id,  # thread.id,
                    run_id=run.id))
                message_content = messages[0].content[0].text
                annotations = message_content.annotations
                citations = []
                for index, annotation in enumerate(annotations):
                    message_content.value = message_content.value.replace(
                        annotation.text, '')  # f"[{index}]"
                    if file_citation := getattr(annotation, "file_citation", None):
                        cited_file = client.files.retrieve(
                            file_citation.file_id)
                        citations.append(f"[{index}] {cited_file.filename}")
                gpt_response = message_content.value
                data = {}
                data['oai_thread_id'] = thread_id
                data['id'] = originalMessageId
                data['roomId'] = room_id
                data['direction'] = 'Bot to Human'
                data['type'] = 'Webex Teams Message'
                data['purpose'] = 'RAG Answer'
                data['sent_to'] = emailAddress
                data['sent_from'] = 'AskorgBot'
                timenow = datetime.now()
                timenow = timenow.strftime('%Y-%m-%d %H:%M')
                data['datetime'] = timenow
                data['reply_email_sent'] = 'no'
                data['agent_approved'] = 'not applicable'
                data['inquiry_request_type'] = 'not applicable'
                data['inquiry_sender_email'] = activity['actor']['emailAddress']
                data['inquiry_recent_inquiry'] = message
                createdDate = datetime.now()
                createdDate = createdDate.strftime('%Y-%m-%d')
                data['inquiry_created_date'] = createdDate
                data['inquiry_suggested_response'] = 'not applicable'
                data['actual_response'] = gpt_response
                data['citations'] = citations
                # no entity_key
                complete_key = datastore_client.key('orgThreads')
                task = datastore.Entity(key=complete_key,
                                        exclude_from_indexes=[
                                            "actual_response", "citations"]
                                        )
                task.update(data)
                datastore_client.put(task)
                print('ai rag response: ', gpt_response)
                return (gpt_response)
