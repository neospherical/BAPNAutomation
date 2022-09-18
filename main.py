#Python 3.9 highly recommended
import gspread
import discord
from oauth2client.service_account import ServiceAccountCredentials
from discord.ext import commands
from discord.ui import Button, View

#from discord_components import DiscordComponents, Button, ButtonStyle
#from webserver import keep_alive
import os
# from pprint import pprint
import time
import requests
import json
import asyncio
#import music
import datetime
from roblox import Client

# import random


# ROBLOX Stuff

roClient = Client("YOUR RO CLIENT")


# Google Sheets Stuff


scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)

sheetClient = gspread.authorize(creds)

spreadsheet = sheetClient.open("BAPN Official Leaderboard")
rankingsSheet = spreadsheet.worksheet("Rankings")
challengeLogsSheet = spreadsheet.worksheet("Challenge Logs")
exampleSheet = spreadsheet.worksheet("EXAMPLE")
katanaTemplate = spreadsheet.worksheet("Katana Template")
heavyTemplate = spreadsheet.worksheet("Heavy Template")

# Discord Stuff

#cogs = [music]


class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        help_embed = discord.Embed(
            title="Commands",
            color=6559841
        )
        help_embed.add_field(name="```.ping```", value="*Use this to check the ping of the bot's server*", inline=True)
        help_embed.add_field(name="```.challenge (Your Username) (Opponent Username)```",
                             value="*Use this to challenge another player on the leaderboard*", inline=True)
        help_embed.add_field(name="```.rankCheck (Username)```",
                             value="*Use this to check a person's rank on the leaderboard*", inline=True)
        help_embed.add_field(name="```.overseerCheck```", value="*Used to check if you are an Overseer*", inline=True)
        help_embed.add_field(name="```.log (player1) (player2) (score)```",
                             value="*Used to log completed officials\n\nThis can only be used by Overseers*",
                             inline=True)
        help_embed.add_field(name="```.cancel (player1) (player2)```",
                             value="*Used to cancel challenges\n\nThis can only be used by Overseers*", inline=True)
        help_embed.add_field(name="```.calculate (player1) (player2) (score)```",
                             value="*Calculates the hypothetical points and positions of two players of the leaderboard*",
                             inline=True),
        help_embed.add_field(name="```.leaderboard```",
                             value="*Use this to display the current Official Leaderboard Rankings*", inline=True)
        help_embed.add_field(name="```.challenges```", value="*Use this to display all active challenges*")
        help_embed.add_field(name="```.ayuda```", value="*Displays this command in spanish*", inline=True)
        help_embed.add_field(name="```.addme```",
                             value="*Use this to request to participate on the Official Leaderboard Rankings*",
                             inline=True)

        await self.get_destination().send(embed=help_embed)


status = "please send .help"
prefix = "."
intents = discord.Intents.all()
discordClient = commands.Bot(command_prefix=prefix, help_command=CustomHelpCommand(), intents=intents)
#DiscordComponents(discordClient)


'''for i in range(len(cogs)):
    cogs[i].setup(discordClient)
'''
overseers = [
    344872876199116802,  # Dave
    819989575215874148,  # Poss
    498154140116058123,  # Sentrox
    # 479432457775742989, # Tyrant
    # 240219562623107073, # Pancakes
    # 428022970548748289, # Xyphel
    633711913066561536,  # Charon
    # 594321994678272000, # Palm
    # 463442449898143766, # Half
    484856866506014732,  # Suit
    835158077564256287,  # Tav
    # 894451789921931294, # Tanner
    # 488349873050222602, # Joe
    745817231832907816,  # Emanuelo
    581117906906251272,  # Ghost
    356661412686331904,  # Potat
    585157724224880675  # Jheerio
]


def insertChallengeLog(row):
    freeRow = len(challengeLogsSheet.col_values(1)) + 1
    challengeLogsSheet.insert_row(row, freeRow)
    challengeLogsSheet.format("A2", {
        "backgroundColor": {
            "red": 0.956863,
            "green": 0.8,
            "blue": 0.8
        }
    })
    challengeLogsSheet.format("B2", {
        "backgroundColor": {
            "red": 0.788235,
            "green": 0.854902,
            "blue": 0.972549
        }
    })
    challengeLogsSheet.format("C2", {
        "backgroundColor": {
            "red": 0.85098,
            "green": 0.917647,
            "blue": 0.827451
        }
    })

