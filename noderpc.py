#encoding=utf-8
import requests
from logger import logging

NODE_ENDPOINT = "https://eth-mainnet.nodereal.io/v1/a4a9f892480d45e395f93945c4b77c6e"

session = requests.Session()


def demo_get_block_number(node_url=None):
    """
    query
    """
    try:
        url = node_url if node_url else NODE_ENDPOINT
        data = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}
        # res = requests.post(url, json=data)
        res = session.post(url, json=data)
        result = res.json()
    except Exception as e:
        logging.info(e)
        return None
    return result.get("result", {})


def demo_get_block_by_number(block_number, node_url=None):
    """
    get block
    """
    url = node_url if node_url else NODE_ENDPOINT
    data = {"jsonrpc": "2.0", "method": "eth_getBlockByNumber", "params": [block_number, True], "id": 1}
    try:
        # res = requests.post(url, json=data)
        res = session.post(url, json=data)
        result = res.json()
    except Exception as e:
        logging.info(f"get block: {block_number} error: {e}")
        return None
    return result.get("result", {})


def demo_get_transaction_receipt(txid, node_url=None):
    """
    get receipt
    """
    data = {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionReceipt",
        "params": [txid],
        "id": 1
    }
    url = node_url if node_url else NODE_ENDPOINT
    try:
        # res = requests.post(url, json=data)
        res = session.post(url, json=data)
        result = res.json()
    except Exception as e:
        logging.info(f"get tx: {txid} error: {e}")
        return None
    return result.get("result", {})
