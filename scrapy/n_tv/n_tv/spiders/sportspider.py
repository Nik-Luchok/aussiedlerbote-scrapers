
from datetime import datetime
import os
from urllib.parse import urlencode

from n_tv.spiders.spider_models import NtvSitemapSpider
from n_tv.itemsloaders import NtvArticleLoader
from n_tv.items import NtvArticle


PROXY_KEY = os.environ.get('PROXY_KEY')
PROXY_API_URL = os.environ.get('PROXY_API_URL')

TODAY = 31

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
            date_time = datetime.strptime(
                entry['news']['publication_date'],
                '%Y-%m-%dT%H:%M:%S+02:00')
            
            if date_time.day == TODAY:
                yield entry
    
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


