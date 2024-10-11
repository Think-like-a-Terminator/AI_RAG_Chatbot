from webexteamssdk.models.cards.actions import Submit, OpenUrl
from webexteamssdk.models.cards import Image, Colors, TextBlock, FontWeight, \
    FontSize, Column, AdaptiveCard, \
    ColumnSet, Text, \
    HorizontalAlignment, TextInputStyle


def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)


def strfloat_to_num(inputString):
    inputString = float(inputString)
    inputString = int(inputString)
    inputString = str(inputString)
    return inputString


class SimpleCard:
    """
    Returns a simple Adaptive Card with title, multiple text blocks, and
    an image if provided

    Required params:
        mainTitle: str = Title of card (required)
        textblocks: list = List of text descriptions or text inside the card

    Optional params:
        imageUrl: str = URL LINK to Image (optional)
        additional_textblocks: list = Additional text blocks (optional)
    """

    def __init__(self, mainTitle: str, textblocks: list, imageUrl=None,
                 additional_textblocks=None):
        self.imageUrl = imageUrl
        if imageUrl:
            self.webexImage = Image(url=imageUrl)
        else:
            self.webexImage = None

        self.text1 = TextBlock(mainTitle,
                               weight=FontWeight.BOLDER, wrap=True,
                               size=FontSize.DEFAULT,
                               horizontalAlignment=HorizontalAlignment.CENTER,
                               color=Colors.DARK
                               )
        self.textblocks = [
            TextBlock(text, wrap=True, color=Colors.DARK) for text in textblocks]
        self.additional_textblocks = [TextBlock(text, wrap=True, color=Colors.DARK)
                                      for text in additional_textblocks] if additional_textblocks else []

    def getcard(self, clickOpenUrl, title, width):
        # Create the body of the card with the main title and initial textblocks
        card_body = [self.text1] + self.textblocks + self.additional_textblocks

        # Add image if provided
        if self.webexImage:
            card_body.insert(0, self.webexImage)

        return AdaptiveCard(
            body=[ColumnSet(columns=[Column(items=card_body, width=width)])],
            actions=[OpenUrl(url=clickOpenUrl, title=title)]
        )


class MenuCard:

    """
    Returns an Adaptive Card with image, title, and Menu items with descriptions

    Required params:
        mainTitle: str = Title of card (required)
        menu_items: dict = Dictionary of menu items with their descriptions

    Optional params:
        imageUrl: str = URL LINK to Image (optional, gets displayed at top of card)
    """

    def __init__(self, mainTitle: str, menu_items: dict, imageUrl=None):
        # required
        self.mainTitle = TextBlock(mainTitle,
                                   weight=FontWeight.BOLDER, wrap=True,
                                   size=FontSize.DEFAULT,
                                   horizontalAlignment=HorizontalAlignment.LEFT,
                                   color=Colors.DARK)
        self.menu_items = menu_items
        # optional
        self.imageUrl = imageUrl

    def getcard(self, width, clickOpenUrl=None, title=None):
        """
        Returns Adaptive Card with Menu Items and image at top if available
        """

        # Create the body of the card with the main title
        card_body = [self.mainTitle]

        # Add the menu items dynamically
        for item, desc in self.menu_items.items():
            card_body.append(TextBlock(item,
                                       weight=FontWeight.BOLDER, wrap=True,
                                       size=FontSize.DEFAULT,
                                       horizontalAlignment=HorizontalAlignment.LEFT,
                                       color=Colors.DARK))
            card_body.append(TextBlock(desc, wrap=True, color=Colors.DARK))

        # Add image if provided
        if self.imageUrl:
            card_body.insert(0, ColumnSet(
                columns=[Column(items=[Image(url=self.imageUrl)], width=width)]))

        if clickOpenUrl and title:
            return AdaptiveCard(
                body=[
                    ColumnSet(columns=[Column(items=card_body, width=width)])],
                actions=[OpenUrl(url=clickOpenUrl, title=title)]
            )
        else:
            return AdaptiveCard(
                body=[ColumnSet(columns=[Column(items=card_body)])]
            )



def summaryCard(custSumTitle, firstName, lastName, crpartyid, crpartyname,
                cxcustbuid, slLevel2, slLevel6, country, allCDOMessage,
                allCRBOMessage, emailInteractionSummary, sentimentSummary):
    text1 = TextBlock(custSumTitle,
                      weight=FontWeight.BOLDER, wrap=True, size=FontSize.DEFAULT,
                      horizontalAlignment=HorizontalAlignment.CENTER,
                      color=Colors.DARK)
    text2 = TextBlock("FULL NAME:",
                      weight=FontWeight.BOLDER, wrap=True, color=Colors.DARK)
    text3 = TextBlock(str(firstName) + ' ' + str(lastName),
                      wrap=True, color=Colors.DARK)
    text4 = TextBlock("PERSON ID:",
                      weight=FontWeight.BOLDER, wrap=True, color=Colors.DARK)
    text5 = TextBlock(crpartyid,
                      wrap=True, color=Colors.DARK)
    text6 = TextBlock("CR PARTY NAME:",
                      weight=FontWeight.BOLDER, wrap=True, color=Colors.DARK)
    text7 = TextBlock(crpartyname,
                      wrap=True, color=Colors.DARK)
    text8 = TextBlock("CUSTOMERID:",
                      weight=FontWeight.BOLDER, wrap=True, color=Colors.DARK)
    if has_numbers(cxcustbuid):
        cxcustbuid = strfloat_to_num(cxcustbuid)
    text9 = TextBlock(cxcustbuid,
                      wrap=True, color=Colors.DARK)
    text10 = TextBlock("Sales Level 2 & 6:",
                       weight=FontWeight.BOLDER, wrap=True, color=Colors.DARK)
    text11 = TextBlock(str(slLevel2) + ', ' + str(slLevel6),
                       wrap=True, color=Colors.DARK)
    text12 = TextBlock("Country:",
                       weight=FontWeight.BOLDER, wrap=True, color=Colors.DARK)
    text13 = TextBlock(str(country),
                       wrap=True, color=Colors.DARK)
    text18 = TextBlock("CDO Data:",
                       weight=FontWeight.BOLDER, wrap=True, color=Colors.DARK)
    text19 = TextBlock(str(allCDOMessage),
                       wrap=True, color=Colors.DARK)
    text20 = TextBlock("Company Ready Data:",
                       weight=FontWeight.BOLDER, wrap=True, color=Colors.DARK)
    text21 = TextBlock(str(allCRBOMessage),
                       wrap=True, color=Colors.DARK)
    text22 = TextBlock("Prior Inbound Cases Summary:",
                       weight=FontWeight.BOLDER, wrap=True, color=Colors.DARK)
    text23 = TextBlock(emailInteractionSummary,
                       wrap=True, color=Colors.DARK)
    text24 = TextBlock("Overall Sentiment:",
                       weight=FontWeight.BOLDER, wrap=True, color=Colors.DARK)
    text25 = TextBlock(sentimentSummary,
                       wrap=True, color=Colors.DARK)
    card = AdaptiveCard(
        body=[
            ColumnSet(columns=[Column(items=[text1, text2, text3,
                                             text4, text5, text6,
                                             text7, text8, text9,
                                             text10, text11, text12,
                                             text13,
                                             text18, text19, text20,
                                             text21, text22, text23,
                                             text24, text25
                                             ])]),
        ])
    return card
