# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class WikipediaItem(Item):
	# define the fields for your item here like:
	# name = scrapy.Field()
	code = Field()
	alias = Field()
	en_name = Field()
	zh_name = Field()
	en_wiki_url = Field()
	zh_wiki_url = Field()

		


