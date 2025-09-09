import asyncio
import os
import argparse

from browser_use import Agent, Browser, ChatGoogle, ChatOpenAI
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI as LangchainChatGoogle
from langchain_openai import ChatOpenAI as LangchainChatOpenAI
from pydantic import BaseModel

load_dotenv()


class Search(BaseModel):
    search_ranch: bool = False
    search_epd: bool = False
    search_animal: bool = False


class RanchProfile(BaseModel):
    type: str
    member: str
    prefix: str
    member_name: str
    dba: str
    city: str
    state_or_province: str


class Cell(BaseModel):
    epd: float
    change: float
    acc: float
    rank: str


class EPDAnimal(BaseModel):
    registration: str
    tattoo: str
    name: str
    ce_direct: Cell
    birth_weight: Cell
    weaning_weight: Cell
    yearling_weight: Cell
    milk: Cell
    tm: Cell
    ce_maternal: Cell
    stayability: Cell
    yield_grade: Cell
    carcass_weight: Cell
    ribeye_area: Cell
    fat_thickness: Cell
    marbling: Cell
    cez_dollar_index: Cell
    bmi_dollar_index: Cell
    cpi_dollar_index: Cell
    f_dollar_index: Cell


class Animal(BaseModel):
    registration: str
    prefix_or_tattoo: str
    name: str
    birth_date: str


def create_chat():
    open_ai_key = os.getenv("OPENAI_API_KEY")
    if open_ai_key:
        return LangchainChatOpenAI(model="gpt-4.1-mini")
    else:
        return LangchainChatGoogle(model="gemini-2.5-flash")


def create_llm():
    open_ai_key = os.getenv("OPENAI_API_KEY")
    if open_ai_key:
        return ChatOpenAI(model="gpt-4.1-mini")
    else:
        return ChatGoogle(model="gemini-2.5-flash")


async def main(task: str):
    chat = create_chat()
    chat_task = chat.with_structured_output(Search)
    search_task = chat_task.invoke(task)

    browser = Browser(keep_alive=True)
    await browser.start()

    if search_task.search_animal:
        task += " Reference for Animal search: Radio button index 105 is bulls (index 100 is bulls for EPD search), index 106 is both (bulls & females), index 107 is females, index 108 is Registration #, index 109 is Tattoo, index 110 is Name, and index 111 is EID. Use search field box to enter search value"

    agent = Agent(
        task=task + " Use extract_structured_data tool to data as JSON list of dictionaries",
        llm=create_llm(),
        browser_session=browser,
    )
    history = await agent.run()
    if not search_task.search_ranch and not search_task.search_epd and not search_task.search_animal:
        return history.final_result()
    else:
        browser_session = agent.browser_session
        cdp_session = await browser_session.get_or_create_cdp_session()
        try:
            body_id = await cdp_session.cdp_client.send.DOM.getDocument(
                session_id=cdp_session.session_id
            )
            page_html_result = await cdp_session.cdp_client.send.DOM.getOuterHTML(
                params={"backendNodeId": body_id["root"]["backendNodeId"]},
                session_id=cdp_session.session_id,
            )
            page_html = page_html_result["outerHTML"]
            _ = await browser_session.get_current_page_url()
        except Exception as e:
            raise RuntimeError(f"Couldn't extract page content: {e}")

        llm = create_chat()
        if search_task.search_ranch:
            structured_llm = llm.with_structured_output(RanchProfile)
            extra_prompt = "(from start to end: type, member, prefix, member_name, dba, city, state_or_province)"
        elif search_task.search_epd:
            structured_llm = llm.with_structured_output(EPDAnimal)
            extra_prompt = ""
        elif search_task.search_animal:
            structured_llm = llm.with_structured_output(Animal)
            extra_prompt = ""
        if search_task.search_epd:
            rows = page_html.split("onmouseover")[2:]
        else:
            rows = page_html.split("onmouseover")[1:]
        results = []
        for row in rows:
            response = structured_llm.invoke(
                f"extract the data from this html table row {extra_prompt} and convert to json:\n\n{row}"
            )
            results.append(response)
            print(response.model_dump_json())

        print("Agent complete, stopping browser")
        await browser.kill()

        return results


