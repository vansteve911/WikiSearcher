import scrapy
import time

from scrapy.spiders import BaseSpider
from ..common.utils import load_csv_file
from ..parsers.google import GoogleParser
from ..parsers.wikipedia import WikipediaParser

# constants

def parser_factory(name):
	if name == 'google':
		return GoogleParser()
	raise Exception('search parser not supported!')

class WikiSearcherSpider(BaseSpider):

  name = 'wiki_searcher'
  keywords = []

  def __init__(self,
               data_file,
               search_parser = 'google',
               offset = 0,
               size = 100,
               *args,
               **kwargs):
  	super(WikiSearcherSpider, self).__init__(*args, **kwargs)
  	self.search_parser = parser_factory(search_parser)
  	self.wiki_parser = WikipediaParser()
  	# load data from csv
  	if not data_file:
  		raise Exception('no data file!')
  	self.keywords = load_csv_file(data_file, read_cols = [0], offset = int(offset), size = int(size)) # default 100

  def start_requests(self):
  	for w in self.keywords:
  		# set search query in request meta
  		request = scrapy.Request(self.search_parser.get_search_url(w))
  		request.meta.update({
  				'wiki_data': {
  					'query': w
  				}
  			})
  		# sleep for a while
  		time.sleep(2)
  		yield request

  def parse(self, response):
  	# search in google result
  	pattern_dict = {'en_wiki': 'https://en.wikipedia.org[^\?]+', 'zh_wiki': 'https://zh.wikipedia.org[^\?]+'}
  	wiki_data = self.search_parser.parse_result_items(response, pattern_dict)
  	wiki_data['query'] = unicode(response.meta.get('wiki_data').get('query'),'utf8')
  	print(wiki_data)
  	# check item data integrity and get item
  	# if all info collected, yield item, otherwise yield request
  	yield self.wiki_parser.check_and_go_on(wiki_data)
    