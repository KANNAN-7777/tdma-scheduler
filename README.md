# TDMA Schedule Planner and EMANE Integration

A centralized TDMA scheduling system for a 16-node wireless network, using distance-2 graph coloring for interference-aware slot allocation and EMANE for schedule-driven runtime validation.

## Overview

This project implements a two-stage workflow:

**Part 1 — TDMA Schedule Planner and Optimizer**
- Builds a communication graph from static node coordinates.
- Uses a 500 m communication range to identify direct links.
- Builds a distance-2 conflict graph to model one-hop and two-hop interference.
- Evaluates multiple greedy graph-coloring heuristics.
- Performs local slot optimization and spatial reuse.
- Produces a direct Node-to-Slot mapping and a Slot × Node binary matrix.
- Verifies that no conflicting nodes share a TDMA slot.

**Part 2 — EMANE TDMA Integration**
- Converts the Part 1 schedule into a native EMANE TDMA schedule.
- Publishes the generated schedule to a 16-NEM EMANE runtime.
- Validates schedule acceptance and rejection counters.
- Performs an allowed/blocked packet enforcement experiment using the Part 1 schedule.

---

## System Architecture

```text
Node Coordinates
      │
      ▼
Communication Graph
      │
      ▼
Distance-2 Conflict Graph
      │
      ▼
Graph Coloring Heuristics
      │
      ▼
Slot Optimization
      │
      ▼
Node-to-Slot Mapping
      │
      ▼
Slot × Node Matrix
      │
      ▼
Conflict Verification
      │
      ▼
schedule.json
      │
      ▼
generate_emane_schedule.py
      │
      ▼
emane_tdma_schedule.xml
      │
      ▼
emaneevent-tdmaschedule
      │
      ▼
16-NEM EMANE Runtime
      │
      ▼
Schedule Enforcement Test
```

---

# Part 1 — TDMA Schedule Planner

## Problem Model

Each wireless node is represented as a graph vertex.

A direct communication edge is created when the Euclidean distance between two nodes is less than or equal to **500 meters**:

```text
d = sqrt((x2 - x1)^2 + (y2 - y1)^2)
```

The communication graph is then converted into a **distance-2 conflict graph**. Two nodes cannot share a TDMA slot when they are:

- directly connected, or
- separated by two hops through a common neighbor.

Nodes outside this conflict relationship may safely reuse the same slot.

## Coloring Strategy

The scheduler evaluates three greedy coloring strategies:

1. **Largest First**
2. **Smallest Last**
3. **Saturation Largest First**

Each graph color represents one TDMA slot.

The best result among the tested heuristics is selected, followed by a local optimization stage that attempts to move nodes into lower-numbered existing slots without creating conflicts.

The final slot count is reported as a **heuristic result**, not as a proof of global minimum coloring.

## Final Part 1 Result

| Metric | Result |
|---|---:|
| Nodes | 16 |
| Communication range | 500 m |
| 1-hop communication links | 42 |
| Distance-2 conflict links | 90 |
| Coloring strategies tested | 3 |
| TDMA slots | 9 |
| Reused slots | 5 |
| Maximum nodes in one slot | 4 |
| Verification | **PASS** |

## Node-to-Slot Mapping

| Node | Slot |
|---|---:|
| Node_01 | 9 |
| Node_02 | 5 |
| Node_03 | 6 |
| Node_04 | 9 |
| Node_05 | 7 |
| Node_06 | 1 |
| Node_07 | 2 |
| Node_08 | 7 |
| Node_09 | 8 |
| Node_10 | 3 |
| Node_11 | 4 |
| Node_12 | 8 |
| Node_13 | 9 |
| Node_14 | 5 |
| Node_15 | 6 |
| Node_16 | 9 |

## Spatial Reuse

| Slot | Nodes |
|---|---|
| 5 | Node_02, Node_14 |
| 6 | Node_03, Node_15 |
| 7 | Node_05, Node_08 |
| 8 | Node_09, Node_12 |
| 9 | Node_01, Node_04, Node_13, Node_16 |

Slot 9 has the highest reuse, with four non-conflicting nodes sharing the same transmission opportunity.

## Slot × Node Matrix

`1` = scheduled to transmit in the slot  
`0` = not scheduled in the slot

| Slot | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| 5 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| 6 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| 7 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| 9 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |

## Verification Rule

For every edge `(u, v)` in the distance-2 conflict graph:

```text
slot(u) != slot(v)
```

The final schedule passed the verification stage.

---

# Part 2 — EMANE TDMA Integration

## Integration Flow

```text
Part 1 Node-to-Slot Mapping
        ↓
schedule.json
        ↓
generate_emane_schedule.py
        ↓
emane_tdma_schedule.xml
        ↓
emaneevent-tdmaschedule
        ↓
16-NEM EMANE Runtime
```

## Native TDMA Configuration

| Parameter | Value |
|---|---:|
| NEMs | 16 |
| Slot duration | 1 ms |
| Frames | 1 |
| TDMA slots | 9 |
| Frequency | 2.4 GHz |
| Bandwidth | 1 MHz |
| Data rate | 1 Mbit/s |
| Service class | 0 |

The generated EMANE multiframe uses `class="0"`.

## EMANE Slot Assignments

| Slot | NEMs |
|---|---|
| 1 | NEM 6 |
| 2 | NEM 7 |
| 3 | NEM 10 |
| 4 | NEM 11 |
| 5 | NEM 2, NEM 14 |
| 6 | NEM 3, NEM 15 |
| 7 | NEM 5, NEM 8 |
| 8 | NEM 9, NEM 12 |
| 9 | NEM 1, NEM 4, NEM 13, NEM 16 |

