#anonbot

import discord
import asyncio
import re
import configparser
import sys

configname = 'anonbot.ini'
if len(sys.argv) > 1:
    configname = sys.argv[1]

import os
if not os.path.exists(configname):
    print("Generating default config...")
    config = configparser.ConfigParser()
    config['default'] = {'server': 'Server Name Here', 'bottoken': 'Bot Token Here'}
    with open(configname, 'w') as configfile:
        config.write(configfile)
        
    print("Config file {} generated. Please edit it to add appropriate values before use.".format(configname))
    
    sys.exit()

config = configparser.ConfigParser()
config.read(configname)
token = config['default']['bottoken']
server_name = config['default']['server']    

def get_phrase_prefixes(name):
    na = name.split(' ')
    for i in range(len(na), 0, -1):
        yield ' '.join(na[0:i])

#server_name = 'bored@butler'

mentions_regex = '@[\w #()]*'
mentions_re = re.compile(mentions_regex)

client = discord.Client()
server = None

@client.event
async def on_ready():
    global server
    print('Logged in as')
    for s in client.servers:
        print("Connected to", s.name)

    
    server = discord.utils.find(lambda s: s.name == server_name, client.servers)
    if server is None:
        print("WARNING: not connected to", server_name)
    else:
        print("*** Anonbot for {} ***".format(server.name))
        print("Available channels:")
        for channel in server.channels:
            print(channel.name)
            
        for member in server.members:
            try:
                print(member.name)
            except UnicodeEncodeError:
                print("WeirdName")
        
        print("Default channel is {}".format(server.default_channel.name))
        print(server.members)
        print("------")
        
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    global server
    if message.channel.is_private and message.author.id != client.user.id:
        print("anonbot is handling a message...")
        channel = server.default_channel
        cname = channel.name
        content = message.content
        
        match = mentions_re.search(message.content)
        startpos = 0
        while match is not None:
            mention_str = content[match.start() + startpos + 1:match.end()]
            member = None
            for name in get_phrase_prefixes(mention_str):
                member = discord.utils.find(lambda m: m.name == name or m.nick == name, server.members)
                if member is not None:
                    content = content[:startpos + match.start()] + member.mention + content[startpos + match.start() + len(name) + 1:]
                    startpos += match.start() + len(member.mention)
                    break
            
            if member is None:
                startpos += match.end()
            
            match = mentions_re.search(message.content[startpos:])
                
        print(content)
        
       
        content_arr = content.split(' ')
        
        '''
        for i in range(len(content_arr)):
            if mentions_re.match(content_arr[i]) is not None:
                mention = content_arr[i][1:]
                member = discord.utils.find(lambda m: m.name == mention or m.nick == mention, server.members)
                
                if member is not None:
                    content_arr[i] = member.mention
        '''
        if message.content.lstrip(' ').startswith('#'):
            
            if len(content_arr) == 0:
                return
            
            cname = content_arr[0].lstrip('#')
            channel = discord.utils.find(lambda c: c.name == cname, server.channels)
            if channel is None:
                await client.send_message(message.channel, "Don't know channel {} in {}.".format(cname, server_name))
                return
        
            content = ' '.join(content_arr[1:])
        else:
            content = ' '.join(content_arr)
            
        await client.send_message(channel, content)
        await client.send_message(message.channel, "Your message has been sent to #{}.".format(cname))
        print("anonbot is done")

client.run(token)
