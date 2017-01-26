import re
import scrapy

from ..items import WikipediaItem

COMPLETED = 1
EN_INFO_LACK = 2
ZH_INFO_LACK = 3

class WikipediaParser(object):

	def __check_item_integrity(self, wiki_data):
		if not wiki_data:
			return False
		en_info = wiki_data.get('en_wiki')
		zh_info = wiki_data.get('zh_wiki')
		if en_info and zh_info:
			return COMPLETED
		if en_info:
			return ZH_INFO_LACK
		if zh_info:
			return EN_INFO_LACK
		return False

	def __complete_info(self, wiki_data):
		en_info = wiki_data.get('en_wiki')
		zh_info = wiki_data.get('zh_wiki')
		f_parse = lambda x, k, r: x.get(k).replace(r, '')
		code = None
		if en_info:
			code = f_parse(en_info, 'url', 'https://en.wikipedia.org/wiki/')
		else:
			code = f_parse(zh_info, 'url', 'https://zh.wikipedia.org/wiki/')
		if not code:
			raise Exception('failed to parse code!')
		wiki_data.update({
				'code': code,
				'en_wiki_url': en_info.get('url'),
				'zh_wiki_url': zh_info.get('url'),
				'en_name': f_parse(en_info, 'title', u' - Wikipedia'),
				'zh_name': f_parse(zh_info, 'title', u'- \u7ef4\u57fa\u767e\u79d1\uff0c\u81ea\u7531\u7684\u767e\u79d1\u5168\u4e66'),
			})

	def check_and_go_on(self, wiki_data):
		check_res = self.__check_item_integrity(wiki_data)
		if not check_res:
			return None
		if COMPLETED == check_res:
			__complete_info(wiki_data)
			return WikipediaParser.genWikiItem(wiki_data)
		# emit req for en/zh wiki
		url = None
		callback_func = None
		if EN_INFO_LACK == check_res:
			# emit req for zh wiki
			url = wiki_data.get('zh_wiki').get('url')
			callback_func = self.parse_zh_wiki
		elif ZH_INFO_LACK == check_res:
			# emit req for zh wiki
			url = wiki_data.get('en_wiki').get('url')
			callback_func = self.parse_en_wiki
		request = scrapy.Request(url, callback=callback_func)
		request.meta.update({
				'wiki_data': wiki_data
		})
		return request
			
	def parse_zh_wiki(self, response):
		# find en title and en wiki url from response
		link_sel = response.css('div#p-lang.portal ul li.interwiki-en a')
		if not link_sel:
			print('no en wiki page found on %s' % response.url)
			return
		en_url = link_sel.xpath('@href').extract_first()
		en_title = link_sel.xpath('@title').extract_first().replace(u' \u2013 \u82f1\u8bed', '')
		wiki_data = response.meta.get('wiki_data')
		wiki_data['en_wiki'] = {'url': en_url, 'title': en_title}
		self.__complete_info(wiki_data)
		yield WikipediaParser.genWikiItem(wiki_data)

	def parse_en_wiki(self, response):
		# find zh title and zh wiki url from response
		link_sel = response.css('div#p-lang.portal ul li.interwiki-zh a')
		wiki_data = response.meta.get('wiki_data')
		if not link_sel:
			print('no zh wiki page found on %s' % response.url)
		else:
			zh_url = link_sel.xpath('@href').extract_first()
			zh_title = link_sel.xpath('@title').extract_first().replace(u' \u2013 Chinese', '')
			wiki_data['zh_wiki'] = {'url': zh_url, 'title': zh_title}
		self.__complete_info(wiki_data)
		yield WikipediaParser.genWikiItem(wiki_data)


	@staticmethod
	def genWikiItem(data):
		# self['code'] = data.get('code')
		item = WikipediaItem()
		item['code'] = data.get('code')
		item['alias'] = data.get('query')
		item['en_name'] = data.get('en_name')
		item['zh_name'] = data.get('zh_name')
		item['en_wiki_url'] = data.get('en_wiki_url')
		item['zh_wiki_url'] = data.get('zh_wiki_url')
		return item

