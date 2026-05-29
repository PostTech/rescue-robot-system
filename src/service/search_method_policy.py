"""SearchMethod compatibility policy.

Validates that a SearchMethod is compatible with the current terrain.
"""

from __future__ import annotations

from config.mission_policy import is_method_compatible
from domain_types.mission import SearchMethod
from domain_types.validation import ValidationError, ValidationResult


def validate_search_method(
    method: SearchMethod,
    terrain_class: str,
) -> ValidationResult:
    """Validate that a search method is compatible with the terrain.

    Args:
        method: The selected search method.
        terrain_class: The terrain classification string.

    Returns:
        ValidationResult with is_valid=True if compatible.
    """
    if is_method_compatible(terrain_class, method):
        return ValidationResult(is_valid=True, errors=())

    return ValidationResult(
        is_valid=False,
        errors=(
            ValidationError(
                field="search_method",
                code="INCOMPATIBLE_TERRAIN",
                message=(f"SearchMethod {method} is not compatible with terrain {terrain_class}"),
            ),
        ),
    )
