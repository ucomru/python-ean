from copy import copy
from pathlib import Path

from lxml.etree import Element, SubElement, ElementTree, tostring

"""
    European Article Number or EAN:

    https://wikipedia.org/wiki/European_Article_Number

    First digit MASK:

        L: 6 left digit
        R: 6 right digit
"""
MASK = {
    "0": {
        "L": "LLLLLL",
        "R": "RRRRRR",
    },
    "1": {
        "L": "LLGLGG",
        "R": "RRRRRR",
    },
    "2": {
        "L": "LLGGLG",
        "R": "RRRRRR",
    },
    "3": {
        "L": "LLGGGL",
        "R": "RRRRRR",
    },
    "4": {
        "L": "LGLLGG",
        "R": "RRRRRR",
    },
    "5": {
        "L": "LGGLLG",
        "R": "RRRRRR",
    },
    "6": {
        "L": "LGGGLL",
        "R": "RRRRRR",
    },
    "7": {
        "L": "LGLGLG",
        "R": "RRRRRR",
    },
    "8": {
        "L": "LGLGGL",
        "R": "RRRRRR",
    },
    "9": {
        "L": "LGGLGL",
        "R": "RRRRRR",
    },
}

"""
    CODE (7 bit) = digit[MASK]
"""
CODE = {
    "0": {
        "L": "0001101",
        "R": "1110010",
        "G": "0100111",
    },
    "1": {
        "L": "0011001",
        "R": "1100110",
        "G": "0110011",
    },
    "2": {
        "L": "0010011",
        "R": "1101100",
        "G": "0011011",
    },
    "3": {
        "L": "0111101",
        "R": "1000010",
        "G": "0100001",
    },
    "4": {
        "L": "0100011",
        "R": "1011100",
        "G": "0011101",
    },
    "5": {
        "L": "0110001",
        "R": "1001110",
        "G": "0111001",
    },
    "6": {
        "L": "0101111",
        "R": "1010000",
        "G": "0000101",
    },
    "7": {
        "L": "0111011",
        "R": "1000100",
        "G": "0010001",
    },
    "8": {
        "L": "0110111",
        "R": "1001000",
        "G": "0001001",
    },
    "9": {
        "L": "0001011",
        "R": "1110100",
        "G": "0010111",
    },
}


class Ean13:
    def __init__(self, barcode: str) -> None:
        barcode = barcode.replace("-", "")

        if not barcode.isdigit():
            raise ValueError("Invalid character in barcode (digits and `-` only)")

        if len(barcode) not in (12, 13):
            raise ValueError("EAN13 wrong length (12 or 13 characters only)")

        if len(barcode) == 13:
            self.barcode, check_sum = barcode[:12], barcode[12]
            self._check_sum_()
            if check_sum != self.check_sum:
                raise ValueError(
                    (
                        f"Invalid check summ digit `{check_sum}`, "
                        f"expecting `{self.check_sum}`"
                    )
                )
        else:
            self.barcode = barcode
            self._check_sum_()

        self._code_()
        self._build_()

    def _check_sum_(self) -> None:
        """Calculates the checksum for EAN13 code"""

        def _sum(digits: str, start: int | None = None) -> int:
            return sum((int(digit) for digit in digits[start::2]))

        barcode = self.barcode
        check_sum = str(-((_sum(barcode) + _sum(barcode, 1) * 3) % 10) % 10)

        self.check_sum = check_sum
        self.barcode = barcode + check_sum

    def _code_(self) -> None:
        """Build barcodes array"""
        barcode = self.barcode
        masks = MASK[barcode[0]]
        digits = {"L": barcode[1:7], "R": barcode[7:]}
        group = {}
        for side in ("L", "R"):
            group[side] = []
            for i in range(6):
                digit = digits[side][i]
                mask = masks[side][i]
                code = CODE[digit][mask]
                group[side].append(code)

        code = "".join(("I0I", *group["L"], "0I0I0", *group["R"], "I0I"))

        code_pack = copy(code)
        # Max len of joined dark bars == 4
        for block, pack in (("1111", "4"), ("111", "3"), ("11", "2")):
            if block in code:
                code_pack = code_pack.replace(block, pack)

        self._code = code
        self._code_pack = code_pack

    @property
    def code(self) -> str:
        """Code array"""
        return self._code.replace("I0I", "101")

    def _build_(self) -> None:
        """Build EAN13 svg block"""

        barcode = self.barcode
        code_pack = self._code_pack

        top = 0
        width = 220
        height = 160  # 118
        light = "#FFDDEE"  # '#FFFFFF'
        dark = "#000000"
        bar_heigh = height - top - 18
        sep_heigh = bar_heigh + 10  # +18 | +10 | 0
        spacing = 4  # 0..4

        root = Element(
            "svg",
            xmlns="http://www.w3.org/2000/svg",
            version="1.1",
            width=str(width),
            height=str(height),
        )

        SubElement(root, "desc").text = f"python-ean, {barcode}"

        barcode_elem = SubElement(root, "g", id="barcode", fill=dark)

        SubElement(
            barcode_elem,
            "rect",
            x="0",
            y="0",
            width=str(width),
            height=str(height),
            fill=light,
        )

        x = 0
        for code in code_pack:
            if code == "0":
                # clear width 2 px
                x += 2
            else:
                # width = 2_px * bar_width[1 ... 4]
                w = 2 if code in ("1", "I") else int(code) * 2
                # 'I' is a separate line, '1' ... '4' is a regular bar
                h = sep_heigh if code == "I" else bar_heigh
                SubElement(
                    barcode_elem,
                    "rect",
                    x=str(20 + x),
                    y=str(top),
                    width=str(w),
                    height=str(h),
                )
                x += w

        text_style = {
            "font-family": "Helvetica, sans-serif",
            "font-size": "20",
        }
        barcode_text_elem = SubElement(root, "g", id="text", **text_style)

        text_digit = (barcode[0], barcode[1:7], barcode[7:13])
        text_y = str(height - 1)
        text_param = {
            "x": ("0", "68", "162"),
            "y": (text_y, text_y, text_y),
            "text-anchor": ("start", "middle", "middle"),
        }
        for i in range(3):
            param = {key: text_param[key][i] for key in text_param}

            if spacing and i > 0:
                param["letter-spacing"] = str(spacing * 0.5)

            SubElement(barcode_text_elem, "text", **param).text = text_digit[i]

        self._svg = ElementTree(root)

    def xml(
        self, declaration: bool = True, pretty: bool = True, decode: bool = True
    ) -> str:
        """Get xml string"""
        xml_string = tostring(
            self._svg,
            encoding="utf-8",
            xml_declaration=declaration,
            pretty_print=pretty,
        )

        if decode:
            return xml_string.decode()
        else:
            return xml_string

    def save(
        self, file: Path | None = None, declaration: bool = True, pretty: bool = True
    ) -> None:
        """Save to the .svg file"""
        if file is None:
            file_name = Path(self.barcode).with_suffix(".svg")
        else:
            file_name = file.with_suffix(".svg")

        self._svg.write(
            file_name,
            encoding="utf-8",
            xml_declaration=declaration,
            pretty_print=pretty,
        )
