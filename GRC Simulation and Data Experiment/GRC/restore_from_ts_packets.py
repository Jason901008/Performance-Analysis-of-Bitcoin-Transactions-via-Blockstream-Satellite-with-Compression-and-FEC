# restore_from_ts_packets.py

import sys

TS_PACKET_SIZE = 188
TS_HEADER_SIZE = 4
PAYLOAD_SIZE = TS_PACKET_SIZE - TS_HEADER_SIZE

def restore_from_ts(input_path, output_path):
    with open(input_path, "rb") as f_in, open(output_path, "wb") as f_out:
        while True:
            packet = f_in.read(TS_PACKET_SIZE)
            if not packet:
                break
            if len(packet) != TS_PACKET_SIZE or packet[0] != 0x47:
                print("[✘] 發現無效 TS 封包，結束還原")
                break
            payload = packet[TS_HEADER_SIZE:]
            f_out.write(payload)

    print(f"[✔] 還原完成：{output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python3 restore_from_ts_packets.py input.ts output.zip")
        sys.exit(1)
    restore_from_ts(sys.argv[1], sys.argv[2])

