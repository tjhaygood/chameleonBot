import discord
from discord.utils import get
from helperFunctions import *
from botToken import key
import asyncio
import datetime
from datetime import timedelta
import threading
import random


client = discord.Client()

numberEmojis = {
    1 : '1️⃣',
    2 : '2️⃣',
    3 : '3️⃣',
    4 : '4️⃣',
    5 : '5️⃣',
    6 : '6️⃣',
    7 : '7️⃣',
    8 : '8️⃣',
    9 : '9️⃣',
    10 : '🔟'
}

guildCardQueues = {}

guildSkips = {}

guildGameInProg = {}

guildVotes = {}

guildPlayers = {}

guildVotingStage = {}

lastPlayers = {}

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    global guildSkips
    global guildGameInProg
    global guildVotes
    global guildPlayers
    global guildVotingStage
    global lastPlayers
    if message.content.startswith('$play') or message.content.startswith('$playagain'):
        guildId = message.guild.id
        if guildId in guildGameInProg:
            if guildGameInProg[guildId]:
                await message.channel.send('Game is already in progress!')
                return
        guildSkips[guildId] = {'skip': False, 'stop': False}
        guildVotes[guildId] = {}
        thinkingDuration = 45
        gameDuration = 180
        hideCard = False
        # parse input
        mentions = message.mentions
        if message.content.startswith('$playagain'):
            if guildId not in lastPlayers:
                await message.channel.send('I don\'t know who played last! Please use `$play`.')
                return
            else:
                mentions = lastPlayers[guildId]
        if len(mentions) == 0:
            await sendPlayUsage(message.channel)
            return
        if len(mentions) < 3:
            await message.channel.send('You must play with at least 3 people!')
            return
        if len(mentions) > 10:
            await message.channel.send('This game can only be played with up to 10 players, sorry!')
            return
        if message.author not in mentions:
            await message.channel.send('You cannot start a game that you are not a part of!')
            return
        for member in mentions:
            if member.bot:
                await message.channel.send('You cannot play this game with bots!')
                return
        if len(mentions) > 6:
            hideCard = True
        guildGameInProg[guildId] = True
        lastPlayers[guildId] = mentions
        guildVotingStage[guildId] = False
        guildPlayers[guildId] = [m.id for m in mentions]
        messageContentList = message.content.split()
        length = len(messageContentList)
        if length > (len(mentions) + 1):
            if length == len(mentions) + 2:
                try:
                    argOne = int(messageContentList[length-1])
                    thinkingDuration = argOne if argOne < 60 else thinkingDuration
                except:
                    pass
            else:
                try:
                    argOne = int(messageContentList[len(mentions) + 1])
                    argTwo = int(messageContentList[len(mentions) + 2])
                    thinkingDuration = argOne if argOne < 60 else thinkingDuration
                    gameDuration = argTwo * 60 if argTwo >= 1 and argTwo <= 5 else gameDuration
                except:
                    pass
        # get words
        global guildCardQueues
        if guildId not in guildCardQueues or len(guildCardQueues[guildId]) == 0:
            guildCardQueues[guildId] = newCardQueue()
        queue = guildCardQueues[guildId]
        category, words = getWordList(queue.pop(0))
        # print word table
        cardText = buildWordsCard(category, words)
        cardMsg = await message.channel.send(cardText)
        # DM players listed
        word = random.choice(words)
        chameleon = random.randint(0, len(mentions)-1)
        for i in range(0, len(mentions)):
            if i == chameleon:
                await sendWordDM('', mentions[i], True)
            else:
                await sendWordDM(word, mentions[i], False)
        # wait for people to come up with words
        i = 0
        while i < thinkingDuration and not guildSkips[guildId]['skip']:
            await asyncio.sleep(1)
            if guildSkips[guildId]['stop']:
                stopGame(guildId)
                await message.channel.send('Game terminated.')
                return
            i += 1
        guildSkips[guildId]['skip'] = False
        if guildSkips[guildId]['stop']:
            stopGame(guildId)
            await message.channel.send('Game terminated.')
            return
        # hide card if > 6
        if hideCard:
            await cardMsg.edit(content='**{}**\n\n*Card is hidden since we have more than 6 players.*')
        await message.channel.send('Say your words!')
        await asyncio.sleep(3 * len(mentions))
        # wait for game time - 30 seconds
        gameTimerMsg = await message.channel.send('Begin discussion!')
        i = 0
        while i < gameDuration - 30 and not guildSkips[guildId]['skip']:
            await asyncio.sleep(1)
            if guildSkips[guildId]['stop']:
                stopGame(guildId)
                await message.channel.send('Game terminated.')
                return
            i += 1
        guildSkips[guildId]['skip'] = False
        if guildSkips[guildId]['stop']:
            stopGame(guildId)
            await message.channel.send('Game terminated.')
            return
        # display voting message, add reactions
        guildVotingStage[guildId] = True
        votingMessageString = await makeVotingMessage(message.mentions, numberEmojis)
        votingMessage = await message.channel.send(votingMessageString)
        # await addVotingReactions(len(message.mentions), numberEmojis, votingMessage)
        # collect votes
        i = 0
        while i < 30 and not guildSkips[guildId]['skip'] and not len(list(guildVotes[guildId].keys())) == len(mentions):
            await asyncio.sleep(1)
            i += 1
        # result = await getResult(votingMessage, numberEmojis)
        result = await getMsgResults(guildVotes[guildId].items(), mentions)
        if result == -1:
            await message.channel.send('Voting resulted in a tie! Chameleon wins!')
            stopGame(guildId)
            return
        else:
            chameleonName = mentions[chameleon].display_name
            # if chameleon not voted, chameleon wins
            if result != chameleon:
                votedFor = mentions[result].display_name
                await message.channel.send('You voted for {}, who was *not* the chameleon. {} wins as the chameleon!'
                                           .format(votedFor, chameleonName))
                stopGame(guildId)
                return
            else:
                # if chameleon voted, give 30 secs to guess word
                await message.channel.send('{0} has been ousted as the chameleon! {0}, you have 30 seconds to guess the word to win!'
                                           .format(chameleonName))
                if hideCard:
                    await cardMsg.edit(content=cardText)
                def check(m):
                    return m.author == mentions[chameleon] and m.channel == message.channel

                answerMsg = await client.wait_for('message', check=check, timeout=30)
                if answerMsg.content.lower().strip() == word.lower():
                    await message.channel.send('{0} has guessed the word correctly! {0} wins as the chameleon!'
                                               .format(chameleonName))
                else:
                    await message.channel.send(
                        '{0} has failed to guess the word correctly! The word was {1}! {0} loses!'
                        .format(chameleonName, word))
            stopGame(guildId)

    if message.content.startswith('$skip'):
        guildSkips[message.guild.id]['skip'] = True

    if message.content.startswith('$stop'):
        guildSkips[message.guild.id]['stop'] = True

    if message.content.startswith('$vote'):
        guildId = message.guild.id
        if message.author.id not in guildPlayers[guildId]:
            await message.channel.send('You\'re not in a game!')
            return
        if guildId in guildGameInProg:
            if not guildGameInProg[guildId]:
                await message.channel.send('There is no game in progress!')
                return
            elif guildGameInProg[guildId]:
                if guildVotingStage[guildId] == False:
                    await message.channel.send('Voting has not begun!')
                    return
        contentSplit = message.content.split()
        if len(contentSplit) != 2:
            await message.channel.send('Usage: `$vote *player number*')
            return
        # try:
        if guildId not in guildVotes:
            guildVotes[guildId] = {}
        try:
            guildVotes[guildId][message.author.id] = int(contentSplit[1])
        except Exception as e:
            print(e)
            await message.channel.send('Your vote must be a number!')

    if message.content.startswith('!num'):
        number = int(message.content.split()[1])
        await message.channel.send(numberEmojis[number])

    if message.content.startswith('!vmsg'):
        guildId = message.guild.id
        votingMessageString = await makeVotingMessage(message.mentions, numberEmojis)
        votingMessage = await message.channel.send(votingMessageString)
        guildGameInProg[guildId] = True
        # await addVotingReactions(len(message.mentions), numberEmojis, votingMessage)
        await asyncio.sleep(5)
        result = await getMsgResults(guildVotes[guildId].items(), message.mentions)
        if result == -1:
            await message.channel.send('Voting resulted in a tie! Chameleon wins!')
        else:
            await message.channel.send('You voted for {}!'.format(message.mentions[result].display_name))
        guildGameInProg[guildId] = False
        guildPlayers[guildId] = []

    if message.content.startswith('!table'):
        category, words = getWordList(0)
        await message.channel.send(buildWordsCard(category, words))

def stopGame(guildId):
    global guildGameInProg
    global guildPlayers
    global guildVotingStage
    global guildVotes
    guildGameInProg[guildId] = False
    guildPlayers[guildId] = []
    guildVotingStage[guildId] = False
    guildVotes[guildId] = {}


@client.event
async def on_raw_reaction_add(payload):
    channel = await client.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    if payload.user_id == 230571124478574592 and payload.emoji.name == '❌' and message.author == client.user:
        await message.delete()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    global guildCardQueues
    for guild in client.guilds:
        guildCardQueues[guild.id] = newCardQueue()



client.run(key)


