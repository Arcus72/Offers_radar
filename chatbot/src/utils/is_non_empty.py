from typing import Any

def is_non_empty(val: Any) -> bool:
    """Sprawdza, czy wartość nie jest None, pustą kolekcją ani pustym napisem."""
    if val is None:
        return False
    if isinstance(val, (str, list, dict, set, tuple)):
        if isinstance(val, str):
            return bool(val.strip())
        return any(is_non_empty(item) for item in val) if isinstance(val, (list, set, tuple)) else bool(val)
    return True
