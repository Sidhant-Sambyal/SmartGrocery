from app.core.constants import STAPLES


def is_staple(item: str):

    item = item.strip().lower()

    return item in STAPLES