def eloFormula(SR1, SR2, score1, score2):
    score1 = int(score1)
    score2 = int(score2)
    deltaWins = score1 - score2
    SR1 = int(SR1)
    SR2 = int(SR2)

    # Calculates the SR change for both players
    winFactor = .9 + ((abs(deltaWins) ** 1.489896102405) * .1)  # Factors the score
    # The ELOs
    if (SR1 - SR2) * deltaWins > 0:
        eloFactor = abs((0 - abs(SR2 - SR1) + 500))
    else:
        eloFactor = (abs(SR2 - SR1) + 500)
    srChange = winFactor * max(0, eloFactor) * .192 + 1  # times or plus an optional constant

    if score1 == 5:
        SR1 = SR1 + 15 + srChange
        SR2 = SR2 - srChange
    else:
        SR2 = SR2 + 15 + srChange
        SR1 = SR1 - srChange

    return [int(round(SR1 * 10) / 10), int(round(SR2 * 10) / 10)]

# async def infiniteLoop():
#  while True:
#    await asyncio.sleep(10)
#    dateValues = challengeLogsSheet.col_values(3)
#    if len(dateValues) < 2:
#      continue

#    for i in range(len(dateValues)):
#      if dateValues[i] == "Date Issued":
#        continue
#      issuedDateList = dateValues[i].split("/")
#      issuedDate = f"{issuedDateList[2]}-{issuedDateList[0]}-{issuedDateList[1]}"
#      actualDate = datetime.date.fromisoformat(issuedDate)
#      delta = datetime.timedelta(days=3)
#      bigDate = actualDate + delta
#      print(f"{issuedDate} // {str(datetime.date.today())}")

# asyncio.ensure_future(infiniteLoop())

# @discordClient.event
# async def on_ready():
#  print("Bot is ready.")

@discordClient.command()
async def ayuda(ctx):
    help_embed = discord.Embed(
        title="Comandos",
        color=6559841
    )
    help_embed.add_field(name="```.ping```", value="Usa esto para mirar el ping del servidor donde se aloja el bot",
                         inline=True)
    help_embed.add_field(name="```.challenge (Tu nombre de usuario) (El nombre de usuario de tu enemigo)```",
                         value="*Usa esto para retar a otro jugador de la clasificatoria*", inline=True)
    help_embed.add_field(name="```.rankCheck (Nombre de usuario)```",
                         value="*Use esto para ver que posición ocupa alguien en la clasificatoria*", inline=True)
    help_embed.add_field(name="```overseerCheck```",
                         value="*Usa esto para ver qué posición ocupa alguien en la clasificatoria*", inline=True)
    help_embed.add_field(name="```.log (jugador1) (jugador2) (puntuación1) (puntiación2)```",
                         value="Comando usado solo por Overseers para registrar batallas oficiales completadas.\n\nSolo los Overseers pueden usar este comando.",
                         inline=True)
    help_embed.add_field(name="```.cancel (jugador1) (jugador2)```",
                         value="Comando usado para cancelar batallas oficiales.\n\nSolo los Overseers pueden usar este comando.",
                         inline=True)
    help_embed.add_field(name="```.calculate (jugador1) (jugador2) (puntuación1) (puntiación2)```",
                         value="Calcula los puntos y las posiciones hipotéticos de dos jugadores de la clasificatoria",
                         inline=True),
    help_embed.add_field(name="```.leaderboard```", value="*Use esto para mostrar la tabla de clasificación*")
    help_embed.set_footer(text="Traducido por Sentrox17")

    await ctx.send(embed=help_embed)

@discordClient.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(discordClient.latency * 1000)}ms")

@discordClient.command()
async def overseerCheck(ctx):
    isAnOverseer = False
    guilds = discordClient.guilds
    print(len(guilds))
    await discordClient.change_presence(status=discord.Status.online, activity=discord.Game(status))
    for i in range(len(overseers)):
        if overseers[i] == ctx.message.author.id:
            isAnOverseer = True
            await ctx.send("You are an Overseer :D")
    if not isAnOverseer:
        await ctx.send("You are not an Overseer :(")
        return

@discordClient.command()
async def rankCheck(ctx, username):
    rank = 0
    players = rankingsSheet.col_values(3)
    for i in range(len(players)):
        if players[i] == username:
            rank = rankingsSheet.cell(i + 1, 2).value

    if rank != 0:
        await ctx.send(f"{username}'s rank is #{rank}")
    else:
        await ctx.send(f"{username} is not on the leaderboard")

