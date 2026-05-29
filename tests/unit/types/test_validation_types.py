"""TC-FUNC-BND-009: Validation types — instantiation, frozen, boundary."""

from __future__ import annotations

import pytest

from domain_types.validation import ValidationError, ValidationResult


class TestValidationError:
    def test_creation(self) -> None:
        err = ValidationError(field="search_area", code="EMPTY", message="좌표가 비어있습니다")
        assert err.field == "search_area"
        assert err.code == "EMPTY"

    def test_frozen(self) -> None:
        err = ValidationError(field="x", code="RANGE", message="범위 초과")
        with pytest.raises(AttributeError):
            err.code = "OK"


class TestValidationResult:
    def test_valid_result(self) -> None:
        result = ValidationResult(is_valid=True, errors=())
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_invalid_result(self) -> None:
        errors = (
            ValidationError(field="area", code="EMPTY", message="구역 미지정"),
            ValidationError(field="method", code="INCOMPATIBLE", message="지형 불일치"),
        )
        result = ValidationResult(is_valid=False, errors=errors)
        assert result.is_valid is False
        assert len(result.errors) == 2

    def test_frozen(self) -> None:
        result = ValidationResult(is_valid=True, errors=())
        with pytest.raises(AttributeError):
            result.is_valid = False

    def test_contradictory_state_allowed(self) -> None:
        """DTO는 값만 보관 — is_valid=True인데 errors가 있어도 생성 가능 (검증은 Service 책임)."""
        result = ValidationResult(
            is_valid=True,
            errors=(ValidationError(field="x", code="WARN", message="경고"),),
        )
        assert result.is_valid is True
        assert len(result.errors) == 1
