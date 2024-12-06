#encoding=utf-8
import requests
# from logger import logging
import logging

logging.basicConfig(format='%(asctime)s-%(name)s-%(levelname)s-%(message)s', level=logging.INFO)



def demo_get_block_number(node_url=None, session=None, headers=None):
    """
    query
    """
    request_headers = {"Content-Type": "application/json"}
    if headers:
        request_headers.update(headers)
    try:
        data = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}
        if session:
            info = f"query block_number by session: {id(session)}"
            logging.info(info)
            res = session.post(node_url, json=data, headers=request_headers)
        else:
            res = requests.post(node_url, json=data, headers=request_headers)
        result = res.json()
    except Exception as e:
        logging.info(e)
        return None
    return result.get("result", {})


def demo_get_block_by_number(block_number, node_url=None, session=None, headers=None):
    """
    get block
    """
    request_headers = {"Content-Type": "application/json"}
    if headers:
        request_headers.update(headers)
    data = {"jsonrpc": "2.0", "method": "eth_getBlockByNumber", "params": [block_number, True], "id": 1}
    try:
        if session:
            info = f"get block by session: {id(session)}"
            logging.info(info)
            res = session.post(node_url, json=data, headers=request_headers)
        else:
            res = requests.post(node_url, json=data, headers=request_headers)
        result = res.json()
    except Exception as e:
        logging.info(f"get block: {block_number} error: {e}")
        return None
    return result.get("result", {})


def demo_get_transaction_receipt(txid, node_url=None, session=None, headers=None):
    """
    get receipt
    """
    request_headers = {"Content-Type": "application/json"}
    if headers:
        request_headers.update(headers)
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
            res = session.post(node_url, json=data, headers=request_headers)
        else:
            res = requests.post(node_url, json=data, headers=request_headers)
        result = res.json()
    except Exception as e:
        logging.info(f"get tx: {txid} error: {e}")
        return None
    return result.get("result", {})


def demo_get_block_receipts(block_number, node_url=None, session=None, headers=None):
    """
    get block receipts
    """
    request_headers = {"Content-Type": "application/json"}
    if headers:
        request_headers.update(headers)
    data = {
        "jsonrpc": "2.0",
        "method": "eth_getBlockReceipts",
        "params": [block_number],
        "id": 1
    }
    try:
        if session:
            slug = session.headers.get("slug")
            info = f"get {block_number} receipt by session: {slug}"
            logging.info(info)
            res = session.post(node_url, json=data, headers=request_headers)
        else:
            res = requests.post(node_url, json=data, headers=request_headers)
        result = res.json()
    except Exception as e:
        logging.info(f"get tx: {block_number} error: {e}")
        return None
    return result.get("result", {})
