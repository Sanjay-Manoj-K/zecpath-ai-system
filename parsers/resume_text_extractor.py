from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List

try:
    from docx import Document
except ImportError:
    Document = None

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


# ============================================================================
# NAMESPACES
# ============================================================================

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

TAG_P = f"{{{W_NS}}}p"
TAG_TBL = f"{{{W_NS}}}tbl"
TAG_TR = f"{{{W_NS}}}tr"
TAG_TC = f"{{{W_NS}}}tc"
TAG_T = f"{{{W_NS}}}t"
TAG_TAB = f"{{{W_NS}}}tab"
TAG_BR = f"{{{W_NS}}}br"


# ============================================================================
# TEXT NORMALIZATION
# ============================================================================

def normalize_spaces(text: str) -> str:
    """
    Normalize whitespace while preserving meaningful punctuation.
    """
    text = text.replace("\u00a0", " ")
    text = text.replace("\u200b", "")
    text = text.replace("\u202f", " ")

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\| *", " | ", text)
    text = re.sub(r" +([,.;:)])", r"\1", text)
    text = re.sub(r"([(]) +", r"\1", text)

    return text.strip()


def clean_line(text: str) -> str:
    text = normalize_spaces(text)

    # Remove repeated separators at the ends.
    text = re.sub(r"^(?:\s*\|\s*)+", "", text)
    text = re.sub(r"(?:\s*\|\s*)+$", "", text)

    return text.strip()


def deduplicate_lines(lines: List[str]) -> List[str]:
    """
    Remove exact duplicate paragraphs while preserving order.
    """
    result: List[str] = []
    seen = set()

    for line in lines:
        line = clean_line(line)

        if not line:
            continue

        key = re.sub(r"\s+", " ", line).strip().lower()

        if key in seen:
            continue

        seen.add(key)
        result.append(line)

    return result


# ============================================================================
# DOCX XML TEXT EXTRACTION
# ============================================================================

def extract_paragraph_text(paragraph_element) -> str:
    """
    Extract an entire Word paragraph as one string.

    IMPORTANT:
    We collect all <w:t> nodes INSIDE one <w:p>, rather than treating
    each XML text node as an individual line. This prevents fragmentation
    such as:

        May
        20
        –
        September
        20

    becoming one proper paragraph:

        May 20xx – September 20xx
    """
    pieces: List[str] = []

    for node in paragraph_element.iter():
        if node.tag == TAG_T:
            if node.text:
                pieces.append(node.text)

        elif node.tag == TAG_TAB:
            pieces.append(" ")

        elif node.tag == TAG_BR:
            pieces.append("\n")

    text = "".join(pieces)

    # Word sometimes stores spacing awkwardly around runs.
    text = normalize_spaces(text)

    return text


def extract_table_element(table_element) -> List[str]:
    """
    Recursively extract paragraphs from a table, including nested tables.

    We walk the XML directly rather than relying on python-docx's
    cell.paragraphs because some resume templates place their visible
    content inside nested tables.
    """
    results: List[str] = []

    for child in table_element:
        if child.tag != TAG_TR:
            continue

        # Process cells in the row in document order.
        for cell in child:
            if cell.tag != TAG_TC:
                continue

            # Process direct blocks inside the cell.
            for block in cell:
                if block.tag == TAG_P:
                    text = extract_paragraph_text(block)

                    if text:
                        results.append(text)

                elif block.tag == TAG_TBL:
                    results.extend(
                        extract_table_element(block)
                    )

    return results


def extract_document_body(doc) -> List[str]:
    """
    Read top-level DOCX body in original order.

    Handles:
        paragraph
        table
            nested paragraph
            nested table
    """
    results: List[str] = []

    body = doc.element.body

    for child in body:
        if child.tag == TAG_P:
            text = extract_paragraph_text(child)

            if text:
                results.append(text)

        elif child.tag == TAG_TBL:
            results.extend(
                extract_table_element(child)
            )

    return results


def extract_header_footer_elements(doc) -> List[str]:
    """
    Extract header/footer paragraphs and tables recursively.
    """
    results: List[str] = []

    try:
        for section in doc.sections:
            header = section.header
            footer = section.footer

            for paragraph in header.paragraphs:
                text = paragraph.text.strip()

                if text:
                    results.append(text)

            for table in header.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text = cell.text.strip()

                        if text:
                            results.append(text)

            for paragraph in footer.paragraphs:
                text = paragraph.text.strip()

                if text:
                    results.append(text)

            for table in footer.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text = cell.text.strip()

                        if text:
                            results.append(text)

    except Exception:
        pass

    return results


