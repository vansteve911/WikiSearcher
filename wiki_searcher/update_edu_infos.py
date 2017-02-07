# -*- coding: utf-8 -*-
import sys
from common.db_client import DbClient
from common.utils import load_csv_file

def update_edu_infos(db_client, ids):
  sql_tmpl = 'SELECT id, college_name FROM education WHERE `id` IN (%s)' % ','.join(ids)
  rows = db_client.query_list(sql_tmpl, ())
  for row in rows:
    college = find_college(db_client, row['college_name'])
    if college:
      res = update_edu_college_id(db_client, row['id'], college['id'])
      print('update: id=%s, college_name=%s, college_id=%s, result: %s' % 
        (row['id'], row['college_name'], college['id'], res))
    else:
      print('>> id=%s, no college found: %s' % (row['id'], row['college_name']))

def find_college(db_client, alias):
  sql_tmpl = 'SELECT * FROM college_alias WHERE alias = %s'
  return db_client.query_one(sql_tmpl, (alias))

def update_edu_college_id(db_client, id, college_id):
  sql_tmpl = 'UPDATE education SET college_id = %s WHERE id = %s'
  return db_client.execute(sql_tmpl, (college_id, id))

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
  # start_id = int(sys.argv[1])
  # end_id = int(sys.argv[2])
  # update_edu_infos(db_client, start_id, end_id)
  data_file = '/Users/vansteve911/project/eliteEngine/data/listings/id_lowed.csv'
  ids = load_csv_file(data_file, [0], spliter = '\t', offset = 0, size = 10000)
  # update_edu_infos(db_client, ids)
  length = len(ids)
  # print(length)
  update_edu_infos(db_client, ids[0 : int(length/3)])
  update_edu_infos(db_client, ids[int(length/3) : 2*int(length/3)])
  update_edu_infos(db_client, ids[2*int(length/3) : length-1])

if __name__ == '__main__':
  main()


