import re

from collector.core.types import PLCConfig, TagConfig


class SiemensS7Adapter:
    """Read-only Siemens S7 adapter for DB and marker-memory addresses."""

    def __init__(self, cfg: PLCConfig):
        self.cfg = cfg
        self.client = None

    def connect(self):
        try:
            import snap7
        except ImportError as exc:
            raise RuntimeError("Install python-snap7") from exc

        self.client = snap7.client.Client()
        self.client.connect(self.cfg.host, self.cfg.rack, self.cfg.slot, self.cfg.port)
        if not self.client.get_connected():
            raise ConnectionError(f"S7 connection failed: {self.cfg.host}")

    def disconnect(self):
        if self.client:
            try:
                if self.client.get_connected():
                    self.client.disconnect()
            finally:
                self.client = None

    def is_connected(self):
        return bool(self.client and self.client.get_connected())

    @staticmethod
    def _decode(raw, data_type, bit=None):
        import snap7.util

        if bit is not None:
            if bit < 0 or bit > 7:
                raise ValueError("S7 bit address must be between 0 and 7")
            return snap7.util.get_bool(raw, 0, bit)

        decoders = {
            "BOOL": lambda: snap7.util.get_bool(raw, 0, 0),
            "INT": lambda: snap7.util.get_int(raw, 0),
            "DINT": lambda: snap7.util.get_dint(raw, 0),
            "REAL": lambda: snap7.util.get_real(raw, 0),
            "FLOAT": lambda: snap7.util.get_real(raw, 0),
            "WORD": lambda: snap7.util.get_word(raw, 0),
            "DWORD": lambda: snap7.util.get_dword(raw, 0),
        }
        try:
            return decoders[data_type.upper()]()
        except KeyError as exc:
            raise ValueError(f"Unsupported S7 data type: {data_type}") from exc

    def read(self, tag: TagConfig):
        if not self.is_connected():
            raise ConnectionError("S7 is disconnected")

        from snap7.type import Areas

        address = tag.address.strip().upper()

        # Siemens marker memory: MW3008 means a two-byte word beginning at
        # marker byte offset 3008. This matches the supplied HMI logger.
        marker = re.fullmatch(r"M([BWD])(\d+)(?:\.(\d+))?", address)
        if marker:
            area_code, offset_text, bit_text = marker.groups()
            size = {"B": 1, "W": 2, "D": 4}[area_code]
            bit = int(bit_text) if bit_text is not None else None
            raw = self.client.read_area(Areas.MK, 0, int(offset_text), size)
            return self._decode(raw, tag.data_type, bit)

        # Data-block support remains available for DBX/DBB/DBW/DBD tags.
        db_match = re.fullmatch(
            r"DB(\d+)\.DB([XBWD])(\d+)(?:\.(\d+))?", address
        )
        if not db_match:
            raise ValueError(
                f"Unsupported S7 address {tag.address!r}; expected MW3008 or DB1.DBW0"
            )

        db_text, area_code, offset_text, bit_text = db_match.groups()
        size = {"X": 1, "B": 1, "W": 2, "D": 4}[area_code]
        bit = int(bit_text) if bit_text is not None else None
        raw = self.client.db_read(int(db_text), int(offset_text), size)
        return self._decode(raw, tag.data_type, bit)
