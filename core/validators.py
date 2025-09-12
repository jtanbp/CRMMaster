# 1. Standard Library
import re

# 2. Third Party Library
from PySide6.QtWidgets import QMessageBox, QWidget

# 3. Internal Library


def validate_required(
        value: str,
        field_name: str,
        parent: QWidget = None) -> bool:
    """Ensure the field is not empty."""
    if not value.strip():
        QMessageBox.warning(
            parent,
            'Validation Error',
            f'{field_name} cannot be empty.')
        return False
    return True


def validate_max_length(
        value: str,
        max_length: int,
        field_name: str,
        parent: QWidget = None) -> bool:
    """Ensure the field does not exceed max length."""
    if len(value.strip()) > max_length:
        QMessageBox.warning(
            parent,
            'Validation Error',
            f'{field_name} exceeds maximum length of {max_length}.')
        return False
    return True


def validate_characters(
        value: str,
        allowed_regex: str,
        field_name: str,
        parent: QWidget = None) -> bool:
    """Validate allowed characters using a regex."""
    if not re.fullmatch(allowed_regex, value.strip()):
        QMessageBox.warning(
            parent,
            'Validation Error',
            f'{field_name} contains invalid characters.')
        return False
    return True


def validate_selection(
        value: str,
        allowed_options: list,
        field_name: str,
        parent: QWidget = None) -> bool:
    """Validate that a dropdown selection is in allowed options."""
    if value not in allowed_options:
        QMessageBox.warning(
            parent,
            'Validation Error',
            f'{field_name} selection is invalid.')
        return False
    return True
