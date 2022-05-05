import os
import random

import discord
import requests
from discord.ext import commands
from discord.errors import Forbidden
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SCREENSHOT_TOKEN = os.getenv('SCREENSHOT_TOKEN')
IMDB_KEY = os.getenv('IMDB_KEY')

embed_color = 0xf0f0f0

bot = commands.Bot(command_prefix='-p ')

async def send_embed(ctx, embed):
    try:
        await ctx.send(embed=embed)
    except Forbidden:
        try:
            await ctx.send("Hey, seems like I can't send embeds. Please check my permissions :)")
        except Forbidden:
            await ctx.author.send(
                f"Hey, seems like I can't send any message in {ctx.channel.name} on {ctx.guild.name}\n"
                f"May you inform the server team about this issue? :slight_smile: ", embed=embed)

class Various(commands.Cog):
    """
    A collection of various random commands with no specific utility in mind.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{bot.user.name} has connected to discord!')

    @commands.command(name='hello', brief="Greets the user.")
    async def hello(self, ctx):
        await ctx.send(f'Hello {ctx.author.display_name}!')

    @commands.command(name='roll', brief='Rolls dice.', usage='<number_of_dice> <number_of_sides>')
    async def roll(self, ctx, number_of_rolls: int, range_of_roll: int):

        """This command is used to make the bot simulate rolling dice for you."""

        if number_of_rolls > 200:
            await ctx.send('Number of rolls must be 200 or less!')
            return
        elif range_of_roll > 100000000:
            await ctx.send('Number of sides must be 100000000 or less!')
            return
        else:
            dice = [
                str(random.choice(range(1, range_of_roll + 1)))
                for _ in range(number_of_rolls)
            ]
            await ctx.send(f"Your roll: {', '.join(dice)}")

    @commands.command(name='age', brief='Guesses a persons age.')
    async def age(self, ctx, name:str):

        """This command is used to make the bot guess a persons age based on their name. Only works with real names."""

        request = f"https://api.agify.io/?name={name}"

        resp = requests.get(request).json()['age']

        if resp is not None:
            if resp == 1:
                resp = str(resp) + " year old."
            else:
                resp = str(resp) + " years old."

            await ctx.send(f"I'm guessing {name} is about {resp}")

        else:
            await ctx.send(f"Please use a name I can recognize :(")

    @commands.command(name='avatar', brief='Fetches a users avatar.', aliases=['av'])
    async def avatar(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author

        embed = discord.Embed(colour=embed_color)
        embed.set_author(name=user.display_name, icon_url=user.avatar_url)
        embed.set_image(url=user.avatar_url)

        await send_embed(ctx, embed)

    @commands.command(name='screenshot', brief='Takes a screenshot of a specified webpage.', usage='<page_url>', aliases=['scr'])
    async def screenshot(self, ctx, url:str):

        """This command is used to take a screenshot of a webpage and then upload it in an embed."""
        try:
            res = requests.get("https://shot.screenshotapi.net/screenshot?token="+str(SCREENSHOT_TOKEN)+"&url="+url).json()
        except KeyError:
            await ctx.send('Please input a URL!')
            return

        embed = discord.Embed(
            url=res['url'],
            title=res['url'],
            colour=embed_color
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.set_image(url=res['screenshot'])

        await send_embed(ctx, embed)

    @commands.command(name='country', brief='Look up information about countries.', aliases=['co'], usage='<country_name>')
    async def country(self, ctx, *country_name):

        """This command is used to search up information about any particular country by name."""

        country_name = str(country_name).replace(' ', '%20')

        try:
            r = requests.get(f"https://restcountries.com/v3.1/name/{country_name}").json()[0]
        except KeyError:
            await ctx.send(f'{country_name} is not a country!')
            return

        name = str(r['name']['common'])

        try:
            languages = list(r['languages'].values())
            lang = ''
            for language in languages:
                lang += f"{language}, "
            lang = lang[0:-2]

        except AttributeError:
            lang = r['languages']

        #########################################
        try:
            capital = r['capital'][0]
        except KeyError:
            print(f"Capital for {name} is not available")
            capital = "not available"

        try:
            subregion = r['subregion']
        except KeyError:
            print(f"Subregion for {name} is not available")
            subregion = 'not available'

        try:
            area = str(r['area']) + ' km2'
        except KeyError:
            print(f"Area for {name} is not available")
            area = 'not available'

        try:
            population = r['population']
        except KeyError:
            print(f"Population for {name} is not available")
            population = 'not available'

        try:
            gini = list(r['gini'].values())[0]
        except KeyError:
            print(f"Gini index for {name} is not available")
            gini = "not available"

        try:
            continents = ', '.join(r['continents'])
        except KeyError:
            print(f"Continents for {name} are not available")
            continents = 'not available'

        try:
            week = r['startOfWeek']
        except KeyError:
            print(f"Start of week for {name} is not available")
            week = 'not available'

        try:
            webdomain = r['tld'][0]
        except KeyError:
            print(f"Web domain for {name} is not available")
            webdomain = 'not available'
        ########################################

        embed = discord.Embed(
            color=embed_color,
            title=name,
            description=str(r['name']['official']),
            url=str(r['maps']['googleMaps'])
        )
        embed.set_thumbnail(url=r['flags']['png'])

        embed.add_field(name=f'Some info about {name}:', value=f"Capital:             {capital}\n"
                                                                 f"Region:              {subregion}\n"
                                                                 f"Area:                {area}\n"
                                                                 f"Population:          {population}\n"
                                                                 f"GINI index:          {gini}\n"
                                                                 f"Languages used:      {lang}\n"
                                                                 f"Continents:          {continents}\n"
                                                                 f"Start of week:       {week}\n"
                                                                 f"Web domain:          {webdomain}", inline=False)

        if r['unMember']:
            unmem = 'Yes.'
        else:
            unmem = 'No.'
        embed.add_field(name=f'Is {name} a member of the UN?', value=unmem, inline=False)

        await send_embed(ctx, embed)

class Literature(commands.Cog):
    """
    A collection of commands related to literature used to look up information about movies, TV series, directors and actors.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='book', brief='Look up information about a book.', aliases=['b'], usage='<book_title>')
    async def book(self, ctx, *book_title):

        """This command is used to look up information about a specific book. To use it, simply type in quotation marks the name and author of the book you want to look up!
        Returns things like author name, average number of pages or the year the book was first published."""

        book_title = str(book_title)

        res = requests.get(
            f"http://openlibrary.org/search.json?q={book_title.replace(' ', '+')}&fields=title,author_name,first_publish_year,number_of_pages_median,edition_count,cover_i,key&limit=1").json()
        book = res['docs'][0]

        #################################
        try:
            author = str(book['author_name'][0])
        except KeyError:
            author = 'not available'

        try:
            publishyear = book['first_publish_year']
        except KeyError:
            publishyear = 'not available'

        try:
            pages = book['number_of_pages_median']
        except KeyError:
            pages = 'not available'

        try:
            editions = book['edition_count']
        except KeyError:
            editions = 'not available'
        ##################################
        embed = discord.Embed(
            colour=embed_color,
            title=book['title'],
            url=f"https://openlibrary.org{book['key']}/",
            description=f"Written by {author}\n"
                        f"Year first published: {publishyear}\n"
                        f"Pages: {pages}\n"
                        f"Editions: {editions}",
        )
        try:
            cover = f"https://covers.openlibrary.org/b/ID/{book['cover_i']}-L.jpg"
            embed.set_image(url=cover)
        except KeyError:
            print('No cover found!')
            pass

        await send_embed(ctx, embed)

