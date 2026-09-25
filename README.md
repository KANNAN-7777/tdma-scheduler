# TDMA Schedule Planner and EMANE Integration

Centralized TDMA scheduler for a 16-node wireless network with EMANE integration.

## Overview

This project implements a centralized TDMA Schedule Planner and Optimizer using graph-based interference modelling and graph-coloring heuristics.

The project has two parts:

- Part 1: TDMA Schedule Planner and Optimizer
- Part 2: EMANE TDMA Integration and Schedule Enforcement

Part 1 converts node coordinates into a communication graph, builds a distance-2 conflict graph, assigns TDMA slots using multiple coloring heuristics, performs slot optimization, enables spatial reuse, generates a Slot × Node matrix, and verifies the final schedule.

Part 2 converts the Part 1 schedule into a native EMANE TDMA schedule, runs it on a 16-NEM EMANE platform, and validates packet behavior under allowed and blocked transmission opportunities.

---

## Part 1 – TDMA Schedule Planner and Optimizer

### Problem

In a TDMA wireless network, nodes transmit in assigned time slots.

Two nodes that can interfere with each other must not transmit in the same slot. To model both direct and two-hop interference, the communication graph is converted into a distance-2 conflict graph.

The scheduler then applies graph-coloring heuristics to assign TDMA slots while allowing spatial reuse between non-conflicting nodes.

### Input

The scheduler uses static coordinates for 16 wireless nodes.

The communication range is:

```text
500 meters
