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
            go to {link} {prompt}
            """,
            llm=ChatOpenAI(model="gpt-4.1-mini"),
            browser_session=browser,
            save_conversation_path=f"./.session_data/{session_id}/conversation",
            file_system_path=f"./.session_data/{session_id}/files",
            tools=tools,
        )
        _ = await agent.run()
        print("browser agent flow done")
        await browser.kill()
        print("browser killed")
    return


if __name__ == "__main__":
    asyncio.run(
        main(
            session_id="7",
            link="https://medrecruit.medworld.com/jobs/list?location=New+South+Wales&page=1",
            prompt="use extract_info_from_subpages tool with param {subpage_links_to_extract: ['https://medrecruit.medworld.com/jobs/registrar/obstetrics-and-gynaecology/jn00306752'], information_to_find: 'job details'}",
        )
    )
