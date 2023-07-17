import discord
from discord import app_commands
from discord.utils import get
from discord.ext.commands import has_permissions, MissingPermissions
from discord.ext import commands
import datetime
import time
import requests 
import pprint
import random
import pickle
import google.generativeai as palm
from serpapi import GoogleSearch
import math
f = open("keys.txt", "r")
data = f.readlines()
if "None" in data[0]:
    given_token = input("Enter your Discord bot token: ")
    if given_token == "":
      given_token = "None"
else:
    given_token = data[0][15:]
    given_token = given_token.replace("\n", "")
if "None" in data[1]:
    given_palm_key = input("(Optional) Enter your Palm API key: ")
    if given_palm_key == "":
      given_palm_key = "None"
else:
    given_palm_key = data[1][10:]
    given_palm_key = given_palm_key.replace("\n", "")
if "None" in data[2]:
    serp_api_key = input("(Optional) Enter your SerpAPI key: ")
    if serp_api_key == "":
      serp_api_key = "None"
else:
    serp_api_key = data[2][10:]
    serp_api_key = serp_api_key.replace("\n", "")
verify = input("Are you sure that your inputted keys are correct? (y/n) ")
sync = input("Do you want to sync commands? Must be done at least once. (y/n) ")
if verify == "n":
  given_token = input("Enter your Discord bot token: ")
  if given_token == "":
    given_token = "None"
  given_palm_key = input("(Optional) Enter your Palm API key: ")
  if given_palm_key == "":
    given_palm_key = "None"
  serp_api_key = input("(Optional) Enter your SerpAPI key: ")
  if serp_api_key == "":
    serp_api_key = "None"
file_write = "discord_token: " + given_token + "\n" + "palm_API: " + given_palm_key + "\n" + "serp_api: " + serp_api_key + "\n"

f = open("keys.txt", "w")
f.write(file_write)
f.close()
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
palm.configure(api_key=given_palm_key)
BASE = "https://discord.com/api/v9/"
TOKEN = given_token
def timeout_user(*, user_id: int, guild_id: int, until: int):
    endpoint = f'guilds/{guild_id}/members/{user_id}'
    headers = {"Authorization": f"Bot {TOKEN}"}
    url = BASE + endpoint
    timeout = (datetime.datetime.utcnow() + datetime.timedelta(minutes=until)).isoformat()
    json = {'communication_disabled_until': timeout}
    session = requests.patch(url, json=json, headers=headers)
    if session.status_code in range(200, 299):
        return session.json()
    else: 
        return print("Did not find any\n", session.status_code)

def add_strings(nested_list, string1, string2):
  new_nested_list = nested_list
  new_nested_list.append([string1, string2])
  return new_nested_list
if sync == "y":
  @client.event
  async def on_ready():
    await tree.sync()
    print("Synced")
@client.event
async def on_message(message):
  global destroy_queue
  if message.author == client.user:
    return
  print(message.author.display_name + ":" + message.content)
@tree.command(name='server-sync', description='Sync custom Magnum Opus Commands')
@has_permissions(administrator=True)
async def sync(interaction: discord.Interaction):
  try:
    await tree.sync(guild=discord.Object(id=interaction.guild.id))
    print('Command tree synced.')
    await interaction.response.send_message('Command tree synced.')
  except:
        await interaction.response.send_message('Issue Encountered. Check Console if owner.')
@tree.command(name='register-mute-id', description='Register a mute role')
@has_permissions(manage_roles=True)
async def registermute(interaction: discord.Interaction, role: discord.Role):
  id = role.id
  server_id = interaction.guild.id
  if 0 == 1:
    embed=discord.Embed(title="No Auth", description="You need to have the right perms in order to register the mute role.", color=0xFFFF00)
    await interaction.response.send_message(embed=embed)
    return
  try:
    id = int(id)
    try:
      with open("mute_id_list.pkl", "rb") as f:
        mute_id_list = pickle.load(f)
    except:
      mute_id_list = []
    mute_id_list = add_strings(mute_id_list, str(server_id), str(id))
    print(mute_id_list)
    with open("mute_id_list.pkl", "wb") as f:
      pickle.dump(mute_id_list, f)
    embed=discord.Embed(title="Mute ID Registered", description="Success: " + str(id), color=0xFFFF00)
    await interaction.response.send_message(embed=embed)
  except:
    embed=discord.Embed(title="Int Error", description="You need to provide a proper ID", color=0xFFFF00)
    await interaction.response.send_message(embed=embed)
    
