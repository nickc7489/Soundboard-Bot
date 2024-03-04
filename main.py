import discord
import random
import os
import youtube_dl
import requests
import emojis

ydl_opts = {
    "format":
    "bestaudio/best",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
    }],
}

serverDict = {}

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)


def is__connected(guildd):
    for vc in client.voice_clients:
        if vc.guild == guildd and vc.is_connected():
            return True
    return False


def find_voice(message):
    for vc in client.voice_clients:
        if vc.guild == message.guild:
            return vc


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.content.startswith("--soundboard"):
        if message.guild not in serverDict.keys() or len(
                serverDict[message.guild].keys()) == 0:
            await message.channel.send(
                '**You need to add an emoji sound button!**')
            return
        await message.channel.send(
            '**Soundboard -- React to this message to play sounds**')
        mssg = await message.channel.fetch_message(
            message.channel.last_message_id)
        for emoji in serverDict[message.guild].keys():
            try:
                await mssg.add_reaction(emoji)
            except:
                pass

    if message.content.startswith("--join"):
        channel = message.author.voice.channel
        await channel.connect()

    if message.content.startswith("--leave"):
        for vc in client.voice_clients:
            if vc.guild == message.guild:
                await vc.disconnect()

    if message.content.startswith("--pause"):
        for vc in client.voice_clients:
            if vc.guild == message.guild:
                if vc.is_playing():
                    vc.pause()
                else:
                    await message.channel.send('**No sound is playing!**')

    if message.content.startswith("--addsound"):
        msg = message.content.split(' ')
        print(message.content)
        print(msg)
        if len(msg) < 3:
            await message.channel.send('**Command too short!**')
            return
        if len(msg) > 3:
            await message.channel.send('**Command too long!**')
            return
        if msg[0] != "--addsound":
            await message.channel.send('**Command misspelled!**')
            return
        if len(emojis.get(emojis.encode(msg[1]))) == 0:
            await message.channel.send('**Invalid emoji!**')
            return
        if len(emojis.get(emojis.encode(msg[1]))) > 1:
            await message.channel.send('**Multiple emojis!**')
            return
        if msg[2].startswith('https://www.youtube.com/watch?v=') == False:
            await message.channel.send('**Youtube link invalid!**')
            return
        req = requests.get(msg[2])
        if "Video unavailable" in req.text:
            await message.channel.send('**Youtube link invalid!**')
            return
        if message.guild not in serverDict.keys():
            serverDict[message.guild] = {}
        serverDict.get(message.guild)[emojis.encode(msg[1])] = msg[2]
        url = msg[2]
        for file in os.listdir("./"):
            if file == str(message.guild.id) + emojis.decode(msg[1]) + '.mp3':
                os.remove(file)
                break
        await message.channel.send('**Downloading sound...**')
        toEdit = await message.channel.fetch_message(
            message.channel.last_message_id)
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        await toEdit.edit(content='**Download complete!**')
        os.rename(
            os.listdir("./")[-1],
            str(message.guild.id) + emojis.decode(msg[1]) + '.mp3')
        print(os.listdir("./")[-1])

    if message.content.startswith("--removesound") and len(
            message.content.split(' ')) == 2 and len(
                emojis.get(emojis.encode(message.content.split(' ')[1]))) == 1:
        serverDict[message.guild].pop(
            emojis.encode(message.content.split(' ')[1]), None)
        await message.channel.send('**Sound removed!**')

    if message.content.startswith("--soundslist"):
        if message.guild not in serverDict.keys():
            serverDict[message.guild] = {}
        if len(serverDict[message.guild].keys()) == 0:
            await message.channel.send(
                "**No sounds added yet, use the '--addsound' command to add a sound!**"
            )
        else:
            for emoji in serverDict[message.guild].keys():
                await message.channel.send(emoji + ' : ' + str(serverDict[message.guild][emoji]))

    if message.content.startswith("--test"):
        for member in message.guild.members:
            print(member.name)


@client.event
async def on_reaction_add(reaction, user):

    if reaction.message.content.startswith(
            "**Soundboard -- React to this message to play sounds**"
    ) and reaction.message.author == client.user and user.name != 'Soundboard Bot' and reaction.emoji in serverDict[
            reaction.message.guild].keys():
        channel = user.voice.channel
        if is__connected(reaction.message.guild) == False:
            await channel.connect()
        for vc in client.voice_clients:
            if vc.guild == reaction.message.guild:
                try:
                    vc.play(
                        discord.FFmpegPCMAudio('./' +str(reaction.message.guild.id) +emojis.decode(reaction.emoji) +'.mp3'))
                except discord.errors.ClientException:
                    await reaction.message.channel.send(
                        '**Sound already playing!**')

client.run(os.getenv('TOKEN'))
