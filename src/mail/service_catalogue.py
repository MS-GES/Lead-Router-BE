
from dataclasses import dataclass


@dataclass(frozen=True)
class PortfolioCatalogue:
    supported_services: tuple[str, ...]
    unsupported_services: tuple[str, ...]


PORTFOLIO_CATALOGUE: dict[str, PortfolioCatalogue] = {
    "MS": PortfolioCatalogue(
        supported_services=(
            "Company Incorporation (ADGM, DIFC, QFC, RAK ICC)",
            "Company Incorporation",
            "SPV & Holding Company Setup",
            "SPV Setup",
            "Holding Company Setup",
            "SPVs and foundations",
            "Foundation Setup",
            "Corporate Tax Advisory & Filings",
            "Corporate Tax",
            "VAT Advisory & Compliance",
            "VAT",
            "Transfer Pricing",
            "Accounting & Bookkeeping Services",
            "Accounting",
            "Bookkeeping",
            "Payroll Services",
            "Payroll",
            "Outsourced Compliance Officer & MLRO",
            "Outsourced Compliance",
            "MLRO Services",
            "Company Secretarial Services",
            "Residency & Visa Services",
            "Visa Services",
            "Corporate Services",
        ),
        unsupported_services=(
            "Direct Statutory Financial Auditing & Audit Opinions",
            "Direct Statutory Financial Auditing",
            "Statutory Audit",
            "Financial Auditing",
            "Audit Opinions",
            "Audit Support",
            "Business Loans, Commercial Financing & Working Capital Lending",
            "Business Loans",
            "Commercial Financing",
            "Working Capital Lending",
            "Legal Court Representation & Dispute Litigation",
            "Legal Court Representation",
            "Dispute Litigation",
            "Managed IT Infrastructure, Hardware & Helpdesk Support",
            "Managed IT Infrastructure",
            "Helpdesk Support",
            "Custom Software Development & Web Engineering",
            "Custom Software Development",
            "Web Engineering",
            "Executive Search & Commercial Staffing Recruitment",
            "Commercial Staffing Recruitment",
            "Commercial Branding, Digital Marketing & PR Campaigns",
            "Commercial Branding",
            "Digital Marketing",
            "PR Campaigns",
            "Salary Benchmarking",
        ),
    ),
    "MS Kapital": PortfolioCatalogue(
        supported_services=(
            "Valuation",
            "Business Valuation",
            "Investment Banking",
            "Transaction Advisory",
            "Deal Scouting",
            "Deal Sourcing",
            "Exit Strategy & Execution",
            "Exit Strategy",
            "Buy a Business Advisory",
            "Sell a Business Advisory",
            "Mergers and acquisitions",
            "M&A",
            "Due Diligence",
            "Capital Raising",
        ),
        unsupported_services=(
            "Statutory Audit & Financial Accounting",
            "Statutory Audit",
            "Financial Accounting",
            "Commercial Lending & Debt Financing",
            "Commercial Lending",
            "Debt Financing",
            "Tax Compliance & Regulatory Filings",
            "Tax Compliance",
            "Regulatory Filings",
            "Job Recruiting & Executive Search",
            "Job Recruiting",
            "Business Formation & Trade Licensing",
            "Business Formation",
            "Trade Licensing",
            "Franchise & Retail Property Brokering",
            "Franchise Brokering",
            "Retail Property Brokering",
            "Distressed Asset & Liquidation Auctioning",
            "Distressed Asset & Liquidation Auction",
        ),
    ),
    "Dot&": PortfolioCatalogue(
        supported_services=(
            "Executive Search",
            "Technology Hiring",
            "Reputation Risk Intelligence (RRI)",
            "Reputation Risk Intelligence",
            "RRI",
            "Social Investment Intelligence (SII)",
            "Social Investment Intelligence",
            "SII",
            "Cyber Strategy & Governance",
            "Cyber Risk & Resilience",
            "Digital & Asset Protection",
            "Cyber Advisory & Assurance",
        ),
        unsupported_services=(
            "Managed IT services / helpdesk support",
            "Managed IT services",
            "Helpdesk support",
            "High-volume, contingent, or entry-level recruitment",
            "High-volume recruitment",
            "Entry-level recruitment",
            "Contingent recruitment",
            "Custom software engineering / application development",
            "Custom software engineering",
            "Application development",
            "Commercial PR / public branding campaigns",
            "Commercial PR",
            "Public branding campaigns",
            "Managed Security Operations Center (SOC) / 24/7 SIEM monitoring",
            "Managed Security Operations Center",
            "SOC",
            "24/7 SIEM monitoring",
        ),
    ),
    "E7 Estates": PortfolioCatalogue(
        supported_services=(
            "Off-Market Deal Advisory",
            "Commercial & Residential Real Estate Advisory",
            "Real Estate Advisory",
            "Commercial Real Estate Advisory",
            "Residential Real Estate Advisory",
            "Off-Plan Property Investment Advisory",
            "Off-Plan Property Investment",
            "Land Acquisition & Allocation Advisory",
            "Land Acquisition",
            "Rental Yield Advisory",
            "Luxury Real Estate",
            "Property Purchase",
            "Off-market luxury properties",
        ),
        unsupported_services=(
            "Public Real Estate Portal Listings & Mass Brokerage",
            "Public Real Estate Portal Listings",
            "Mass Brokerage",
            "Property Management, Facility Maintenance & Tenant Operations",
            "Property Management",
            "Facility Maintenance",
            "Tenant Operations",
            "Mortgage Lending, Debt Financing & Bank Underwriting",
            "Mortgage Lending",
            "Debt Financing",
            "Bank Underwriting",
            "Architectural Engineering, Interior Design & Construction Contracting",
            "Architectural Engineering",
            "Interior Design",
            "Construction Contracting",
            "Short-Term Holiday Let Management & Vacation Rentals",
            "Short-Term Holiday Let Management",
            "Vacation Rentals",
        ),
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

    # Services offered by other portfolios in the group are unsupported for this portfolio
    other_portfolio_services = {
        item.casefold()
        for p_name, p_cat in PORTFOLIO_CATALOGUE.items()
        if p_name != portfolio
        for item in p_cat.supported_services
    }
    if normalized_service in other_portfolio_services:
        return "unsupported"

    return "unknown"
