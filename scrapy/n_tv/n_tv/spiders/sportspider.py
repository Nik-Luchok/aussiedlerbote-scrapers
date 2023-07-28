
from datetime import datetime
import os
from urllib.parse import urlencode

from n_tv.spiders.spider_models import NtvSitemapSpider


PROXY_KEY = os.environ.get('PROXY_KEY')
PROXY_API_URL = os.environ.get('PROXY_API_URL')

TODAY = 27


def get_proxy_url(url):
    """Get proxy url leading to the website being scraped
    param: url
        url of the website to scrape
    """
    payload = {'api_key': PROXY_KEY, 'url': url}
    proxy_url = PROXY_API_URL + urlencode(payload)
    return proxy_url


class NtvSportSpider(NtvSitemapSpider):
    name = 'ntvsportspider'
    sitemap_urls = ['https://www.n-tv.de/news.xml']
    sitemap_rules = [('/sport/', 'sport_parse')]

    def sitemap_filter(self, entries):
        ''''''
        for entry in entries:
            date_time = datetime.strptime(
                entry['news']['publication_date'],
                '%Y-%m-%dT%H:%M:%S+02:00')
            
            if date_time.day == TODAY:
                yield entry
    
    def sport_parse(self, response):
        yield {'url': response.url}

