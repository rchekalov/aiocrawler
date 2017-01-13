import asyncio
import abc

DEFAULT_CONCUR_REQ = 42
DEFAULT_DELAY = 600

class ABCrawler(metaclass=abc.ABCMeta):
    def __init__(self, config, loop=None, delay=DEFAULT_DELAY, answer_callback=None):
        self._loop = loop or asyncio.get_event_loop()
        self._config = config
        self.delay = delay
        self.answer_callback = answer_callback

    @abc.abstractmethod
    async def crawl(self, config, semaphore):
        """Specific crawler implementation"""

    def start(self):
        asyncio.ensure_future(self.run())
        self._loop.run_forever()

    async def run(self, concur_req=DEFAULT_CONCUR_REQ):
        semaphore = asyncio.Semaphore(concur_req)
        while True:
            await self.crawl(self._config, semaphore)
            await asyncio.sleep(self.delay)

    def stop(self):
        self._loop.close()
