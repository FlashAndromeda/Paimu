import os
import sys
import random
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

# Paimu hello
@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)
    print(
        f'{client.user} is connected to the following guild:\n'
        f'  {guild.name} (id: {guild.id})'
    )

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content.lower()
    author_name = str(message.author)[0:-5]

    greetingslist = ['Hey ', 'Hello ', 'Heyoo ', 'Yo ', 'Wassup ', 'Howdy ', 'Greetings ', 'Sup ', 'Nice seeing you ', "It's good to see you "]
    goodbyelist = ['Cya ', 'See ya ', 'See you later ', 'Bye ', 'Goodbye ', 'See you around ']

    if 'paimu' and 'help' in content:
        with open('help.txt') as file:
            for line in file:
                await message.channel.send(line)
    elif message.content == 'raise-exception':
        raise discord.DiscordException

    if 'paimu' and 'hello' in content:
        greeting = random.choice(greetingslist)
        await message.channel.send(f'{greeting}{author_name}')

    if 'paimu' and 'bye' in content:
        goodbye = random.choice(goodbyelist)
        await message.channel.send(f'{goodbye}{author_name}')

@client.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n'
                    f'{sys.exc_info()}\n')
        else:
            raise

client.run(TOKEN)