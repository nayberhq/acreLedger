"""Lossless fixed-width structural reader for official Census finance public-use files.

Field semantics intentionally NOT inferred until verified against Census technical PDFs.
"""
from dataclasses import dataclass
import io, zipfile

@dataclass(frozen=True)
class RawRecord:
    source_member: str
    line_number: int
    raw: str

EXPECTED_WIDTHS={"finance":32,"government_directory":146,"state_type":35}

def inspect_records(archive_bytes, member_suffix, kind, limit=None):
    if kind not in EXPECTED_WIDTHS:
        raise ValueError("Unknown record kind")
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        members=[m for m in archive.namelist() if m.endswith(member_suffix)]
        if len(members)!=1:
            raise ValueError(f"Expected one member ending {member_suffix}, got {members}")
        name=members[0]
        with archive.open(name) as handle:
            for number,line in enumerate(handle,1):
                raw=line.decode("latin-1").rstrip("\r\n")
                if len(raw)!=EXPECTED_WIDTHS[kind]:
                    raise ValueError(f"{name}:{number}: expected width {EXPECTED_WIDTHS[kind]}, got {len(raw)}")
                yield RawRecord(name,number,raw)
                if limit is not None and number>=limit:break
