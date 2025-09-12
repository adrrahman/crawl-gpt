import asyncio
import json
import os
from typing import List

import nest_asyncio
from browser_use import ActionResult, Agent, Browser, BrowserSession, ChatOpenAI, Tools
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from scrapegraphai.graphs import SmartScraperGraph, SmartScraperMultiLiteGraph

from scrape_gpt.tools.base import tools

nest_asyncio.apply()

load_dotenv()


class ExtractInfoInput(BaseModel):
    information_to_find: str = Field(
        ..., description="what information to find on each subpage"
    )
    subpage_links_to_extract: List[str] = Field(
        ..., description="a single subpage link to extract information from"
    )


async def extract_links_from_dom(subpage_to_find: str, browser_session: BrowserSession):
    """
    Custom action that extract links from a webpage DOM.
    """
    try:
        cdp_session = await browser_session.get_or_create_cdp_session()
        body_id = await cdp_session.cdp_client.send.DOM.getDocument(
            session_id=cdp_session.session_id
        )
        page_html_result = await cdp_session.cdp_client.send.DOM.getOuterHTML(
            params={"backendNodeId": body_id["root"]["backendNodeId"]},
            session_id=cdp_session.session_id,
        )
        page_html = page_html_result["outerHTML"]
        current_url = await browser_session.get_current_page_url()

        scraper = SmartScraperGraph(
            prompt=f"Extract links leading to {subpage_to_find}. Use full URL not only relative path. Current url is "
            + current_url,
            source=page_html,
            config={
                "llm": {
                    "api_key": os.getenv("OPENAI_API_KEY"),
                    "model": "gpt-4.1-mini",
                },
            },
        )
        result = scraper.run()
        success_msg = f'✅ Extracted {json.dumps(result["content"])} links leading to {subpage_to_find}'

        return ActionResult(
            extracted_content=success_msg,
            include_in_memory=True,
            long_term_memory=f'Extracted {subpage_to_find} links with number of {len(result["content"])}',
        )

    except Exception as e:
        error_msg = f"❌ Extract links from DOM failed: {str(e)}"
        return ActionResult(error=error_msg)


async def extract_info_from_subpages(params: ExtractInfoInput):
    """
    Custom action that extract information from subpage links.
    """
    try:

        scraper = SmartScraperMultiLiteGraph(
            prompt=f"Extract {params['information_to_find']}",
            source=params["subpage_links_to_extract"],
            config={
                "llm": {
                    "api_key": os.getenv("OPENAI_API_KEY"),
                    "model": "gpt-4.1-mini",
                },
            },
        )
        result = scraper.run()
        success_msg = f'✅ Extracted {json.dumps(result)} from {params["subpage_links_to_extract"]}'

        return ActionResult(
            extracted_content=success_msg,
            include_in_memory=True,
            long_term_memory=success_msg,
        )

    except Exception as e:
        error_msg = f"❌ Extract subpage(s) information failed: {str(e)}"
        return ActionResult(error=error_msg)


async def extract_current_page_info(
    information_to_find: str, browser_session: BrowserSession
):
    """
    Custom action that extract information from current page.
    """
    try:

        cdp_session = await browser_session.get_or_create_cdp_session()
        body_id = await cdp_session.cdp_client.send.DOM.getDocument(
            session_id=cdp_session.session_id
        )
        page_html_result = await cdp_session.cdp_client.send.DOM.getOuterHTML(
            params={"backendNodeId": body_id["root"]["backendNodeId"]},
            session_id=cdp_session.session_id,
        )
        page_html = page_html_result["outerHTML"]

        scraper = SmartScraperGraph(
            prompt=f"Extract {information_to_find}.",
            source=page_html,
            config={
                "llm": {
                    "api_key": os.getenv("OPENAI_API_KEY"),
                    "model": "gpt-4.1-mini",
                },
            },
        )
        result = scraper.run()
        success_msg = f"✅ Extracted {json.dumps(result)}"

        return ActionResult(
            extracted_content=success_msg,
            include_in_memory=True,
            long_term_memory=success_msg,
        )

    except Exception as e:
        error_msg = f"❌ Extract subpage(s) information failed: {str(e)}"
        return ActionResult(error=error_msg)


async def main(session_id: str, prompt: str, link: str = None):
    if link:
        tools = Tools(exclude_actions=["extract_structured_data"])
        _ = tools.registry.action(
            "Extract links from a webpage DOM using a specialized agent"
        )(extract_links_from_dom)
        _ = tools.registry.action(
            "Extract information from several subpage links using a specialized agent e.g. extract_info_from_subpages with param {information_to_find: 'job details', subpage_links_to_extract: ['link1', 'link2']}"
        )(extract_info_from_subpages)
        _ = tools.registry.action(
            "Extract information from current page using a specialized agent"
        )(extract_current_page_info)

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