@discordClient.command()
async def challenge(ctx, your_username, opponent_username):
    await ctx.send("Loading challenge request, could take up to 5 minutes...")

    found_your_username = False
    found_opponent_username = False
    participants = rankingsSheet.col_values(3)
    for i in range(len(participants)):
        if participants[i] == your_username:
            found_your_username = True
        elif participants[i] == opponent_username:
            found_opponent_username = True

    timesHasChallenged = 0
    challengers = challengeLogsSheet.col_values(1)
    for i in range(len(challengers)):
        if len(challengers) >= 100:
            time.sleep(1)
        if challengers[i] == your_username:
            timesHasChallenged += 1

    timesHasBeenChallenged = 0
    timesChallengedInSeason = 0
    challengedPlayers = challengeLogsSheet.col_values(2)
    for i in range(len(challengedPlayers)):
        if len(challengedPlayers) >= 100:
            time.sleep(1)
        if challengedPlayers[i] == opponent_username:
            timesHasBeenChallenged += 1
            if challengeLogsSheet.cell(i, 1).value == your_username:
                timesChallengedInSeason += 1

    def challengeChecks():
        if found_your_username == True and found_opponent_username == True:
            if timesHasChallenged < 5 and timesHasBeenChallenged < 3:
                if timesChallengedInSeason < 2:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    if challengeChecks():
        date = str(datetime.date.today())
        rowToInsert = [your_username, opponent_username, date]
        insertChallengeLog(rowToInsert)
        challengedID = spreadsheet.worksheet(opponent_username).cell(3, 8).value

        challengeEmbed = discord.Embed(
            title="Your challenge has been logged!",
            description=f"{your_username} ({ctx.message.author.mention}) has challenged {opponent_username} (<@{challengedID}>)",
            color=65280
        )
        channelEmbed = discord.Embed(
            title=(f'{ctx.message.author} has logged a challenge between {your_username} and '
                   f'{opponent_username}'),
            color=25855
        )
        channelEmbed.set_author(name=str(ctx.message.author), icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=challengeEmbed)
        logChannel = discordClient.get_channel(867247000390336542)
        await logChannel.send(embed=channelEmbed)
        try:
            user = discordClient.get_user(int(challengedID))
            dm = await user.create_dm()
            await dm.send(
                f"You have been challenged by {ctx.message.author.mention} ({your_username})! Please consider contacting them in order to schedule your fight.")
        except:
            return
    else:
        errorEmbed = discord.Embed(
            title="An Error has Occurred",
            description="The problem could be one of the following:",
            color=16711680
        )
        errorEmbed.add_field(name="You are not on the leaderboard",
                             value="*Ask Bagel_Seedz or Possible to put you on it*", inline=True)
        errorEmbed.add_field(name="The person you challenged is not on the leaderboard",
                             value="*Challenge somebody on the leaderboard*", inline=True)
        errorEmbed.add_field(name="You have challenged the max of 5 people",
                             value="*Finish your other challenges before challenging more people*", inline=True)
        errorEmbed.add_field(name="The person you challenged has already been challenged the max of 3 times",
                             value="*Wait for them to finish their challenges before challenging them*", inline=True)
        errorEmbed.add_field(name="Another error has occurred", value="*Please contact Bagel_Seedz*", inline=True)
        await ctx.send(embed=errorEmbed)

