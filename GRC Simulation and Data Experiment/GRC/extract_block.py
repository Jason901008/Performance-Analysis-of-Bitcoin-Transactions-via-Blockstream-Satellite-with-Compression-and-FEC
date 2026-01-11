#!/usr/bin/env python3
import argparse, struct, hashlib, sys

MAGICS = {
    b'\xf9\xbe\xb4\xd9': 'mainnet',
    b'\x0b\x11\x09\x07': 'testnet',
    b'\xfa\xbf\xb5\xda': 'regtest',
    b'\xfd\xd9\xf1\xf2': 'signet',
}

def dbl_sha256(b: bytes) -> bytes:
    import hashlib
    return hashlib.sha256(hashlib.sha256(b).digest()).digest()

def calc_block_hash(block_payload: bytes) -> str:
    header = block_payload[:80]
    h = dbl_sha256(header)[::-1].hex()
    return h

def find_next_magic(f):
    # 逐位點進搜尋下一個魔數
    buf = b''
    while True:
        b = f.read(1)
        if not b: return None, None
        buf += b
        if len(buf) >= 4:
            last4 = buf[-4:]
            if last4 in MAGICS:
                return last4, f.tell() - 4

def iter_blocks(path):
    with open(path, 'rb') as f:
        while True:
            magic, pos = find_next_magic(f)
            if magic is None:
                return
            sz_b = f.read(4)
            if len(sz_b) < 4:
                return
            size = struct.unpack('<I', sz_b)[0]
            payload = f.read(size)
            if len(payload) < size:
                return
            yield pos, magic, size, payload

def main():
    ap = argparse.ArgumentParser(description="Extract one block from bitcoin .dat")
    ap.add_argument('--in', dest='inp', required=True, help='input bitcoin.dat (multi-block)')
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--nth', type=int, help='extract the N-th block in the file (1-based)')
    g.add_argument('--hash', dest='want_hash', help='extract the block matching this hash (hex, big-endian)')
    ap.add_argument('--out', required=True, help='output single-block dat file')
    args = ap.parse_args()

    idx = 0
    found = None
    for pos, magic, size, payload in iter_blocks(args.inp):
        idx += 1
        bhash = calc_block_hash(payload)
        if (args.nth and idx == args.nth) or (args.want_hash and bhash == args.want_hash.lower()):
            found = (magic, size, payload, bhash, idx)
            break

    if not found:
        target = f"N={args.nth}" if args.nth else f"hash={args.want_hash}"
        print(f"[!] Block not found ({target})")
        sys.exit(1)

    magic, size, payload, bhash, n = found
    with open(args.out, 'wb') as fo:
        fo.write(magic)
        fo.write(struct.pack('<I', len(payload)))
        fo.write(payload)

    net = MAGICS.get(magic, 'unknown')
    print(f"[ok] wrote {args.out}")
    print(f"     file index = {n}, network = {net}, payload bytes = {len(payload)}")
    print(f"     block hash = {bhash}")

if __name__ == '__main__':
    main()

