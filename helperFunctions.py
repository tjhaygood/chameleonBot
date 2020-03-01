import json
import random

async def sendPlayUsage(channel):
    await channel.send('Usage: `$play [mentions] thinkingDuration* gameDuration*`\n* - optional')

def getWordList(index):
    file = open('categories.json', 'r')
    jsonString = file.read()
    file.close()
    cats = json.loads(jsonString)
    tupleList = list(cats.items())
    return tupleList[index]

def getNumCats():
    file = open('categories.json', 'r')
    jsonString = file.read()
    file.close()
    cats = json.loads(jsonString)
    keyList = list(cats.keys())
    return len(keyList)

def newCardQueue():
    numCats = getNumCats()
    indexList = list(range(numCats))
    random.shuffle(indexList)
    return indexList


async def sendWordDM(word, user, chameleon):
    if chameleon:
        await messageUser('You are the chameleon! Try to blend in!', user)
    else:
        await messageUser('The secret word is: **{}**\nGive a word related to the secret word. Try not to give it to the chameleon!'.format(word), user)

async def makeVotingMessage(members, numberEmojis):
    returnString = 'Cast your votes using `$vote *number*` now!\n\n'
    for i in range(0, len(members)):
        returnString += numberEmojis[i+1] + ' : ' + members[i].display_name + '\n'
    return returnString

async def addVotingReactions(membersNum, numberEmojis, message):
    for i in range(0, membersNum):
        await message.add_reaction(numberEmojis[i+1])

async def getReactResults(vmessage, numberEmojis):
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

async def getMsgResults(results, members):
    counts = {}
    memberIds = [x.id for x in members]
    for tuple in results:
        memberId = tuple[0]
        vote = tuple[1]
        if memberId in memberIds and vote in range(1, len(members)+1):
            if vote in counts:
                counts[vote] += 1
            else:
                counts[vote] = 1
    max = float('-inf')
    maxIndex = None
    for tuple in counts.items():
        if tuple[1] > max:
            maxIndex, max = tuple
    maxCount = 0
    for tuple in counts.items():
        if tuple[1] == max:
            maxCount += 1
    if maxCount > 1 or maxIndex is None:
        return -1
    else:
        return maxIndex-1


def buildWordsCard(category, list):
    returnString = '**' + category + '** \n \n'
    returnString += '```'
    maxLength = 0
    for i in list:
        curLength = len(str(i))
        if curLength > maxLength:
            maxLength = curLength
    line = '|'
    space = ' '
    dash = '-'
    block = (dash * (maxLength + 3)) + line
    numColumns = 4
    returnString += line + block*numColumns + '\n'
    i=0
    while i < len(list):
        for j in range(0, numColumns):
            # # printing last column with a blank space
            # if j == numColumns-1 and i > numColumns:
            #     returnString += line + space * (maxLength + 3)
            # else:
            returnString += line + space
            returnString += str(list[i]) + space * ((maxLength + 2) - len(str(list[i])))
            i += 1
        returnString += line + '\n'
        returnString += line + (block * numColumns) + '\n'
    returnString += '```'
    return returnString


async def messageUser(message, user):
    dm = user.dm_channel
    if dm is None:
        dm = await user.create_dm()
    return await dm.send(message)
