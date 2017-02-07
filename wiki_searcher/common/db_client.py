# -*- coding: utf-8 -*-

import pymysql
import traceback

class DbClient(object):

  def __init__(self, config):
    self.host = config['MYSQL_HOST']
    self.port = config['MYSQL_PORT']
    self.db_name = config['MYSQL_DBNAME']
    self.user = config['MYSQL_USER']
    self.passwd = config['MYSQL_PASSWD']
    self.charset = config['MYSQL_CHARSET']

  def query_list(self, sql_tmpl, params):
    def query_func(cursor, sql):
      cursor.execute(sql, params)
      return cursor.fetchall()
    return self.execute(sql_tmpl, params, query_func)

  def query_one(self, sql_tmpl, params):
    def query_func(cursor, sql):
      cursor.execute(sql, params)
      return cursor.fetchone()
    return self.execute(sql_tmpl, params, query_func)

  def execute(self, sql, params, query_func=None, rollback_on_err = True):
    if not isinstance(sql, str):
      return
    connection = None
    try:
      connection = pymysql.connect(
          host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db_name, charset=self.charset)
      with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        if callable(query_func):
          # query
          return query_func(cursor, sql)
        else:
          # update query
          try:
            # 执行sql语句
            # print(params, 'list?', params is list)
            if type(params) == list:
              for p in params:
                # print(p)
                cursor.execute(sql, p)
            else:
              cursor.execute(sql, params)
            # 提交到数据库执行
            connection.commit()
            return True
          except Exception as e:
            print('error occured when execute update', e)
            traceback.print_exc()
            if rollback_on_err:
              # 如果发生错误则回滚
              print('error occured when execute update, will rollback', e)
              connection.rollback()
    except Exception as e:
      print('error occured!', e)
      traceback.print_exc()
    finally:
      if connection:
        connection.close()

if __name__ == '__main__':
  config = {
      'MYSQL_HOST': 'localhost',
      'MYSQL_PORT': 3306,
      'MYSQL_DBNAME': 'elite',
      'MYSQL_USER': 'elite',
      'MYSQL_PASSWD': 'elite',
      'MYSQL_CHARSET': 'utf8', 
  }
  db_client = DbClient(config)
  # sql = '''INSERT INTO college (id, name, name_zh, country, rank) VALUES (%s, %s, %s, %s, %s)'''
  # params = (1, 'Princeton University', '普林斯顿大学', 1, 1)
  sql = '''SELECT id, college_name FROM education WHERE id BETWEEN %s AND %s'''
  params = (1, 10)
  print(db_client.query_list(sql, params))
