from pathlib import Path

import pandas as pd

rows = []


def add_device(asset_id, name, asset_type, os_name, os_version,
               touches_phi="Y", segment="clinic", portable="N",
               encrypted="Y", notes="Fictional device"):
    rows.append({
        "asset_id": asset_id,
        "asset_name": name,
        "asset_type": asset_type,
        "location": "Satellite clinic",
        "owner_role": "IT contractor",
        "os_name": os_name,
        "os_version": os_version,
        "touches_phi": touches_phi,
        "internet_facing": "N",
        "portable": portable,
        "encrypted": encrypted,
        "auto_update": "Y",
        "last_patched": "2026-10-01",
        "network_segment": segment,
        "notes": notes,
    })


for number in range(1, 23):
    add_device(
        f"WH-WS{number:02d}", f"Workstation {number}",
        "workstation", "Windows", "11 24H2",
    )

for number in range(1, 4):
    add_device(
        f"WH-SRV{number:02d}", f"Server {number}",
        "server", "Windows Server", "2022",
    )

add_device(
    "WH-VPN01", "Campus VPN appliance", "network_device",
    "Vendor firmware", "Unknown", touches_phi="Unknown",
    segment="management", encrypted="Unknown",
)

add_device(
    "WH-MD01", "Vitals monitor", "medical_device",
    "Vendor firmware", "Unknown", segment="medical",
    notes="Support status requires vendor confirmation",
)

add_device(
    "WH-MD02", "Ultrasound workstation", "medical_device",
    "Windows", "7", segment="clinic",
    notes="No extended support; shares workstation network",
)
rows[-1]["last_patched"] = "2020-01-14"

for number in range(1, 4):
    add_device(
        f"WH-PR{number:02d}", f"Printer {number}",
        "printer", "Vendor firmware", "Unknown",
        encrypted="Unknown",
    )

for number in range(1, 5):
    add_device(
        f"WH-LT{number:02d}", f"Laptop {number}",
        "laptop", "Windows", "11 24H2", portable="Y",
    )

rows[-4]["os_version"] = "10 22H2"
rows[-4]["encrypted"] = "Unknown"
rows[-4]["last_patched"] = "2025-10-14"
rows[-4]["notes"] = "No extended security update coverage"

project = Path(__file__).resolve().parents[1]
destination = project / "samples" / "westside_health" / "assets.csv"
pd.DataFrame(rows).to_csv(destination, index=False)

print(f"Created Westside inventory with {len(rows)} assets")