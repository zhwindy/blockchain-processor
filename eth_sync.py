#!/usr/bin/env python
#encoding=utf-8
import json
import requests
import redis
import time

prev_block_number = 0 
prev_gasPrice = 0


def sync_block_info_new():
    key = "block_info"
    sync_block_key = "sync_block_info"
    rt = redis.Redis(host='127.0.0.1', port=6379)
    # url = "http://127.0.0.1:18759"
    url = "http://10.66.178.171:18759"

    while True:
        sync_info = rt.get(sync_block_key)

        data = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}
        res = requests.post(url, json=data)
        result = res.json()
        newest_block_number = int(result.get("result", "0"), base=16)

        new_block_number = 0
        new_gasPrice = 0

        if not sync_info:
            sync_info = newest_block_number
        # print "已同步到区块:", sync_info
        for num in range(int(sync_info)+1, newest_block_number+1):
            # print "检测区块:", num
            block_num = hex(int(num))
            data = {"jsonrpc": "2.0", "method": "eth_getBlockByNumber", "params": [block_num, True], "id": 1}
            res = requests.post(url, json=data)
            result = res.json()
            datas = result.get("result")
            transactions = datas.get("transactions", [])
            if not transactions:
                continue
            for tx in transactions:
                v_in = tx.get("input", "")
                if not v_in:
                    continue
                if ("0xf6a4932f" not in v_in):
                    continue
                new_block_number = int(tx.get("blockNumber", "0"), base=16)
                new_gasPrice = int(tx.get("gasPrice", "0"), base=16)

            if new_block_number and new_gasPrice:
                block_info = {
                    "nest_block": new_block_number,
                    "gasPrice": new_gasPrice,
                }
                rt.set(key, json.dumps(block_info))
        rt.set(sync_block_key, newest_block_number)
        time.sleep(0.2)


def sync_block_info():
    key = "block_info"
    rt = redis.Redis(host='127.0.0.1', port=6379)
    url = "http://10.66.178.171:18759"
    global prev_block_number
    global prev_gasPrice

    while True:
        data = {"jsonrpc": "2.0", "method": "eth_getBlockByNumber", "params": ["latest", True], "id": 1}
        new_block_number = 0
        new_gasPrice = 0
        res = requests.post(url, json=data)
        result = res.json()
        datas = result.get("result")
        transactions = datas.get("transactions", [])
        block_number = int(datas.get("number", "0"), base=16)
        if block_number and (block_number != prev_block_number):
            if not transactions:
                continue
            for tx in transactions:
                v_in = tx.get("input", "")
                if not v_in:
                    continue
                if ("0xf6a4932f" not in v_in):
                    continue
                new_block_number = int(tx.get("blockNumber", "0"), base=16)
                new_gasPrice = int(tx.get("gasPrice", "0"), base=16)

            nest_block = new_block_number if new_block_number else prev_block_number
            gasPrice = new_gasPrice if new_gasPrice else prev_gasPrice

            prev_block_number = nest_block
            prev_gasPrice = gasPrice

            block_info = {
                "nest_block": nest_block,
                "gasPrice": gasPrice,
            }
            rt.set(key, json.dumps(block_info))
        time.sleep(0.1)


if __name__ == "__main__":
    sync_block_info_new()