class Cinematography(commands.Cog):

    """
    A collection of commands related to cinematography used to look up information about movies, shows, directors etc.
    """

    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='movie', brief='Look up information about a movie.', aliases=['mov'], usage='<movie_name>')
    async def movie(self, ctx, *movie_name):

        """This command is used to look up information about any particular movie using the IMDB API."""

        movie_name = str(movie_name).replace(' ', '%20')

        try:
            r = requests.get(f"https://imdb-api.com/en/API/SearchMovie/{IMDB_KEY}/{movie_name}").json()['results'][0]
        except TypeError:
            await ctx.send("Daily API calls limit exceeded!")
            return

        movie_id = r['id']

        r2 = requests.get(f"https://imdb-api.com/en/API/Title/{IMDB_KEY}/{movie_id}/Posters,Ratings,Wikipedia").json()
        ratings = r2['ratings']
        box = r2['boxOffice']


        embed = discord.Embed(color=embed_color, title=f"{r2['fullTitle']}", description=r2['plot'], url=f"https://www.imdb.com/title/{movie_id}/")
        embed.set_image(url=r2['posters']['posters'][0]['link'])

        try:
            embed.add_field(name='Directed by:', value=f"{r2['directors']}", inline=True)
        except KeyError:
            pass

        try:
            embed.add_field(name='Written by:', value=f"{r2['writers']}", inline=True)
        except KeyError:
            pass

        try:
            embed.add_field(name='Starring:', value=f"{r2['stars']}", inline=False)
        except KeyError:
            pass

        try:
            embed.add_field(name=f"Genres:", value=f"{r2['genres']}", inline=False)
        except KeyError:
            pass

        try:
            embed.add_field(name='Ratings:', value=f"IMDB: {ratings['imDb']}\n"
                                                      f"Metacritic: {ratings['metacritic']}\n"
                                                      f"Rotten tomatoes: {ratings['rottenTomatoes']}", inline=True)
        except KeyError:
            pass

        try:
            embed.add_field(name=f'Box Office:', value=f"Budget: {box['budget']}\n"
                                                      f"Opening weekend USA: {box['openingWeekendUSA']}\n"
                                                      f"Gross USA: {box['grossUSA']}\n"
                                                      f"Gross worldwide: {box['cumulativeWorldwideGross']}", inline=True)
        except KeyError:
            pass

        await send_embed(ctx, embed)



def setup(bot):
    bot.add_cog(Various(bot))
    bot.add_cog(Literature(bot))

setup(bot)
bot.run(TOKEN)