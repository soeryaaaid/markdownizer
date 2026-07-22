from odf import table as odf_table
from odf import teletype, text
from odf.opendocument import load

TEXTNS = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"


def _table_to_md(table_element) -> str | None:
    rows = []
    for row in table_element.getElementsByType(odf_table.TableRow):
        cells = []
        for cell in row.getElementsByType(odf_table.TableCell):
            t = " ".join(
                teletype.extractText(p).strip() for p in cell.getElementsByType(text.P)
            ).strip()
            cells.append(t)
        if any(c for c in cells):
            rows.append(cells)

    if not rows:
        return None
    n = max(len(r) for r in rows)
    rows = [r + [""] * (n - len(r)) for r in rows]
    lines = [
        "| " + " | ".join(rows[0]) + " |",
        "| " + " | ".join(["---"] * n) + " |",
    ]
    lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(lines)


def _convert_text_doc(file_path: str) -> str | None:
    doc = load(file_path)
    office_text = doc.body.childNodes[0]
    parts = []

    for child in office_text.childNodes:
        qname = getattr(child, "qname", None)
        if qname is None:
            continue

        if qname[1] == "p":
            t = teletype.extractText(child).strip()
            if t:
                parts.append(t)

        elif qname[1] == "h":
            level = child.attributes.get((TEXTNS, "outline-level"), "1")
            t = teletype.extractText(child).strip()
            if t:
                parts.append(f"{'#' * int(level)} {t}")

        elif qname[1] == "table":
            result = _table_to_md(child)
            if result:
                parts.append(result)

    return "\n\n".join(parts) if parts else None


def _convert_presentation(file_path: str) -> str | None:
    doc = load(file_path)
    office_presentation = doc.body.childNodes[0]
    parts = []

    for page in office_presentation.childNodes:
        qname = getattr(page, "qname", None)
        if qname is None or qname[1] != "page":
            continue

        page_name = page.attributes.get(
            ("urn:oasis:names:tc:opendocument:xmlns:drawing:1.0", "name"), ""
        )
        slide_parts = []
        if page_name:
            slide_parts.append(f"## {page_name}")

        tb_ord = 0
        for frame in page.childNodes:
            fq = getattr(frame, "qname", None)
            if fq is None or fq[1] != "frame":
                continue
            for tb in frame.childNodes:
                tbq = getattr(tb, "qname", None)
                if tbq is None or tbq[1] != "text-box":
                    continue
                tb_ord += 1
                paras = []
                for p in tb.getElementsByType(text.P):
                    t = teletype.extractText(p).strip()
                    if t:
                        paras.append(t)
                if not paras:
                    continue
                if tb_ord == 1 and len(paras) <= 1:
                    slide_parts.append(paras[0])
                else:
                    for para in paras:
                        slide_parts.append(f"- {para}")

        if slide_parts:
            parts.append("\n".join(slide_parts))

    return "\n\n".join(parts) if parts else None


def _convert_spreadsheet(file_path: str) -> str | None:
    doc = load(file_path)
    office_spreadsheet = doc.body.childNodes[0]
    parts = []

    for child in office_spreadsheet.childNodes:
        qname = getattr(child, "qname", None)
        if qname is None or qname[1] != "table":
            continue

        table_name = child.attributes.get(
            ("urn:oasis:names:tc:opendocument:xmlns:table:1.0", "name"), ""
        )
        lines = []
        if table_name:
            lines.append(f"### {table_name}")

        result = _table_to_md(child)
        if result:
            lines.append(result)

        if lines:
            parts.append("\n".join(lines))

    return "\n\n".join(parts) if parts else None


def convert_opendoc(file_path: str) -> str | None:
    try:
        doc = load(file_path)
    except Exception:
        return None

    body = doc.body
    if not body.childNodes:
        return None

    office = body.childNodes[0]
    qname = getattr(office, "qname", None)
    if qname is None:
        return None

    tag = qname[1]
    if tag == "text":
        return _convert_text_doc(file_path)
    elif tag == "presentation":
        return _convert_presentation(file_path)
    elif tag == "spreadsheet":
        return _convert_spreadsheet(file_path)

    return None