@tree.command(name='mute-user', description='Mute/Unmute a User (Global, use this)')
@has_permissions(manage_roles=True)
async def mute_change(interaction: discord.Interaction ,member:discord.Member,mute: bool):
  server_id = interaction.guild.id
  if 0 == 1:
    embed=discord.Embed(title="No Auth", description="You need to be Admin in order to mute/unmute a user", color=0xFFFF00)
    await interaction.response.send_message(embed=embed)
    return
  with open("mute_id_list.pkl", "rb") as f:
    mute_id_list = pickle.load(f)
  mute_role = ""
  for i in range(len(mute_id_list)):
    if mute_id_list[i][0] == str(server_id):
      mute_role = mute_id_list[i][1]
      break
  current_registers = ""
  for i in range(len(mute_id_list)):
    current_registers = current_registers + "\n" + mute_id_list[i][0] + ":" + mute_id_list[i][1]
  if mute_role == "":
    embed=discord.Embed(title="No Mute ID Registered for this Server", description="Please use /register-mute-id and provide a Role ID.\nCurrent List:\n" + current_registers, color=0xFFFF00)
    await interaction.response.send_message(embed=embed)
  role = interaction.guild.get_role(int(mute_role))
  if mute == True:
    await member.add_roles(role)
    embed=discord.Embed(title="Mute Successful", description=member.name + " has been muted.", color=0xFFFF00)
  else:
    await member.remove_roles(role)
    embed=discord.Embed(title="Unmute Successful", description=member.name + " has been unmuted.", color=0xFFFF00)
  await interaction.response.send_message(embed=embed)

@tree.command(name = "global-warn", description = "Warn someone")
@has_permissions(manage_messages=True)
async def global_warn(interaction: discord.Interaction, member:discord.Member, reason: str):
  user = interaction.user
  if True:
    print("warn auth successful")
  else:
    await interaction.response.send_message("You need the right perms to warn someone.")
    return
  mod = str(interaction.user.name)
  try:
    if True == True:
      user = member
      try:
        embed=discord.Embed(title="Super DM Warning!", description=user.name +" **You have been warned.** Reason: " + reason + " Mod: " + mod, color=0xFF0000)
        await user.send(embed=embed)
      except:
        embed=discord.Embed(title="Super DM Warning!", description=user.name + " **You have been warned.** " + "Mod: " + mod, color=0xFF0000)
        await user.send(embed=embed)
      try:
        embed=discord.Embed(title="Warning: ", description=str(user.name) + " has been warned! Reason: " + reason + " Mod: " + mod, color=0xFF0000)
        await interaction.response.send_message(embed=embed)
      except:
        embed=discord.Embed(title="Warning without Reason: ", description=str(user.name) + " has been warned! Mod: " + mod, color=0xFF0000)
        await interaction.response.send_message(embed=embed)
    else:
      embed=discord.Embed(title="Wrong Password:", description="You need the right password to authenticate this warning. Mod: " + mod, color=0xFF0000)
      await interaction.response.send_message(embed=embed)
  except Exception as e:
    print(e)

@tree.command(name = "add", description = "Add two numbers")
async def add(interaction: discord.Interaction, num1: str, num2: str):
  try:
    num1 = float(num1)
    num2 = float(num2)
    sum = num1 + num2
    embed=discord.Embed(title="Sum Result", description="The sum of " + str(num1) + " and " + str(num2) + " is " + str(sum) + ".", color=0x0000FF)
    await interaction.response.send_message(embed=embed)
  except:
    embed=discord.Embed(title="Sum Result", description="Check your inputs and try again.", color=0x0000FF)
    await interaction.response.send_message(embed=embed)

