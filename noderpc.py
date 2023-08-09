#encoding=utf-8
import requests
from logger import logging


def demo_get_block_number(node_url=None, session=None):
    """
    query
    """
    try:
        data = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}
        if session:
            info = f"query block_number by session: {id(session)}"
            logging.info(info)
            res = session.post(node_url, json=data)
        else:
            res = requests.post(node_url, json=data)
        result = res.json()
    except Exception as e:
        logging.info(e)
        return None
    return result.get("result", {})


def demo_get_block_by_number(block_number, node_url=None, session=None):
    """
    get block
    """
    data = {"jsonrpc": "2.0", "method": "eth_getBlockByNumber", "params": [block_number, True], "id": 1}
    try:
        if session:
            info = f"get block by session: {id(session)}"
            logging.info(info)
            res = session.post(node_url, json=data)
        else:
            res = requests.post(node_url, json=data)
        result = res.json()
    except Exception as e:
        logging.info(f"get block: {block_number} error: {e}")
        return None
    return result.get("result", {})


def demo_get_transaction_receipt(txid, node_url=None, session=None):
    """
    get receipt
    """
    data = {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionReceipt",
        "params": [txid],
        "id": 1
    }
    try:
        if session:
            slug = session.headers.get("slug")
            info = f"get {txid} receipt by session: {slug}"
            logging.info(info)
            res = session.post(node_url, json=data)
        else:
            res = requests.post(node_url, json=data)
        result = res.json()
    except Exception as e:
        logging.info(f"get tx: {txid} error: {e}")
        return None
    return result.get("result", {})
