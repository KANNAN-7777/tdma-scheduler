#!/usr/bin/env python3
"""
Vaan Megam Part 2 schedule-enforcement test.

Run this inside the TDMA repository under WSL Ubuntu as root.

The test performs two clean EMANE runs:
  ALLOWED: NEM 1 has its Part-1 TX slot and NEM 2 receives traffic.
  BLOCKED: NEM 1's Part-1 TX slot is changed to RX, so NEM 1 has no TX
            opportunity; the same traffic is generated and NEM 2 should
            receive zero test packets.

The EMANE process is restarted between cases so queued packets do not
contaminate the blocked result.
"""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
BASE_XML = ROOT / "emane_tdma_schedule.xml"
ALLOWED_XML = ROOT / "emane_tdma_schedule_allowed.xml"
BLOCKED_XML = ROOT / "emane_tdma_schedule_blocked.xml"
PLATFORM_XML = ROOT / "platforms16" / "platform16.xml"
RESULT_FILE = ROOT / "Part2_Enforcement_Evidence.txt"

ENV = os.environ.copy()
ENV["PYTHONPATH"] = "/usr/local/lib/python3/dist-packages"
ENV["EMANEMANIFESTPATH"] = "/usr/local/share/emane/manifest"

TX_IFACE = "emane1"
RX_IFACE = "emane2"
COUNT = 50
DST = bytes.fromhex("020200000002")
SRC = bytes.fromhex("020200000001")
ETHERTYPE = b"\x88\xb5"
PAYLOAD = b"TDMA_SCHEDULE_ENFORCEMENT"


def run(cmd, check=True):
    return subprocess.run(cmd, cwd=ROOT, env=ENV, text=True,
                          capture_output=True, check=check)


def stop_existing():
    subprocess.run(["pkill", "-f", "emane --loglevel 4 platforms16/platform16.xml"],
                   text=True, capture_output=True)
    time.sleep(2)


def wait_ready(timeout=15):
    end = time.time() + timeout
    while time.time() < end:
        p = subprocess.run(["bash", "-lc", "ss -lnt | grep -q ':47000 '"],
                           text=True, capture_output=True)
        if p.returncode == 0:
            break
        time.sleep(.25)
    else:
        raise RuntimeError("EMANE control port 47000 did not become ready")

    end = time.time() + timeout
    while time.time() < end:
        ok = all(subprocess.run(["ip", "link", "show", iface],
                                text=True, capture_output=True).returncode == 0
                 for iface in (TX_IFACE, RX_IFACE))
        if ok:
            time.sleep(1)
            return
        time.sleep(.25)
    raise RuntimeError("emane1/emane2 interfaces did not appear")


def start_emane():
    log = open(ROOT / "part2_enforcement_emane.log", "w", encoding="utf-8")
    proc = subprocess.Popen(["emane", "--loglevel", "4", str(PLATFORM_XML)],
                            cwd=ROOT, env=ENV, stdout=log,
                            stderr=subprocess.STDOUT, text=True)
    wait_ready()
    return proc, log


def stop_emane(proc, log):
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=8)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
    log.close()
    time.sleep(2)


def make_schedules():
    if not BASE_XML.exists():
        raise FileNotFoundError(BASE_XML)

    tree = ET.parse(BASE_XML)
    root = tree.getroot()

    node1_slot = None
    for slot in root.findall(".//slot"):
        nodes = slot.get("nodes", "")
        if nodes == "1" or "1" in nodes.split(","):
            tx = slot.find("tx")
            if tx is not None:
                node1_slot = slot
                break

    if node1_slot is None:
        raise RuntimeError("Could not find NEM 1 TX slot in generated schedule")

    # Part 1 assigns Node_01 to slot 9; EMANE slot indices are zero based.
    if node1_slot.get("index") != "8":
        raise RuntimeError(
            f"NEM 1 TX slot is {node1_slot.get('index')!r}; expected EMANE index 8"
        )

    tree.write(ALLOWED_XML, encoding="UTF-8", xml_declaration=True)

    blocked_tree = ET.parse(BASE_XML)
    blocked_root = blocked_tree.getroot()
    changed = False
    for slot in blocked_root.findall(".//slot"):
        nodes = slot.get("nodes", "")
        if nodes == "1" or "1" in nodes.split(","):
            tx = slot.find("tx")
            if tx is not None:
                slot.remove(tx)
                slot.append(ET.Element("rx", {"frequency": "2.4G"}))
                changed = True
                break

    if not changed:
        raise RuntimeError("Could not convert NEM 1 TX slot to RX")
    blocked_tree.write(BLOCKED_XML, encoding="UTF-8", xml_declaration=True)


