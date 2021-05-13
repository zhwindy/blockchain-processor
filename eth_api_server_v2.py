#!/usr/bin/env python
# encoding=utf-8
import json
import requests
import time
from config.env import CONFIG
from service import redis_client, get_uni_all_history
from flask import Flask, request, make_response, jsonify

app = Flask(__name__)


@app.route('/')
def main():
    """
    欢迎信息
    """
    data = {
        "message": "welcome to blockchain world!"
    }
    return make_response(jsonify(data))


@app.route('/api/v2/history/<string:contract>/')
def uni_latest_history(contract):
    """
    最新50条记录
    """
    if not contract or len(str(contract)) != 42:
        result = {
            "message": "invalid contract address",
            "count": 0,
            "contract": contract,
            "data": []
        }
    else:
        token_contract = str(contract).lower()
        token_history_key =  "uni_v2_" + token_contract + "_his"
        history = redis_client.lrange(token_history_key, 0, 50)
        his = [json.loads(i) for i in history]
        result = {
            "message": "success",
            "count": 50,
            "contract": token_contract,
            "data": his
        }
    return make_response(jsonify(result))


@app.route('/api/v2/txs')
def uni_all_history():
    """
    uni的所有历史记录,有分页,默认每页20条记录
    """
    contract = request.args.get('contract')
    page = request.args.get('page', 1)

    result = get_uni_all_history(contract, page)

    return make_response(jsonify(result))


@app.route('/api/v2/sync/status')
def sync_status():
    """
    同步情况
    """
    # 已同步的高度
    uni_sync_his_number_key = "uni_his_already_synced_number"
    # 已同步得交易数量
    uni_already_synced_tx_count_key = "uni_already_synced_tx_count"

    server_time = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    uni_sync_block = json.loads(redis_client.get(uni_sync_his_number_key))
    uni_sync_tx_count = json.loads(redis_client.get(uni_already_synced_tx_count_key))

    result = {
        "message": "success",
        "uni_sync_tx_count": uni_sync_tx_count,
        "uni_sync_block": uni_sync_block,
        "server_time": server_time
    }
    return make_response(jsonify(result))


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 18788
    debug = CONFIG['debug']
    app.run(host=host, port=port, debug=debug)
