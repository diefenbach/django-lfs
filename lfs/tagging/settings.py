# coding=utf-8

import re

STOP_WORDS = (
    "und", "was", "u\.", "&", "\d" "\W", "mit", "das", "gehört", "\ber", "wohin", "\?"
)

RE_STOP_WORDS = re.compile("|".join(STOP_WORDS), re.IGNORECASE)
RE_SEPARATORS = re.compile("[\-_]")
