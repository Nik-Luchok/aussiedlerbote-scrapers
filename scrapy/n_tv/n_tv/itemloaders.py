from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst
from w3lib.html import replace_escape_chars, strip_html5_whitespace


class NtvArticleLoader(ItemLoader):
    default_output_processor = TakeFirst()
    kicker_in = MapCompose(lambda x: x.strip())
    teaser_in = MapCompose(lambda x: x.strip())
    article_html_in = MapCompose(strip_html5_whitespace, replace_escape_chars)