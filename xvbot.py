import discord
from discord.ext import commands
import httplib2, psutil, os, sys
from watchdog import observers, events

class ModifiedHandler(events.FileSystemEventHandler):
  def on_modified(self, event):
    if (event.src_path[2:] == __file__):
      reboot_self()

modified_handler = ModifiedHandler()
sObserver = observers.Observer()
sObserver.schedule(modified_handler, './', recursive=False)
sObserver.start()

description = ''' XVBot does things. '''

bot = commands.Bot(command_prefix='xv:', description=description)

gateway = "https://gateway.xvicario.us"

token = open('client.id.cfg', 'r').readline().strip()

@bot.event
async def on_ready():
  print('Logged in as')
  print(bot.user.name)
  print(bot.user.id)
  print('------------')
  await bot.change_presence(game = discord.Game(name="The Game of Life", url="https://reddit.com/r/outside"))

@bot.command()
async def check(service : str):
  code = __get_status_code(gateway, "/" + service)
  if (code == 404):
    await bot.say((service[0].upper() + service[1:]) + " is down.")
    return
  await bot.say((service[0].upper() + service[1:]) + " seems to be fine.")

@bot.command()
async def end():
  await bot.close()

@bot.command()
async def reboot():
  await reboot_self()

@bot.command(pass_context=True)
async def c(ctx):
  print(ctx)

@bot.event
async def on_message(message):
    await bot.say("...")

def reboot_self():
  bot.change_presence(status = discord.Status.offline)
  __soft_close()
  python = sys.executable
  sObserver.stop()
  os.execl(python, python, *sys.argv)

def __get_status_code(host, path="/"):
  try:
    connection = httplib2.Http()
    response, content = connection.request(host + "/" + path, "HEAD")
    return response.status
  except StandardError:
    return None

def __soft_close():
  for extension in tuple(bot.extensions):
    try:
      bot.unload_extension(extension)
    except:
      pass
  for cog in tuple(bot.cogs):
    try:
      bot.remove_cog(cog)
    except:
      pass
  return True

bot.run(token)
