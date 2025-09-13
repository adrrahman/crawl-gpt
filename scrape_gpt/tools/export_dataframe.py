
import json
import pandas as pd
import os
from typing import Any, Dict, List

from browser_use import ActionResult
from browser_use.llm import BaseChatModel
from browser_use.llm.messages import SystemMessage, UserMessage
from browser_use.filesystem.file_system import FileSystem, CsvFile
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from dotenv import load_dotenv
from pydantic import BaseModel, Field
load_dotenv()

desc = "Export previous extracted information to a pandas dataframe."


class CsvData(BaseModel):
    data: List[Dict[str, Any]] = Field(
        description="List of dictionaries representing the data"
    )


async def export_dataframe(file_to_export: List[str], file_system: FileSystem):
    """
    Custom action that export previous extracted information to a pandas dataframe.
    """
    try:
        file_content = ""
        for file in file_to_export:
            if file not in file_system.files:
                return ActionResult(error=f'❌ File "{file}" not found in the file system.')
            file_content += await file_system.read_file(file)
            file_content += "\n"

        example = """
        [
            {"column1": "value1", "column2": 123, "column3": "value3"},
            {"column1": "value4", "column2": 456, "column3": "value6"}
        ]
        """
        template = """
        You are an expert data analyst. Given the following extracted content, convert it into a JSON structured dictionary that can be imported using pandas.Dataframe().
        Ideal output list of key value pairs where keys are column names and values are either strings or numbers.
        Example output:
        {example}
        
        Transform an attribute to integer if it represents a numeric value.
        e.g. rate should be 5 not "5" or "$1000" should be 1000 not "$1000".
        use rate_type column to determine if rate is per hour or per year and convert accordingly.
        Break down complex attributes into simpler ones if needed.
        e.g. location attribute should be broken down to city, state and country if possible.
        Don't include any text other than the JSON dictionary in your response.

        {extracted_content}
        """
        llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-4.1", temperature=0)
        parser = JsonOutputParser()
        prompt = PromptTemplate(
            template=template,
            input_variables=["example", "extracted_content"],
        )
        chain = prompt | llm | parser

        response = await chain.ainvoke({"example": example, "extracted_content": file_content})
        df = pd.DataFrame(response)

        initial_filename = f'extracted_csv_{file_system.extracted_content_count}'
        extracted_filename = f'{initial_filename}.csv'
        content_example = df.head().to_string()
        file_obj = CsvFile(name=initial_filename, content=content_example)
        df.to_csv(file_system.data_dir / extracted_filename, index=False)
        file_system.files[extracted_filename] = file_obj
        file_system.extracted_content_count += 1

        success_msg = f'✅ Extracted dataframe saved to {extracted_filename} successfully.'

        return ActionResult(extracted_content=success_msg + content_example, include_in_memory=True, long_term_memory=success_msg)

    except Exception as e:
        error_msg = f'❌ Extract dataframe(s) failed: {str(e)}'
        return ActionResult(error=error_msg)