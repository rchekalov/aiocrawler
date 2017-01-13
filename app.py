import yaml
import bot
from crawler.crawler_rss import RSSCrawler

if __name__ == '__main__':
    with open('config.yml', 'r', encoding='utf-8') as stream:
        bot.start()
        crawler_rss = RSSCrawler(yaml.load(stream), answer_callback=bot.send)
        crawler_rss.start()
