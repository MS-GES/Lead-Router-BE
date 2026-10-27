 

import pytest

from src.mail.service_catalogue import (
    get_portfolio_catalogue,
    get_service_fit,
)


def test_ms_supported_service():
    assert get_service_fit(
        "MS", "Company incorporation"
    ) == "supported"


def test_ms_explicitly_unsupported_service():
    assert get_service_fit(
        "MS", "Payroll"
    ) == "unsupported"


def test_unknown_service_is_not_automatically_unsupported():
    assert get_service_fit(
        "MS", "Something not listed"
    ) == "unknown"


def test_missing_service_is_unknown():
    assert get_service_fit("MS", None) == "unknown"


def test_ms_kapital_catalogue():
    catalogue = get_portfolio_catalogue("MS Kapital")

    assert "Business valuation" in catalogue.supported_services
    assert catalogue.unsupported_services == ()


def test_unknown_portfolio_raises_error():
    with pytest.raises(ValueError):
        get_portfolio_catalogue("Unknown Brand")
