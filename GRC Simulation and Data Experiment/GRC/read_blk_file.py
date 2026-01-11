from bitcoin.core import CBlock
import os

with open("blk04832.dat", "rb") as f:
    while True:
        magic = f.read(4)
        if not magic:
            break
        size = int.from_bytes(f.read(4), "little")
        block_data = f.read(size)

        block = CBlock.deserialize(block_data)
        print("區塊哈希:", block.GetHash())
        print("版本:", block.nVersion)
        print("交易數量:", len(block.vtx))
        print("----------")

