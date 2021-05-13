#encoding=utf-8
import pymysql
from dbutils.pooled_db import PooledDB
from config.env import CONFIG

MYSQL_CONFIG = CONFIG['mysql']

pool = PooledDB(
    creator=pymysql,
    maxconnections=3,
    mincached=2,
    host=MYSQL_CONFIG.get("host", "localhost"),
    port=MYSQL_CONFIG.get("port", 3306),
    user=MYSQL_CONFIG.get("user"),
    password=MYSQL_CONFIG.get("passwd"),
    db=MYSQL_CONFIG.get("db"),
    charset='utf8')


class Mysql(object):
    def __init__(self, pool):
        self.pool = pool
    
    def create_conn(self):
        conn = self.pool.connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        # cursor = conn.cursor()
        return conn, cursor

    def close_conn(self, conn, cursor):
        conn.close()
        cursor.close()

    def query(self, sql):
        """
        数据库查询
        """
        conn, cursor = self.create_conn()
        try:
            cursor.execute(sql)  # 返回 查询数据 条数 可以根据 返回值 判定处理结果
            data = cursor.fetchall()  # 返回所有记录列表
            return data
        except Exception as e:
            return None
        finally:
            self.close_conn(conn, cursor)

mysqldb = Mysql(pool)
