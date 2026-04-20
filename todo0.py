from resiliparse.extract.html2text import extract_plain_text
from resiliparse.parse.encoding import detect_encoding


def foo(byte_string: bytes) -> str:
    detected = detect_encoding(byte_string)
    encoding = detected if detected else "utf-8"
    html_text = byte_string.decode(encoding, errors="replace")
    return extract_plain_text(html_text)