@tree.command(name = "multiply", description = "Multiply two numbers")
async def mult(interaction: discord.Interaction, num1: str, num2: str):
  try:
    num1 = float(num1)
    num2 = float(num2)
    sum = num1 * num2
    embed=discord.Embed(title="Multiply Result", description="The product of " + str(num1) + " and " + str(num2) + " is " + str(sum) + ".", color=0x0000FF)
    await interaction.response.send_message(embed=embed)
  except:
    embed=discord.Embed(title="Multiply Result", description="Check your inputs and try again.", color=0x0000FF)
    await interaction.response.send_message(embed=embed)
@tree.command(name = "divide", description = "Multiply two numbers")
async def divide(interaction: discord.Interaction, dividend: str, divisor: str):
  try:
    dividend = float(dividend)
    divisor = float(divisor)
    sum = dividend / divisor
    embed=discord.Embed(title="Quotient Result", description="The quotient of " + str(dividend) + " and " + str(divisor) + " is " + str(sum) + ".", color=0x0000FF)
    await interaction.response.send_message(embed=embed)
  except:
    embed=discord.Embed(title="Quotient Result", description="Check your inputs and try again.", color=0x0000FF)
    await interaction.response.send_message(embed=embed)
@tree.command(name = "subtract", description = "Subtract two numbers (num1-num2)")
async def sub(interaction: discord.Interaction, num1: str, num2: str):
  try:
    num1 = float(num1)
    num2 = float(num2)
    sum = num1 - num2
    embed=discord.Embed(title="Difference Result", description="The difference of " + str(num1) + " and " + str(num2) + " is " + str(sum) + ".", color=0x0000FF)
    await interaction.response.send_message(embed=embed)
  except:
    embed=discord.Embed(title="Difference Result", description="Check your inputs and try again.", color=0x0000FF)
    await interaction.response.send_message(embed=embed)
@tree.command(name = "exponent", description = "Base to the power of exponent")
async def exponent(interaction: discord.Interaction, base: str, exponent: str):
  try:
    base = float(base)
    exponent = float(exponent)
    sum = base ** exponent
    embed=discord.Embed(title="Power Result", description=str(base) + " to the power of " + str(exponent) + " is " + str(sum) + ".", color=0x0000FF)
    await interaction.response.send_message(embed=embed)
  except:
    embed=discord.Embed(title="Power Result", description="Check your inputs and try again.", color=0x0000FF)
    await interaction.response.send_message(embed=embed)
@tree.command(name = "guess-age", description = "Predicts the age of a user.")
async def guess_age(interaction: discord.Interaction, user: discord.Member):
  try:
    messages_str = ""
    async for text in interaction.channel.history(limit=200):
      if text.author == user:
        messages_str = messages_str + text.content + "\n"
    create_time = user.created_at
    await interaction.response.defer()
    response = palm.chat(messages=["SYSTEM_COMMAND # Answer quickly: Guess the age of a discord user who joined at " + str(create_time) + ", has a username of " + str(user.name) + " and these are his/her latest messages " + 
messages_str  + " Use indicators in their name, join date, and especially messages. Just provide a number, it does not have to be robust."])
    embed=discord.Embed(title="Age Prediction for " + str(user.name), description=response.last, color=0xFF00FF)
    await interaction.followup.send(embed=embed)
  except Exception as e:
    embed=discord.Embed(title="Error in Response", description="Check your inputs and try again." + " Error: " + e, color=0xFF00FF)
    await interaction.response.send_message(embed=embed)
    await interaction.followup.send("This command may not be available due to a lack of a key.")
@tree.command(name = "palm-chat", description = "Interact with the Palm API")
async def palm_chat(interaction: discord.Interaction, message: str):
  try:
    await interaction.response.defer()
    response = palm.chat(messages=[message])
    print(response.last)
    if len(response.last) > 2000:
      response.last = response.last[0:1999]
    await interaction.followup.send(response.last)
  except Exception as e:
    try:
      print(response.last)
    except:
      print("No response.")
    await interaction.response.send_message("Error: " + e)
    await interaction.followup.send("This command may not be available due to a lack of a key.")
