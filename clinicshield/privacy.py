BLOCKED_HEADER_TERMS = (
    "patient", "pt_name", "patient_name", "first_name", "last_name",
    "dob", "date_of_birth", "mrn", "medical_record", "ssn",
    "social_security", "diagnosis", "dx", "icd", "insurance_id",
    "member_id", "policy_number", "phone", "email_address", "address",
)

REJECTION_MESSAGE = (
    "This file looks like it contains patient or personal information. "
    "ClinicShield only needs information about devices, software, "
    "and settings. Please remove those columns and try again."
)


def validate_headers(headers):
    """Reject prohibited column names without reporting file contents."""
    for header in headers:
        normalized = "_".join(
            str(header).strip().casefold().replace("-", " ").split()
        )
        if any(term in normalized for term in BLOCKED_HEADER_TERMS):
            raise ValueError(REJECTION_MESSAGE)