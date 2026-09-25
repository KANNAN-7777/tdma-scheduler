import xml.etree.ElementTree as ET

FILE = "emane_tdma_schedule.xml"

try:
    tree = ET.parse(FILE)
    root = tree.getroot()
except Exception as e:
    print("TDMA XML INVALID")
    print(e)
    raise SystemExit(1)

print("TDMA XML VALID")
print("Root:", root.tag)

for elem in root.iter():
    tag = elem.tag.lower()

    if tag in ("multiframe", "frame", "slot", "tx"):
        print(tag, dict(elem.attrib))

print("Validation completed successfully.")
