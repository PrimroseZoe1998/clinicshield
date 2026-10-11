# ClinicShield Inventory Templates

Use these templates to list your organization's equipment,
software, and listening network services.

Do not include patient names, dates of birth, medical records,
diagnoses, insurance details, or other personal information.

The example rows are fictional. Replace them with your inventory
before running a checkup.

## Files

- assets.csv: One row per device.
- software.csv: One row per application on a device or cloud service.
- services.csv: One row per listening network service. Optional.

## Filling in the files

Keep the column names unchanged.

Use the same asset_id across files to connect software and services
to a device. Use CLOUD for software hosted by a cloud provider.

Y means Yes. N means No. Unknown means you have not checked.
NA means Not applicable and is allowed only in fields that support it.

Use YYYY-MM-DD for dates. Leave optional dates blank if unknown.

touches_phi asks whether the device or software accesses protected
health information. Enter Y, N, or Unknown, never patient information.

internet_facing asks whether a device is reachable from outside
your organization's network.

For services, exposure must be internal, internet, or unknown.
If unsure, use unknown or ask your IT vendor.

Creating or uploading these files does not initiate a network scan.