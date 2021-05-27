#!/usr/bin/env python
# encoding=utf-8
import json
import requests
import redis
import time
import pymongo
import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

UNI_CONTRACT = "0x7a250d5630b4cf539739df2c5dacb4c659f2488d"

NODE = "https://mainnet.infura.io/v3/ae11572b527444de8713205f186027ef"

TX_NODE = "http://127.0.0.1:18759"

client = pymongo.MongoClient("mongodb://nftscan:nftscan!123@124.156.168.171:27017/nftscan?authSource=nftscan")


redis_conn = redis.Redis(host='127.0.0.1', port=6379, password="redis-123456")

def nft_sync_server():
    """
    同步uni合约历史记录
    起始同步高度: 10207858
    """
    # 已同步的高度
    uni_sync_his_number_key = "nftscan_already_synced_number"
    # 已同步得交易数量
    uni_already_synced_tx_count_key = "nftscan_already_synced_tx_count"
    # 每次请求的块数,动态调整
    interval = 5

    while True:
        # data = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}
        # res = requests.post(NODE, json=data)
        # result = res.json()
        # 查询当前最新高度
        # new_block_num = int(result.get("result", "0"), base=16)
        new_block_num = 12345678
        # 延迟2个区块解析数据,防止分叉情况
        new_block_num = new_block_num - 2
        # 初始化已同步的高度
        synced_block_number = redis_conn.get(uni_sync_his_number_key)
        if not synced_block_number:
            return False
        already_synced = int(synced_block_number)
        # 2021-05-16发现问题: interval至少从2开始,若interval=1则可能出现end_block=start_block相导致无限等待的情况
        interval = max(2, interval)
        start_block = already_synced + 1
        end_block = min(already_synced+interval, new_block_num)
        # 若已追到最新区块则等会儿
        if start_block >= end_block:
            logger.info(f"[waiting]: interval:{interval}, start_block:{start_block}, end_block:{end_block}")
            interval = 1
            time.sleep(30)
            continue
        txs = []
        for num in range(start_block, end_block):
            block_num = hex(int(num))
            try:
                start_time = time.time()
                data = {"jsonrpc": "2.0", "method": "eth_getBlockByNumber", "params": [block_num, True], "id": 1}
                res = requests.post(TX_NODE, json=data)
                result = res.json()
                end_time = time.time()
                diff = round(end_time - start_time, 2)
                logger.info(f"request block num:{num} cost_time: {diff}s")
                datas = result.get("result")
                block_hash = datas.get("hash")
                timestamp = datas.get("timestamp")
                if timestamp:
                    tx_time = int(str(timestamp), base=16)
                else:
                    tx_time = 123456
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
                    tx["timestamp"] = tx_time
                    txs.append(tx)
                already_synced = num
            except Exception as e:
                logger.info(e)
                break
        logger.info(f"interval:{interval}, start_block:{start_block}, end_block:{end_block}")
        if not txs:
            interval += 5
            redis_conn.set(uni_sync_his_number_key, already_synced)
            continue
        tx_ids = [tx.get("hash") for tx in txs]
        start_time = time.time()
        tx_receipts = demo_get_many_receipts(tx_ids)
        end_time = time.time()
        diff = round(end_time - start_time, 2)
        tx_counts = len(tx_ids)
        logger.info(f"tx_receipts count: {tx_counts} cost_time: {diff}s")
        if not tx_receipts:
            continue
        full_detail_txs = []
        for index, tx in enumerate(txs):
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
            tx['status'] = status
            tx['gasUsed'] = gasUsed
            tx['logs'] = logs
            full_detail_txs.append(tx)
        txs_count = len(txs)
        if txs_count < 50:
            interval += 1
        else:
            interval -= 1
        sync_block_count = end_block - start_block
        logger.info(f"start:{start_block}, end:{end_block}, block_count:{sync_block_count}, get tx_count:{txs_count}")
        try:
            db = client.nftscan
            collection = db.history_raw
            collection.insert_many(full_detail_txs)
        except Exception as e:
            logger.info(e)
            continue
        redis_conn.set(uni_sync_his_number_key, already_synced)
        redis_conn.incrby(uni_already_synced_tx_count_key, txs_count)

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
    res = requests.post(TX_NODE, json=payload)
    result = res.json()
    return result



if __name__ == "__main__":
    nft_sync_server()
