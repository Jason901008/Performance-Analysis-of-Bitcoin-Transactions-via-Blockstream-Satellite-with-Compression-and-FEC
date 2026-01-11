# split_fec_from_bin.py
CHUNK_SIZE = 133000  # 根據你之前的 bitcoin.zpaq_xx_15.fec 平均大小
input_file = "bitcoin_fec_restored.bin"

with open(input_file, "rb") as f:
    index = 0
    while True:
        chunk = f.read(CHUNK_SIZE)
        if not chunk:
            break
        with open(f"restored_{index:02d}.fec", "wb") as out:
            out.write(chunk)
        index += 1

print(f"切割完成，共 {index} 份 .fec 檔案")

