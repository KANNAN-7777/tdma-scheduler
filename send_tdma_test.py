import socket
import time

interface = "emane1"

src = bytes.fromhex("020200000001")
dst = bytes.fromhex("020200000002")

ethertype = b"\x88\xb5"
payload = b"TDMA_EMANE_TEST_PACKET"

frame = dst + src + ethertype + payload

sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
sock.bind((interface, 0))

print("Sending 50 Ethernet frames from NEM 1 toward NEM 2...")

for i in range(50):
    sock.send(frame)
    time.sleep(0.01)

sock.close()

print("Done.")