# ============================================================================
# DOCX TABLE CLEANING
# ============================================================================

def split_table_separators(lines: List[str]) -> List[str]:
    """
    Split actual table-column separators while keeping the text itself
    intact.

    Example:

        "EDUCATION | EDUCATION"

    becomes:

        "EDUCATION"
        "EDUCATION"

    which can then be deduplicated safely.
    """
    result: List[str] = []

    for line in lines:
        line = clean_line(line)

        if not line:
            continue

        parts = [
            part.strip()
            for part in re.split(r"\s*\|\s*", line)
            if part.strip()
        ]

        if len(parts) <= 1:
            result.append(line)
        else:
            result.extend(parts)

    return result


def remove_repeated_adjacent_content(lines: List[str]) -> List[str]:
    """
    Remove accidental adjacent repetition caused by Word table layouts.

    Example:

        Marketing Intern
        Marketing Intern

    becomes:

        Marketing Intern
    """
    result: List[str] = []

    previous_key = None

    for line in lines:
        key = re.sub(r"\s+", " ", line).strip().lower()

        if key == previous_key:
            continue

        result.append(line)
        previous_key = key

    return result


# ============================================================================
# DOCX
# ============================================================================

def extract_docx_text(file_path: str) -> str:
    if Document is None:
        raise ImportError(
            "python-docx is not installed. "
            "Run: pip install python-docx"
        )

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    print(f"Reading DOCX: {file_path}")

    doc = Document(str(path))

    print(f"Paragraphs found: {len(doc.paragraphs)}")
    print(f"Tables found: {len(doc.tables)}")

    # Main body.
    body_lines = extract_document_body(doc)

    # Headers/footers.
    header_footer_lines = extract_header_footer_elements(doc)

    # Prefer main document body. Headers/footers are added only as
    # supplementary content.
    all_lines = body_lines + header_footer_lines

    # First break table-column content into logical pieces.
    all_lines = split_table_separators(all_lines)

    # Remove repeated adjacent blocks.
    all_lines = remove_repeated_adjacent_content(all_lines)

    # Remove exact duplicates globally.
    all_lines = deduplicate_lines(all_lines)

    # Final cleanup.
    cleaned_lines: List[str] = []

    for line in all_lines:
        line = clean_line(line)

        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


# ============================================================================
# PDF
# ============================================================================

def extract_pdf_text(file_path: str) -> str:
    if fitz is None:
        raise ImportError(
            "PyMuPDF is not installed. "
            "Run: pip install pymupdf"
        )

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    print(f"Reading PDF: {file_path}")

    document = fitz.open(str(path))

    lines: List[str] = []

    for page in document:
        text = page.get_text("text")

        if not text:
            continue

        for line in text.splitlines():
            line = clean_line(line)

            if line:
                lines.append(line)

    document.close()

    lines = remove_repeated_adjacent_content(lines)

    return "\n".join(lines).strip()


# ============================================================================
# TXT
# ============================================================================

def extract_txt_text(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    print(f"Reading TXT: {file_path}")

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="latin-1")

    lines = []

    for line in text.splitlines():
        line = clean_line(line)

        if line:
            lines.append(line)

    return "\n".join(lines).strip()


# ============================================================================
# UNIFIED API
# ============================================================================

def extract_resume_text(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    extension = path.suffix.lower()

    print(f"\nSelected file: {file_path}")
    print(f"Extension: {extension}")

    if extension == ".docx":
        return extract_docx_text(str(path))

    if extension == ".pdf":
        return extract_pdf_text(str(path))

    if extension == ".txt":
        return extract_txt_text(str(path))

    raise ValueError(
        f"Unsupported file type: {extension}. "
        "Supported types: .docx, .pdf, .txt"
    )


# ============================================================================
# CLI
# ============================================================================

def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage:\n"
            "  python parsers/resume_text_extractor.py <resume-file>"
        )
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        text = extract_resume_text(file_path)

        print("\n" + "=" * 70)
        print("EXTRACTED RESUME TEXT")
        print("=" * 70)
        print(text)

        print("\n" + "=" * 70)
        print(f"Characters extracted: {len(text)}")
        print(f"Lines extracted: {len(text.splitlines())}")
        print("=" * 70)

    except Exception as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()