@discordClient.command()
async def log(ctx, player1, player2, score1, score2):
    isAnOverseer = False
    for i in range(len(overseers)):
        if overseers[i] == ctx.message.author.id:
            isAnOverseer = True
    if not isAnOverseer:
        await ctx.send("This command is only for overseers, sorry")
        return

    await ctx.send("Loading log request...")

    SR1 = 0
    SR2 = 0
    participants = rankingsSheet.col_values(3)
    for i in range(len(participants)):
        if participants[i] == player1:
            SR1 = int(rankingsSheet.cell(i + 1, 4).value)
        elif participants[i] == player2:
            SR2 = int(rankingsSheet.cell(i + 1, 4).value)

    if SR1 == 0 or SR2 == 0:
        await ctx.send("One or more of the players inputted are not on the leaderboard.")
        return

    # Calculates the SR change for both players (Programmed by Possible_NenUser)
    SRValues = eloFormula(SR1, SR2, score1, score2)
    SR1 = SRValues[0]
    SR2 = SRValues[1]

    # Update Leaderboard
    for i in range(len(participants)):
        if participants[i] == player1:
            rankingsSheet.update_cell(i + 1, 4, SR1)
        elif participants[i] == player2:
            rankingsSheet.update_cell(i + 1, 4, SR2)
    try:
        rankingsSheet.sort((4, 'des'))
    except:
        print("failed to sort for some reason?")

    participants = rankingsSheet.col_values(3)
    newRank1 = 0
    newRank2 = 0
    for i in range(len(participants)):
        if participants[i] == player1:
            newRank1 = i
        elif participants[i] == player2:
            newRank2 = i

    # Update Personal Sheets
    personalSheet1 = sheetClient.open("BAPN Official Leaderboard").worksheet(player1)
    personalSheet2 = sheetClient.open("BAPN Official Leaderboard").worksheet(player2)

    freeRow1 = len(personalSheet1.col_values(1)) + 1
    freeRow2 = len(personalSheet2.col_values(1)) + 1

    stringScore1 = f'{score1}-{score2}'
    stringScore2 = f'{score2}-{score1}'

    rowToInsert1 = [player2, stringScore1, f'#{newRank1}', SR1]
    rowToInsert2 = [player1, stringScore2, f'#{newRank2}', SR2]
    personalSheet1.insert_row(rowToInsert1, freeRow1)
    personalSheet2.insert_row(rowToInsert2, freeRow2)

    personalSheet1.update_cell(1, 2, SR1)
    personalSheet2.update_cell(1, 2, SR2)

    # Update Challenge Logs
    challengers = challengeLogsSheet.col_values(1)
    defenders = challengeLogsSheet.col_values(2)
    for i in range(len(challengers)):
        if challengers[i] == player1 and defenders[i] == player2:
            challengeLogsSheet.delete_row(i + 1)
        elif challengers[i] == player2 and defenders[i] == player1:
            challengeLogsSheet.delete_row(i + 1)
    logEmbed = discord.Embed(
        title=":white_check_mark: The results of this fight have been logged",
        description="The leaderboard has been updated successfully.",
        color=25855
    )
    logEmbed.add_field(name=player1, value=f"Rank: {newRank1}\nSR: {SR1}", inline=True)
    logEmbed.add_field(name=player2, value=f"Rank: {newRank2}\nSR: {SR2}", inline=True)
    await ctx.send(embed=logEmbed)

@discordClient.command()
async def cancel(ctx, player1, player2):
    isAnOverseer = False
    for i in range(len(overseers)):
        if overseers[i] == ctx.message.author.id:
            isAnOverseer = True
    if not isAnOverseer:
        await ctx.send("This command is only for overseers, sorry")
        return

    challengers = challengeLogsSheet.col_values(1)
    defenders = challengeLogsSheet.col_values(2)
    rowDeleted = False

    for i in range(len(challengers)):
        cancelEmbed = discord.Embed(
            title=":white_check_mark: Challenge Cancelled.",
            color=16776960
        )
        if challengers[i] == player1 and defenders[i] == player2:
            challengeLogsSheet.delete_row(i + 1)
            rowDeleted = True
            await ctx.send(embed=cancelEmbed)
            break
        elif challengers[i] == player2 and defenders[i] == player1:
            challengeLogsSheet.delete_row(i + 1)
            rowDeleted = True
            await ctx.send(embed=cancelEmbed)
            break
    if rowDeleted == False:
        await ctx.send("Sorry, this challenge doesn't exist")

