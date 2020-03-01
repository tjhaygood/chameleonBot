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

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$play'):
        thinkingDuration = 45
        gameDuration = 180
        hideCard = False
        # parse input
        mentions = message.mentions
        if len(mentions) == 0:
            await sendPlayUsage(message.channel)
            return
        if len(mentions) < 3:
            await message.channel.send('You must play with at least 3 people!')
            return
        if len(mentions) > 10:
            await message.channel.send('This game can only be played with up to 10 players, sorry!')
            return
        if len(mentions) > 6:
            hideCard = True
        messageContentList = message.content.split()
        length = len(messageContentList)
        if length > (len(mentions) + 1):
            if length == len(mentions) + 2:
                try:
                    thinkingDuration = int(messageContentList[length-1])
                except:
                    pass
            else:
                try:
                    thinkingDuration = int(messageContentList[len(mentions) + 1])
                    gameDuration = int(messageContentList[len(mentions) + 2])
                except:
                    pass
        # get words
        category, words = getWordList(0)
        # print word table
        # DM players listed
        word = random.choice(words)
        chameleon = random.randint(0, len(mentions))
        for i in range(0, len(mentions)):
            if i == chameleon:
                await sendWordDM('', mentions[i], True)
            else:
                await sendWordDM(word, mentions[i], False)
        # wait for people to come up with words
        await asyncio.sleep(thinkingDuration)
        # hide card if > 8
        await message.channel.send('Say your words!')
        await asyncio.sleep(3 * len(mentions))
        # wait for game time - 30 seconds
        gameTimerMsg = await message.channel.send('Begin discussion!')
        await asyncio.sleep(gameDuration - 30)
        # display voting message, add reactions
        votingMessageString = await makeVotingMessage(message.mentions, numberEmojis)
        votingMessage = await message.channel.send(votingMessageString)
        await addVotingReactions(len(message.mentions), numberEmojis, votingMessage)
        # collect votes
        await asyncio.sleep(30)
        result = await getResult(votingMessage, numberEmojis)
        if result == -1:
            await message.channel.send('Voting resulted in a tie! Chameleon wins!')
            return
        else:
            chameleonName = mentions[chameleon].display_name
            # if chameleon not voted, chameleon wins
            if result != chameleon:
                votedFor = mentions[result].display_name
                await message.channel.send('You voted for {}, who was *not* the chameleon. {} wins as the chameleon!'
                                           .format(votedFor, chameleonName))
                return
            else:
                # if chameleon voted, give 30 secs to guess word
                await message.channel.send('{0} has been ousted as the chameleon! {0}, you have 30 seconds to guess the word to win!'
                                           .format(chameleonName))
                def check(m):
                    return m.author == mentions[chameleon] and m.channel == message.channel

                answerMsg = await client.wait_for('message', check=check, timeout=30)
                if answerMsg.content.lower() == word.lower():
                    await message.channel.send('{0} has guessed the word correctly! {0} wins as the chameleon!'
                                               .format(chameleonName))
                else:
                    await message.channel.send(
                        '{0} has failed to guess the word correctly! {0} loses!'
                        .format(chameleonName))
    if message.content.startswith('!num'):
        number = int(message.content.split()[1])
        await message.channel.send(numberEmojis[number])

    if message.content.startswith('!vmsg'):
        votingMessageString = await makeVotingMessage(message.mentions, numberEmojis)
        votingMessage = await message.channel.send(votingMessageString)
        await addVotingReactions(len(message.mentions), numberEmojis, votingMessage)
        await asyncio.sleep(5)
        result = await getResult(votingMessage, numberEmojis)
        if result == -1:
            await message.channel.send('Voting resulted in a tie! Chameleon wins!')
        else:
            await message.channel.send('You voted for {}!'.format(message.mentions[result].display_name))
            if result != 2:
                await message.channel.send('You voted for')

    if message.content.startswith('!table'):
        category, words = getWordList(0)



@client.event
async def on_raw_reaction_add(payload):
    channel = await client.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    if payload.user_id == 230571124478574592 and payload.emoji.name == '❌' and message.author == client.user:
        await message.delete()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))



client.run(key)


