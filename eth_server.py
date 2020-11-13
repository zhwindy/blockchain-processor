#!/usr/bin/env python
# encoding=utf-8
import json
import requests
import redis
import time
from flask import Flask, request, make_response, jsonify

app = Flask(__name__)

rt = redis.Redis(host='127.0.0.1', port=6379)

NODE_URL = "http://127.0.0.1:18759"

OUT_URL = "http://172.17.67.187:18759"


@app.route('/')
def main():
    """
    欢迎信息
    """
    data = {
        "message": "welcome to blockchain world!"
    }
    return make_response(jsonify(data))


@app.route('/block/<string:contract>/')
def block(contract):
    """
    查询当前节点信息
    """
    if not contract or len(str(contract)) != 42:
        info = {
            "message": "failed",
            "contract": contract
        }
    else:
        urls = [NODE_URL]

        token_info_key = "token_info"
        result = rt.get(token_info_key)
        info = json.loads(result)

        data = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}
        new_block_nums = []
        for url in urls:
            res = requests.post(url, json=data)
            result = res.json()
            new_block_nums.append(int(result.get("result", "0"), base=16))

        info['new_block'] = max(new_block_nums)
        info['server_time'] = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        info['contract'] = contract

    return make_response(jsonify(info))


@app.route('/pending')
def pending():
    """
    查询pending相关信息
    """
    math = []
    data = {"jsonrpc": "2.0", "method": "txpool_content", "params": [], "id": 1}
    res = requests.post(NODE_URL, json=data)
    mempool_result = res.json()

    datas = mempool_result.get("result")
    pending = datas.get("pending", {})
    queued = datas.get("queued", {})

    gas_data = {"jsonrpc": "2.0", "method": "eth_gasPrice", "params": [], "id": 1}
    res_1 = requests.post(NODE_URL, json=gas_data)
    rt = res_1.json()
    gas_price = int(rt.get("result", "0"), base=16)

    for txs in pending.values():
        for tx in txs.values():
            v_in = tx.get("input", "")
            from_info = tx.get("from", "")
            gasPrice = int(tx.get("gasPrice", "0"), base=16)
            # txid = tx.get("hash", "")
            if not from_info:
                continue
            # if v_in and ("0xf6a4932f" in v_in) and (gasPrice > (gas_price - 5000000000)):
            if v_in and ("0xf6a4932f" in v_in) and (gasPrice > gas_price):
                math.append(tx)

    for txs in queued.values():
        for tx in txs.values():
            v_in = tx.get("input", "")
            from_info = tx.get("from", "")
            gasPrice = int(tx.get("gasPrice", "0"), base=16)
            # txid = tx.get("hash", "")
            if not from_info:
                continue
            # if v_in and ("0xf6a4932f" in v_in) and (gasPrice > (gas_price - 5000000000)):
            if v_in and ("0xf6a4932f" in v_in) and (gasPrice > gas_price):
                math.append(tx)
    # sorted_math = sorted(math, key=lambda x: x['gasPrice'], reverse=True)
    # ss = sorted_math[0] if sorted_math else {}
    ss = math[0] if math else {}
    gasPrice = int(ss.get("gasPrice", "0"), base=16)

    pending_result = {
        "count": len(math),
        "txgasPrice": gasPrice,
        "bestgasPrice": gas_price
    }
    return make_response(jsonify(pending_result))


@app.route('/mempool')
def mempool():
    math = []
    data = {"jsonrpc": "2.0", "method": "txpool_content", "params": [], "id": 1}
    res = requests.post(NODE_URL, json=data)
    result = res.json()
    datas = result.get("result")
    pending = datas.get("pending", {})
    queued = datas.get("queued", {})
    if not datas:
        return []
    for txs in pending.values():
        for tx in txs.values():
            v_in = tx.get("input", "")
            from_info = tx.get("from", "")
            if not from_info:
                continue
            if v_in and ("0xf6a4932f" in v_in):
                math.append(tx)

    for txs in queued.values():
        for tx in txs.values():
            v_in = tx.get("input", "")
            from_info = tx.get("from", "")
            if not from_info:
                continue
            if v_in and ("0xf6a4932f" in v_in):
                math.append(tx)
    mempool_result = {
        "message": "success",
        "data": math,
    }
    return make_response(jsonify(mempool_result))


@app.route('/history/<string:contract>/')
def history(contract):
    """
    历史记录
    """
    if not contract or len(str(contract)) != 42:
        result = {
            "message": "failed",
            "contract": contract,
            "data": []
        }
    else:
        history_key = "token_history"
        history = rt.lrange(history_key, 0, 50)
        his = [json.loads(i) for i in history]
        result = {
            "message": "success",
            "contract": contract,
            "data": his
        }
    return make_response(jsonify(result))


@app.route('/broadcast', methods=['POST'])
def broadcast():
    """
    广播交易
    """
    urls = [
        "http://127.0.0.1:18759",
        "https://web3.mytokenpocket.vip",
        # "http://10.66.178.171:18759",
        "https://mainnet.infura.io/v3/dd70b311da9a4147b5974c8698dec90b",
        # "http://172.17.67.187:18759",
        "https://ethje115qd1174d.swtc.top",
        "https://main-rpc.linkpool.io",
        "https://eth626892d.jccdex.cn",
        "https://white-weathered-glade.quiknode.pro/b4833cf3833d3cdd7612734c5dc853eb3c33415d/",
        "https://ethje116qd6892d.swtc.top",
        "https://ethjeqd0430103d.swtc.top"
    ]
    request_data = json.loads(request.data)

    rawtx = request_data.get("rawtx")
    if not rawtx:
        result = {"result": 0}
    else:
        send_data = {"jsonrpc": "2.0", "method": "eth_sendRawTransaction", "params": [rawtx], "id": 1}
        for url in urls:
            requests.post(url, json=send_data, timeout=5)
        result = {"result": 1}

    return make_response(jsonify(result))


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 18788
    debug = True
    app.run(host=host, port=port, debug=debug)
