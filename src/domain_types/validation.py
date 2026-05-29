"""Validation result types for domain rule checking."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationError:
    """Single validation failure."""

    field: str
    code: str
    message: str


@dataclass(frozen=True)
class ValidationResult:
    """Aggregate validation outcome."""

    is_valid: bool
    errors: tuple[ValidationError, ...]
