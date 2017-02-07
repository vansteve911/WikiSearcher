# -*- coding: utf-8 -*-
import json
import requests
from common.utils import load_csv_file
from common.db_client import DbClient

GET_ID_URL = 'http://127.0.0.1:8080/api/internal/genID'

def store_colleges_aliases(db_client, data_file):
  offset = 0
  lines = load_csv_file(data_file, spliter = '\t', offset = offset, size = 10000)
  line_num = offset
  for line in lines:
    entity = parse_to_company_entity(line)
    if entity:
      res1 = add_company(db_client, entity)
      res2 = add_company_alias(db_client, entity)
      log_info = '[LINE-%s] load entity: %s, add college res: %s, add alias res: %s' % (line_num, entity, res1, res2)
      print(log_info)
    line_num += 1

def add_company(db_client, entity):
  attributes = json.dumps({
      'enWikiUrl': entity['en_wiki_url'],
      'zhWikiUrl': entity['zh_wiki_url'],
    })
  sql_tmpl = 'INSERT IGNORE INTO `company` (`id`, `code`, `en_name`, `zh_name`, `attributes`) VALUES (%s, %s, %s, %s, %s)'
  row = (entity['id'], entity['code'], entity['en_name'], entity['zh_name'], attributes)
  return db_client.execute(sql_tmpl, row, rollback_on_err = False)

def add_company_alias(db_client, entity):
  sql_tmpl = 'INSERT IGNORE INTO `company_alias` (`id`, `company_id`, `alias`) VALUES (%s, %s, %s)'
  row = (entity['alias_id'], entity['id'], entity['alias'])
  return db_client.execute(sql_tmpl, row, rollback_on_err = False)

def parse_to_company_entity(cols):
  if not cols or len(cols) != 6:
    print('illegal row: %s' % cols)
    return
  if cols[0] == 'N/A':
    print('wiki not found for alias: %s' % cols[1])
    return
  return {
    'id': get_id('Company', cols[0]),
    'alias_id': get_id('CompanyAlias', cols[1]),
    'code': cols[0],
    'alias': cols[1],
    'en_wiki_url': cols[2],
    'en_name': cols[3],
    'zh_wiki_url': cols[4],
    'zh_name': cols[5],
  }

def get_id(prefix, input):
  url = '%s?prefix=%s&input=%s' % (GET_ID_URL, prefix, input)
  resp = requests.get(url)
  return int(resp.text)

def main():
  config = {
      'MYSQL_HOST': 'localhost',
      'MYSQL_PORT': 33306,
      'MYSQL_DBNAME': 'elite',
      'MYSQL_USER': 'elite',
      'MYSQL_PASSWD': 'ElitEEnginE@)17',
      'MYSQL_CHARSET': 'utf8', 
  }
  db_client = DbClient(config)
  data_file = '/Users/vansteve911/project/eliteEngine/data/listings/intern_exp.csv'
  store_colleges_aliases(db_client, data_file)

if __name__ == '__main__':
  main()



