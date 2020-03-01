import json

async def sendPlayUsage(channel):
    await channel.send('Usage: `$play [mentions] thinkingDuration* gameDuration*`\n* - optional')

def getWordList(index):
    file = open('categories.json', 'r')
    jsonString = file.read()
    file.close()
    cats = json.loads(jsonString)
    tupleList = list(cats.items())
    return tupleList[index]


async def sendWordDM(word, user, chameleon):
    if chameleon:
        await messageUser('You are the chameleon! Try to blend in!', user)
    else:
        await messageUser('The secret word is: {}\nGive a word related to the secret word. Try not to give it to the chameleon!'.format(word), user)

async def makeVotingMessage(members, numberEmojis):
    returnString = 'Cast your votes now!\n\n'
    for i in range(0, len(members)):
        returnString += numberEmojis[i+1] + ' : ' + members[i].display_name + '\n'
    return returnString

async def addVotingReactions(membersNum, numberEmojis, message):
    for i in range(0, membersNum):
        await message.add_reaction(numberEmojis[i+1])

async def getResult(vmessage, numberEmojis):
    validEmojis = list(numberEmojis.values())
    counts = {}
    message = await vmessage.channel.fetch_message(vmessage.id)
    for reaction in message.reactions:
        if reaction.emoji not in validEmojis:
            continue
        counts[reaction.emoji] = reaction.count
    max = float('-inf')
    maxEmoji = None
    for tuple in counts.items():
        if tuple[1] > max:
            maxEmoji, max = tuple
    maxCount = 0
    for tuple in counts.items():
        if tuple[1] == max:
            maxCount += 1
    if maxCount > 1:
        return -1
    else:
        for i in range(0, len(validEmojis)):
            if maxEmoji == validEmojis[i]:
                return i

# async def


async def messageUser(message, user):
    dm = user.dm_channel
    if dm is None:
        dm = await user.create_dm()
    return await dm.send(message)
