def is_valid_item_id(item_id: str) -> bool:
    """Check if the item id is valid"""
    return isinstance(item_id, str) and len(item_id) == 32
