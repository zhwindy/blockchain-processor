#encoding=utf-8
import time
import requests
from concurrent.futures import ProcessPoolExecutor, as_completed
from noderpc import demo_get_block_number, demo_get_block_by_number, demo_get_transaction_receipt


def main():
    last_process_number = None
    while True:
        block_number = demo_get_block_number()
        b1 = int(block_number, base=16)
        # print("get block_number:", b1)
        # 首次赋值
        if not last_process_number:
            last_process_number = b1 

        for number in range(last_process_number, b1):
            print("process:", number)
            result = demo_get_block_by_number(hex(number))
            txs = result.get("transactions", []) if result else []
            txids = [tx.get("hash") for tx in txs]
            with ProcessPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(demo_get_transaction_receipt, txid) for txid in txids]
                for future in as_completed(futures):
                    continue
                    # print(future.result())
        last_process_number = b1
        time.sleep(5)


if __name__ == "__main__":
    main()
