from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

from app.services import __name__ as services_package


# Maximum allowed file size: 10 MB
MAX_FILE_SIZE = 10 * 1024 * 1024


class DocumentExtractionError(Exception):
    """Raised when a document cannot be safely processed."""
    pass


def validate_file_size(file_bytes: bytes) -> None:
    """
    Validate file size and reject empty files.
    """

    if not isinstance(file_bytes, bytes):
        raise DocumentExtractionError(
            "Invalid file content."
        )

    if not file_bytes:
        raise DocumentExtractionError(
            "Uploaded file is empty."
        )

    if len(file_bytes) > MAX_FILE_SIZE:
        raise DocumentExtractionError(
            "File size exceeds the 10 MB limit."
        )


def validate_filename(filename: str) -> str:
    """
    Validate filename and return its lowercase extension.
    """

    if not isinstance(filename, str) or not filename.strip():
        raise DocumentExtractionError(
            "Filename is required."
        )

    extension = Path(filename).suffix.lower()

    if extension not in {".pdf", ".txt"}:
        raise DocumentExtractionError(
            "Unsupported file format. Only PDF and TXT are allowed."
        )

    return extension


def extract_pdf_text(file_bytes: bytes) -> str:
    """
    Extract text from a PDF file.
    """

    # Validate PDF file signature.
    if not file_bytes.startswith(b"%PDF-"):
        raise DocumentExtractionError(
            "Invalid PDF file signature."
        )

    try:
        reader = PdfReader(
            BytesIO(file_bytes),
            strict=True
        )

        # Reject encrypted PDFs.
        if reader.is_encrypted:
            raise DocumentExtractionError(
                "Encrypted PDF files are not supported."
            )

        extracted_pages = []

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text and page_text.strip():
                extracted_pages.append(page_text.strip())

        full_text = "\n\n".join(extracted_pages).strip()

        if not full_text:
            raise DocumentExtractionError(
                "No extractable text found in PDF."
            )

        return full_text

    except DocumentExtractionError:
        raise

    except Exception as exc:
        raise DocumentExtractionError(
            "Unable to read PDF file."
        ) from exc


def extract_txt_text(file_bytes: bytes) -> str:
    """
    Extract text from a UTF-8 TXT file.
    """

    try:
        text = file_bytes.decode("utf-8-sig")

    except UnicodeDecodeError as exc:
        raise DocumentExtractionError(
            "TXT file must use UTF-8 encoding."
        ) from exc

    # Reject binary-like content.
    if "\x00" in text:
        raise DocumentExtractionError(
            "Invalid text file content."
        )

    text = text.strip()

    if not text:
        raise DocumentExtractionError(
            "TXT file contains no readable text."
        )

    return text


def extract_document_text(
    filename: str,
    file_bytes: bytes
) -> str:
    """
    Main extraction function.

    Supports PDF and TXT files.
    """

    # Step 1: Validate file size.
    validate_file_size(file_bytes)

    # Step 2: Validate filename and extension.
    extension = validate_filename(filename)

    # Step 3: Extract text based on file type.
    if extension == ".pdf":
        return extract_pdf_text(file_bytes)

    if extension == ".txt":
        return extract_txt_text(file_bytes)

    raise DocumentExtractionError(
        "Unsupported file format."
    )
