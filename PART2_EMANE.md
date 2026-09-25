# Part 2 - EMANE TDMA Integration

## Objective

Connect the Part 1 TDMA schedule to the native EMANE TDMA radio model.

## Implemented integration

1. Part 1 produces a Node -> Slot mapping.
2. `schedule.json` stores that mapping.
3. `generate_emane_schedule.py` converts the mapping to native EMANE TDMA schedule XML.
4. The bridge converts Part 1's 1-based slot numbers to EMANE's 0-based slot indices.
5. The generated schedule uses a 1 ms slot duration, one frame, and the nine slots required by the current Part 1 heuristic result.
6. `emaneevent-tdmaschedule` publishes the schedule as the native TDMA schedule event used by EMANE.

## Current schedule

- Nodes: 16
- TDMA slots: 9
- Slot duration: 1 ms
- Frames: 1
- Frequency: 2.4 GHz
- Bandwidth: 1 MHz
- Data rate: 1 Mbps

## Generated slot assignments

- Slot 1: NEM 6
- Slot 2: NEM 7
- Slot 3: NEM 10
- Slot 4: NEM 11
- Slot 5: NEM 2, 14
- Slot 6: NEM 3, 15
- Slot 7: NEM 5, 8
- Slot 8: NEM 9, 12
- Slot 9: NEM 1, 4, 13, 16

## WSL validation commands

From the TDMA project directory:

```bash
python3 generate_emane_schedule.py --input schedule.json --output emane_tdma_schedule.xml

PYTHONPATH=/usr/local/lib/python3/dist-packages python3 -c "from emane.events import TDMASchedule; s=TDMASchedule('emane_tdma_schedule.xml'); print('TDMA XML VALID'); print(s.structure()); print(s.info())"
```

Expected structure:

```text
{'slotduration': 1000, 'slotoverhead': 0, 'bandwidth': 1000000, 'slots': 9, 'frames': 1}
```

Then, while the EMANE platform is running:

```bash
PYTHONPATH=/usr/local/lib/python3/dist-packages emaneevent-tdmaschedule emane_tdma_schedule.xml
```

## Part 2 status

The native TDMA schedule generation and event-publishing path is implemented. A complete packet-level permit/drop demonstration was not completed in the WSL environment. The internship problem statement explicitly states that a full Part 2 result is not expected, so the submission should present this as the Part 2 approach and current integration status, not as a completed packet-level experiment.
