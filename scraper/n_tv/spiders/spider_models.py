from scrapy.spiders import SitemapSpider
from scrapy.spiders.sitemap import iterloc

from n_tv.sitemap import NtvSitemap

import logging
from scrapy.http import Request
from scrapy.utils.sitemap import sitemap_urls_from_robots

logger = logging.getLogger(__name__)


class NtvSitemapSpider(SitemapSpider):
    sitemap_urls = ['https://www.n-tv.de/news.xml']

    # change Sitemap object. The default class doesn't provide the children of 
    # news tag to get publication_date for filter
    def _parse_sitemap(self, response):
        if response.url.endswith("/robots.txt"):
            for url in sitemap_urls_from_robots(response.text, base_url=response.url):
                yield Request(url, callback=self._parse_sitemap)
        else:
            body = self._get_sitemap_body(response)
            if body is None:
                logger.warning(
                    "Ignoring invalid sitemap: %(response)s",
                    {"response": response},
                    extra={"spider": self},
                )
                return

            # changed Sitemap class
            s = NtvSitemap(body)
            it = self.sitemap_filter(s)

            if s.type == "sitemapindex":
                for loc in iterloc(it, self.sitemap_alternate_links):
                    if any(x.search(loc) for x in self._follow):
                        yield Request(loc, callback=self._parse_sitemap)
            elif s.type == "urlset":
                for loc in iterloc(it, self.sitemap_alternate_links):
                    for r, c in self._cbs:
                        if r.search(loc):
                            yield Request(loc, callback=c)
                            break