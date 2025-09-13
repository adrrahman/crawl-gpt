import asyncio

import nest_asyncio
from browser_use import Agent, Browser, ChatOpenAI
from dotenv import load_dotenv

from scrape_gpt.tools.create import create_tools

load_dotenv()
nest_asyncio.apply()


async def main(session_id: str, prompt: str, link: str = None):
    if link:
        tools = create_tools()

        browser = Browser(keep_alive=True)
        await browser.start()
        agent = Agent(
            task=f"""
            Go to {link} {prompt}
            If you need to access subpage, before using go_to_url tool, use extract_links_from_dom to get the links
            Always call export_dataframe as last step to export previous extracted content to a pandas dataframe
            """,
            llm=ChatOpenAI(model="gpt-4.1-mini"),
            browser_session=browser,
            save_conversation_path=f"./.session_data/{session_id}/conversation",
            file_system_path=f"./.session_data/{session_id}/files",
            tools=tools,
        )
        _ = await agent.run()
        await browser.kill()
    else:
        print("Please provide a link to start with.")


if __name__ == "__main__":
    # asyncio.run(
    #     main(
    #         session_id="medrecruit",
    #         link="https://medrecruit.medworld.com/jobs/list?location=New+South+Wales&page=1",
    #         prompt="extract first 3 job details including job title, company name, location, salary, job type, experience level, date posted and job description.",
    #     )
    # )

    # asyncio.run(
    #     main(
    #         session_id="1",
    #         link="https://www.azsoccerassociation.org/member-clubs/",
    #         prompt="Find emails and phone number of first 3 clubs",
    #     )
    # )

    asyncio.run(
        main(
            session_id="printer-1",
            link="https://support.hp.com/us-en/drivers/printers",
            prompt="Find software and driver details for each printer page by clicking each popular printer page",
        )
    )
