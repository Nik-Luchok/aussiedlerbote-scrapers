# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
format_function = format
type_obj = type


class NtvArticle(scrapy.Item):
    default_values = {
        "format": "digitalwires@0.8.0",
        "type": "composite",
        "entry_id": None,
        "updated": None,
        "urn": None,
        "version_created": None,
        "version": 1,
        "pubstatus": "usable",
        "signal": None,
        "embargoed": None,
        "language": None,
        "urgency": 1,
        "kicker": None,
        "headline": None,
        "subhead": None,
        "teaser": None,
        "byline": None,
        "dateline": None,
        "article_html": None,
        "infobox_html": None,
        "linkbox_html": None,
        "creditline": "ntv",
        "copyrightnotice": None,
        "usageterms": None,
        "autopublishnotice": None,
        "notepad": None,
        "ednotes": None,
        "descriptions": None,
        "associations": None,
        "categories": None,
        "current_rubric_names": [],
        "rubric_names": [],
        "dpasubject_names": None,
        "geosubject_names": None,
        "keyword_names": [],
        "desk_names": None,
        "genre_names": None,
        "poi_names": None,
        "scope_names": None,
    }

    # for debug
    url = scrapy.Field()

    # metadata
    urn = scrapy.Field()  # generate
    language = scrapy.Field()
    creditline = scrapy.Field()

    # rubric, tags, keywords
    current_rubric_names = scrapy.Field()
    rubric_names = scrapy.Field()

    # date/time
    updated = scrapy.Field()
    version_created = scrapy.Field()
    embargoed = scrapy.Field()
    dateline = scrapy.Field()
    keyword_names = scrapy.Field()
 
    # textual data
    headline = scrapy.Field()
    kicker = scrapy.Field()
    teaser = scrapy.Field()
    article_html = scrapy.Field()
    # may be null
    subhead = scrapy.Field()
    byline = scrapy.Field()

    # deafult
    format = scrapy.Field()  # def "digitalwires@0.8.0"
    type = scrapy.Field()  # def "composite"
    descriptions = scrapy.Field()  # def null
    entry_id = scrapy.Field()  # def null
    version = scrapy.Field()  # def 1
    pubstatus = scrapy.Field()  # def "usable"
    signal = scrapy.Field()  # def null
    urgency = scrapy.Field()  # def 1
    infobox_html = scrapy.Field()  # def null
    linkbox_html = scrapy.Field()  # def null
    copyrightnotice = scrapy.Field()  # def null
    usageterms = scrapy.Field()  # def null
    autopublishnotice = scrapy.Field()  # def null
    notepad = scrapy.Field()  # def null
    ednotes = scrapy.Field()  # def null
    associations = scrapy.Field()  # def null
    categories = scrapy.Field()  # def null
    dpasubject_names = scrapy.Field()  # def null
    geosubject_names = scrapy.Field()  # def null
    desk_names = scrapy.Field()  # def null
    genre_names = scrapy.Field()  # def null
    poi_names = scrapy.Field()  # def null
    scope_names = scrapy.Field()  # def null



