# 完整穩定版封裝器：每個封包固定為 188 bytes，結尾自動補足
import sys
import os

TS_PACKET_SIZE = 188
TS_HEADER_SIZE = 4
PAYLOAD_SIZE = TS_PACKET_SIZE - TS_HEADER_SIZE

def generate_ts_header(pid, counter):
    return bytearray([
        0x47,                          # Sync byte
        0x40 | ((pid >> 8) & 0x1F),    # Payload unit start indicator + PID (high)
        pid & 0xFF,                   # PID (low)
        0x10 | (counter & 0x0F)       # Continuity counter
    ])

def wrap_to_ts(input_path, output_path):
    pid = 0x100
    counter = 0
    with open(input_path, "rb") as f_in, open(output_path, "wb") as f_out:
        while True:
            data = f_in.read(PAYLOAD_SIZE)
            if not data:
                break

            # 補齊不足的 payload
            if len(data) < PAYLOAD_SIZE:
                data += b'\xFF' * (PAYLOAD_SIZE - len(data))

            header = generate_ts_header(pid, counter)
            ts_packet = header + data
            assert len(ts_packet) == 188

            f_out.write(ts_packet)
            counter = (counter + 1) % 16
    print(f"[✔] 封裝完成：{output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python wrap_to_ts_packets_final.py input.dat output.ts")
        sys.exit(1)
    wrap_to_ts(sys.argv[1], sys.argv[2])

