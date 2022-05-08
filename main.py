import os
import random

import logging
import secrets
from datetime import date
import discord
import requests
from discord.ext import commands
from discord.errors import Forbidden
from dotenv import load_dotenv

# TODO Expand Cinematography category
# TODO Add NASA API integration / sort of done
# TODO Add music playback functionality

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SCREENSHOT_TOKEN = os.getenv('SCREENSHOT_TOKEN')
IMDB_KEY = os.getenv('IMDB_KEY')
NASA_KEY = os.getenv('NASA_KEY')

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

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = "**It's on cooldown**, please try again in {:.2f}s".format(error.retry_after)
        await ctx.send(msg)

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

        embed = discord.Embed(colour=embed_color, type='image')
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

        capital = r.get('capital', 'not available')[0]
        subregion = r.get('subregion', 'not available')
        area = str(r.get('area', 'not available')) + ' km2'
        population = r.get('population', 'not available')
        week = r.get('startOfWeek', 'not available')
        webdomain = r.get('tld', 'not available')[0]
        gini = list(r.get('gini', 'not available').values())[0]
        continents = ', '.join(r.get('continents', 'not available'))

        embed = discord.Embed(
            color=embed_color,
            title=name,
            description=str(r['name']['official']),
            url=str(r['maps']['googleMaps'])
        )
        embed.set_thumbnail(url=r['flags']['png'])

        embed.add_field(name=f'Some info about {name}:', value=f"**Capital:**             {capital}\n"
                                                               f"**Region:**              {subregion}\n"
                                                               f"**Area:**                {area}\n"
                                                               f"**Population:**          {population}\n"
                                                               f"**GINI index:**          {gini}\n"
                                                               f"**Languages used:**      {lang}\n"
                                                               f"**Continents:**          {continents}\n"
                                                               f"**Start of week:**       {week}\n"
                                                               f"**Web domain:**          {webdomain}", inline=False)

        if r['unMember']:
            unmem = 'Yes.'
        else:
            unmem = 'No.'
        embed.add_field(name=f'Is {name} a member of the UN?', value=unmem, inline=False)

        await send_embed(ctx, embed)

    @commands.command(name='pick', brief='Picks one thing from a list of items.')
    async def pick(self, ctx, *items):
        """
        This command is used to randomly pick one item from a list of items. To use it, simply type in "-p pick" followed by a number of items separated by spaces.
        """

        items = list(items)

        await ctx.send(f"I've chosen: {secrets.choice(items)}")

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

        book_title = str(book_title).replace(' ', '%20')

        res = requests.get(
            f"http://openlibrary.org/search.json?q={book_title}&fields=title,author_name,first_publish_year,number_of_pages_median,edition_count,cover_i,key&limit=1").json()
        book = res['docs'][0]

        author = book.get('author_name', 'not available')[0]
        publishyear = book.get('first_publish_year', 'not available')
        pages = book.get('number_of_pages_median', 'not available')
        editions = book.get('edition_count', 'not available')

        embed = discord.Embed(
            colour=embed_color,
            title=book['title'],
            url=f"https://openlibrary.org{book['key']}/",
            description=f"**Written by** {author}\n"
                        f"**Year first published:** {publishyear}\n"
                        f"**Pages:** {pages}\n"
                        f"**Editions:** {editions}",
        )
        try:
            cover = f"https://covers.openlibrary.org/b/ID/{book['cover_i']}-L.jpg"
            embed.set_image(url=cover)
        except KeyError:
            print('No cover found!')
            pass

        await send_embed(ctx, embed)

    @commands.command(name='author', brief='Look up information about an author.', aliases=['aut'], usage='<author_name>')
    async def author(self, ctx, *author_name):

        """
        A command used to look up information about a specific author.
        """

        author_name = str(author_name).replace(' ', '%20')

        r = requests.get(f"https://openlibrary.org/search/authors.json?q={author_name}").json()
        key = r['docs'][0]['key']

        r2 = requests.get(f"https://openlibrary.org/authors/{key}.json").json()

        ########################################
        try:
            name = f"{r2['name']} ({r2['fuller_name']})"
        except KeyError:
            name = r2.get('name')

        bio = r2.get('bio', 'Bio not available.')
        birth_date = r2.get('birth_date', 'not available')
        death_date = r2.get('death_date', None)
        top_work = r['docs'][0].get('top_work', 'not available')
        work_count = r['docs'][0].get('work_count', 'not available')

        ########################################

        embed = discord.Embed(colour=embed_color, title=name, description=bio,
                              url=f"https://openlibrary.org{r2['key']}")

        embed.add_field(name=f"About {r2['name']}:", value=f"**Birth date:** {birth_date}\n"
                                                           f"**Death date:** {death_date}\n"
                                                           f"**Top work:** {top_work}\n"
                                                           f"**Work count:** {work_count}", inline=False)

        await send_embed(ctx, embed)

    @commands.cooldown(5, 60, commands.BucketType.user)
    @commands.command(name='subject', brief='Look up books by subject.', aliases=['sub'], usage='<book_subject>')
    async def subject(self, ctx, *book_subject):

        """
        This command is used to look up a number of works on a certain subject. It displays only the top 5 works.
        """

        r = requests.get(f"http://openlibrary.org/subjects/{book_subject[0]}.json?limit=5").json()
        works = r.get('works')

        embed = discord.Embed(colour=embed_color, title=f"Subject: {r.get('name')}", description=f"Works found total: {r.get('work_count', 'none')}", url=f"http://openlibrary.org{r.get('key')}")

        for work in works:
            key = work.get('cover_edition_key')

            r2 = requests.get(f"http://openlibrary.org/books/{key}.json").json()

            title = r2.get('title', 'not available')
            author = (work.get('authors', 'not available')[0]).get('name')
            edition_count = work.get('edition_count', 'not available')
            pages = r2.get('number_of_pages', 'not available')
            book_url = f"http://openlibrary.org{key}"

            embed.add_field(name=title, value=f"Written by {author}\n"
                                              f"Pages: {pages}\n"
                                              f"Editions: {edition_count}\n"
                                              f"[Link to book.]({book_url})\n", inline=False)

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

