# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
class MuslmItem(Item):
    # Primary fields
    title = Field()
    body = Field()
    # description = Field()
    # address = Field()
    # image_urls = Field()
    # Calculated fields
    # images = Field()
    # location = Field()
    # Housekeeping fields
    url = Field()
    project = Field()
    spider = Field()
    server = Field()
    date = Field()