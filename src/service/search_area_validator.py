"""SearchArea validation service.

Validates SearchArea geometry according to mission_policy rules.
"""

from __future__ import annotations

from config.mission_policy import SearchAreaPolicy
from domain_types.mission import SearchArea
from domain_types.validation import ValidationError, ValidationResult

_DEFAULT_POLICY = SearchAreaPolicy()


def validate_search_area(
    area: SearchArea,
    policy: SearchAreaPolicy | None = None,
) -> ValidationResult:
    """Validate a SearchArea against policy constraints.

    Returns a ValidationResult with is_valid=True if all checks pass.
    """
    policy = policy or _DEFAULT_POLICY
    errors: list[ValidationError] = []

    # Check minimum coordinate count
    min_count = policy.min_coordinates.get(area.area_type)
    if min_count is not None and len(area.coordinates) < min_count:
        errors.append(
            ValidationError(
                field="coordinates",
                code="MIN_COORDINATES",
                message=(
                    f"{area.area_type} requires at least {min_count} coordinates, "
                    f"got {len(area.coordinates)}"
                ),
            )
        )

    # Check frame_id is not empty
    if not area.frame_id.strip():
        errors.append(
            ValidationError(
                field="frame_id",
                code="EMPTY_FRAME_ID",
                message="frame_id must not be empty",
            )
        )

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=tuple(errors),
    )
