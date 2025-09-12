import json
import os
from typing import List

from browser_use import ActionResult
from browser_use.filesystem.file_system import FileSystem
from pydantic import BaseModel, Field
from scrapegraphai.graphs import SmartScraperMultiLiteGraph


class ExtractInfoInput(BaseModel):
    information_to_find: str = Field(
        ..., description="what information to find on each subpage"
    )
    subpage_links_to_extract: List[str] = Field(
        ..., description="subpage link(s) to extract information from"
    )


async def extract_info_from_subpages(params: ExtractInfoInput, file_system: FileSystem, available_file_paths: List[str]):
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
        
        extracted_content = json.dumps(result)

        save_result = await file_system.save_extracted_content(extracted_content)
        memory = f'Extracted content from for query: {params["information_to_find"]} from {params["subpage_links_to_extract"]}\nContent saved to file system: {save_result} and displayed in <read_state>.'

        return ActionResult(
            extracted_content=extracted_content,
            include_extracted_content_only_once=True,
            long_term_memory=memory,
        )

    except Exception as e:
        error_msg = f"❌ Extract subpage(s) information failed: {str(e)}"
        return ActionResult(error=error_msg)
