"""Example: post-parse prompting programmatic usage."""

import asyncio
import logging
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, field_validator

from doc_parser.core.registry import ParserRegistry
from doc_parser.core.settings import Settings

# mypy: ignore-errors

logging.basicConfig(level=logging.INFO)


class QuestionAnswer(BaseModel):
    """A model representing a question and its corresponding answer extracted from a document.

    Usage:
        >>> qa = QuestionAnswer(question='What is AI?', answer='AI is artificial intelligence')
        >>> print(qa)
        question='What is AI?' answer='AI is artificial intelligence'
    """

    question: str = Field(description="The question in the document")
    answer: str = Field(description="The answer to the question")


class DocumentSummary(BaseModel):
    """A model capturing metadata and detailed summary of a document.

    Attributes:
        authors (list[str]): Who is the author(s) of the document.
        title (str): Title of the document.
        date (Optional[str]): Date of the document.
        publisher (Optional[str]): Publisher of the document.
        document_type (str): Type of the document.
        summary (str): A brief summary of the document.
        topic_timelessness (str): Whether the topic is timeless or time sensitive.
        keywords (list[str]): Key keywords or themes from the document.
        key_points (list[str]): List of key points and takeaways.
        key_questions (list[QuestionAnswer]): List of key questions and answers.
        key_recommendations (list[str]): List of key recommendations.
        key_risks (list[str]): List of key risks.
        key_assumptions (list[str]): List of key assumptions.

    Usage:
        >>> data = {
        ...     'Author': ['Alice', 'Bob'],
        ...     'Title': 'Example Doc',
        ...     'Document Type': 'blog_post',
        ...     'Summary': 'This document discusses important topics.',
        ...     'Topic Timelessness': 'timeless',
        ...     'Keywords': ['AI', 'ML'],
        ...     'Key Points': ['Point1', 'Point2'],
        ...     'Key Questions': [{'question': 'Q?', 'answer': 'A'}],
        ...     'Key Recommendations': ['Rec1'],
        ...     'Key Risks': ['Risk1'],
        ...     'Key Assumptions': ['Assumption1']
        ... }
        >>> summary = DocumentSummary.parse_obj(data)
        >>> print(summary.authors)
        ['Alice', 'Bob']
    """

    model_config = ConfigDict(populate_by_name=True)

    authors: list[str] = Field(
        default_factory=list,
        alias="Author",
        description="Who is the author of the document?",
    )
    title: str = Field(
        default="",
        alias="Title",
        description="What is the title of the document?",
    )
    date: str | None = Field(
        default=None, alias="Date", description="What is the date of the document?"
    )
    publisher: str | None = Field(
        default=None,
        alias="Publisher",
        description="Who is the publisher of the document?",
    )
    document_type: str = Field(
        default="other",
        alias="Document Type",
        description="Type of document (one of: bank_broker_report, academic_research, whitepaper, blog_post, financial_statement, marketing_material, other)",
    )
    summary: str = Field(
        default="",
        alias="Summary",
        description="Write a less than 250 word summary of the text below.",
    )
    topic_timelessness: str = Field(
        default="",
        alias="Topic Timelessness",
        description="Is the topic timeless or time sensitive (e.g time sensitive: if it is about a current event, stock, or market, timeless: if it is about a fundamental concept, theory, or idea)?",
    )
    keywords: list[str] = Field(
        default_factory=list,
        alias="Keywords",
        description="Write a list of up to 5 key keywords or themes from the document.",
    )
    key_points: list[str] = Field(
        default_factory=list,
        alias="Key Points",
        description="Write a list of the key points and takeaways from the document.",
    )
    key_questions: list[QuestionAnswer] = Field(
        default_factory=list,
        alias="Key Questions",
        description='Write a list of the key questions in the document and answers to those questions. For each question, include the question and the answer in a json format {{"question": <Question>, "answer": <Answer>}}.',
    )
    key_recommendations: list[str] = Field(
        default_factory=list,
        alias="Key Recommendations",
        description="Write a list of the key recommendations from the document.",
    )
    key_risks: list[str] = Field(
        default_factory=list,
        alias="Key Risks",
        description="Write a list of the key risks from the document.",
    )
    key_assumptions: list[str] = Field(
        default_factory=list,
        alias="Key Assumptions",
        description="Write a list of the key assumptions from the document.",
    )

    @field_validator("authors", mode="before")
    def ensure_authors_list(cls, v):
        if isinstance(v, str):
            return [v]
        return v

    @field_validator("date", mode="before")
    def ensure_date(cls, v):
        if v is None:
            return ""
        return v

    @field_validator("publisher", mode="before")
    def ensure_publisher(cls, v):
        if v is None:
            return ""
        return v


async def main():
    load_dotenv() 

    cfg = Settings(
        post_prompt="Summarise the document using the following model: {{response_model}}",
        response_model="examples.post_processing_example.DocumentSummary",
        use_cache=False,
    )
    pdf_path = Path(
        "/Users/joneickmeier/Documents/Papers Library/JFDS-2025-Varlashova-jfds.2025.1.191.pdf"
    )  # Replace with your PDF
    parser = ParserRegistry.from_path(pdf_path, cfg)
    result = await parser.parse(pdf_path)
    # print("Primary content length:", len(result.content))
    if result.post_content:
        # If the post-processed content is a Pydantic model, leverage its
        # built-in JSON serialisation for a nicely formatted, indented output.
        from pydantic import BaseModel  # Local import to avoid unused-import warnings

        if isinstance(result.post_content, BaseModel):
            print(
                "\nPost-processed output:\n",
                result.post_content.model_dump_json(indent=2),
            )
        else:
            import json
            print(
                "\nPost-processed output:\n",
                json.dumps(result.post_content, indent=2, default=str),
            )



if __name__ == "__main__":
    asyncio.run(main())
