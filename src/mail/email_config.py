# src/mail/email_config.py

PORTFOLIOS = {
    "MS": {
        "brand": "MS",
        "meeting": "30-minute introductory call",
        "booking_link": None,
    },
    "MS Kapital": {
        "brand": "MS Kapital",
        "meeting": "30-minute introductory consultation",
        "booking_link": None,
    },
    "Dot&": {
        "brand": "Dot&",
        "meeting": "30-minute introductory conversation",
        "booking_link": None,
    },
    "E7 Estates": {
        "brand": "E7 Estates",
        "meeting": "30-minute introductory call",
        "booking_link": None,
    },
}


SOURCE_LINES = {
    "Meta (Facebook)": (
        "Thank you for your interest in {brand} through Facebook."
    ),
    "Meta (Instagram)": (
        "Thank you for your interest in {brand} through Instagram."
    ),
    "LinkedIn ads": (
        "Thank you for your interest in {brand} through LinkedIn."
    ),
    "Google Ads landing page": (
        "Thank you for contacting {brand} through our website."
    ),
    "Website (SEO / organic)": (
        "Thank you for contacting {brand} through our website."
    ),
    "Google Form": (
        "Thank you for submitting your enquiry to {brand}."
    ),
}

DEFAULT_SOURCE_LINE = "Thank you for getting in touch with {brand}."