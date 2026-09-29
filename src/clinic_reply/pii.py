"""Remove personal data from a message before it is stored, embedded or logged (ADR 0003).

What gets replaced, and by what:

- e-mail addresses -> [EMAIL]
- Brazilian phone numbers, with or without country code, area code and separators -> [PHONE]
- CPF numbers written with their separators -> [CPF]
- dates with a year, such as the birth date on the sign-up form -> [DATE]; an appointment
  date such as "22/07" keeps its day and month
- names -> [NAME], for every word in the given set, matched whole, without regard to case
  or accents

Names are not detected by a model. The caller passes the set of name words taken from the
export itself (the patients' profile names and the attendants' names), which is the list
this corpus can give us. A name that never appears in that list goes through untouched.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_CPF = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")
_FULL_DATE = re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b")
# +55 31 99999-1234, (31) 99999-1234, 31 9 9999-1234, 31999991234, 99999-1234
_PHONE = re.compile(
    r"(?<!\d)(?:\+?55[\s.-]?)?(?:\(?\d{2}\)?[\s.-]?)?(?:9[\s.-]?)?\d{4}[\s.-]?\d{4}(?!\d)"
)
_WORD = re.compile(r"[^\W\d_]+")

# Words that appear inside full names without being names.
CONNECTIVES = ("de", "da", "do", "das", "dos", "e")


def fold(word: str) -> str:
    """Lowercase without accents, so that "Verçosa" and "vercosa" share one key."""
    decomposed = unicodedata.normalize("NFKD", word.lower())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def name_words(
    names: Iterable[str], min_length: int = 3, ignore: Iterable[str] = CONNECTIVES
) -> frozenset[str]:
    """Split full names into folded words, dropping short ones and the words in ignore."""
    skip = {fold(word) for word in ignore}
    words: set[str] = set()
    for name in names:
        for word in _WORD.findall(name):
            key = fold(word)
            if len(key) >= min_length and key not in skip:
                words.add(key)
    return frozenset(words)


def scrub(text: str, names: frozenset[str] = frozenset()) -> str:
    """Return the text with e-mails, CPFs, full dates, phones and the given names replaced."""
    text = _EMAIL.sub("[EMAIL]", text)
    text = _CPF.sub("[CPF]", text)
    text = _FULL_DATE.sub("[DATE]", text)
    text = _PHONE.sub("[PHONE]", text)
    if names:
        text = _WORD.sub(lambda m: "[NAME]" if fold(m.group()) in names else m.group(), text)
    return text
