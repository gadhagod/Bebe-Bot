import discord
from rockset import Client
from requests import get
from os import getenv

client = discord.Client()

rs = Client(
        api_key=getenv('ROCKSET_SECRET'),
        api_server='api.rs2.usw2.rockset.com'
    )

users = rs.Collection.retrieve('baby_users')
commands = rs.Collection.retrieve('baby_commands')

@client.event
async def on_ready():
    print('logged in as {}'.format(client.user))
    await client.change_presence(
        activity=discord.Game(name='!help')
    )

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content.lower().replace('!', '')
    command_docs = []

    if msg == 'help':
        await message.channel.send(
            get(
                'http://babyapi.herokuapp.com/v1', 
                params={
                    'text': 'I\'m Bebé Bot, a Baby-to-English translator. Use me with `!baby {phrase}` and I\'ll convert it to Baby.'
                }
            ).json()['translated']
        )
        command_docs.append({
            'command': 'help',
            'user_name': message.author.name,
            'user_id':  str(message.author.id)
        })

    if msg.startswith('baby'):
        res =  get(
            'http://babyapi.herokuapp.com/v1', 
            params={
                'text': message.content.replace('!baby ', '')
            }
        ).json()['translated']
        
        await message.channel.send(res)
        command_docs.append({
            'command': 'baby',
            'response': res,
            'user_name': message.author.name,
            'user_id':  str(message.author.id)
        })
        
    if command_docs != []:
        commands.add_docs(command_docs)

    users.add_docs(
        [{
            '_id': str(message.author.id),
            'name': message.author.name,
        }]
    )

client.run(getenv('BABY_TOKEN'))