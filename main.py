import os

import youtube_dl
import discord
from discord.ext import commands, tasks
import asyncio
import logging
import os
import pydirectory


token = os.environ['DISCORD_TOKEN']
intents = discord.Intents().all()
client = discord.Client(intents=intents)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
bot = commands.Bot(command_prefix='!', intents=intents)
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'C:/Users/shado/Desktop/SONGS from disc%(title)s-%(id)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename


@bot.event
async def on_ready():
    print('Bot is ready to go!')


@bot.command(name='join', help='tells bot to join voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send('{} is not connected to a voice channel'.format(ctx.message.author.name))
        return
    elif ctx.message.author.voice:
        channel = ctx.message.author.voice.channel
    await channel.connect()


@bot.command(name='play', help='tells bot to join voice channel if not connected, and plays selected url or song')
async def play(ctx, url):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():

        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
        await ctx.send('This is playing : {}'.format(filename))
    else:
        await ctx.send('The bot is not connected.')


@bot.command(name='stop', help='tells bot to join voice channel if not connected, and plays selected url or song')
async def stop(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_channel.stop()
    else:
        ctx.send('The bot is not playing anything')


@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    # channel = ctx.message.author.voice.channel
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
        # await channel.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")
# TODO create a pause, and resume feature
# TODO delete all the client commands


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$kolton'):
        await message.channel.send('dont ever type this command in again')

    if message.content.startswith('$sus'):
        await message.channel.send('kill you are self')

    if message.content.startswith('$amogus'):
        for x in range(5):
            await message.channel.send('<@134461127533920258>')


@client.event
async def on_message_delete(message):
    await message.channel.send('pussy')
# TODO clean everything up, make it look more presentable
# client.run(token)

if __name__ == "__main__":
    bot.run(token)

# TODO add and create things that are interesting or fun, expand.