async def ranch_search_all(debug: bool = True):
    browser = Browser(keep_alive=True)
    await browser.start()

    agent = Agent(
        task="Navigate https://shorthorn.digitalbeef.com/ and find all ranch(es), prioritize using each dropdown instead of text box in form. Skip dropdown value of 'United States - All'. Use extract_clean_markdown tool to get all data and processed by another agent",
        llm=create_llm(),
        browser_session=browser,
        # output_model_schema=RanchProfile
    )
    if debug:
        await agent.run(max_steps=4)
    else:
        await agent.run()

    browser_session = agent.browser_session
    cdp_session = await browser_session.get_or_create_cdp_session()
    try:
        body_id = await cdp_session.cdp_client.send.DOM.getDocument(
            session_id=cdp_session.session_id
        )
        page_html_result = await cdp_session.cdp_client.send.DOM.getOuterHTML(
            params={"backendNodeId": body_id["root"]["backendNodeId"]},
            session_id=cdp_session.session_id,
        )
        page_html = page_html_result["outerHTML"]
        _ = await browser_session.get_current_page_url()
    except Exception as e:
        raise RuntimeError(f"Couldn't extract page content: {e}")

    llm = create_chat()
    structured_llm = llm.with_structured_output(RanchProfile)
    rows = page_html.split("onmouseover")[1:]
    results = []
    for row in rows:
        response = structured_llm.invoke(
            f"extract the data from this html table row (from start to end: type, member, prefix, member_name, dba, city, state_or_province) and convert to json:\n\n{row}"
        )
        results.append(response)
        print(response.model_dump_json())

    print("Ranch Agent complete, stopping browser")
    await browser.kill()


async def epd_search_all(debug: bool = True):
    browser = Browser(keep_alive=True)
    await browser.start()

    agent = Agent(
        task="Navigate https://shorthorn.digitalbeef.com/ and find all epd(s), iterate over each CE Direct attribute using min max gap of 1. CE Direct min 0 max 0, CE Direct min 1 max 1, and so on. Use wait tool for 15 seconds due to long time of filtering. Use extract_clean_markdown tool to get all data and processed by another agent",
        llm=create_llm(),
        browser_session=browser,
    )
    if debug:
        await agent.run(max_steps=4)
    else:
        await agent.run()

    browser_session = agent.browser_session
    cdp_session = await browser_session.get_or_create_cdp_session()
    try:
        body_id = await cdp_session.cdp_client.send.DOM.getDocument(
            session_id=cdp_session.session_id
        )
        page_html_result = await cdp_session.cdp_client.send.DOM.getOuterHTML(
            params={"backendNodeId": body_id["root"]["backendNodeId"]},
            session_id=cdp_session.session_id,
        )
        page_html = page_html_result["outerHTML"]
        _ = await browser_session.get_current_page_url()
    except Exception as e:
        raise RuntimeError(f"Couldn't extract page content: {e}")

    llm = create_chat()
    structured_llm = llm.with_structured_output(EPDAnimal)
    rows = page_html.split("onmouseover")[2:]
    results = []
    for row in rows:
        response = structured_llm.invoke(
            f"extract the data from this html table row and convert to json:\n\n{row}"
        )
        results.append(response)
        print(response.model_dump_json())

    print("EPD Agent complete, stopping browser")
    await browser.kill()


async def animal_search_all(debug: bool = True):
    browser = Browser(keep_alive=True)
    await browser.start()

    agent = Agent(
        task="Navigate https://shorthorn.digitalbeef.com/ and find all animal(s), iterate by clicking Tattoo radio button first then using search value of A-Z and 0-9. Use extract_clean_markdown tool to get all data so other agent can process it. Radio button reference: Reg is index 108 and Tattoo is index 109. Use extract_clean_markdown tool to get all data and processed by another agent",
        llm=create_llm(),
        browser_session=browser,
    )
    if debug:
        await agent.run(max_steps=5)
    else:
        await agent.run()

    browser_session = agent.browser_session
    cdp_session = await browser_session.get_or_create_cdp_session()
    try:
        body_id = await cdp_session.cdp_client.send.DOM.getDocument(
            session_id=cdp_session.session_id
        )
        page_html_result = await cdp_session.cdp_client.send.DOM.getOuterHTML(
            params={"backendNodeId": body_id["root"]["backendNodeId"]},
            session_id=cdp_session.session_id,
        )
        page_html = page_html_result["outerHTML"]
        _ = await browser_session.get_current_page_url()
    except Exception as e:
        raise RuntimeError(f"Couldn't extract page content: {e}")

    llm = create_chat()
    structured_llm = llm.with_structured_output(Animal)
    rows = page_html.split("onmouseover")[1:]
    results = []
    for row in rows:
        response = structured_llm.invoke(
            f"extract the data from this html table row and convert to json:\n\n{row}"
        )
        results.append(response)
        print(response.model_dump_json())

    print("Animal Agent complete, stopping browser")
    await browser.kill()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run scraping agents.")
    parser.add_argument(
        "--prompt",
        type=str,
        required=True,
        help="Specify description to run",
    )
    args = parser.parse_args()
    asyncio.run(main(args.prompt))
