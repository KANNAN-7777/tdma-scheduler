import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def load_schedule(path: Path):
    with path.open("r", encoding="utf-8") as f:
        schedule = json.load(f)

    if not isinstance(schedule, dict) or not schedule:
        raise ValueError("Schedule must be a non-empty JSON object.")

    for node, slot in schedule.items():
        if not isinstance(node, str):
            raise ValueError("Node names must be strings.")
        if not isinstance(slot, int) or slot < 1:
            raise ValueError(f"Invalid slot for {node}: {slot}")

    return schedule


def node_id(node_name: str) -> str:
    """Convert Node_01 -> 1 for EMANE NEM IDs."""
    try:
        value = int(node_name.split("_")[-1])
    except ValueError as exc:
        raise ValueError(
            f"Node name '{node_name}' must end in a numeric NEM ID."
        ) from exc

    if value < 1:
        raise ValueError(f"NEM ID must be >= 1: {node_name}")

    return str(value)


def build_schedule_xml(schedule, output_path: Path):
    slot_count = max(schedule.values())

    root = ET.Element("emane-tdma-schedule")

    ET.SubElement(
        root,
        "structure",
        {
            "slotduration": "1000",   # 1 ms in microseconds
            "slotoverhead": "0",
            "frames": "1",
            "slots": str(slot_count),
            "bandwidth": "1M",
        },
    )

    multiframe = ET.SubElement(
        root,
        "multiframe",
        {
            "frequency": "2.4G",
            "power": "0",
            "class": "0",
            "datarate": "1M",
        },
    )

    frame = ET.SubElement(multiframe, "frame", {"index": "0"})

    for slot_number in range(1, slot_count + 1):
        node_ids = [
            node_id(node)
            for node, assigned_slot in sorted(schedule.items())
            if assigned_slot == slot_number
        ]

        if not node_ids:
            continue

        slot = ET.SubElement(
            frame,
            "slot",
            {
                # Part 1 uses 1-based slots; EMANE schedule indices are 0-based.
                "index": str(slot_number - 1),
                "nodes": ",".join(node_ids),
            },
        )
        ET.SubElement(slot, "tx")

    tree = ET.ElementTree(root)
    ET.indent(tree, space="    ")
    tree.write(output_path, encoding="utf-8", xml_declaration=True)

    return slot_count


def main():
    parser = argparse.ArgumentParser(
        description="Convert Part 1 TDMA Node->Slot JSON into native EMANE TDMA XML."
    )
    parser.add_argument(
        "--input",
        default="schedule.json",
        help="Part 1 Node->Slot JSON file",
    )
    parser.add_argument(
        "--output",
        default="emane_tdma_schedule.xml",
        help="Output EMANE TDMA schedule XML",
    )
    args = parser.parse_args()

    schedule = load_schedule(Path(args.input))
    slots = build_schedule_xml(schedule, Path(args.output))

    print(f"Generated: {args.output}")
    print(f"Nodes: {len(schedule)}")
    print(f"TDMA slots: {slots}")


if __name__ == "__main__":
    main()