class Astronomy(commands.Cog):
    """
    A collection of commands related to space and astronomy.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(name='apod', brief="Returns NASA's picture of the day.")
    async def apod(self, ctx):
        """
        Returns the NASA's Astronomy picture of the day.
        """

        r = requests.get(f"https://api.nasa.gov/planetary/apod?api_key={NASA_KEY}").json()

        author = r.get('copyright')
        date = r.get('date')
        description = r.get('explanation')
        hdurl = r.get('hdurl')
        url = r.get('url')
        title = r.get('title')

        embed = discord.Embed(colour=embed_color, title=title, description=description, url=hdurl)
        embed.set_author(name=author)
        embed.set_image(url=url)
        embed.set_footer(text=date)

        await send_embed(ctx, embed)

    @commands.cooldown(1, 120, commands.BucketType.guild)
    @commands.command(name='neo', brief='Returns information about near earth Asteroids.')
    async def neo(self, ctx):
        """
        This command returns a list and details about near earth Asteroids based on their closest approach to Earth. It only displays data for the current day.
        """


        r = requests.get(f"https://api.nasa.gov/neo/rest/v1/feed?start_date={date.today()}&end_date={date.today()}&api_key={NASA_KEY}").json()
        day = r['near_earth_objects'][f"{date.today()}"]

        element_count = r.get('element_count')

        embed = discord.Embed(colour=embed_color, title=f"NEO's on {date.today()}", description=f"NEO's found total: {element_count}")

        for a in day:
            name = a.get('name')
            neo_id = a.get('neo_reference_id')
            absolute_magnitude = a.get('absolute_magnitude_h')
            diam_min = a['estimated_diameter']['meters']['estimated_diameter_min']
            diam_max = a['estimated_diameter']['meters']['estimated_diameter_max']
            is_hazard = a.get('is_potentially_hazardous_asteroid')

            data = a['close_approach_data'][0]
            approach_date = data['close_approach_date_full']
            relative_vel = data['relative_velocity']['kilometers_per_second']
            miss_dist_au = data['miss_distance']['astronomical']
            orbiting_body = data['orbiting_body']

            is_sentry = a.get('is_sentry_object')

            embed.add_field(name=name, value=f"ID: {neo_id}\n"
                                             f"Absolute magnitude: {absolute_magnitude}\n"
                                             f"Minimum estimated diameter: {round(float(diam_min), 2)}m\n"
                                             f"Maximum estimated diameter: {round(float(diam_max), 2)}m\n"
                                             f"Is it potentially a hazardous asteroid? {is_hazard}\n"
                                             f"Is it a sentry object? {is_sentry}\n\n"
                                             f"Close approach date: {approach_date}\n"
                                             f"Relative velocity: {round(float(relative_vel), 2)} km/s\n"
                                             f"Miss distance: {round(float(miss_dist_au), 3)} AU\n"
                                             f"Orbiting body: {orbiting_body}\n", inline=True)

        await send_embed(ctx, embed)

def setup(bot):
    bot.add_cog(Various(bot))
    bot.add_cog(Literature(bot))
    bot.add_cog(Cinematography(bot))
    bot.add_cog(Astronomy(bot))

setup(bot)
bot.run(TOKEN)