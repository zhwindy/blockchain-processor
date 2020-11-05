#!/usr/bin/env python
#encoding=utf-8
import json
import requests
import redis
import time


def sync_his_info():
    """
    同步历史记录
    """
    # url = "http://127.0.0.1:18759"
    url = "http://172.17.67.187:18759"
    sync_his_key = "sync_his_info"
    history_key = "history"
    rt = redis.Redis(host='127.0.0.1', port=6379)

    while True:
        data = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}
        res = requests.post(url, json=data)
        result = res.json()
        new_block_num = int(result.get("result", "0"), base=16)

        synced_block_number = int(rt.get(sync_his_key))

        #print(100*"*", synced_block_number, new_block_num)

        for num in range(synced_block_number+1, new_block_num):
            #print(10*"*", 'sync:', num)
            block_num = hex(int(num))
            data = {"jsonrpc": "2.0", "method": "eth_getBlockByNumber", "params": [block_num, True], "id": 1}
            res = requests.post(url, json=data)
            result = res.json()
            datas = result.get("result")
            transactions = datas.get("transactions", [])
            if not transactions:
                continue
            history = []
            for tx in transactions:
                new_block_number = int(tx.get("blockNumber", "0"), base=16)
                # 若块高没有增加,则略过
                v_in = tx.get("input", "")
                if not v_in:
                    continue
                if ("0xf6a4932f" not in v_in):
                    continue
                v_from = tx.get("from", "")
                if v_from and (str(v_from).lower() in  ["0x9c9800ea23eA152B57DC9f2D2E0D85B2fC027C44".lower()]):
                    history.append(tx)

            for his in history:
                txid = his.get("hash")
                if not txid:
                    continue
                data = {"jsonrpc": "2.0", "method": "eth_getTransactionReceipt", "params": [txid], "id": 1}

                res = requests.post(url, json=data)
                result = res.json()
                tx_detail = result.get("result")
                # print(10*"*", tx_detail)
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
            synced_block_number = num
            rt.set(sync_his_key, synced_block_number)

        time.sleep(10)


if __name__ == "__main__":
    sync_his_info()

