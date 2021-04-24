#!/usr/bin/env python
# encoding=utf-8
import json
import requests
import redis
import time
from flask import Flask, request, make_response, jsonify

app = Flask(__name__)

rt = redis.Redis(host='127.0.0.1', port=6379, password="redis-123456")

NODE_URL = "http://127.0.0.1:18759"

OUT_URL = "http://172.17.67.187:18759"

# NEST报价合约地址
NEST_COCNTRACT = "0xc83e009c7794e8f6d1954dc13c23a35fc4d039f6"
# Token报价合约地址
nTOKEN_COCNTRACT = "0x1542e790a742333ea6a2f171c5d07a2e7794eef4"

TOKEN_CONTRACT = {
    "HBTC": "0x0316eb71485b0ab14103307bf65a021042c6d380",
    "HT": "0x6f259637dcd74c767781e37bc6133cd6a68aa161",
    "WBTC": "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",
    "DAI": "0x6b175474e89094c44da98b954eedeac495271d0f",
    "HUSD": "0xdf574c24545e5ffecb9a659c229253d4111d87e1",
    "YFI": "0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e",
    "YFIII": "0x4be40bc9681D0A7C24A99b4c92F85B9053Fc2A45",
    "UNI": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
    "NEST": "0xc83e009c7794e8f6d1954dc13c23a35fc4d039f6",
}

CONTRACT_TOKEN = {
    "0x0316eb71485b0ab14103307bf65a021042c6d380": "HBTC",
    "0x6f259637dcd74c767781e37bc6133cd6a68aa161": "HT",
    "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599": "WBTC",
    "0x6b175474e89094c44da98b954eedeac495271d0f": "DAI",
    "0xdf574c24545e5ffecb9a659c229253d4111d87e1": "HUSD",
    "0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e": "YFI",
    "0x4be40bc9681D0A7C24A99b4c92F85B9053Fc2A45": "YFIII",
    "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984": "UNI",
    "0xc83e009c7794e8f6d1954dc13c23a35fc4d039f6": "NEST",
}


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
            "message": "invalid contract address",
            "contract": contract
        }
    else:
        urls = [NODE_URL]

        token_contract = str(contract).lower()
        token_symbol = CONTRACT_TOKEN.get(token_contract)
        if not token_symbol:
            info = {
                "message": "not support contract",
                "contract": token_contract
            }
        else:
            token_info_key = str(token_symbol).lower() + "_" + token_contract + "_token"

            result = rt.get(token_info_key)
            info = json.loads(result)

            data = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}
            new_block_nums = []
            for url in urls:
                res = requests.post(url, json=data)
                result = res.json()
                new_block_nums.append(int(result.get("result", "0"), base=16))

            info['new_block_height'] = max(new_block_nums)
            info['server_time'] = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    return make_response(jsonify(info))


@app.route('/pending/<string:contract>/')
def pending(contract):
    """
    查询pending相关信息
    """
    if not contract or len(str(contract)) != 42:
        pending_result = {
            "message": "invalid contract address",
            "contract": contract
        }
    else:
        token_contract = str(contract).lower()
        token_symbol = CONTRACT_TOKEN.get(token_contract)
        if not token_symbol:
            pending_result = {
                "message": "not support contract",
                "contract": token_contract
            }
        else:
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
                    v_input = tx.get("input", "")
                    from_info = tx.get("from", "")
                    gasPrice = int(tx.get("gasPrice", "0"), base=16)
                    if not from_info:
                        continue
                    # if v_in and ("0xf6a4932f" in v_in) and (gasPrice > (gas_price - 5000000000)):
                    if not v_input:
                        continue
                    v_to = tx.get("to", "")
                    if not v_to:
                        continue
                    if ("0xf6a4932f" not in v_input):
                        continue
                    if (gasPrice < gas_price):
                        continue
                    if str(v_to).lower() == NEST_COCNTRACT:
                        math.append(tx)
                    else:
                        if (token_contract.replace("0x", "") in v_input):
                            math.append(tx)

            for txs in queued.values():
                for tx in txs.values():
                    v_input = tx.get("input", "")
                    from_info = tx.get("from", "")
                    gasPrice = int(tx.get("gasPrice", "0"), base=16)
                    if not from_info:
                        continue
                    if not v_input:
                        continue
                    # if v_in and ("0xf6a4932f" in v_in) and (gasPrice > (gas_price - 5000000000)):
                    if not v_input:
                        continue
                    v_to = tx.get("to", "")
                    if not v_to:
                        continue
                    if ("0xf6a4932f" not in v_input):
                        continue
                    if (gasPrice < gas_price):
                        continue
                    if str(v_to).lower() == NEST_COCNTRACT:
                        math.append(tx)
                    else:
                        if (token_contract.replace("0x", "") in v_input):
                            math.append(tx)
            # sorted_math = sorted(math, key=lambda x: x['gasPrice'], reverse=True)
            # ss = sorted_math[0] if sorted_math else {}
            ss = math[0] if math else {}
            gasPrice = int(ss.get("gasPrice", "0"), base=16)

            pending_result = {
                "mempool_count": len(math),
                "tx_gas_price": gasPrice,
                "best_gas_price": gas_price,
                "token_symbol": token_symbol,
                "token_contract": token_contract
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
            "message": "invalid contract address",
            "contract": contract,
            "data": []
        }
    else:
        token_contract = str(contract).lower()
        token_symbol = CONTRACT_TOKEN.get(token_contract)
        if not token_symbol:
            result = {
                "message": "not support contract",
                "contract": token_contract
            }
        else:
            token_history_key = str(token_symbol).lower() + "_" + str(token_contract).lower() + "_his"
            history = rt.lrange(token_history_key, 0, 50)
            his = [json.loads(i) for i in history]
            result = {
                "message": "success",
                "contract": contract,
                "data": his
            }
    return make_response(jsonify(result))


@app.route('/api/v2/history/<string:contract>/')
def uni_history(contract):
    """
    历史记录
    """
    if not contract or len(str(contract)) != 42:
        result = {
            "message": "invalid contract address",
            "contract": contract,
            "data": []
        }
    else:
        token_contract = str(contract).lower()
        token_history_key =  "uni_v2_" + token_contract + "_his"
        history = rt.lrange(token_history_key, 0, 100)
        his = [json.loads(i) for i in history]
        result = {
            "message": "success",
            "contract": token_contract,
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
    debug = False
    app.run(host=host, port=port, debug=debug)
