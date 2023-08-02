from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst, Identity
from w3lib.html import replace_escape_chars, strip_html5_whitespace


class NtvArticleLoader(ItemLoader):
    default_output_processor = TakeFirst()

    kicker_in = MapCompose(str.strip)
    teaser_in = MapCompose(str.strip)
    article_html_in = MapCompose(strip_html5_whitespace, replace_escape_chars)

    keyword_names_in = MapCompose(lambda x: x.split(sep=','), str.strip)
    keyword_names_out = Identity()
    current_rubric_names_out = Identity()
    rubric_names_out = Identity()