## 16-NEM Runtime Validation

| Validation | Result |
|---|---|
| Full schedule acceptance | **16/16 NEMs** |
| `scheduleAcceptFull` | **1 for every NEM** |
| `scheduleRejectFrameIndexRange` | **0** |
| `scheduleRejectOther` | **0** |
| `scheduleRejectSlotIndexRange` | **0** |
| `scheduleRejectUpdateBeforeFull` | **0** |

The final clean run showed that all 16 NEMs accepted the generated schedule with zero tested schedule-rejection counters.

## Schedule Enforcement Test

The final experiment uses the actual Part 1 assignment:

```text
Node_01 → Slot 9
```

EMANE uses zero-based slot indices, so Part 1 Slot 9 corresponds to EMANE slot index 8.

### Allowed Case

NEM 1 has a transmit opportunity in its assigned slot.

- Test frames generated: **50**
- NEM 2 processed upstream packets: **17**
- Result: **PASS**

### Blocked Case

The same NEM 1 slot is changed from TX to RX, leaving NEM 1 without a transmit opportunity in that slot.

- Test frames generated: **50**
- NEM 2 processed upstream packets: **0**
- Result: **PASS**

### Final Enforcement Result

```text
Allowed traffic received: PASS
Blocked traffic not received: PASS
Overall schedule enforcement: PASS
```

The experiment demonstrates schedule-controlled packet behavior derived from the Part 1 Node-to-Slot mapping. The packet counters are used to establish the allowed/blocked behavior and are not interpreted as a percentage delivery metric.

---

# Validation Tests

| Test | Purpose | Result |
|---|---|---|
| `test_chain.json` | Two-hop conflict handling | PASS |
| `test_reuse.json` | Spatial reuse | PASS |
| `test_boundary.json` | Exact 500 m boundary | PASS |
| Final 16-node scheduler run | Full scheduler + verifier | PASS |
| 16-NEM EMANE schedule test | Schedule publication + acceptance | PASS |
| TDMA enforcement test | Allowed vs blocked transmission | PASS |

---

# Repository Structure

```text
tdma-scheduler/
├── .gitignore
├── README.md
├── requirements.txt
│
├── main.py
├── graph_builder.py
├── coloring.py
├── scheduler.py
├── verifier.py
│
├── generate_emane_schedule.py
├── send_tdma_test.py
├── part2_enforcement_test.py
├── validate_emane.py
│
├── sample_input.json
├── schedule.json
├── test_chain.json
├── test_reuse.json
├── test_boundary.json
├── test_tdma_schedule.xml
│
├── emane_tdma_schedule.xml
├── emane_tdma_schedule_allowed.xml
├── emane_tdma_schedule_blocked.xml
│
├── platform.xml
├── tdmanem.xml
├── tdmaradiomodel.xml
├── transraw.xml
├── transvirtual.xml
├── start16.sh
├── platforms16/
│
├── Part1_Final_Run.txt
├── Part2_Final_Evidence.txt
├── Part2_Enforcement_Evidence.txt
├── PART2_EMANE.md
│
├── TDMA_Final_Submission_Documentation.pdf
└── TDMA_Final_Submission_Presentation.pptx
```

---

# Running the Project

## Part 1

```bash
python3 main.py --input sample_input.json --range 500 --verbose
```

Expected result:

```text
TDMA slots: 9
Verification: PASS
```

## Generate the EMANE Schedule

```bash
python3 generate_emane_schedule.py
```

Expected output:

```text
Generated: emane_tdma_schedule.xml
Nodes: 16
TDMA slots: 9
```

## Validate the TDMA XML

```bash
xmllint --noout emane_tdma_schedule.xml
```

## Run the Enforcement Test

```bash
python3 part2_enforcement_test.py
```

The enforcement test generates:

- `Part2_Enforcement_Evidence.txt`
- `emane_tdma_schedule_allowed.xml`
- `emane_tdma_schedule_blocked.xml`

---

# Key Results

| Area | Final Result |
|---|---|
| Network size | 16 nodes |
| Communication range | 500 m |
| Direct communication links | 42 |
| Distance-2 conflict links | 90 |
| TDMA slots | 9 |
| Reused slots | 5 |
| Maximum nodes per slot | 4 |
| Part 1 verification | **PASS** |
| EMANE NEMs | 16 |
| Schedule acceptance | **16/16** |
| Tested schedule rejection counters | **0** |
| Allowed packet test | **17 upstream packets** |
| Blocked packet test | **0 upstream packets** |
| Overall schedule enforcement | **PASS** |

---

# References

- [NetworkX Documentation](https://networkx.org/documentation/stable/)
- [EMANE TDMA Radio Model](https://emane.io/tdma-radio-model)
- Distance-2 graph-coloring concepts for one-hop and two-hop wireless interference modelling

---

# Submission

**GitHub Repository:**

https://github.com/KANNAN-7777/tdma-scheduler

The repository contains the source code, test cases, EMANE configuration, generated schedules, validation evidence, technical documentation PDF, and presentation PPT.

---

# Conclusion

The project implements a centralized TDMA scheduling workflow based on distance-2 graph coloring and integrates the resulting schedule with EMANE.

For the tested 16-node topology, the scheduler generated a conflict-free 9-slot schedule with spatial reuse across five slots.

The generated schedule was converted into a native EMANE TDMA schedule and accepted by all 16 NEMs with zero tested schedule-rejection counters.

The final schedule-enforcement experiment showed:

```text
Allowed schedule → 17 upstream packets processed
Blocked schedule → 0 upstream packets processed
Overall result   → PASS
```

The repository contains the implementation, tests, EMANE configuration, generated schedules, validation evidence, documentation, and presentation.
