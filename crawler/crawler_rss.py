import contextlib
import html
from string import Template
import aiohttp
import asyncio
import feedparser
from crawler.abc_crawler import ABCrawler
from emoji import emojize
import aioredis
import os

class RSSCrawler(ABCrawler):

    async def _download_rss(self, url, semaphore):
        with (await semaphore):
            resp = await aiohttp.request('GET', url)
        with contextlib.closing(resp):
            if resp.status == 200:
                return await resp.read()
            else:
                raise aiohttp.HttpProcessingError(
                    code=resp.status,
                    message=resp.reason,
                    headers=resp.headers
                )

    async def worker(self, feed, semaphore, redis):
        with (await semaphore):
            rss = feedparser.parse(await self._download_rss(feed['url'], semaphore))
        for entry in rss.entries:
            tags = []
            if 'tags' in entry:
                tags = [tag['term'] for tag in entry['tags']]
            template_dict = {
                'author': html.escape(entry.get('author', '')),
                'description': html.escape(entry.get('summary', '')),
                'tags': html.escape(', '.join(tags)),
                'time': entry.get('published'),
                'title': html.escape(entry.get('title', '')),
                'url': entry['id']
            }
            result = emojize(Template(feed['format']).safe_substitute(template_dict))
            if not redis.sismember('rss_id_set', entry['id']):
                redis.sadd('rss_id_set', entry['id'])
                with (await semaphore):
                    await self.answer_callback(result)

    async def crawl(self, config, semaphore):
        host = os.environ.get('REDIS_HOST', 'localhost')
        redis = await aioredis.create_redis((host, 6379), encoding="utf-8")
        [asyncio.ensure_future(self.worker(feed, semaphore, redis)) for feed in config['feeds']]
