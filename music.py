import discord
from discord.ext import commands
import youtube_dl
import asyncio
import json
from youtube_search import YoutubeSearch
from pytube import Playlist
import re
import random
import tracemalloc
tracemalloc.start()


class music(commands.Cog):
  def __init__(self, client):
    self.client = client

  global currentQueue
  currentQueue = []

  @commands.command()
  async def join(self, ctx):
    if ctx.author.voice is None:
      await ctx.send("You are not in a voice channel!")
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
      await voice_channel.connect()
    else:
      await ctx.voice_client.move_to(voice_channel)

  @commands.command()
  async def disconnect(self, ctx):
    if ctx.author.voice is None:
      await ctx.send("You are not in a voice channel!")
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
      await voice_channel.connect()
    else:
      await ctx.voice_client.move_to(voice_channel)
    
    global currentQueue
    currentQueue = []
    await ctx.voice_client.disconnect()

  @commands.command()
  async def play(self, ctx):
    url = ctx.message.content.strip(".play ")
    global currentQueue
    if ctx.author.voice is None:
      await ctx.send("You are not in a voice channel!")
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
      await voice_channel.connect()
    else:
      await ctx.voice_client.move_to(voice_channel)

    await ctx.send("One moment...")

    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    YDL_OPTIONS = {'format':'bestaudio'}
    vc = ctx.voice_client

    async def myAfter():
      await asyncio.sleep(2)
      currentQueue.pop(0)
      if len(currentQueue) > 0:
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
          info = currentQueue[0]
          await ctx.send(f"Now Playing: **{info['title']}**")
          url2 = info['formats'][0]['url']
          source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
          vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(myAfter(), self.client.loop))

    if url[0:8] == "https://":
      if url.find("list=") == -1:
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
          info = ydl.extract_info(url, download=False)
          currentQueue.insert(len(currentQueue), info)
          if not vc.is_playing():
            await ctx.send(f"Now Playing: **{info['title']}**")
            url2 = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
            vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(myAfter(), self.client.loop))
          else:
            await ctx.send(f"Added ``{info['title']}`` to the queue.")
      else:
        playlist = Playlist(f'{url}')
        playlist._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")
        for pUrl in playlist.video_urls:
          with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(pUrl, download=False)
            currentQueue.insert(len(currentQueue), info)
            if not vc.is_playing():
              await ctx.send(f"Now Playing: **{info['title']}**")
              url2 = info['formats'][0]['url']
              source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
              vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(myAfter(), self.client.loop))
            else:
              await ctx.send(f"Added ``{info['title']}`` to the queue.")
    else:
      results = YoutubeSearch(url, max_results=1).to_json()
      resultsList = json.loads(results)
      newURL = f"https://www.youtube.com{resultsList['videos'][0]['url_suffix']}"
      
      with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(newURL, download=False)
        currentQueue.insert(len(currentQueue), info)
        if not vc.is_playing():
          await ctx.send(f"Now Playing: **{info['title']}**")
          url2 = info['formats'][0]['url']
          source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
          vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(myAfter(), self.client.loop))
        else:
          await ctx.send(f"Added ``{info['title']}`` to the queue.")

  @commands.command()
  async def pause(self, ctx):
    if ctx.author.voice is None:
      await ctx.send("You are not in a voice channel!")
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
      await voice_channel.connect()
    else:
      await ctx.voice_client.move_to(voice_channel)
    
    await ctx.send("Paused.")
    await ctx.voice_client.pause()

  @commands.command()
  async def resume(self, ctx):
    if ctx.author.voice is None:
      await ctx.send("You are not in a voice channel!")
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
      await voice_channel.connect()
    else:
      await ctx.voice_client.move_to(voice_channel)
    
    await ctx.voice_client.resume()
    await ctx.send("Resumed.")
  
  @commands.command()
  async def stop(self, ctx):
    if ctx.author.voice is None:
      await ctx.send("You are not in a voice channel!")
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
      await voice_channel.connect()
    else:
      await ctx.voice_client.move_to(voice_channel)
    
    await ctx.send("Stopped.")
    global currentQueue
    currentQueue = []
    ctx.voice_client.stop()

  @commands.command()
  async def queue(self, ctx):
    if ctx.author.voice is None:
      await ctx.send("You are not in a voice channel!")
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
      await voice_channel.connect()
    else:
      await ctx.voice_client.move_to(voice_channel)

    global currentQueue

    if len(currentQueue) != 0:
      qString = "__CURRENT QUEUE__"
      for i in range(len(currentQueue)):
        obj = currentQueue[i]
        sAdd = f"``{i+1}.`` - {obj['title']}"
        qString = f"{qString}\n{sAdd}"
      await ctx.send(qString)
    else:
      await ctx.send("There is nothing in the queue.")
  
  @commands.command()
  async def skip(self, ctx):
    if ctx.author.voice is None:
      await ctx.send("You are not in a voice channel!")
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
      await voice_channel.connect()
    else:
      await ctx.voice_client.move_to(voice_channel)
    
    await ctx.send("Skipped.")
    ctx.voice_client.stop()

  @commands.command()
  async def shuffle(self, ctx):
    global currentQueue
    if len(currentQueue) == 0:
      await ctx.send("Theres nothing to shuffle. Add something to the queue with ``.play``")
    
    currentSong = currentQueue[0]
    currentQueue.pop(0)
    currentQueue = random.sample(currentQueue, k=len(currentQueue))
    currentQueue.insert(0, currentSong)

    await ctx.send(f"Successfully shuffled {len(currentQueue)} songs.")
  
  @commands.command()
  async def clear(self, ctx):
    global currentQueue
    currentQueue = []
    await ctx.send("Queue Cleared.")
    ctx.voice_client.stop()
  
  @commands.command()
  async def remove(self, ctx, index):
    global currentQueue
    if len(currentQueue) == 0:
      await ctx.send("Theres nothing to shuffle. Add something to the queue with ``.play``")
    
    currentQueue.pop(int(index)-1)
    if index == 1:
      ctx.voice_client.stop()
    await ctx.send(f"Removed song #{index} from the queue")

def setup(client):
  client.add_cog(music(client))
