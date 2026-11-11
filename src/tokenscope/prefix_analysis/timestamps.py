"""Located calendar-valid dates. Path overlap is decided by the slot consumer."""

import re
from datetime import datetime

DATE = re.compile(
    r"(?<!\d)(?P<year>\d{4})(?:-(?P<month>\d{1,2})-(?P<day>\d{1,2})"
    r"|/(?P<slash_month>\d{1,2})/(?P<slash_day>\d{1,2})"
    r"|年(?P<cn_month>\d{1,2})月(?P<cn_day>\d{1,2})日)"
    r"(?:(?:T|[ \t]+|(?<=日))(?P<hour>\d{1,2})(?::|时)(?P<minute>\d{2})"
    r"(?:(?::|分)(?P<second>\d{2})(?:\.\d{1,9})?秒?)?分?"
    r"(?P<zone>Z|[+-]\d{2}:?\d{2})?)?(?!\d)"
)


def valid_timestamps(text: str) -> list[tuple[int, int, str]]:
    result = []
    for match in DATE.finditer(text):
        fields = match.groupdict()
        try:
            datetime(
                int(fields["year"]),
                int(fields["month"] or fields["slash_month"] or fields["cn_month"]),
                int(fields["day"] or fields["slash_day"] or fields["cn_day"]),
                int(fields["hour"] or 0),
                int(fields["minute"] or 0),
                int(fields["second"] or 0),
            )
            zone = fields["zone"]
            if zone and zone != "Z":
                digits = zone[1:].replace(":", "")
                if int(digits[:2]) > 23 or int(digits[2:]) > 59:
                    continue
        except ValueError:
            continue
        result.append((match.start(), match.end(), match.group()))
    return result
