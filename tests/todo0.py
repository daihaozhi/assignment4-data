from fastwarc.warc import ArchiveIterator, WarcRecordType
from resiliparse.extract.html2text import extract_plain_text
from resiliparse.parse.encoding import detect_encoding


def foo(byteString: bytes):
    detected = detect_encoding(byteString)
    encoding = detected if detected else "utf-8"
    html_text = byteString.decode(encoding, errors="replace")
    return extract_plain_text(html_text)
