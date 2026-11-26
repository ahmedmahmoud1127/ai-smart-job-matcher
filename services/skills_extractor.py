"""Dictionary + regex skill extraction."""
import re
from collections import OrderedDict

from data.skills_catalog import ALIASES, CATEGORIES, SKILL_CATEGORY


def _pattern(alias: str) -> re.Pattern:
    esc = re.escape(alias).replace(r"\ ", r"[\s\-]+")
    return re.compile(rf"(?<![A-Za-z0-9+#.]){esc}(?![A-Za-z0-9+#])", re.I)


_PATTERNS = {name: [_pattern(a) for a in aliases] for name, aliases in ALIASES.items()}


def find_skills(text: str) -> list:
    """Return [{'name','category','mentions'}] for every catalog skill found in the text."""
    found = []
    for name, patterns in _PATTERNS.items():
        count = sum(len(p.findall(text)) for p in patterns)
        if count:
            found.append({"name": name, "category": SKILL_CATEGORY[name], "mentions": count})
    order = {c: i for i, c in enumerate(CATEGORIES)}
    return sorted(found, key=lambda s: (order[s["category"]], -s["mentions"], s["name"]))


def group_by_category(skills: list) -> "OrderedDict[str, list]":
    grouped = OrderedDict((c, []) for c in CATEGORIES)
    for s in skills:
        grouped[s["category"]].append(s["name"])
    return OrderedDict((c, v) for c, v in grouped.items() if v)


def canonical_names(text: str) -> set:
    """Map free text (e.g. a profile skill such as 'Git & GitHub') to canonical catalog names."""
    return {s["name"] for s in find_skills(text)}
