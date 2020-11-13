#!/usr/bin/env python
# encoding=utf-8
import json
import requests
import redis
import time

NODE_URL = "http://127.0.0.1:18759"


def syncing_newest_block_info():
    token_info_key = "token_info"
    sync_node_number_key = "node_already_synced_number"
    rt = redis.Redis(host='127.0.0.1', port=6379)
    while True:
        data = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}
        res = requests.post(NODE_URL, json=data)
        result = res.json()
        new_block_num = int(result.get("result", "0"), base=16)

        synced_block_number = rt.get(sync_node_number_key)
        if not synced_block_number:
            already_synced = int(new_block_num) - 10
        else:
            already_synced = int(synced_block_number)

        new_block_number, new_gasPrice = 0, 0

        for num in range(int(already_synced) + 1, new_block_num + 1):
            block_num = hex(int(num))
            data = {"jsonrpc": "2.0", "method": "eth_getBlockByNumber", "params": [block_num, True], "id": 1}
            res = requests.post(NODE_URL, json=data)
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
                token_block_info = {
                    "nest_block": new_block_number,
                    "gasPrice": new_gasPrice,
                }
                rt.set(token_info_key, json.dumps(token_block_info))
            rt.set(sync_node_number_key, num)
        time.sleep(0.2)


if __name__ == "__main__":
    syncing_newest_block_info()