@discordClient.command()
async def calculate(ctx, player1, player2, score):
    SR1 = 0
    SR2 = 0
    participants = rankingsSheet.col_values(3)
    for i in range(len(participants)):
        if participants[i] == player1:
            SR1 = int(rankingsSheet.cell(i + 1, 4).value)
        elif participants[i] == player2:
            SR2 = int(rankingsSheet.cell(i + 1, 4).value)

    if SR1 == 0 or SR2 == 0:
        await ctx.send("One or more of the players inputted are not on the leaderboard.")
        return

    # Calculates the SR change for both players (Programmed by Possible_NenUser)
    score1 = score[0]
    score2 = score[2]
    SRValues = eloFormula(SR1, SR2, score1, score2)
    SR1 = SRValues[0]
    SR2 = SRValues[1]

    rank1 = 0
    rank2 = 0
    players = rankingsSheet.col_values(3)
    for i in range(len(players)):
        if players[i] == player1:
            rank1 = int(rankingsSheet.cell(i + 1, 2).value)
        if players[i] == player2:
            rank2 = int(rankingsSheet.cell(i + 1, 2).value)

    tp1 = None
    tp2 = None
    elos = rankingsSheet.col_values(4)
    elos.pop(0)
    elos.pop(rank1 - 1)
    elos.pop(rank2 - 1)

    for i in range(len(elos)):
        if SR1 > int(elos[i]) and not tp1:
            tp1 = i + 1
        if SR2 > int(elos[i]) and not tp2:
            tp2 = i + 1

    if SR1 < SR2:
        tp1 += 1
    elif SR1 > SR2:
        tp2 += 1

    calcEmbed = discord.Embed(
        title=f":pencil: Calculation of {player1} vs. {player2} | {score}",
        description="*Hypothetical Calculation*",
        color=255
    )
    calcEmbed.add_field(name=f"__{player1}__", value=f"Rank: {tp1}\nSR: {SR1}", inline=True)
    calcEmbed.add_field(name=f"__{player2}__", value=f"Rank: {tp2}\nSR: {SR2}", inline=True)

    await ctx.send(embed=calcEmbed)

@discordClient.command()
async def leaderboard(ctx):
    rankCol = rankingsSheet.col_values(2)
    playersCol = rankingsSheet.col_values(3)
    srCol = rankingsSheet.col_values(4)

    desc = ""
    for i in range(len(playersCol)):
        desc = f"{desc}\n**{rankCol[i]}.**   __{playersCol[i]}__  -  {srCol[i]}"

    lbEmbed = discord.Embed(
        title="BAPN OFFICIAL LEADERBOARD",
        description=desc,
        color=16766976
    )
    await ctx.send(embed=lbEmbed)

@discordClient.command()
async def challenges(ctx):
    challengerCol = challengeLogsSheet.col_values(1)
    challengedCol = challengeLogsSheet.col_values(2)
    datesCol = challengeLogsSheet.col_values(3)

    desc = ""
    for i in range(len(challengerCol)):
        desc = f"{desc}\n{challengerCol[i]} ⚔ {challengedCol[i]} **|** *{datesCol[i]}*"

    challengeEmbed = discord.Embed(
        title="CHALLENGE LOGS 🗡",
        description=desc,
        color=38655
    )
    await ctx.send(embed=challengeEmbed)

