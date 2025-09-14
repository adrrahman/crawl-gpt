import json
import os

from browser_use import ActionResult, BrowserSession
from browser_use.filesystem.file_system import FileSystem
from scrapegraphai.graphs import SmartScraperGraph

from scrape_gpt.tools.export_dataframe import export_dataframe
from scrape_gpt.tools.extract_subpages import extract_info_from_subpages


async def extract_links_from_dom(browser_session: BrowserSession):
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
            prompt=f"Extract all links. Use full URL not only relative path. Current url is "
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
        success_msg = f'✅ Extracted links {json.dumps(result["content"])}'

        return ActionResult(
            extracted_content=success_msg,
            include_in_memory=True,
            long_term_memory=success_msg,
        )

    except Exception as e:
        error_msg = f"❌ Extract links from DOM failed: {str(e)}"
        return ActionResult(error=error_msg)


async def extract_current_page_info(
    information_to_find: str, browser_session: BrowserSession, file_system: FileSystem
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
        extracted_content = json.dumps(result)

        save_result = await file_system.save_extracted_content(extracted_content)
        memory = f'Extracted content from for query: {information_to_find}\nContent saved to file system: {save_result} and displayed in <read_state>.'

        return ActionResult(
            extracted_content=extracted_content,
            include_extracted_content_only_once=True,
            long_term_memory=memory,
        )

    except Exception as e:
        error_msg = f"❌ Extract subpage(s) information failed: {str(e)}"
        return ActionResult(error=error_msg)
    

def create_tools():
    from browser_use import Tools

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
    _ = tools.registry.action(
        "Export previous extracted_content_ to a pandas dataframe"
    )(export_dataframe)

    return tools
