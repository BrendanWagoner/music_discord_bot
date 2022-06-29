import yt_dlp
import discord
from discord.ext import commands, tasks
import asyncio
import logging
import os


token = os.environ['DISCORD_TOKEN']
intents = discord.Intents().all()
client = discord.Client(intents=intents)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
bot = commands.Bot(command_prefix='!', intents=intents)
yt_dlp.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'worstaudio/worst',
    'outtmpl': 'C:/Users/shado/PycharmProjects/discord_bot.py/downloads/%(title)s-%(id)s.%(ext)s',
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

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)


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


url_queue = []


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
    global url_queue
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await queue(ctx, url)
    else:
        if url not in url_queue:
            url_queue.append(url)
        if voice_client.is_connected():
            server = ctx.message.guild
            voice_channel = server.voice_client
            async with ctx.typing():
                filename = await YTDLSource.from_url(url_queue[0], loop=bot.loop)
                voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
            await ctx.send('This is playing {}'.format(url))
            del url_queue[0]
        else:
            await ctx.send('The bot is not connected.')


@bot.command(name='pause', help='tells bot to pause current music playing')
async def pause(ctx):
    voice_channel = ctx.message.guild.voice_client
    if voice_channel.is_playing():
        voice_channel.pause()
    else:
        await ctx.send('Nothing is currently playing.')


@bot.command(name='resume', help='tells bot to resume currently paused song')
async def resume(ctx):
    voice_channel = ctx.message.guild.voice_client
    if voice_channel.is_paused:
        voice_channel.resume()
    else:
        await ctx.send('nothing is paused.')


@bot.command(name='stop', help='tells bot to join voice channel if not connected, and plays selected url or song')
async def stop(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_channel.stop()
    else:
        await ctx.send('The bot is not playing anything')


@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='queue', help='queue songs to play one after another')
async def queue(ctx, url):
    global url_queue
    url_queue.append(url)
    await ctx.send('{} has been added to he playlist!'.format(url))


@bot.command(name='playnext', help='will play the next song in the queue')
async def play_next(ctx):
    voice_client = ctx.message.guild.voice_client
    if len(url_queue) >= 1:
        if voice_client.is_connected():
            server = ctx.message.guild
            voice_channel = server.voice_client
            async with ctx.typing():
                filename = await YTDLSource.from_url(url_queue[0], loop=bot.loop)
                voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
            await ctx.send('The next song is now playing')
            del url_queue[0]
        else:
            await ctx.send('You are not connected to a channel right now.')
    else:
        await ctx.send('Nothing is in the queue right now.')


@bot.command(name='skip', help='skips song to the next in queue')
async def skip(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.stop()
        await play_next(ctx)
    else:
        await ctx.send('Nothing is playing right now, queue something up!')


@bot.command(name='view', help='views what songs are inside the queue')
async def view(ctx):
    await ctx.send('your queue is now {}'.format(url_queue))


if __name__ == "__main__":
    bot.run(token)

# TODO fix the queue system, and add a skip command
# TODO need to make a file management script
# TODO clean everything up, make it look more presentable
