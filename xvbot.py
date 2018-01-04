import discord
import asyncio
import re
import json
from pathlib import Path
import gettext

# todo: i18n support for this terrible bot
es = gettext.translation('xvbot', localedir = 'locale', languages = ['es'])

_ = lambda s: s

def openMemes(filePath):
    if not filePath.exists():
        f = open(filePath, 'w+')
        f.write("{}")
        f.close()
    return json.load(open(filePath))

client = discord.Client()

TOKEN = open('client.id.cfg', 'r').readline().strip()

NEW_MEME_COMMAND = "CHECK OUT THIS FRESH MEME CALLED "
LIST_MEMES_COMMAND = "WHAT ARE THE MEMES?"
HELP_COMMAND = "HOW DO I USE THIS FUCKING BOT!?"

CALL_MEME_REGEX = re.compile("(?<=\;)(.*?)(?=\;)")
VALID_MEME_REGEX = re.compile(".*[.\\\\/:*?\"<>|].*")

MEMES_FILE = Path("./memes.json")
MEMES_LIST = openMemes(MEMES_FILE)

TRIAL_FILE = Path("./trial.json")
TRIAL_ONGOING = False
TRIAL_FOR_MEME = openMemes(TRIAL_FILE)

async def list_memes(message, message_sender):
    the_memes = ""
    for meme in MEMES_LIST.keys():
        the_memes += meme + '\n'
    await client.send_message(message.channel, (_("%s, the memes are: \n") + the_memes) % message_sender)

def dump_memes():
    with open(MEMES_FILE, 'w') as f:
        json.dump(MEMES_LIST, f)
    f.close()

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
            await client.send_message(message.channel, _("%s , you forgot to add the meme!") % message_sender)
        elif len(message.attachments) > 1:
            await client.send_message(message.channel, _("%s, meme overload! Please only submit one meme at a time!!!1") % message_sender)
        else:
            meme_name = message.content[len(NEW_MEME_COMMAND):].lower()
            if meme_name in MEMES_LIST.keys():
                await client.send_message(message.channel, _("%s, that meme already exists. Try again.") % message_sender)
                return
            if not VALID_MEME_REGEX.search(message.content) == None:
                await client.send_message(message.channel, _("%s, that isn't a valid name for a meme...") % message_sender)
                return
            MEMES_LIST[meme_name] = {}
            MEMES_LIST[meme_name]['url'] = message.attachments[0]['url']
            dump_memes()
            await client.send_message(message.channel, _("%s, thank you for that tasty meme :3") % message_sender)
    elif CALL_MEME_REGEX.search(message.content):
        requested_meme = CALL_MEME_REGEX.search(message.content).group(0)
        try:
            embeded = discord.Embed()
            embeded.set_image(url = MEMES_LIST[requested_meme]['url'])
            MEMES_LIST[requested_meme]["refs"] += 1
            embeded.description = (_("This meme has been referenced %s times") % MEMES_LIST[requested_meme]["refs"])
            await client.send_message(message.channel, embed=embeded)
            dump_memes()
            return
        except:
            print("no meme named " + requested_meme)
            await client.send_message(message.channel, _("%s, what?") % message_sender)
    elif message.content.startswith(LIST_MEMES_COMMAND):
        await list_memes(message, message_sender)
    elif message.content == HELP_COMMAND:
        await client.send_message(message.channel, "%s you may use me any way you like" % message_sender)

client.run(TOKEN)