@discordClient.command()
async def addme(ctx):
    def __init__(self, client):
        self.client = client

    avk = None
    bio = None
    weapon = None
    startingSR = None
    proofURL = None
    verified = False

    dm = await ctx.message.author.create_dm()

    def messageCheck(m):
        return m.channel == dm and m.author.id == ctx.message.author.id

    def buttonCheck(b):
        return b.channel == dm

    await ctx.send("Check your dms!")

    roverUser = None
    try:
        roverR = requests.get(f"https://verify.eryn.io/api/user/{str(ctx.message.author.id)}")
        roverParse = json.loads(roverR.text)
        roverUser = roverParse["robloxUsername"]
        verified = True
    except:
        await dm.send("It looks like you haven't been verified with RoVer. What is your full roblox username?")
        tempRUser = await discordClient.wait_for("message", check=messageCheck, timeout=60.0)
        try:
            await roClient.get_user_by_username(tempRUser.content)
            roverUser = tempRUser.content
        except:
            await dm.send("That roblox user does not exist. Please say \".addme\" and try again.")
            return

    playerPic = None
    rUser = None
    try:
        rUserClient = await roClient.get_user_by_username(roverUser)
        rUser = rUserClient.name
        playerPicTuple = await roClient.thumbnails.get_user_avatar_thumbnails(users=[rUserClient.id], size="352x352")
        playerPic = playerPicTuple[0].image_url
    except:
        await dm.send("ERROR: Contact Bagel_Seedz or Possible_NenUser to add you to the leaderboard manually.")
        return

    competitors = rankingsSheet.col_values(3)
    for person in competitors:
        if person == rUser:
            await dm.send("You are already on the leaderboard.")
            return

    introEmbed = discord.Embed(
        title="BAPN OFFICIAL LEADERBOARD APPLICATION",
        description="This automated application process was created to allow new competitors to be augmented into the pro leaderboard easily. It is **required** that all compeitors familiarize themselves with the [Official 1v1 Rules](https://docs.google.com/document/d/1Y1fX6Cq-d5hKvxRsn2ShkVQiQ6tzY3Jzlv6iBrr3FtM/edit?usp=sharing) before applying. Click ``Continue`` if you are prepared to apply."
    )
    '''components = [
        Button(style=ButtonStyle.gray, label="Continue")
    ]'''
    continueButton = Button(style=discord.ButtonStyle.gray, label="Continue")
    continueView = View()
    continueView.add_item(continueButton)
    continueView.timeout = None

    msg = await dm.send(embed=introEmbed, view = continueView)

    async def onContinue(interaction):

        await interaction.message.edit(embed=introEmbed, view=None)

        #await discordClient.wait_for("button_click", check=buttonCheck)
        startingSR = 0
        avkEmbed = discord.Embed(
            title="Question 1",
            description="What is your AVK?",
            color=255
        )
        await dm.send(embed=avkEmbed)
        res = await discordClient.wait_for("message", check=messageCheck, timeout=60.0)
        try:
            res = float(res.content)
        except:
            await dm.send(
                "An error has occurred. The bot detected an invalid input. Please say ``.addme`` and try again with a valid AVK.")
            return
        if res < 50.0:
            await dm.send(
                "You do not have enough avk to rejoin the leaderboard. Please come back when you have ganed at least 50 avk.")
            return
        elif 50.0 <= res < 100.0:
            startingSR = 4700
        elif res >= 100.0:
            startingSR = 5000

        avk = res

        avkProofEmbed = discord.Embed(
            title="AVK PROOF",
            description="Please send IMAGE PROOF of your AVK INCLUDING the username on the in-game leaderboard at the top right corner. (Please attach an image and __not__ a link/url)",
            color=255
        )
        avkProofEmbed.set_image(
            url="https://cdn.discordapp.com/attachments/718291713738670151/933913994337607690/azlinsavk.png")


        skillIssueEmbed = discord.Embed(
            title="SKILL ISSUE",
            description="You did not submit a valid image. Please run .addme again",
            color=221
        )
        count = 0
        proofURL = None
        while proofURL == None and count < 3:
            try:
                proofURL = res.attachments[0].url
            except:
                await dm.send(embed=avkProofEmbed)
                res = await discordClient.wait_for("message", check=messageCheck, timeout=300.0)
                count+=1
        if proofURL == None:
            await dm.send(embed=skillIssueEmbed)
            return


        weaponEmbed = discord.Embed(
            title="Question 2",
            description="What weapon do you mainly use?",
            color=65280
        )
        '''components = [
            Button(style=ButtonStyle.red, label="Katana", custom_id="Katana"),
            Button(style=ButtonStyle.blue, label="Heavy", custom_id="Heavy")
        ]'''
        weapon = None
        katanaButton = Button(style=discord.ButtonStyle.red, label="Katana")
        heavyButton = Button(style=discord.ButtonStyle.blurple, label="Heavy")
        weaponView = View()
        weaponView.add_item(katanaButton)
        weaponView.add_item(heavyButton)
        weaponView.timeout = None

        msg = await dm.send(embed=weaponEmbed, view=weaponView)
        #res = await discordClient.wait_for("button_click", check=buttonCheck)
        bioEmbed = discord.Embed(
            title="Question 3",
            description="What do you want your bio to be?",
            color=0
        )
        async def katanaButtonFunction(interaction):
            await msg.edit(embed=weaponEmbed, view=None)
            await interaction.response.send_message(embed=bioEmbed)
            weapon = "Katana"
        async def heavyButtonFunction(interaction):
            await msg.edit(embed=weaponEmbed, view=None)
            await interaction.response.send_message(embed=bioEmbed)
            weapon = "Heavy"
        katanaButton.callback = katanaButtonFunction
        heavyButton.callback = heavyButtonFunction
        #await discordClient.wait_for("button_click", check=buttonCheck)



        #await dm.send(embed=bioEmbed)

        res = await discordClient.wait_for("message", check=messageCheck, timeout=300.0)

        bio = res.content
        confirmationPrompt = discord.Embed(
            title="BAPN LEADERBOARD APPLICATION",
            description="Is all of this information correct? All of this information will be sent to the Head Overseers for approval.",
            color=16776960
        )
        confirmationPrompt.add_field(name="__Username__", value=rUser, inline=True)
        confirmationPrompt.add_field(name="__RoVer Verified__", value=verified, inline=True)
        confirmationPrompt.add_field(name="__AVK__", value=f"{avk} (Your starting Skill Rating will be {startingSR})",
                                     inline=False)
        confirmationPrompt.add_field(name="__Bio__", value=bio, inline=True)
        confirmationPrompt.add_field(name="__Weapon__", value=weapon, inline=True)
        confirmationPrompt.set_image(url=proofURL)
        confirmationPrompt.set_thumbnail(url=str(playerPic))
        confirmationPrompt.set_author(name=str(ctx.message.author), icon_url=ctx.message.author.avatar.url)
        '''components = [
            Button(style=ButtonStyle.green, label="Send", custom_id="yes"),
            Button(style=ButtonStyle.red, label="Dont Send", custom_id="no")
        ]'''
        yesno = None
        yesButton = Button(style=discord.ButtonStyle.green, label="Send")
        noButton = Button(style=discord.ButtonStyle.red, label="Dont Send")
        choiceView = View()
        choiceView.add_item(yesButton)
        choiceView.add_item(noButton)
        choiceView.timeout = None

        msg = await dm.send(embed=confirmationPrompt, view=choiceView)
        #res = await discordClient.wait_for("button_click", check=buttonCheck)
        async def noButtonFunction(interaction):
            weapon = "no"
            await res.respond(content="Your response has not been sent.")

        noButton.callback = noButtonFunction
        async def yesButtonFunction(interaction):
            weapon = "yes"
            #await res.respond(content="Your response has been sent.")
            await interaction.message.edit(embed=weaponEmbed, view=None)
            await interaction.message.edit(embed=confirmationPrompt, view=None)
            '''if res.component.custom_id == "yes":
                await res.respond(content="Your response has been sent.")
            elif res.component.custom_id == "no":
                await res.respond(content="Your response has not been sent.")
                return'''

            applicationChannel = discordClient.get_channel(934093336816545902)

            def modChannelCheck(b):
                return b.channel.id == applicationChannel.id

            '''newComponents = [
                Button(style=ButtonStyle.green, label="Accept", custom_id="ye"),
                Button(style=ButtonStyle.red, label="Deny", custom_id="nah")
            ]'''

            acceptButton = Button(style=discord.ButtonStyle.green, label="Accept")
            denyButton = Button(style=discord.ButtonStyle.red, label="Deny")
            accdenyView = View()
            accdenyView.add_item(acceptButton)
            accdenyView.add_item(denyButton)
            accdenyView.timeout = None

            msg = await applicationChannel.send(embed=confirmationPrompt, view=accdenyView)

            async def denyButtonFunction(interaction):
                await msg.edit(content=f"``Denied by {str(res.author)}`` ", embed=confirmationPrompt, view=None)
                await dm.send("Sorry, your request has been denied. You have not been added to the leaderboard.")

            denyButton.callback = denyButtonFunction

            def acceptButtonFunctionJank(interaction, startingSR):
                worksheets = spreadsheet.worksheets()
                alreadyHasSheet = False
                for worksheet in worksheets:
                    if worksheet.title == rUser:
                        alreadyHasSheet = True

                if not alreadyHasSheet:
                    newWorksheet = None
                    if weapon == "Katana":
                        newWorksheet = spreadsheet.duplicate_sheet(1511070903, insert_sheet_index=0,
                                                                   new_sheet_name=rUser)
                    elif weapon == "Heavy":
                        newWorksheet = spreadsheet.duplicate_sheet(2115675779, insert_sheet_index=0,
                                                                   new_sheet_name=rUser)
                    worksheets = spreadsheet.worksheets()
                    sheetsToSort = []
                    for worksheet in worksheets:
                        sheetsToSort.append(worksheet.title)
                    sheetsToSort.sort()
                    newSheets = []
                    for i in range(len(sheetsToSort)):
                        for worksheet in worksheets:
                            if worksheet.title == "Rankings" or worksheet.title == "Challenge Logs" or worksheet.title == "EXAMPLE" or worksheet.title == "Katana Template" or worksheet.title == "Heavy Template":
                                continue
                            if sheetsToSort[i] == worksheet.title:
                                newSheets.append(worksheet)
                                break
                    newSheets.insert(0, rankingsSheet)
                    newSheets.insert(1, challengeLogsSheet)
                    newSheets.insert(2, exampleSheet)
                    newSheets.insert(3, katanaTemplate)
                    newSheets.insert(4, heavyTemplate)
                    spreadsheet.reorder_worksheets(newSheets)

                    newWorksheet.update_acell('A1', f'=HYPERLINK("#gid={newWorksheet.id}","{rUser}")')
                    newWorksheet.update_cell(1, 2, startingSR)
                    newWorksheet.update_cell(3, 2, bio)
                    newWorksheet.update_cell(3, 8, str(ctx.message.author.id))
                    newWorksheet.update_cell(3, 1, f'=image("{str(playerPic)}")')
                else:
                    sheet = spreadsheet.worksheet(rUser)
                    oldSR = int(sheet.cell(1, 2).value)
                    startingSR = oldSR

                freeRow = len(rankingsSheet.col_values(3)) + 1
                rankingsSheet.update_cell(freeRow, 3, f"={rUser}!A1")
                rankingsSheet.update_cell(freeRow, 4, str(startingSR))
                rankingsSheet.sort((4, 'des'))

            async def acceptButtonFunction(interaction):
                acceptButtonFunctionJank(interaction, startingSR)
                await msg.edit(content=f"``Accepted by {str(res.author)}`` ", embed=confirmationPrompt, view=None)
                await dm.send("You have been accepted into the pro leaderboard.")

            acceptButton.callback = acceptButtonFunction

            '''res = await discordClient.wait_for("button_click", check=modChannelCheck)
            if res.component.custom_id == "ye":
                await msg.edit(f"``Accepted by {str(res.author)}`` ", embed=confirmationPrompt, components=[])
                await dm.send("You have been accepted into the pro leaderboard.")
            elif res.component.custom_id == "nah":
                await msg.edit(f"``Denied by {str(res.author)}``", embed=confirmationPrompt, components=[])
                await dm.send("Sorry, your request has been denied. You have not been added to the leaderboard.")
                return'''

        yesButton.callback = yesButtonFunction






    continueButton.callback = onContinue
         
         
