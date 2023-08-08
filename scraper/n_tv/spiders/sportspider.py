
from datetime import datetime
import os
from urllib.parse import urlencode

from n_tv.spiders.spider_models import NtvSitemapSpider
from n_tv.itemsloaders import NtvArticleLoader
from n_tv.items import NtvArticle


PROXY_KEY = os.environ.get('PROXY_KEY')
PROXY_API_URL = os.environ.get('PROXY_API_URL')

TODAY = 8

rubric = 'sport'


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
    sitemap_rules = [(f'/{rubric}/', 'sport_parse')]

    def sitemap_filter(self, entries):
        ''''''
        for entry in entries:
            # date filter
            date_time = self._str_to_daytime(entry)
            if date_time.day == TODAY:
                yield entry

    @classmethod
    def _str_to_daytime(cls, entry) -> datetime:
        date_time = datetime.strptime(
                        entry['news']['publication_date'],
                        '%Y-%m-%dT%H:%M:%S+02:00')
        return date_time
    
    def sport_parse(self, response):
        article = response.css("article.article")
        language = response.css("html::attr('lang')").get()
        last_modified = response.css("[name='last-modified']::attr('content')").get()
        keywords_str = response.css("[name='keywords']::attr('content')").get()
        
        # textual data
        article_loader = NtvArticleLoader(item=NtvArticle(), selector=article)

        article_loader.add_css('teaser', "div.article__text p strong::text")
        article_loader.add_css('headline', "span.article__headline::text")
        article_loader.add_css('kicker', "span.article__kicker::text")
        self._clean_article(article)
        article_loader.add_css('article_html', "div.article__text")

        # metadata
        article_loader.add_value('url', response.url)
        article_loader.add_value('language', language)

        # Quelle, sources
        article_loader.add_css('creditline', "p.article__source::text")

        
        # rubtic, keywords, tags
        article_loader.add_value('current_rubric_names', rubric)
        article_loader.add_value('rubric_names', rubric)
        article_loader.add_value('keyword_names', keywords_str)

        # date/time
        article_loader.add_value('dateline', last_modified)
        article_loader.add_value('embargoed', last_modified)
        article_loader.add_value('version_created', last_modified)
        article_loader.add_value('updated', last_modified)

        yield article_loader.load_item()
  
    def _clean_article(self, article) -> None:
        # remove teaser tag from HTML DOM
        article.css("div.article__text p")[0].drop()
        
        # remove side article__aside
        article.css("div.article__aside").drop()

        # remove interaction & scripts
        article.css("interaction").drop()
        article.css("script").drop()


class NotDpaSpider(NtvSitemapSpider):
    name = "notdpaspider"
    custom_settings = {
        'ITEM_PIPELINES': {

        },
        'CONCURRENT_REQUESTS': 17

    }

    def sitemap_filter(self, entries):
        ''''''
        # added counter
        self.counter = 0
        for entry in entries:
            # date filter
            date_time = self._str_to_daytime(entry)
            if date_time.day == TODAY:
                self.counter += 1
                yield entry

    @classmethod
    def _str_to_daytime(cls, entry) -> datetime:
        date_time = datetime.strptime(
                        entry['news']['publication_date'],
                        '%Y-%m-%dT%H:%M:%S+02:00')
        return date_time

    def parse(self, response):
        is_dpa = False
        article = response.css("article.article")
        quelle = article.css("p.article__source::text").get()
        if quelle.find("dpa") != -1:
            is_dpa = True

        yield {
            'url': response.url,
            'total_articles': self.counter,
            'quelle': quelle,
            'is_dpa': is_dpa
        }
        

