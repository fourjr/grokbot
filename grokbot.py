'''
MIT License
Copyright (c) 2017 Grok
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


import discord
from discord.ext import commands
from ext.context import CustomContext
from ext.config import ConfigDatabase
from collections import defaultdict
import asyncio
import aiohttp
import datetime
#import psutil
import time
import json
import sys
import os
import re
import sqlite3
import traceback
import textwrap


class GrokBot(commands.Bot):
    '''
    GrokBot!
    '''
    _mentions_transforms = {
        '@everyone': '@\u200beveryone',
        '@here': '@\u200bhere'
    }

    _mention_pattern = re.compile('|'.join(_mentions_transforms.keys()))

    def __init__(self, **attrs):
        super().__init__(command_prefix=self.get_pre)
        self.db = ConfigDatabase(self)
        self.session = aiohttp.ClientSession(loop=self.loop)
        #self.process = psutil.Process()
        self._extensions = [x.replace('.py', '') for x in os.listdir('cogs') if x.endswith('.py')]
        self.messages_sent = 0
        self.commands_used = defaultdict(int)
        #self.remove_command('help')
        self.add_command(self.ping)
        self.load_extensions()
        self.load_community_extensions()

    def load_extensions(self, cogs=None, path='cogs.'):
        '''Loads the default set of extensions or a seperate one if given'''
        for extension in cogs or self._extensions:
            try:
                self.load_extension(f'{path}{extension}')
                print(f'Loaded extension: {extension}')
            except Exception as e:
                traceback.print_exc()

    def load_community_extensions(self):
        '''Loads up community extensions.'''
        with open('data/community_cogs.txt') as fp:
            to_load = fp.read().splitlines()
        if to_load:
            self.load_extensions(to_load, 'cogs.community.')

    @staticmethod
    async def get_pre(bot, message):
        '''Returns the prefix.'''
        with open('./data/config.json') as f: # TODO: server specific prefixes
            prefix = json.load(f).get('PREFIX')
        return os.environ.get('PREFIX') or prefix or 'g.'

    @staticmethod
    def run_wizard():
        '''Wizard for first start'''
        print('------------------------------------------')
        token = input('Enter your token:\n> ')
        print('------------------------------------------')
        prefix = input('Enter a prefix for your bot:\n> ')
        data = {
                "TOKEN" : token,
                "PREFIX" : prefix,
            }
        with open('./data/config.json','w') as f:
            f.write(json.dumps(data, indent=4))
        print('------------------------------------------')
        print('Restarting...')
        print('------------------------------------------')
        os.execv(sys.executable, ['python'] + sys.argv)

    @classmethod
    def init(bot, token=None):
        '''Starts the actual bot'''
        bot = bot()
        try:
            bot.run(os.environ.get('TOKEN'), reconnect=True)
        except Exception as e:
            print(e)

    async def on_connect(self):
        print('---------------\n'
              'GrokBot connected!')

    async def on_ready(self):
        '''Bot startup, sets uptime.'''
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()

        for guild in self.guilds: # sets default configs for all guilds.
            if self.db.get_data(guild.id) is None:
                self.db.set_default_config(guild.id)

        print(textwrap.dedent(f'''
        ---------------
        Client is ready!
        ---------------
        Authors: verixx, fourjr, kwugfighter, FloatCobra, add the rest here bois
        ---------------
        Logged in as: {self.user}
        User ID: {self.user.id}
        ---------------
        '''))

    async def on_command(self, ctx):
        cmd = ctx.command.qualified_name.replace(' ', '_')
        self.commands_used[cmd] += 1

    async def process_commands(self, message):
        '''Utilises the CustomContext subclass of discord.Context'''
        ctx = await self.get_context(message, cls=CustomContext)
        if ctx.command is None:
            return
        await self.invoke(ctx)

    async def on_message(self, message):
        '''Extra calculations'''
        if message.author == self.user:
            return
        self.messages_sent += 1
        self.last_message = time.time()
        await self.process_commands(message)

    @commands.command()
    async def ping(self, ctx):
        """Pong! Returns your websocket latency."""
        em = discord.Embed()
        em.title ='Pong! Websocket Latency:'
        em.description = f'{self.ws.latency * 1000:.4f} ms'
        em.color = 0x00FFFF
        try:
            await ctx.send(embed=em)
        except discord.HTTPException:
            em_list = await embedtobox.etb(emb)
            for page in em_list:
                await ctx.send(page)

if __name__ == '__main__':
    GrokBot.init()
