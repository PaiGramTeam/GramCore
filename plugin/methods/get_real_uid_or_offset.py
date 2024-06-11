import re
from typing import TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:
    from telegram import Update

REGEX = r"@(\d{10})|@(\d{9})|@(\d)"


class GetRealUidOrOffset:
    @staticmethod
    def get_real_uid_or_offset(update: "Update") -> Tuple[Optional[int], Optional[int]]:
        message = update.effective_message
        if not message:
            return None, None
        text = message.text or message.caption
        if not text:
            return None, None
        if matches := re.findall(REGEX, text):
            if numbers := [int(num) for match in matches for num in match if num != ""]:
                if 1 < numbers[0] < 10:
                    return None, numbers[0] - 1
                elif numbers[0] in [0, 1]:
                    return None, None
                return numbers[0], None
        return None, None
