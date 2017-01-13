import logging
import asyncio
import aioredis
import os
import json
from aiotg import Bot, chat

with open("config.json") as cfg:
    config = json.load(cfg)
    chat_id = config['chat_id']
    del config['chat_id']
bot = Bot(**config)

logger = logging.getLogger(chat_id)
redis = None

chat = chat.Chat(bot, chat_id)

async def send(text):
    await chat.send_text(text)

def start():
    asyncio.ensure_future(run())

async def run():
    global redis
    host = os.environ.get('REDIS_HOST', 'localhost')
    redis = await aioredis.create_redis((host, 6379), encoding="utf-8")
    await bot.loop()
