import re


# Email address pattern
EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)


# US Social Security Number pattern
SSN_PATTERN = re.compile(
    r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)"
)


# Basic international and local phone number pattern
PHONE_PATTERN = re.compile(
    r"(?<!\w)(?:\+?\d{1,3}[\s.-]?)?"
    r"(?:\(?\d{2,4}\)?[\s.-]?)?"
    r"\d{3,4}[\s.-]?\d{3,4}(?!\w)"
)


def detect_pii(text: str) -> dict:
    """
    Detect supported PII types in text.

    Currently supported:
        - Email
        - Phone
        - SSN
    """

    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    return {
        "emails": EMAIL_PATTERN.findall(text),
        "phones": PHONE_PATTERN.findall(text),
        "ssns": SSN_PATTERN.findall(text)
    }


def mask_pii(text: str) -> str:
    """
    Replace detected PII with placeholders.

    SSN is masked first to avoid overlapping
    with phone number detection.
    """

    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    # Mask SSN
    text = SSN_PATTERN.sub("[SSN]", text)

    # Mask Email
    text = EMAIL_PATTERN.sub("[EMAIL]", text)

    # Mask Phone
    text = PHONE_PATTERN.sub("[PHONE]", text)

    return text
