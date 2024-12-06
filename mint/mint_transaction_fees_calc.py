#encoding=utf-8
import time
from noderpc import demo_get_block_receipts


ENDPOINT = "https://asia.rpc.mintchain.io"


def main():
    start_block_number = 8297935
    end_block_number = 8341134
    start_timestamp = 1732204800
    end_timestamp = 1732291200
    total_fee = 0
    total_l1_fee = 0
    while start_block_number <= end_block_number:
        # print("start block:", start_block_number)
        block_receipts = demo_get_block_receipts(hex(start_block_number), node_url=ENDPOINT)
        if not block_receipts:
            continue
        block_fee = 0
        block_l1_fee = 0
        for rece in block_receipts:
            from_addr = rece.get("from", "")
            if str(from_addr) == "0xdeaddeaddeaddeaddeaddeaddeaddeaddead0001":
                continue
            else:
                hex_gas_used = rece.get("gasUsed")
                hex_gas_price = rece.get("effectiveGasPrice")
                hex_l1_fee = rece.get("l1Fee")
                if hex_gas_used and hex_gas_price:
                    gas_used = int(hex_gas_used, base=16)
                    gas_price = int(hex_gas_price, base=16)
                    tx_fee = gas_used * gas_price
                    block_fee += tx_fee
                if hex_l1_fee:
                    l1_fee += int(hex_l1_fee, base=16)
                    block_l1_fee += l1_fee

        total_fee += block_fee
        total_l1_fee += l1_fee
        
        print(f"block: {start_block_number}, block_fee: {block_fee}, total_fee: {total_fee}")

        time.sleep(0.1)
        start_block_number+=1
    
    print("total l1 fee:", total_l1_fee)
    return total_fee


if __name__ == "__main__":
    total_fee = main()
    print("total fee:", total_fee)
