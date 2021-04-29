#!/usr/bin/env python
# encoding=utf-8
import json
import requests
import redis
import time
import pymysql
import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)

handler = logging.StreamHandler()
# formatter = logging.Formatter('%(asctime)s %(filename)s %(lineno)s %(message)s')
formatter = logging.Formatter('%(asctime)s %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

ENV = 'LOCAL'

UNI_CONTRACT = "0x7a250d5630b4cf539739df2c5dacb4c659f2488d"

if ENV == 'LOCAL':
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
        "table": "tx_history",
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
        "table": "tx_history_test",
        "node": "http://101.201.126.224:18759"
    }

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
    table = CONFIG['table']
    # 已同步的高度
    uni_sync_his_number_key = "uni_his_already_synced_number"
    # 已同步得交易数量
    uni_already_synced_tx_count_key = "uni_already_synced_tx_count"

    redis_conn = redis_client()

    config = CONFIG['mysql']
    connection = pymysql.connect(**config)

    # 每次请求的块数,动态调整
    interval = 5

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

        end_block = min(already_synced+interval, new_block_num)

        txs = []
        syncing_block = already_synced
        for num in range(already_synced + 1, end_block):
            block_num = hex(int(num))
            # logger.info("process block:{}".format(num))
            try:
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
                syncing_block = num
            except Exception as e:
                logger.info(e)
                break
        logger.info(f"interval:{interval}, syncing block:{syncing_block}")
        if not txs:
            interval += 5
            redis_conn.set(uni_sync_his_number_key, syncing_block)
            continue
        txs_count = len(txs)
        if txs_count < 100:
            interval += 5
        else:
            interval -= 2
        logger.info(f"get tx count:{txs_count}")
        values = ",".join(["('{token_name}', {block_height}, '{block_hash}', '{tx_hash}')".format(**one) for one in txs])
        try:
            # with connection:
            #     with connection.cursor() as cursor:
            cursor = connection.cursor()
            sql = f"""
               INSERT IGNORE INTO {table}(`token_name`, `block_height`, `block_hash`, `tx_hash`) values {values};
            """
            cursor.execute(sql)
            connection.commit()
        except Exception as e:
            logger.info(f"syncing block:{syncing_block}")
            logger.info(e)
            continue
        redis_conn.set(uni_sync_his_number_key, syncing_block)
        redis_conn.incrby(uni_already_synced_tx_count_key, txs_count)

        time.sleep(0.2)


if __name__ == "__main__":
    sync_uni_v2_his_info()
