#!/usr/bin/env python
# encoding=utf-8
import json
import requests
import redis
import time


def sync_pending_info():
    key = "pending"
    rt = redis.Redis(host='127.0.0.1', port=6379)
    url = "http://127.0.0.1:18759"
    while True:
        math = []
        data = {"jsonrpc": "2.0", "method": "txpool_content", "params": [], "id": 1}
        res = requests.post(url, json=data)
        result = res.json()
        datas = result.get("result")
        pending = datas.get("pending", {})
        queued = datas.get("queued", {})

        for txs in pending.values():
            for tx in txs.values():
                v_in = tx.get("input", "")
                if v_in and ("0xf6a4932f" in v_in):
                    math.append(tx)
        for txs in queued.values():
            for tx in txs.values():
                v_in = tx.get("input", "")
                if v_in and ("0xf6a4932f" in v_in):
                    math.append(tx)
        sorted_math = sorted(math, key=lambda x: x['gasPrice'], reverse=True)
        ss = sorted_math[0] if sorted_math else {}
        gasPrice = int(ss.get("gasPrice", "0"), base=16)
        pending_result = {"count": len(sorted_math),"gasPrice": gasPrice}
        rt.set(key, json.dumps(pending_result))
        time.sleep(0.5)


if __name__ == "__main__":
    sync_pending_info()
