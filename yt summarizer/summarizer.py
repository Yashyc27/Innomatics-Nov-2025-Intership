import os
import time
from typing import List
from dotenv import load_dotenv

from langchain_mistralai import ChatMistralAI
from langchain_community.document_loaders import YoutubeLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate

from langchain_core.run_nables import RunnableLambda

from langchain_core.runnables import RunnableLambda

from langchain_core.output_parsers import StrOutputParser

load_dotenv()
os.environ['MISTRAL_API_KEY'] = os.getenv('MISTRAL_API_KEY')

mistral_model = ChatMistralAI(model="mistral-large-latest", temperature=0.2)

def fetch_transcript(youtube_url: str) -> str:
    try:
        loader = YoutubeLoader.from_youtube_url(youtube_url, add_video_info=True)
        docs = loader.load()
        if not docs:
            raise ValueError("No transcript available")
        return docs[0].page_content
    except Exception as e:
        raise Exception(f"Fetch Error: {str(e)}")

def segment_text(text: str, size: int = 4000) -> List[str]:
    divider = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " "]
    )
    return divider.split_text(text)

def process_long_video(raw_text: str):
    parts = segment_text(raw_text)
    final_draft = ""
    for part in parts:
        time.sleep(1.2)
        refine_prompt = f"Current Summary: {final_draft}\n\nAdd this segment: {part}\n\nTask: Refine the summary."
        response = mistral_model.invoke(refine_prompt)
        final_draft = response.content
    return final_draft

def route_input(url: str):
    content = fetch_transcript(url)
    if len(content) > 4000:
        return process_long_video(content)
    return content

blog_editor_role = "You are a Technical Content Editor."
article_structure = "Write a professional technical article based on this: {transcript}"
frontend_role = "You are a Senior Web Architect. Output code inside --html--, --css--, and --js-- tags."
frontend_task = "Build a Medium-style page for: {article_content}"

article_gen_prompt = ChatPromptTemplate.from_messages([
    ("system", blog_editor_role),
    ("user", article_structure)
])

web_dev_prompt = ChatPromptTemplate.from_messages([
    ("system", frontend_role),
    ("user", frontend_task)
])

full_service_pipeline = (
    RunnableLambda(route_input) 
    | article_gen_prompt 
    | mistral_model 
    | StrOutputParser() 
    | web_dev_prompt 
    | mistral_model 
    | StrOutputParser()
)