@tree.command(name = "palm-respond", description = "Ask the Palm API to respond to the chat.")
async def palm_respond(interaction: discord.Interaction, message: str):
  try:
    await interaction.response.defer()
    messages_str = ""
    async for text in interaction.channel.history(limit=55):
      name = text.author.display_name
      if client.user == text.author:
        name = "magnum opus (yourself)"
      messages_str = name + " said: " + text.content + "\n" + messages_str 
    response = palm.chat(messages=["SYSTEM: You are Magnum Opus, a discord bot. **You MUST respond in discord parsable text.**","Previous messages in discord channel: " + messages_str,interaction.user.display_name + ": " + message])
    if len(response.last) > 2000:
      response.last = response.last[0:1999]
    await interaction.followup.send("**[Interaction request by " + interaction.user.display_name + "]** " + response.last)
  except:
    try:
      print(response.last)
    except:
      print("No response.")
    try:
      embed=discord.Embed(title="Embed response for formatting issues", description=response.last, color=0xFF00FF)
      await interaction.followup.send(embed=embed)
    except Exception as e:
      await interaction.followup.send("**Error: **" + str(e))
      await interaction.followup.send("This command may not be available due to a lack of a key.")
@tree.command(name = "google-image", description = "Search in the Google Images database. Max 5 images.")
async def google_image(interaction: discord.Interaction, message: str, amount: str):
  try:
    amount = int(amount)
    if amount > 5:
      await interaction.response.send_message("The maximum is 5 images, not " + str(amount) + ".")
    await interaction.response.defer()
    params = {
    "q": message,
    "engine": "google_images",
    "ijn": "0",
    "api_key": serp_api_key
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    image_results = ""
    i = 0
    while amount > 0:
      amount = amount - 1
      image_results = image_results + " " + results["images_results"][i]["original"]
      i = i + 1
    print(image_results)
    await interaction.followup.send(image_results)
  except Exception as e:
    await interaction.followup.send("Error: " + str(e))
    await interaction.followup.send("The bot host may have not provided the optional SERP API key required for this command.")
@tree.command(name='grant-role', description='Grant any Role')
@has_permissions(manage_roles=True)
async def grant_role(interaction: discord.Interaction, member:discord.Member, role:discord.Role, give: bool):
  try: 
    if give == True:
      await member.add_roles(role)
      embed=discord.Embed(title="Role Grant Successful", description=member.name + " has been given the " + role.name + " role.", color=0xFFFF00)
    else:
      await member.remove_roles(role)
      embed=discord.Embed(title="Role Removal Successful", description=member.name + " has been revoked his " + role.name + " role.", color=0xFFFF00)
    await interaction.response.send_message(embed=embed)
  except Exception as e:  
    await interaction.response.send_message(str(e))
@tree.command(name='timeout', description='Timeout a user.')
@has_permissions(manage_roles=True)
async def timeout(interaction: discord.Interaction,member:discord.Member, minutes: str):
  minutes = int(minutes)
  guild_id = interaction.guild.id
  user_id = member.id
  member0 = timeout_user(user_id=user_id, guild_id=guild_id,until=minutes)
  pprint.pprint(member0)
  await interaction.response.send_message("Timeout of " + str(member.name)  + " successful for " + str(minutes) + " minutes.")
@tree.command(name='pattern', description='Display a numerical sequence')
async def pattern(interaction: discord.Interaction):
  await interaction.response.send_message(content="Loading...")
  n = 0
  list = []
  list_str = ""
  while 100 > n:
    list.append([str(random.randint(10000000,99999999))])
    n = n + 1
  n = 0
  list_str = str(list[n]) + "\n" + str(list[n+1]) + "\n" + str(list[n+2]) + "\n" + str(list[n+3])
  n = n + 1
  while True:
    list_str = ""
    x = 0
    while 20 > x:
      list_str = list_str + " " * abs((int(60 * math.cos((x*3+n*3)**0.5)) + 20)) + str(list[(n+x) % len(list)]) + "\n"
      x = x + 1
    list_str = "```" + list_str + "```"
    await interaction.edit_original_response(content=list_str)
    n = n + 1
    if n > 900:
      break
@tree.command(name='create-invite', description='Create an invite link')
async def invite(interaction: discord.Interaction, expiration_in_hours: str):
  link = await interaction.channel.create_invite(max_age = int(expiration_in_hours) * 3600)
  await interaction.response.send_message("Link: " + str(link) + " This will expire in " + expiration_in_hours + " hours.")

client.run(given_token)

