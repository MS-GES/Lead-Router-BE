
import asyncio

from src.mail.helper import screen_lead_exception


async def main():
    test_cases = [
        {
            "name": "Job seeker",
            "client_name": "John Doe",
            "client_notes": (
                "I am looking for a frontend developer job. "
                "Please find my CV attached."
            ),
            "expected": "job_seeker",
        },
        {
            "name": "Vendor",
            "client_name": "Sales Representative",
            "client_notes": (
                "We sell CRM software to companies. "
                "Would you like to purchase a subscription?"
            ),
            "expected": "vendor",
        },
        {
            "name": "Normal business enquiry",
            "client_name": "Jane Doe",
            "client_notes": (
                "I need help incorporating a company in the UAE."
            ),
            "expected": "none",
        },
        {
            "name": "Empty notes",
            "client_name": "Unknown",
            "client_notes": "",
            "expected": "manual_review",
        },
    ]

    for case in test_cases:
        print(f"\nTesting: {case['name']}")

        result = await screen_lead_exception(
            client_name=case["client_name"],
            client_notes=case["client_notes"],
        )

        print("Expected:", case["expected"])
        print("Actual:  ", result.category)
        print("Reason:  ", result.reason)


if __name__ == "__main__":
    asyncio.run(main())