def clear_stats():
    run(["emanesh", "localhost", "clear", "stat", "nems", "mac"])


def publish(schedule):
    run(["emaneevent-tdmaschedule", str(schedule), "-i", "eth0"])
    time.sleep(.75)


def pathloss():
    run(["emaneevent-pathloss", "1:2", "10", "-i", "eth0"])


def send_frames():
    frame = DST + SRC + ETHERTYPE + PAYLOAD
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
    try:
        s.bind((TX_IFACE, 0))
        for _ in range(COUNT):
            s.send(frame)
            time.sleep(.002)
    finally:
        s.close()


def stats():
    p = run(["emanesh", "localhost", "get", "stat", "2", "mac"])
    keys = (
        "processedDownstreamPackets",
        "processedUpstreamPackets",
        "numRxSlotValid",
        "numRxSlotErrorMissed",
        "numTxSlotValid",
        "scheduler.scheduleAcceptFull",
        "scheduler.scheduleRejectFrameIndexRange",
        "scheduler.scheduleRejectOther",
        "scheduler.scheduleRejectSlotIndexRange",
        "scheduler.scheduleRejectUpdateBeforeFull",
    )
    lines = [ln.strip() for ln in p.stdout.splitlines()
             if any(k in ln for k in keys)]
    return "\n".join(lines)


def value(text, key):
    for ln in text.splitlines():
        if key in ln and "=" in ln:
            try:
                return int(ln.rsplit("=", 1)[1].strip())
            except ValueError:
                return None
    return None


def case(name, schedule):
    stop_existing()
    proc, log = start_emane()
    try:
        clear_stats()
        publish(schedule)
        pathloss()
        before = stats()
        send_frames()
        time.sleep(1)
        after = stats()
        upstream = value(after, "processedUpstreamPackets") or 0
        return (
            f"\n[{name}]\n"
            f"Schedule: {schedule.name}\n"
            f"Before test:\n{before}\n"
            f"After {COUNT} generated frames:\n{after}\n"
            f"NEM2 processedUpstreamPackets: {upstream}\n",
            upstream,
            after,
        )
    finally:
        stop_emane(proc, log)


def main():
    if os.geteuid() != 0:
        print("Run as root in WSL.", file=sys.stderr)
        return 2

    make_schedules()

    allowed_text, allowed_rx, allowed_stats = case("ALLOWED", ALLOWED_XML)
    blocked_text, blocked_rx, blocked_stats = case("BLOCKED", BLOCKED_XML)

    allowed_pass = allowed_rx > 0
    blocked_pass = blocked_rx == 0

    report = (
        "VAAN MEGAM PART 2 - TDMA SCHEDULE ENFORCEMENT\n"
        "===============================================\n"
        "The test uses the Part-1 Node_01 -> slot 9 mapping (EMANE slot index 8).\n"
        "ALLOWED: NEM1 slot 8 = TX; NEM2 is able to receive.\n"
        "BLOCKED: NEM1 slot 8 = RX; NEM1 has no TX opportunity.\n"
        "50 raw Ethernet frames are generated in each clean EMANE run.\n"
        "10 dB pathloss is applied between NEM1 and NEM2.\n"
        + allowed_text + blocked_text +
        "\nRESULTS\n"
        f"Allowed traffic received: {'PASS' if allowed_pass else 'FAIL'}\n"
        f"Blocked traffic not received: {'PASS' if blocked_pass else 'FAIL'}\n"
        f"Overall schedule enforcement: {'PASS' if allowed_pass and blocked_pass else 'FAIL'}\n"
    )

    RESULT_FILE.write_text(report, encoding="utf-8")
    print(report)
    print(f"Evidence written to {RESULT_FILE}")
    return 0 if allowed_pass and blocked_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
