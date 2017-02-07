# -*- coding: utf-8 -*-
import time
import traceback
import sys

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from common.utils import load_csv_file

GOOGLE_HOME = 'https://www.google.com.hk'
# EDU_KEYWORDS = ['education','college','universit', 'school', 'academy', u'\u6559\u80b2', u'\u6821']
COMPANY_KEYWORDS = ['company', 'companies', 'corporation', 'firm', 'brand']

def init_driver():
  return webdriver.Chrome()

def wait_until_ready(driver, elemend_id, delay = 5):
  retry_cnt = 4
  while retry_cnt > 0:
    try:
      element = WebDriverWait(driver, delay).until(
          EC.presence_of_element_located((By.ID, elemend_id))
      )
      return
    except TimeoutException:
      print('Loading took too much time! will refresh and try again. retry count: %s' % retry_cnt)
      delay *= 1.5
      time.sleep(delay)
      driver.get(driver.current_url)
      retry_cnt -= 1

def search_google(driver, word):
  if not GOOGLE_HOME in driver.current_url:
    print('requesting %s for word: %s...' % (GOOGLE_HOME, word))
    driver.get(GOOGLE_HOME)
  search_box = driver.find_element_by_name('q')
  search_box.clear()
  search_box.send_keys(word)
  search_box.submit()
  time.sleep(2)
  wait_until_ready(driver, 'resultStats')
  return [dict({'title': r.text, 'url': r.get_attribute('href')}) 
    for r in driver.find_elements_by_css_selector('div#search div.g h3.r a')]

def find_wiki_results(results, word):
  info = {
    'word': word,
    'code': None,
    'en_wiki_url': None,
    'en_name': None,
    'zh_wiki_url': None,
    'zh_name': None,
  }
  for r in results:
    if 'https://en.wikipedia.org' in r['url']:
      info['en_wiki_url'] = r['url']
      info['en_name'] = r['title'].replace(u' - Wikipedia', '')
    elif 'https://zh.wikipedia.org' in r['url']:
      info['zh_wiki_url'] = r['url']
      info['zh_name'] = r['title'].replace(u'- \u7ef4\u57fa\u767e\u79d1\uff0c\u81ea\u7531\u7684\u767e\u79d1\u5168\u4e66', '')
  if not info['en_name'] and not info['zh_name']:
    print('no wikipedia found for word: %s' % word)
    info.update({
      'code': 'N/A',
      'en_wiki_url': '',
      'en_name': '',
      'zh_wiki_url': '',
      'zh_name': '',
    })
  return info

def complete_wikipedia_info(driver, info):
  if not info:
    return
  if not info['en_wiki_url'] and not info['zh_wiki_url']:
    print('no wiki found')
    return None
  def update_info(lang, url, do_filter = True):
    print('requesting %s...' % url)
    driver.get(url)
    wait_until_ready(driver, 'p-lang')
    # check if is a wiki about education
    cat_titles= [e.get_attribute('title') for e in driver.find_elements_by_css_selector('div#catlinks ul li a')]
    if do_filter:
    # if False: # TODO
      info.update({
          'code': 'N/A',
          'en_wiki_url': '',
          'en_name': '',
          'zh_wiki_url': '',
          'zh_name': '',
        })
      raise Exception('not a company wiki: %s' % url)
    wiki_url = ''
    name = ''
    wiki_link = None
    try:
      wiki_link = driver.find_element_by_css_selector('div#p-lang.portal ul li.interwiki-%s a' % lang)
    except Exception as e:
      print('no wiki of language: %s' % lang)
    if wiki_link:
      wiki_url = wiki_link.get_attribute('href')
      name = wiki_link.get_attribute('title')
      if lang == 'zh':
        name = name.replace(u' \u2013 Chinese', '')
      else:
        name = name.replace(u' \u2013 \u82f1\u8bed', '')
    info.update({
        '%s_wiki_url' % lang: wiki_url,
        '%s_name' % lang: name,
      })
  if info['en_wiki_url']:
    info['code'] = info['en_wiki_url'].replace('https://en.wikipedia.org/wiki/', '')
  elif info['zh_wiki_url']:
    info['code'] = info['zh_wiki_url'].replace('https://zh.wikipedia.org/', '')
  try:
    if not info['zh_wiki_url']:
      update_info('zh', info['en_wiki_url'], do_filter = False)
    elif not info['en_wiki_url']:
      update_info('en', info['zh_wiki_url'], do_filter = False)
    if info['en_wiki_url'] and info['code'] != info['en_wiki_url']:
      info['code'] = info['en_wiki_url'].replace('https://en.wikipedia.org/wiki/', '')
  except Exception as e:
    traceback.print_exc()
  return info

def search(driver, word):
  # try:
  word = unicode(word.replace('"', '').decode('utf8'))
  results = search_google(driver, word)
  info = find_wiki_results(results, word)
  complete_wikipedia_info(driver, info)
  # print('>>>%s' % info)
  return info
  # except Exception as e:
  #   traceback.print_exc()

def main():
  data_file = '/Users/vansteve911/project/eliteEngine/data/listings/certificates.csv'
  out_file = '/Users/vansteve911/project/eliteEngine/data/listings/out_certificates.csv'
  line_num = int(sys.argv[1])
  lines = load_csv_file(data_file, spliter = '\t', offset = line_num, size = int(sys.argv[2]))
  driver = init_driver()
  for line in lines:
    line_num += 1
    cert_name = line[1]
    ca_name = line[2]
    print('[LINE-%s] cert name: %s, ca name: %s' % (line_num, cert_name, ca_name))
    # retry at most 4 times
    result = ''
    for word in [cert_name, ca_name]:
      retry_cnt_left = 4
      info = None
      while not info and retry_cnt_left > 0:
        try:
          info = search(driver, word)
        except Exception as e:
          print('[LINE-%s] error occured, word: %s, retry count left: %s' % (line_num, word, retry_cnt_left))
          traceback.print_exc()
          info = None
          time.sleep(1)
          retry_cnt_left -= 1
      if info:
        try:
          result += '%s\t%s\t%s\t%s\t%s\t%s\n' % (info['code'], info['word'], info['en_wiki_url'], info['en_name'], info['zh_wiki_url'], info['zh_name'])
        except Exception as e:
          traceback.print_exc()
    if result:
      result = '%s\t%s' % (line[0], result)
      print('[LINE-%s] result: %s' % (line_num, result))
      with open(out_file, "a") as f:
        f.write(result.encode('utf-8')) 
  driver.quit()

if __name__ == '__main__':
  main()