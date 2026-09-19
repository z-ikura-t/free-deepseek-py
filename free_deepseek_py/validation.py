import uuid

from .src.exceptions import ValidationError


def validate_int(value, name: str, allow_none: bool = False, min_value: int | None = None) -> None:
    if value is None:
        if allow_none: return
        raise ValidationError(f'{name} is required')
    
    if not isinstance(value, int) or isinstance(value, bool):
        if allow_none:
            if min_value is not None: raise ValidationError(f'{name} must be an int >= {min_value} or None')
            raise ValidationError(f'{name} must be an int or None')
        if min_value is not None: raise ValidationError(f'{name} must be an int >= {min_value}')
        raise ValidationError(f'{name} must be an int')
    
    if min_value is not None and value < min_value:
        if allow_none: raise ValidationError(f'{name} must be an int >= {min_value} or None')
        raise ValidationError(f'{name} must be an int >= {min_value}')


def validate_float(value, name: str, allow_none: bool = False) -> None:
    if value is None:
        if allow_none: return
        raise ValidationError(f'{name} is required')
    
    if not isinstance(value, float):
        if allow_none: raise ValidationError(f'{name} must be a float or None')
        raise ValidationError(f'{name} must be a float')


def validate_timestamp(value, name: str) -> None:
    if value is None: return
    
    if not isinstance(value, (int, float)) or isinstance(value, bool): raise ValidationError(f'{name} must be a number or None')
    
    if value < 0: raise ValidationError(f'{name} must be a non-negative number or None')


def validate_str(value, name: str) -> None:
    if not isinstance(value, str): raise ValidationError(f'{name} must be a str')
    
    if not value.strip(): raise ValidationError(f'{name} cannot be empty')


def validate_list(value, name: str, item_type: type | None = None) -> None:
    if not isinstance(value, list): raise ValidationError(f'{name} must be a list')
    
    if not value: raise ValidationError(f'{name} cannot be empty')
    
    if item_type is not None:
        for i, item in enumerate(value):
            if not isinstance(item, item_type): raise ValidationError(f'{name}[{i}] must be {item_type.__name__}')


def validate_bool(value, name: str) -> None:
    if not isinstance(value, bool):
        raise ValidationError(f'{name} must be a bool')


def validate_chat_id(chat_id: str) -> None:
    validate_str(chat_id, 'chat_id')
    try: uuid.UUID(chat_id)
    except ValueError: raise ValidationError('Invalid chat ID format. Must be a valid UUID.')


def validate_chat_ids(chat_ids: list[str]) -> None:
    validate_list(chat_ids, 'chat_ids', item_type=str)
    for chat_id in chat_ids:
        validate_chat_id(chat_id)