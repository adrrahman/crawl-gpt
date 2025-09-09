import asyncio
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
from browser_use import Agent, ChatGoogle


class RanchProfile(BaseModel):
    type: str
    member: str
    prefix: str
    member_name: float
    dba: str
    city: str
    state_or_province: str


async def main():
    agent = Agent(
        task="Navigate https://shorthorn.digitalbeef.com/ and find all ranches, prioritize using each dropdown instead of text box in form. Use extract_structured_data tool using schema provided.",
        llm=ChatGoogle(model="gemini-2.0-flash"),
        output_model_schema=RanchProfile
    )
    await agent.run()


asyncio.run(main())
