#encoding=utf-8
import time
from noderpc import demo_get_block_receipts


ENDPOINT = "https://mainnet.infura.io/v3/c107c439187e4b7c8b18c8684ba34a86"


def main():
    start_block_number = 21303925
    end_block_number = 21525889
    # end_block_number = 21303935
    total_l1_fee = 0
    total_blob_fee = 0
    while start_block_number <= end_block_number:
        block_receipts = demo_get_block_receipts(hex(start_block_number), node_url=ENDPOINT)
        if not block_receipts:
            continue
        block_l1_fee = 0
        block_blob_fee = 0
        for rece in block_receipts:
            from_addr = rece.get("from", "")
            if str(from_addr).strip().lower() == "0x68bdfece01535090c8f3c27ec3b1ae97e83fa4aa":
                hex_gas_used = rece.get("gasUsed")
                hex_gas_price = rece.get("effectiveGasPrice")
                if hex_gas_used and hex_gas_price:
                    gas_used = int(hex_gas_used, base=16)
                    gas_price = int(hex_gas_price, base=16)
                    tx_l1_fee = gas_used * gas_price
                    block_l1_fee += tx_l1_fee

                hex_blobGasPrice = rece.get("blobGasPrice")
                hex_blobGasUsed = rece.get("blobGasUsed")
                if hex_blobGasPrice and hex_blobGasUsed:
                    blob_gas_used = int(hex_blobGasPrice, base=16)
                    blob_gas_price = int(hex_blobGasUsed, base=16)
                    tx_blob_fee = blob_gas_used * blob_gas_price
                    block_blob_fee += tx_blob_fee
            else:
                continue
        total_l1_fee += block_l1_fee
        total_blob_fee += block_blob_fee
        
        print(f"block: {start_block_number}, block_l1_fee: {block_l1_fee}, block_blob_fee: {block_blob_fee}")

        time.sleep(0.1)
        start_block_number+=1
    
    print("total l1 fee:", total_l1_fee)
    print("total blob fee:", total_blob_fee)
    total_fee = total_l1_fee + total_blob_fee
    print("total fee:", total_fee)


if __name__ == "__main__":
    main()
