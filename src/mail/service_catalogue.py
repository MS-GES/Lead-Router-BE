
from dataclasses import dataclass


@dataclass(frozen=True)
class PortfolioCatalogue:
    supported_services: tuple[str, ...]
    unsupported_services: tuple[str, ...]


PORTFOLIO_CATALOGUE: dict[str, PortfolioCatalogue] = {
    "MS": PortfolioCatalogue(
        supported_services=(
            "Company incorporation",
            "Corporate services",
            "Accounting",
            "Bookkeeping",
            "Corporate tax",
            "VAT",
            "SPVs and foundations",
            "Company secretarial services",
            "Outsourced compliance",
            "MLRO services",
            "M&A"
        ),
        unsupported_services=(
            "Payroll",
            "Audit support",
            "Salary benchmarking",
            "Transfer pricing",
        ),
    ),
    "MS Kapital": PortfolioCatalogue(
        supported_services=(
            "Mergers and acquisitions",
            "Business valuation",
            "Capital raising",
            "Transaction advisory",
            "Due diligence",
            "Deal sourcing",
            "Exit strategy",
        ),
        unsupported_services=(),
    ),
    "Dot&": PortfolioCatalogue(
        supported_services=(
            "Consulting",
            "Executive search",
            "Technology hiring",
            "Reputation intelligence",
            "Social investment intelligence",
            "Cybersecurity",
        ),
        unsupported_services=(),
    ),
    "E7 Estates": PortfolioCatalogue(
        supported_services=(
            "Luxury real estate",
            "Property purchase",
            "Off-market luxury properties",
            "Real estate advisory",
        ),
        unsupported_services=(),
    ),
}


def get_portfolio_catalogue(
    portfolio: str,
) -> PortfolioCatalogue:
    """Return the catalogue for a known portfolio."""

    try:
        return PORTFOLIO_CATALOGUE[portfolio]
    except KeyError:
        raise ValueError(
            f"Unknown portfolio: {portfolio}"
        ) from None


def get_service_fit(
    portfolio: str,
    service: str | None,
) -> str:
    """
    Return supported, unsupported, or unknown.

    Only exact canonical service names are matched here.
    AI-based interpretation and aliases will be handled later.
    """

    if not service or not service.strip():
        return "unknown"

    catalogue = get_portfolio_catalogue(portfolio)
    normalized_service = service.strip().casefold()

    supported = {
        item.casefold()
        for item in catalogue.supported_services
    }
    unsupported = {
        item.casefold()
        for item in catalogue.unsupported_services
    }

    if normalized_service in supported:
        return "supported"

    if normalized_service in unsupported:
        return "unsupported"

    return "unknown"
