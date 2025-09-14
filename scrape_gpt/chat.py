import argparse
import asyncio
import glob
import json
import os

import nest_asyncio
import pandas as pd
from browser_use import Agent, ChatOpenAI
from dotenv import load_dotenv
from langchain.agents.agent_types import AgentType
from langchain_core.utils.json import parse_json_markdown
from langchain_experimental.agents.agent_toolkits import \
    create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI as LangChainChatOpenAI

from scrape_gpt.tools.create import create_tools

load_dotenv()
nest_asyncio.apply()

with open("scrape_gpt/prompt/system.md", "r") as f:
    system_prompt = f.read()


async def main(session_id: str, prompt: str, link: str = None):
    chat_history_path = f"./.session_data/{session_id}/chat_history.json"
    if os.path.exists(chat_history_path):
        with open(chat_history_path, "r") as f:
            chat_history = json.load(f)
    else:
        chat_history = []

    if link: # TODO: create route to BrowseAgent or DataFrameAgent
        tools = create_tools()
        agent = Agent(
            task=f"""
            Go to {link} {prompt}
            
            If you have difficulty clicking a link, use extract_links_from_dom tool to get all links on the page and then pick the relevant one to use in go_to_url tool.
            Always save requested information using write_to_file or extract_current_page_info tool.
            Use export_dataframe once as last step to export previous extracted_content_[number].md to a pandas dataframe
            """,
            llm=ChatOpenAI(model="gpt-4.1"),
            save_conversation_path=f"./.session_data/{session_id}/conversation",
            file_system_path=f"./.session_data/{session_id}/files",
            override_system_message=system_prompt,
            tools=tools,
        )
        history = await agent.run()

        chat_history.append({"role": "user", "text": prompt, "link": link})
        csv_path = list(agent.file_system.files)[-1]
        results = pd.read_csv(agent.file_system.data_dir / csv_path).to_dict(orient='records')
        chat_history.append({"role": "assistant", "text": history.final_result(), "results": results})
        with open(chat_history_path, "w") as f:
            json.dump(chat_history, f, indent=4)

        return history.final_result(), results
    else:
        dframe_paths = glob.glob(f"./.session_data/{session_id}/*.csv")
        dframes = []
        for path in dframe_paths:
            dframes.append(pd.read_csv(path))
        agent = create_pandas_dataframe_agent(
            LangChainChatOpenAI(temperature=0, model="gpt-4.1", api_key=os.getenv("OPENAI_API_KEY")),
            dframes,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            allow_dangerous_code=True,
        )
        agent_result = agent.invoke(prompt + "\nReturn in json format")
        results = parse_json_markdown(agent_result["output"])

        chat_history.append({"role": "user", "text": prompt})
        chat_history.append({"role": "assistant", "text": agent_result["output"], "results": results})

        with open(chat_history_path, "w") as f:
            json.dump(chat_history, f, indent=4)
        
        return agent_result["output"], results


def example():
    # asyncio.run(
    #     main(
    #         session_id="medrecruit",
    #         link="https://medrecruit.medworld.com/jobs/list?location=New+South+Wales&page=1",
    #         prompt="visit first 3 job details page from page 1-3 (total 9 jobs); extract job title, company name, location, salary, job type, experience level, date posted and job description.",
    #     )
    # )

    asyncio.run(
        main(
            session_id="medrecruit",
            prompt="Filter data that have pay higher than $2,500 per day only.",
        )
    )

    # asyncio.run(
    #     main(
    #         session_id="club",
    #         link="https://www.azsoccerassociation.org/member-clubs/",
    #         prompt="Find club name, emails, and phone number of first 5 clubs",
    #     )
    # )

    # asyncio.run(
    #     main(
    #         session_id="printer",
    #         link="https://support.hp.com/us-en/drivers/printers",
    #         prompt="Visit first 5 popular printer links, save details about printer name, software/drivers, version, file size, etc",
    #     )
    # )


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run scraping agents.")
    parser.add_argument(
        "--session_id",
        type=str,
        required=True,
        help="Specify session id to run",
    )
    parser.add_argument(
        "--link",
        type=str,
        default="",
        help="Specify link to start with",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        required=True,
        help="Specify description to run",
    )
    args = parser.parse_args()
    text, results = asyncio.run(main(args.session_id, args.prompt, args.link))
    
    print("TEXT: ", text)
    print("RESULTS: ", results)
