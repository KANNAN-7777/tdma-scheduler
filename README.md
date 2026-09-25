# TDMA Schedule Planner and EMANE Integration

A centralized TDMA scheduling system for a 16-node wireless network with native EMANE TDMA integration.

## Overview

This project implements a centralized TDMA Schedule Planner and Optimizer using graph-based interference modelling and graph-coloring heuristics.

The project is divided into two parts:

- **Part 1:** TDMA Schedule Planner and Optimizer
- **Part 2:** EMANE TDMA Integration and Schedule Enforcement

Part 1 converts static node coordinates into a communication graph, builds a distance-2 conflict graph, assigns TDMA slots using multiple coloring heuristics, performs slot optimization, enables spatial reuse, generates a Slot × Node binary matrix, and verifies the final schedule.

Part 2 converts the Part 1 Node-to-Slot mapping into a native EMANE TDMA schedule, publishes it to a 16-NEM EMANE runtime, validates schedule acceptance, and performs a packet-level allowed/blocked schedule enforcement test.

---

## Project Architecture

```text
                    PART 1
┌──────────────────────────────────────────────┐
│ Node Coordinates                             │
│              ↓                               │
│ Communication Graph                          │
│              ↓                               │
│ Distance-2 Conflict Graph                    │
│              ↓                               │
│ Graph Coloring Heuristics                    │
│              ↓                               │
│ Slot Optimization                            │
│              ↓                               │
│ Node-to-Slot Mapping                         │
│              ↓                               │
│ Slot × Node Matrix                           │
│              ↓                               │
│ Conflict Verification                        │
└──────────────────────────────────────────────┘
                       │
                       ▼
                    PART 2
┌──────────────────────────────────────────────┐
│ schedule.json                                │
│              ↓                               │
│ generate_emane_schedule.py                   │
│              ↓                               │
│ emane_tdma_schedule.xml                      │
│              ↓                               │
│ emaneevent-tdmaschedule                      │
│              ↓                               │
│ 16-NEM EMANE Runtime                         │
│              ↓                               │
│ Schedule Enforcement Test                    │
└──────────────────────────────────────────────┘
