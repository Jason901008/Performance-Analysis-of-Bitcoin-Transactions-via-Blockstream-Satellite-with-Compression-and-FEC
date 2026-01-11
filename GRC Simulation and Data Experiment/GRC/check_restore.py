#!/usr/bin/env python3
import sys, os

def compare_files(original, recovered):
    size_orig = os.path.getsize(original)
    size_rec = os.path.getsize(recovered)

    print(f"原始檔: {original} = {size_orig:,} bytes")
    print(f"還原檔: {recovered} = {size_rec:,} bytes")

    # 計算差異與比例
    diff = size_orig - size_rec
    percent = (size_rec / size_orig) * 100 if size_orig > 0 else 0

    print(f"\n缺少 {diff:,} bytes")
    print(f"還原比例: {percent:.2f}%")

    # 驗證前綴是否正確
    with open(original, "rb") as f1, open(recovered, "rb") as f2:
        data1 = f1.read(size_rec)
        data2 = f2.read()
        if data1 == data2:
            print("前綴比對: OK ✅ (還原檔是原始檔的正確前綴)")
        else:
            print("前綴比對: ❌ 不一致 (中間有錯誤或位元受損)")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python3 check_restore.py <原始檔> <還原檔>")
    else:
        compare_files(sys.argv[1], sys.argv[2])

