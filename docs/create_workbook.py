from pathlib import Path

import pandas as pd

project = Path(__file__).resolve().parents[1]
templates = project / "templates"

instructions = pd.DataFrame({
    "Read me first": [
        "ClinicShield inventory templates",
        "Do not include patient or personal information.",
        "Replace the fictional example rows with your inventory.",
        "Keep the column names unchanged.",
        "Use matching asset_id values across sheets.",
        "Y = Yes; N = No; Unknown = not checked.",
        "NA = Not applicable, only where allowed.",
        "Use YYYY-MM-DD for dates.",
        "The services sheet is optional.",
        "This workbook does not initiate a network scan.",
    ]
})

with pd.ExcelWriter(
    templates / "clinicshield_inventory.xlsx",
    engine="openpyxl",
) as writer:
    instructions.to_excel(
        writer, sheet_name="Read me first", index=False
    )
    for name in ("assets", "software", "services"):
        table = pd.read_csv(
            templates / f"{name}.csv", keep_default_na=False
        )
        table.to_excel(writer, sheet_name=name, index=False)

    for sheet in writer.book.worksheets:
        sheet.freeze_panes = "A2"
        for column in sheet.columns:
            width = max(len(str(cell.value or "")) for cell in column)
            sheet.column_dimensions[column[0].column_letter].width = min(
                width + 3, 65
            )

print("Created templates/clinicshield_inventory.xlsx")