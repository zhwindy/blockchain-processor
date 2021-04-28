#!/usr/bin/env python
# encoding=utf-8
import json
import requests
import redis
import time
import pymysql

ENV = 'LOCAL'

UNI_CONTRACT = "0x7a250d5630b4cf539739df2c5dacb4c659f2488d"

if ENV != 'LOCAL':
    CONFIG = {
        "redis":{
            "host": "127.0.0.1",
            "port": 6379,
            "password": "redis-123456"
        },
        "mysql":{
            "host": "127.0.0.1",
            "port": 3306,
            "user": "coldlar",
            "passwd": "eth123456",
            "db": "eth"
        },
        "node": "http://127.0.0.1:18759"
    }
else:
    CONFIG = {
        "redis":{
            "host": "101.201.126.224",
            "port": 6379,
            "password": "redis-123456"
        },
        "mysql":{
            "host": "101.201.126.224",
            "port": 3306,
            "user": "coldlar",
            "passwd": "eth123456",
            "db": "eth"
        },
        "node": "http://101.201.126.224:18759"
    }

def mysql():
    config = CONFIG['mysql']
    conn = pymysql.connect(**config)
    cur = conn.cursor()
    # cur.execute("SELECT * FROM tx_history_test")
    # print(cur.fetchone())
    # cur.close()
    # conn.close()
    return cur


def redis_client():
    config = CONFIG['redis']
    client = redis.Redis(**config)
    return client


def sync_uni_v2_his_info():
    """
    同步uni合约历史记录
    起始同步高度: 10207858
    """
    node = CONFIG['node']
    # 已同步的高度
    uni_sync_his_number_key = "uni_his_already_synced_number"
    # 已同步得交易数量
    uni_already_synced_tx_count_key = "uni_already_synced_tx_count"

    redis_conn = redis_client()
    mysql_cur = mysql()

    while True:
        data = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}
        res = requests.post(node, json=data)
        result = res.json()
        # 查询当前最新高度
        new_block_num = int(result.get("result", "0"), base=16)
        # 延迟2个区块解析数据,防止分叉情况
        new_block_num = new_block_num - 2

        # 初始化已同步的高度
        synced_block_number = redis_conn.get(uni_sync_his_number_key)
        if not synced_block_number:
            already_synced = int(new_block_num) - 10
        else:
            already_synced = int(synced_block_number)

        end_block = min(already_synced+5, new_block_num)

        txs = []
        for num in range(already_synced + 1, end_block):
            block_num = hex(int(num))
            data = {"jsonrpc": "2.0", "method": "eth_getBlockByNumber", "params": [block_num, True], "id": 1}
            res = requests.post(node, json=data)
            result = res.json()
            datas = result.get("result")
            block_hash = datas.get("hash")
            transactions = datas.get("transactions", [])
            if not transactions:
                continue
            for tx in transactions:
                v_from = tx.get("from", "")
                if not v_from:
                    continue
                v_to = tx.get("to", "")
                if not v_to:
                    continue
                v_to_str = v_to.lower()
                if v_to_str != UNI_CONTRACT:
                    continue

                txid = tx.get("hash")
                if not txid:
                    continue
                tmp = {
                    "token_name": "uni",
                    "block_height": num,
                    "block_hash": block_hash,
                    "tx_hash": txid
                }
                txs.append(tmp)
            # redis_conn.set(uni_sync_his_number_key, num)
            # print(txs)
        if txs:
            values = ",".join(["('{token_name}', {block_height}, '{block_hash}', '{tx_hash}')".format(**one) for one in txs])
            sql = f"""
               INSERT IGNORE INTO tx_history_test(`token_name`, `block_height`, `block_hash`, `tx_hash`) values {values};
            """
            print(sql)
            mysql_cur.execute(sql)
            mysql_cur.commit()

        time.sleep(10)


if __name__ == "__main__":
    sync_uni_v2_his_info()
    # mysql()
    # redis_client()
