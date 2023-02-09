#encoding=utf-8
import requests

NODE_URL = "https://eth-mainnet.nodereal.io/v1/a4a9f892480d45e395f93945c4b77c6e"


def demo_get_transaction_receipt(txid):
    """
    查询交易收据
    """
    data = {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionReceipt",
        "params": [txid],
        "id": 1
    }
    res = requests.post(NODE_URL, json=data)
    result = res.json()
    return result.get("result", {})


def demo_get_block_number():
    """
    查最新高度
    """
    data = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}
    res = requests.post(NODE_URL, json=data)
    result = res.json()
    return result.get("result", {})


def demo_get_block_by_number(block_number):
    """
    用区块高度查询区块详情
    """
    data = {"jsonrpc": "2.0", "method": "eth_getBlockByNumber", "params": [block_number, True], "id": 1}
    res = requests.post(NODE_URL, json=data)
    result = res.json()
    return result.get("result", {})
