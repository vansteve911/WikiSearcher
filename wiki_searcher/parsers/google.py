import re
import traceback

SEARCH_URL_TMPL = 'http://www.google.{region}/search?hl=en&as_q=&as_epq={query}&as_oq=&as_eq=&as_nlo=&as_nhi=&lr=&cr=&as_qdr=all&as_sitesearch=&as_occt=any&safe=images&tbs=&as_filetype=&as_rights='

# SEARCH_URL_TMPL = 'http://www.google.{region}/search?safe=strict&q={query}'

class GoogleParser(object):

	region = 'com.hk'

	def get_search_url(self, query):
		return SEARCH_URL_TMPL.format(region=self.region, query='+'.join(query.split()).strip('+'))
	
	def parse_result_items(self, response, pattern_dict = None):
		item_sels = response.css('div#search div.g')
		strip_tag_func = lambda x: (x and re.sub('<[^>]+>','',x)) or ''
		links = []
		try:
			links = [dict({'title': strip_tag_func(sel.css('h3.r a').extract_first()),
									'url': strip_tag_func(sel.css('cite').extract_first())}) for sel in item_sels]
		except Exception as e:
			traceback.print_exc()
		if pattern_dict and type(pattern_dict) is dict:
			result = {}
			for key, pattern in pattern_dict.items():
				matches = filter(lambda link : re.search(pattern, link['url']), links)
				if matches:
					result[key] = matches[0]
			return result
		else:
			return links


