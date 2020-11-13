#!/usr/bin/env python
# encoding=utf-8
import json
import requests
import redis
import time

NEST_COCNTRACT = "0xc83e009c7794e8f6d1954dc13c23a35fc4d039f6"

NODE_URL = "http://127.0.0.1:18759"

TOKEN = {
    "NToken0001": "0x1f832091faf289ed4f50fe7418cfbd2611225d46",
    "HT": "0x6f259637dcd74c767781e37bc6133cd6a68aa161",
    "WBTC": "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",
    "DAI": "0x6b175474e89094c44da98b954eedeac495271d0f",
    "HUSD": "0xdf574c24545e5ffecb9a659c229253d4111d87e1",
    "YFI": "0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e",
    "YFIII": "0x4be40bc9681D0A7C24A99b4c92F85B9053Fc2A45",
    "UNI": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
}

ALL_ADDRESS = True
MY_ADDRESS_LIST = ["0x9c9800ea23ea152b57dc9f2d2e0d85b2fc027c44"]


def sync_token_his_info():
    """
    同步历史记录
    """
    sync_his_number_key = "his_already_synced_number"
    history_key = "token_history"
    rt = redis.Redis(host='127.0.0.1', port=6379)

    while True:
        data = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}
        res = requests.post(NODE_URL, json=data)
        result = res.json()
        # 查询当前最新高度
        new_block_num = int(result.get("result", "0"), base=16)
        # 初始化已同步的高度
        synced_block_number = rt.get(sync_his_number_key)
        if not synced_block_number:
            already_synced = int(new_block_num) - 10
        else:
            already_synced = int(synced_block_number)

        for num in range(already_synced + 1, new_block_num):
            block_num = hex(int(num))
            data = {"jsonrpc": "2.0", "method": "eth_getBlockByNumber", "params": [block_num, True], "id": 1}
            res = requests.post(NODE_URL, json=data)
            result = res.json()
            datas = result.get("result")
            transactions = datas.get("transactions", [])
            if not transactions:
                continue
            history = []
            for tx in transactions:
                v_in = tx.get("input", "")
                if not v_in:
                    continue
                if ("0xf6a4932f" not in v_in):
                    continue
                v_from = tx.get("from", "")
                if not v_from:
                    continue
                if ALL_ADDRESS:
                    history.append(tx)
                else:
                    if str(v_from).lower() in MY_ADDRESS_LIST:
                        history.append(tx)

            for his in history:
                txid = his.get("hash")
                if not txid:
                    continue
                data = {"jsonrpc": "2.0", "method": "eth_getTransactionReceipt", "params": [txid], "id": 1}

                res = requests.post(NODE_URL, json=data)
                result = res.json()
                tx_detail = result.get("result")
                status = tx_detail.get("status")
                if status and status == "0x1":
                    his['isError'] = "0"
                else:
                    his['isError'] = "1"
                his['blockNumber'] = str(int(his.get("blockNumber", "0"), base=16))
                his['gas'] = str(int(his.get("gas", "0"), base=16))
                his['gasPrice'] = str(int(his.get("gasPrice", "0"), base=16))
                his['nonce'] = str(int(his.get("nonce", "0"), base=16))
                rt.lpush(history_key, json.dumps(his))
            rt.set(sync_his_number_key, num)

        time.sleep(30)


if __name__ == "__main__":
    sync_token_his_info()
