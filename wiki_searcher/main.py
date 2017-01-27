# -*- coding: utf-8 -*-
import time
import traceback
import sys

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

GOOGLE_HOME = 'https://www.google.com.hk'
EDU_KEYWORDS = ['education','college','universities', 'school', 'academy', u'\u6559\u80b2', u'\u6821']

def init_driver():
  return webdriver.Chrome()

def wait_until_ready(driver, elemend_id, delay = 5):
  retry_cnt = 4
  while retry_cnt > 0:
    try:
      # print('waiting...')
      element = WebDriverWait(driver, delay).until(
          EC.presence_of_element_located((By.ID, elemend_id))
      )
      return
      # print('Page is ready!')
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
  def update_info(lang, url):
    print('requesting %s...' % url)
    driver.get(url)
    wait_until_ready(driver, 'p-lang')
    # check if is a wiki about education
    cat_titles= [e.get_attribute('title') for e in driver.find_elements_by_css_selector('div#catlinks ul li a')]
    if not filter(lambda x : filter(lambda y:y.lower() in x, EDU_KEYWORDS), cat_titles):
      info.update({
          'code': 'N/A',
          'en_wiki_url': '',
          'en_name': '',
          'zh_wiki_url': '',
          'zh_name': '',
        })
      raise Exception('not a educational wiki: %s' % url)
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
      update_info('zh', info['en_wiki_url'])
    elif not info['en_wiki_url']:
      update_info('en', info['zh_wiki_url'])
  except Exception as e:
    print(e)
  return info

def search(driver, word):
  try:
    word = unicode(word.replace('"', '').decode('utf8'))
    results = search_google(driver, word)
    info = find_wiki_results(results, word)
    complete_wikipedia_info(driver, info)
    # print('>>>%s' % info)
    return info
  except Exception as e:
    traceback.print_exc()

def load_csv_file(file, read_cols = None, spliter = ',', offset = 0, size = 100):
  line = None
  single_col_idx = read_cols and len(read_cols) == 1 and read_cols[0]
  result = []
  cursor = -1
  with open(file) as f:
    while True:
      line = f.readline()
      if line:
        try: 
          cursor += 1
          if cursor < offset:
            continue
          if cursor > offset + size:
            break
          row = line.replace('\n', '').split(spliter)
          if single_col_idx != None:
            row = row[single_col_idx]
          elif read_cols:
            row = [row[i] for i in read_cols]
          result.append(row)
        except Exception as e:
          print('error loading file, line: %s' % line, e)
          traceback.print_exc()
      else:
        break
  return result
  
def main():
  data_file = '/Users/vansteve911/Desktop/distinct_colleges.csv'
  out_file = '/Users/vansteve911/Desktop/the_college_names.csv'
  old_out_file = '/Users/vansteve911/Desktop/college_names.csv'
  loaded_words = set(load_csv_file(old_out_file, [1], spliter = '\t', offset = 0, size = 4500))
  line_num = int(sys.argv[1])
  words = load_csv_file(data_file, [0], offset = line_num, size = int(sys.argv[2]))
  print('loaded words count: %s' % len(loaded_words))
  driver = init_driver()
  for word in words:
    line_num += 1
    if word in loaded_words:
      print('%s is loaded, pass' % word)
      continue
    # filter high schools
    # if 'school' in word.lower():
    #   print('%s is loaded, pass' % word)
    #   continue
    print('[LINE-%s] word: %s' % (line_num, word))
    info = search(driver, word)
    if info:
      try:
        line = '%s\t%s\t%s\t%s\t%s\t%s\n' % (info['code'], info['word'], info['en_wiki_url'], info['en_name'], info['zh_wiki_url'], info['zh_name'])
        print('[LINE-%s] result: %s' % (line_num, line))
        with open(out_file, "a") as f:
          f.write(line.encode('utf-8'))
      except Exception as e:
        traceback.print_exc()

  driver.quit()

if __name__ == '__main__':
  main()
  
