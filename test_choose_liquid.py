
import asyncio
from src.mail.helper import choose_template


async def test_choose_template():
    result = await choose_template(
 portfolio="E7",
    source="Meta (Facebook)",
    service_name="railway portal",
    message=(
        "create a ticket"
        
    ),
   
    )

    print("\n--- Liquid AI Decision ---")
    print("Result:", result)
    print("Selected scenario:", result.scenario)


if __name__ == "__main__":
    asyncio.run(test_choose_template())