@discordClient.command()
async def SeasonEloSoftReset(ctx, season_number):
    user = ctx.message.author
    if not (user.id == 344872876199116802 or user.id == 819989575215874148):  # If the author is Poss or Dave
        await ctx.channel.send("Sorry, this command can only be run by Head Overseers.")
        return

    try:
        int(season_number)
    except:
        await ctx.channel.send("The Season Number must be an integer.")
        return
    
    msg = await ctx.channel.send("``Soft Reset Loading ...``")
    
    playersCol = rankingsSheet.col_values(3)
    for i in range(len(playersCol)):
        try:
            currentSR = int(rankingsSheet.cell(i+1, 4).value)
            newSR = round((currentSR + 5000)/2)
            rankingsSheet.update_cell(i+1, 4, str(newSR))

            personalSheet = sheetClient.open("BAPN Official Leaderboard").worksheet(playersCol[i])
            personalSheet.update_cell(1, 2, str(newSR))

            def getEnding(number):
                mod10 = int(number) % 10
                if number == 11 or number == 12 or number == 13: return "th"
                if mod10 == 1: return "st"
                if mod10 == 2: return "nd"
                if mod10 == 3: return "rd"
                return "th"
            personalSheet.update_cell(3, 6, f"{personalSheet.cell(3, 6).value}\nSeason {season_number} - {i}{getEnding(i)} place")

            firstCol = personalSheet.col_values(1)
            rowValue = len(firstCol)+1
            personalSheet.merge_cells(f"A{rowValue}:C{rowValue}")
            personalSheet.update_cell(rowValue, 1, f"SEASON {season_number}")
            personalSheet.update_cell(rowValue, 4, str(newSR))
        except:
            continue

    await msg.edit(content="``SOFT ELO RESET COMPLETE``")



    
#keep_alive()
TOKEN = "ODY3MjIwNDgwMTQxMTY0NTY1.GJCgWD.iYLIk6QB0c9YbXC3CLGSxUxRE_BhtriiA3P_gU"
discordClient.run(TOKEN)
#keep_alive()
TOKEN = "YOUR DISCORD BOT TOKEN"
discordClient.run(TOKEN)
