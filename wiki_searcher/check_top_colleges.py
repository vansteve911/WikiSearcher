# -*- coding: utf-8 -*-

from common.utils import load_csv_file
from common.db_client import DbClient

def find_college(db_client, alias):
  sql_tmpl = 'SELECT c.id, c.en_name, a.alias FROM college_alias a JOIN college c ON a.college_id = c.id WHERE a.alias = %s'
  return db_client.query_one(sql_tmpl, (alias))
  
def main():
  config = {
      'MYSQL_HOST': 'localhost',
      'MYSQL_PORT': 3306,
      'MYSQL_DBNAME': 'elite',
      'MYSQL_USER': 'elite',
      'MYSQL_PASSWD': 'elite',
      'MYSQL_CHARSET': 'utf8', 
  }
  db_client = DbClient(config)
  data_file = '/Users/vansteve911/project/eliteEngine/data/listings/Australia_colleges.csv'
  lines = load_csv_file(data_file, spliter = ',', offset = 0, size = 10000)
  line_num = 0
  for line in lines:
    if not line or len(line) < 2:
      print('illegal line: %s' % line)
      line_num += 1
    college = find_college(db_client, line[0])
    if not college:
      college = find_college(db_client, line[1])
    if not college:
      print('[LINE-%s] word: %s, no result' % (line_num, line[1]))
    line_num += 1

if __name__ == '__main__':
  main()