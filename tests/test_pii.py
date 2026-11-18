from app.services.pii_service import (
    detect_pii,
    mask_pii
)


def test_detect_email():
    text = "Contact john@example.com"

    result = detect_pii(text)

    assert "john@example.com" in result["emails"]


def test_detect_phone():
    text = "My phone is 09123456789"

    result = detect_pii(text)

    assert len(result["phones"]) >= 1


def test_detect_ssn():
    text = "My SSN is 123-45-6789"

    result = detect_pii(text)

    assert "123-45-6789" in result["ssns"]


def test_mask_email():
    text = "Email: john@example.com"

    result = mask_pii(text)

    assert "[EMAIL]" in result
    assert "john@example.com" not in result


def test_mask_phone():
    text = "Phone: 09123456789"

    result = mask_pii(text)

    assert "[PHONE]" in result
    assert "09123456789" not in result


def test_mask_ssn():
    text = "SSN: 123-45-6789"

    result = mask_pii(text)

    assert "[SSN]" in result
    assert "123-45-6789" not in result


def test_mask_multiple_pii():
    text = (
        "John's email is john@example.com "
        "and phone is 09123456789."
    )

    result = mask_pii(text)

    assert "[EMAIL]" in result
    assert "[PHONE]" in result

    assert "john@example.com" not in result
    assert "09123456789" not in result


if __name__ == "__main__":
    test_detect_email()
    test_detect_phone()
    test_detect_ssn()

    test_mask_email()
    test_mask_phone()
    test_mask_ssn()
    test_mask_multiple_pii()

    print("All PII tests passed!")
