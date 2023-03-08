#encoding=utf-8
import time
import requests
from logger import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from noderpc import demo_get_block_number, demo_get_block_by_number, demo_get_transaction_receipt


ENDPOINT = "https://bsc-mainnet.nodereal.io/v1/a4a9f892480d45e395f93945c4b77c6e"


def main():
    last_process_number = 0
    while True:
        block_number = demo_get_block_number(node_url=ENDPOINT)
        if not block_number:
            time.sleep(2)
            continue
        new = int(block_number, base=16)
        if not last_process_number:
            last_process_number = new
        
        with requests.Session() as session:
            session.headers.update({"slug": str(last_process_number)})
            for number in range(last_process_number, new):
                result = demo_get_block_by_number(hex(number), node_url=ENDPOINT)
                if not result:
                    continue
                txs = result.get("transactions", []) if result else []
                txids = [tx.get("hash") for tx in txs]
                count = len(txids)
                slug = session.headers.get("slug")
                logging.info(f"=========================start process block: {number}, tx count {count}, session: {slug}")
                with ProcessPoolExecutor(max_workers=6) as executor:
                    futures = [executor.submit(process_tx_receipt, txid, session) for txid in txids]
                    for future in as_completed(futures):
                        break
                last_process_number = number
                logging.info(f"--------------------------block {number} process success-------------------------------------")
            time.sleep(5)


def process_tx_receipt(txid, session):
    result = demo_get_transaction_receipt(txid, node_url=ENDPOINT, session=session)


if __name__ == "__main__":
    main()
