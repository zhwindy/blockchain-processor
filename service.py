#encoding=utf-8
import redis
import pymysql
import requests
import json
from functools import lru_cache
from config.env import CONFIG
from db import mysqldb

redis_config = CONFIG['redis']
redis_client = redis.Redis(**redis_config)

node_url = CONFIG['node']

table = CONFIG['table']


def demo_get_many_transactions(txids):
    """
    批量查询交易详情
    """
    payload = [{
        "jsonrpc": "2.0",
        "method": "eth_getTransactionByHash",
        "params": [txid],
        "id": 1
    } for txid in txids]
    res = requests.post(node_url, json=payload)
    result = res.json()
    return result

def demo_get_many_receipts(txids):
    """
    批量查询交易收据
    """
    payload = [{
        "jsonrpc": "2.0",
        "method": "eth_getTransactionReceipt",
        "params": [txid],
        "id": 1
    } for txid in txids]
    res = requests.post(node_url, json=payload)
    result = res.json()
    return result

def demo_get_transaction_receipt(txid):
    """
    查询交易收据
    """
    data = {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionReceipt",
        "params": [txid],
        "id": 1
    }
    res = requests.post(node_url, json=data)
    result = res.json()
    return result.get("result", {})

@lru_cache(maxsize=32)
def get_uni_all_history_v1(contract, page, limit=15, pageSize=15):
    """
    查询历史记录:
    1.单页默认15条
    2.交易详情批量查询,交易收据单独循环查询
    """
    page = max(1, int(page))
    offset = (page - 1) * limit
    # 已同步得交易数量
    uni_already_synced_tx_count_key = "uni_already_synced_tx_count"
    try:
        if not contract or len(str(contract)) != 42:
            result = {
                "message": "invalid contract address",
                "totalCount": 0,
                "page": page,
                "pageSize": pageSize,
                "contract": contract,
                "data": []
            }
        else:
            uni_sync_tx_count = json.loads(redis_client.get(uni_already_synced_tx_count_key))
            total = uni_sync_tx_count
            sql = f"""
                SELECT
                    block_height, block_hash, tx_hash
                FROM
                    {table}
                where
                    id > {offset} limit {limit}
            """
            txids = []
            datas = mysqldb.query(sql)
            txids = [data.get("tx_hash") for data in datas]
            tx_details = demo_get_many_transactions(txids)
            data = []
            for tx in tx_details:
                tmp = tx.get("result", {})
                txid = tmp.get("hash")
                if not txid:
                    continue
                try:
                    tx_receipt = demo_get_transaction_receipt(txid)
                except Exception:
                    continue
                status = tx_receipt.get("status")
                gasUsed = tx_receipt.get("gasUsed")
                logs = tx_receipt.get("logs")
                tmp['status'] = status
                tmp['gasUsed'] = gasUsed
                tmp['logs'] = logs
                data.append(tmp)
            result = {
                "message": "success",
                "totalCount": total,
                "page": page,
                "pageSize": pageSize,
                "contract": contract,
                "data": data
            }
    except Exception as e:
        result = {
            "message": "Error: " + str(e),
            "totalCount": 0,
            "page": 0,
            "pageSize": pageSize,
            "contract": contract,
            "data": []
        }
    return result

@lru_cache(maxsize=32)
def get_uni_all_history(contract, page, limit=10, pageSize=10):
    """
    查询历史记录:
        1.单页默认10条
        2.交易详情批量查询,交易收据单独循环查询
    """
    page = max(1, int(page))
    offset = (page - 1) * limit
    # 已同步得交易数量
    uni_already_synced_tx_count_key = "uni_already_synced_tx_count"
    try:
        if not contract or len(str(contract)) != 42:
            result = {
                "message": "invalid contract address",
                "totalCount": 0,
                "page": page,
                "pageSize": pageSize,
                "contract": contract,
                "data": []
            }
        else:
            uni_sync_tx_count = json.loads(redis_client.get(uni_already_synced_tx_count_key))
            total = uni_sync_tx_count
            sql = f"""
                SELECT
                    block_height, block_hash, tx_hash
                FROM
                    {table}
                where
                    id > {offset} limit {limit}
            """
            txids = []
            datas = mysqldb.query(sql)
            txids = [data.get("tx_hash") for data in datas]
            tx_details = demo_get_many_transactions(txids)
            tx_receipts = demo_get_many_receipts(txids)
            data = []
            for index, tx in enumerate(tx_details):
                tmp = tx.get("result", {})
                txid = tmp.get("hash")
                if not txid:
                    continue
                try:
                    tx_receipt_result = tx_receipts[index]
                except Exception:
                    continue
                tx_receipt = tx_receipt_result.get("result", {})
                if tx_receipt:
                    status = tx_receipt.get("status")
                    gasUsed = tx_receipt.get("gasUsed")
                    logs = tx_receipt.get("logs")
                else:
                    status = ""
                    gasUsed = ""
                    logs = []
                tmp['status'] = status
                tmp['gasUsed'] = gasUsed
                tmp['logs'] = logs
                data.append(tmp)
            result = {
                "message": "success",
                "totalCount": total,
                "page": page,
                "pageSize": pageSize,
                "contract": contract,
                "data": data
            }
    except Exception as e:
        result = {
            "message": "Error: " + str(e),
            "totalCount": 0,
            "page": 0,
            "pageSize": pageSize,
            "contract": contract,
            "data": []
        }
    return result
