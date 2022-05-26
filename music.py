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
  currentQueue = {}

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

    await ctx.voice_client.disconnect()
    
    global currentQueue
    try:
      currentQueue.pop(str(ctx.message.guild.id))
    except:
      return

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
      guildQueue = currentQueue[str(ctx.message.guild.id)]
      guildQueue.pop(0)
      if len(guildQueue) > 0:
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
          info = guildQueue[0]
          await ctx.send(f"Now Playing: **{info['title']}**")
          url2 = info['formats'][0]['url']
          source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
          vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(myAfter(), self.client.loop))

    if url[0:8] == "https://":
      if url.find("list=") == -1:
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
          info = ydl.extract_info(url, download=False)
          guildQueue = None
          try:
            guildQueue = currentQueue[str(ctx.message.guild.id)]
          except:
            currentQueue.update({str(ctx.message.guild.id):[]})
            guildQueue = currentQueue[str(ctx.message.guild.id)]
          guildQueue.insert(len(guildQueue), info)
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
        msg = None
        amtAdded = 0
        for pUrl in playlist.video_urls:
          with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(pUrl, download=False)
            guildQueue = None
            try:
              guildQueue = currentQueue[str(ctx.message.guild.id)]
            except:
              currentQueue.update({str(ctx.message.guild.id):[]})
              guildQueue = currentQueue[str(ctx.message.guild.id)]
            guildQueue.insert(len(guildQueue), info)
            if not vc.is_playing():
              await ctx.send(f"Now Playing: **{info['title']}**")
              url2 = info['formats'][0]['url']
              source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
              vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(myAfter(), self.client.loop))
            else:
              if not msg:
                msg = await ctx.send(f"Added ``{info['title']}`` to the queue.")
                amtAdded += 1
              else:
                await msg.edit(f"Added ``{info['title']}`` and *{amtAdded}* more to the queue.")
                amtAdded += 1
    else:
      results = YoutubeSearch(url, max_results=1).to_json()
      resultsList = json.loads(results)
      newURL = f"https://www.youtube.com{resultsList['videos'][0]['url_suffix']}"
      
      with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(newURL, download=False)
        guildQueue = None
        try:
          guildQueue = currentQueue[str(ctx.message.guild.id)]
        except:
          currentQueue.update({str(ctx.message.guild.id):[]})
          guildQueue = currentQueue[str(ctx.message.guild.id)]
        guildQueue.insert(len(guildQueue), info)
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
    try:
      currentQueue.pop(str(ctx.message.guild.id))
    except:
      return
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
    guildQueue = None
    try:
      guildQueue = currentQueue[str(ctx.message.guild.id)]
    except:
      await ctx.send("There is nothing in the queue.")
      return

    qEmbed = discord.Embed(
      title="__CURRENT QUEUE__",
      color=16711680
    )
    
    if len(guildQueue) != 0:
      qString = ""
      for i in range(len(guildQueue)):
        obj = guildQueue[i]
        sAdd = f"``{i+1}.`` - {obj['title']}"
        qString = f"{qString}\n{sAdd}"
      try:
        qEmbed.description = qString
        await ctx.send(embed=qEmbed)
      except:
        try:
          qEmbed.description = f"{qString[:4090]}..."
          qEmbed.set_footer("Queue was too long to send so I sent as much as I could 😅")
          await ctx.send(embed=qEmbed)
        except:
          await ctx.send("the queue was too long to send 💀")
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
    guildQueue = None
    try:
      guildQueue = currentQueue[str(ctx.message.guild.id)]
    except:
      await ctx.send("Theres nothing to shuffle. Add something to the queue with ``.play``")
      return
    if len(guildQueue) == 0:
      await ctx.send("Theres nothing to shuffle. Add something to the queue with ``.play``")
      return
    
    currentSong = guildQueue[0]
    currentQueue[str(ctx.message.guild.id)].pop(0)
    currentQueue[str(ctx.message.guild.id)] = random.sample(guildQueue, k=len(guildQueue))
    currentQueue[str(ctx.message.guild.id)].insert(0, currentSong)

    await ctx.send(f"Successfully shuffled {len(guildQueue)} songs.")
  
  @commands.command()
  async def clear(self, ctx):
    global currentQueue
    guildQueue = None # Creating a new local variable wont work.
    try:
      guildQueue = currentQueue[str(ctx.message.guild.id)]
    except:
      await ctx.send("Theres nothing to clear.")
      return
    currentQueue[str(ctx.message.guild.id)] = []
    await ctx.send("Queue Cleared.")
    ctx.voice_client.stop()
  
  @commands.command()
  async def remove(self, ctx, index):
    global currentQueue
    guildQueue = None # Creating a new local variable wont work.
    try:
      guildQueue = currentQueue[str(ctx.message.guild.id)]
    except:
      await ctx.send("Theres nothing to remove.")
      return
    if len(guildQueue) == 0:
      await ctx.send("Theres nothing to remove.")
    
    currentQueue[str(ctx.message.guild.id)].pop(int(index)-1)
    if index == 1:
      ctx.voice_client.stop()
    await ctx.send(f"Removed song #{index} from the queue")

def setup(client):
  client.add_cog(music(client))
# https://youtu.be/jHZlvRr9KxM
