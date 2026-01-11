# parse_blkdat_headers.py
# List blocks in a blk*.dat file: magic, size, header fields, tx count, and block hash.

import sys, struct, hashlib, datetime

MAGIC_MAIN = b'\xf9\xbe\xb4\xd9'   # mainnet
MAGIC_TEST = b'\x0b\x11\x09\x07'   # testnet3
MAGIC_REGT = b'\xfa\xbf\xb5\xda'   # regtest
MAGICS = {MAGIC_MAIN: "mainnet", MAGIC_TEST: "testnet", MAGIC_REGT: "regtest"}

def read_varint(f):
    fb = f.read(1)
    if not fb:
        raise EOFError
    v = fb[0]
    if v < 0xfd:
        return v, 1
    if v == 0xfd:
        return struct.unpack('<H', f.read(2))[0], 3
    if v == 0xfe:
        return struct.unpack('<I', f.read(4))[0], 5
    return struct.unpack('<Q', f.read(8))[0], 9

def rh(b):  # reverse hex for hash display (big-endian)
    return b[::-1].hex()

def parse_blk(path, limit=None):
    with open(path, 'rb') as f:
        off = 0
        i = 0
        while True:
            magic = f.read(4)
            if not magic:
                break
            off += 4
            if magic not in MAGICS:
                raise SystemExit(f"Bad magic at 0x{off-4:x}: {magic.hex()}")
            (blen,) = struct.unpack('<I', f.read(4)); off += 4
            if blen < 80:
                raise SystemExit(f"Block length too small at 0x{off-8:x}: {blen}")

            # Read 80-byte header
            hdr = f.read(80); off += 80
            if len(hdr) != 80:
                break

            ver, = struct.unpack('<i', hdr[0:4])
            prev  = hdr[4:36]
            merkle= hdr[36:68]
            ts, bits, nonce = struct.unpack('<III', hdr[68:80])

            # Compute block hash = double-SHA256(header)
            h = hashlib.sha256(hdr).digest()
            h = hashlib.sha256(h).digest()

            # Peek tx count (varint) just for display
            here = f.tell()
            try:
                txc, vsize = read_varint(f)
            except EOFError:
                txc, vsize = None, 0
            # Jump to end of block payload
            f.seek(here + (blen - 80), 0); off += (blen - 80)

            t = datetime.datetime.utcfromtimestamp(ts)
            print(f"#{i:6d} net={MAGICS[magic]:7s} off=0x{here-80-8:08x} len={blen:7d} "
                  f"hash={rh(h)}")
            print(f"       ver={ver} time={t} bits=0x{bits:08x} nonce={nonce} "
                  f"prev={rh(prev)}")
            if txc is not None:
                print(f"       tx_count={txc}")
            else:
                print(f"       tx_count=? (incomplete)")
            i += 1
            if limit and i >= limit:
                break

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 parse_blkdat_headers.py <bitcoin.dat> [limit]")
        sys.exit(1)
    parse_blk(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else None)

