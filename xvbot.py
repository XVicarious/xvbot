import discord
import asyncio
import re
import json
from pathlib import Path

client = discord.Client()

TOKEN = ""

def openMemes(filePath):
    if not filePath.exists():
        f = open(filePath, 'w+')
        f.write("{}")
        f.close()
    return json.load(open(filePath))

LANGUAGE = "en_US"
STRINGS = openMemes(Path("./lang.json"))

NEW_MEME_COMMAND = "CHECK OUT THIS FRESH MEME CALLED "
LIST_MEMES_COMMAND = "WHAT ARE THE MEMES?"
HELP_COMMAND = "HOW DO I USE THIS FUCKING BOT!?"

CALL_MEME_REGEX = re.compile("(?<=\;)(.*?)(?=\;)")
VALID_MEME_REGEX = re.compile(".*[.\\\\/:*?\"<>|].*")

MEMES_FILE = Path("./memes.json")
MEMES_LIST = openMemes(MEMES_FILE)

TRIAL_ONGOING = False
TRIAL_FOR_MEME = {
    "meme": "",
    "date": 0
}

@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------------")

@client.event
async def on_message(message):
    message_sender = "<@" + message.author.id + ">"
    if message.content.startswith(NEW_MEME_COMMAND):
        if len(message.attachments) < 1:
            await client.send_message(message.channel, STRINGS['no_meme'] % message_sender)
        elif len(message.attachments) > 1:
            await client.send_message(message.channel, STRINGS['too_many_meme'] % message_sender)
        else:
            meme_name = message.content[len(NEW_MEME_COMMAND):].lower()
            if meme_name in MEMES_LIST.keys():
                await client.send_message(message.channel, STRINGS['meme_exists'] % message_sender)
                return
            if not VALID_MEME_REGEX.search(message.content) == None:
                await client.send_message(message.channel, STRINGS['invalid_meme'] % message_sender)
                return
            MEMES_LIST[meme_name] = message.attachments[0]['url']
            with open(MEMES_FILE, 'w') as f:
                json.dump(MEMES_LIST, f)
            f.close()
            await client.send_message(message.channel, STRINGS['meme_submitted'] % message_sender)
    elif CALL_MEME_REGEX.search(message.content):
        requested_meme = CALL_MEME_REGEX.search(message.content).group(0)
        try:
            embeded = discord.Embed()
            embeded.set_image(url = MEMES_LIST[requested_meme])
            await client.send_message(message.channel, embed=embeded)
            return
        except:
            print("no meme named " + requested_meme)
            await client.send_message(message.channel, STRINGS['unknown_meme'] % message_sender)
    elif message.content.startswith(LIST_MEMES_COMMAND):
        the_memes = ""
        for meme in MEMES_LIST.keys():
            the_memes += meme + '\n'
        await client.send_message(message.channel, (STRINGS['list_memes'] + the_memes) % message_sender)
    elif message.content == HELP_COMMAND:
        await client.send_message(message.channel, "%s you may use me any way you like" % message_sender)

client.run(TOKEN)
