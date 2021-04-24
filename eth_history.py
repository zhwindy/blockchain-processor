#!/usr/bin/env python
# encoding=utf-8
import json
import requests
import redis
import time

NODE_URL = "http://127.0.0.1:18759"

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
}

ALL_ADDRESS = True
MY_ADDRESS_LIST = ["0x9c9800ea23ea152b57dc9f2d2e0d85b2fc027c44"]

UNI_CONTRACT = "0x7a250d5630b4cf539739df2c5dacb4c659f2488d"


def sync_token_his_info():
    """
    同步历史记录
    """
    sync_his_number_key = "his_already_synced_number"
    rt = redis.Redis(host='127.0.0.1', port=6379, password="redis-123456")

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
                v_input = tx.get("input", "")
                if not v_input:
                    continue
                if ("0xf6a4932f" not in v_input):
                    continue
                v_from = tx.get("from", "")
                if not v_from:
                    continue
                v_to = tx.get("to", "").lower()
                if not v_to:
                    continue
                if ALL_ADDRESS:
                    if v_to == NEST_COCNTRACT:
                        tx['symbol'] = "NEST"
                        tx['contract'] = NEST_COCNTRACT
                    elif v_to == nTOKEN_COCNTRACT:
                        for contract in TOKEN_CONTRACT.values():
                            if del_0x(contract) in v_input:
                                tx['symbol'] = CONTRACT_TOKEN[contract]
                                tx['contract'] = contract
                                break
                    else:
                        continue
                    history.append(tx)
                else:
                    if str(v_from).lower() in MY_ADDRESS_LIST:
                        history.append(tx)

            for his in history:
                tmp = {}
                symbol = his.get("symbol")
                contract = his.get("contract")
                if not symbol or not contract:
                    continue
                txid = his.get("hash")
                if not txid:
                    continue
                data = {"jsonrpc": "2.0", "method": "eth_getTransactionReceipt", "params": [txid], "id": 1}

                res = requests.post(NODE_URL, json=data)
                result = res.json()
                tx_detail = result.get("result")
                status = tx_detail.get("status")
                if status and status == "0x1":
                    tmp['is_error'] = "0"
                else:
                    tmp['is_error'] = "1"
                tmp['txid'] = his['hash']
                tmp['contract'] = his['contract']
                tmp['symbol'] = his['symbol']
                tmp['from'] = his['from']
                tmp['to'] = his['to']
                tmp['value'] = his['value']
                tmp['block_number'] = str(int(his.get("blockNumber", "0"), base=16))
                tmp['gas'] = str(int(his.get("gas", "0"), base=16))
                tmp['gas_price'] = str(int(his.get("gasPrice", "0"), base=16))
                tmp['nonce'] = str(int(his.get("nonce", "0"), base=16))

                token_history_key = str(symbol).lower() + "_" + str(contract).lower() + "_his"
                rt.lpush(token_history_key, json.dumps(tmp))
                # 每个token只保留1000条历史记录
                rt.ltrim(token_history_key, 0, 1000)
            rt.set(sync_his_number_key, num)

        time.sleep(30)


def sync_uni_v2_his_info():
    """
    同步uni合约历史记录
    """
    sync_his_number_key = "his_already_synced_number"
    token_history_key =  "uni_v2_" + UNI_CONTRACT + "_his"

    rt = redis.Redis(host='127.0.0.1', port=6379, password="redis-123456")

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
                rt.lpush(token_history_key, json.dumps(tx))
                # 保留1000条uni历史记录
                rt.ltrim(token_history_key, 0, 1000)
                rt.set(sync_his_number_key, num)

        time.sleep(10)


def del_0x(contract):
    """
    去掉合约地址开头的0x标志
    """
    return str(contract).replace("0x", "").lower()


if __name__ == "__main__":
    sync_uni_v2_his_info()
