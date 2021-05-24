#encoding=utf-8
import json
import redis
import requests
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


def test():
    """
    查询历史记录:
        1.单页默认10条
        2.交易详情批量查询,交易收据单独循环查询
    """
    # 已同步得交易数量
    uni_already_synced_tx_count_key = "uni_already_synced_tx_count"
    uni_sync_tx_count = json.loads(redis_client.get(uni_already_synced_tx_count_key))
    total = uni_sync_tx_count
    sql = f"""
        SELECT
            block_height, block_hash, tx_hash, timestamp
        FROM
            {table}
        where
            id > 1880000 limit 10
    """
    txids = []
    datas = mysqldb.query(sql)
    txids = [data.get("tx_hash") for data in datas]
    tx_details = demo_get_many_transactions(txids)
    tx_receipts = demo_get_many_receipts(txids)
    result_list = []
    for index, tx in enumerate(tx_details):
        data = datas[index]
        timestamp = data.get("timestamp")
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
        tmp['timestamp'] = timestamp
        result_list.append(tmp)
    content = json.dumps(result_list)
    print(content)
    redis_client.set("test_content", content)

if __name__ == '__main__':
    test()
