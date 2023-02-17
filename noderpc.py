#encoding=utf-8
import requests

NODE_ENDPOINT = "https://eth-mainnet.nodereal.io/v1/a4a9f892480d45e395f93945c4b77c6e"


def demo_get_block_number(node_url=None):
    """
    查最新高度
    """
    url = node_url if node_url else NODE_ENDPOINT
    data = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}
    res = requests.post(url, json=data)
    result = res.json()
    return result.get("result", {})


def demo_get_block_by_number(block_number, node_url=None):
    """
    用区块高度查询区块详情
    """
    url = node_url if node_url else NODE_ENDPOINT
    data = {"jsonrpc": "2.0", "method": "eth_getBlockByNumber", "params": [block_number, True], "id": 1}
    res = requests.post(url, json=data)
    result = res.json()
    return result.get("result", {})


def demo_get_transaction_receipt(txid, node_url=None):
    """
    查询交易收据
    """
    data = {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionReceipt",
        "params": [txid],
        "id": 1
    }
    url = node_url if node_url else NODE_ENDPOINT
    res = requests.post(url, json=data)
    result = res.json()
    return result.get("result", {})
