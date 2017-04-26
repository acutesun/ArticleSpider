# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class AticleItem(scrapy.Item):
    url_object_id = scrapy.Field()
    url = scrapy.Field()
    front_image_url = scrapy.Field()
    front_image_path = scrapy.Field()
    title = scrapy.Field()
    create_time = scrapy.Field()
    great_nums = scrapy.Field()
    bookmark_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    tags = scrapy.Field()
    content = scrapy.Field()

