import os
import random
from dotenv import load_dotenv

# 1
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# 2
bot = commands.Bot(command_prefix='...')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to discord!')

@bot.command(name='hello', help="Returns the user's greeting.")
async def hello(ctx):
    await ctx.send(f'Hello!')

@bot.command(name='diceroll', help='Simulates rolling dice.')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(f"Your roll: {', '.join(dice)}")

bot.run(TOKEN)