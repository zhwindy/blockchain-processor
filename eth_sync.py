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


def syncing_newest_block_info():
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
                token_symbol, token_contract = None, None
                if v_to == NEST_COCNTRACT:
                    token_symbol = "NEST"
                    token_contract = NEST_COCNTRACT
                elif v_to == nTOKEN_COCNTRACT:
                    for contract in TOKEN_CONTRACT.values():
                        if del_0x(contract) in v_input:
                            token_symbol = CONTRACT_TOKEN[contract]
                            token_contract = contract
                            break
                else:
                    continue
                token_block_number = int(tx.get("blockNumber", "0"), base=16)
                token_gasPrice = int(tx.get("gasPrice", "0"), base=16)

                # 四个信息齐全才保存
                if token_block_number and token_gasPrice and token_symbol and token_contract:
                    token_info_key = str(token_symbol).lower() + "_" + str(token_contract).lower() + "_token"
                    token_block_info = {
                        "token_symbol": str(token_symbol),
                        "token_contract": str(token_contract),
                        "token_block": token_block_number,
                        "token_gasPrice": token_gasPrice,
                    }
                    rt.set(token_info_key, json.dumps(token_block_info))
            rt.set(sync_node_number_key, num)
        time.sleep(0.2)


def del_0x(contract):
    """
    去掉合约地址开头的0x标志
    """
    return str(contract).replace("0x", "").lower()


if __name__ == "__main__":
    syncing_newest_block_info()
