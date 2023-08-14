from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst, Identity
from w3lib.html import replace_escape_chars, strip_html5_whitespace


def get_rubric_processor(domain_url:str) -> MapCompose:
    return MapCompose(lambda x: x.removeprefix(domain_url),
                      lambda x: x.split('/')[0])


class BaseArticleLoader(ItemLoader):
    # by default return item
    default_output_processor = TakeFirst()

    # default data clearing
    article_html_in = MapCompose(strip_html5_whitespace, replace_escape_chars)
    kicker_in = MapCompose(str.strip)
    teaser_in = MapCompose(str.strip)

    # here we return list values instead if item
    creditline_out = Identity()
    keyword_names_out = Identity()
    current_rubric_names_out = Identity()
    rubric_names_out = Identity()


class NtvArticleLoader(BaseArticleLoader):
    # TODO impement rubric processor
    keyword_names_in = MapCompose(lambda x: x.split(sep=','), 
                                  str.strip)
    creditline_in = MapCompose(lambda x: x.removeprefix('Quelle:'),
                               lambda x: x.split(sep=','), 
                               str.strip)


class BildArticleLoader(BaseArticleLoader):
    keyword_names_in = MapCompose(lambda x: x.split(sep=','), 
                                  str.strip)
    
    rubric_names_in = get_rubric_processor('https://www.bild.de/')
    current_rubric_names_in = get_rubric_processor('https://www.bild.de/')
    
    